import re
from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse

from modules.auth.config import auth_settings
from modules.auth.dependencies import current_user, get_uow
from modules.tickets.api.dtos import (
    PendingTicketRequestDTO,
    SpendingRequestDTO,
    SpendingSummaryDTO,
    TicketPriceConfigurationDTO,
    TicketPriceOverviewDTO,
    TicketPriceUpdateDTO,
    TicketRequestCreateDTO,
    TicketRequestDTO,
    UserSpendingDetailDTO,
    UserSpendingDTO,
)
from modules.tickets.application.approve_ticket_request import ApproveTicketRequest
from modules.tickets.application.create_ticket_request import CreateTicketRequest
from modules.tickets.application.get_ticket_request import GetTicketRequest
from modules.tickets.application.list_pending_tickets import ListPendingTickets
from modules.tickets.application.print_ticket_request import PrintTicketRequest
from modules.tickets.application.set_ticket_price import SetTicketPrice
from modules.tickets.domain.entities.ticket_price import DEFAULT_TICKET_PRICE
from modules.tickets.infrastructure.html_ticket_printer import HtmlTicketPrinter
from modules.tickets.infrastructure.ticket_email_sender import (
    send_approval_email,
    send_reception_emails,
)
from modules.users.api.dependencies import (
    require_accountant,
    require_approver,
    require_spending_access,
)
from modules.users.domain.entities.users import User, UserRole
from shared.uow import UnitOfWork

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _period_range(period: str | None) -> tuple[str, datetime, datetime]:
    period = period or datetime.now(UTC).strftime("%Y-%m")
    try:
        if re.fullmatch(r"\d{4}", period):
            start = datetime(int(period), 1, 1, tzinfo=UTC)
            return period, start, datetime(start.year + 1, 1, 1, tzinfo=UTC)
        if re.fullmatch(r"\d{4}-\d{2}", period):
            start = datetime(int(period[:4]), int(period[5:]), 1, tzinfo=UTC)
            end = (
                datetime(start.year + 1, 1, 1, tzinfo=UTC)
                if start.month == 12
                else datetime(start.year, start.month + 1, 1, tzinfo=UTC)
            )
            return period, start, end
    except ValueError:
        pass
    raise HTTPException(
        status_code=422,
        detail="El periodo debe tener formato YYYY-MM o YYYY",
    )


# Estos endpoints para los empleados
@router.post("/", response_model=TicketRequestDTO, status_code=status.HTTP_201_CREATED)
async def create_ticket_request(
    data: TicketRequestCreateDTO,
    background_tasks: BackgroundTasks,
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    user: Annotated[User, Depends(current_user)],
) -> TicketRequestDTO:
    recipients = [
        candidate.email
        for candidate in await unit_of_work.users.list_all()
        if candidate.role == UserRole.APPROVER
    ]
    ticket_request = await CreateTicketRequest(unit_of_work).create(data.cantidad, user.id)
    if recipients:
        background_tasks.add_task(
            send_reception_emails,
            recipients,
            ticket_request,
            user,
            f"{auth_settings.success_redirect_url.rstrip('/')}/recepcion",
        )
    return TicketRequestDTO.model_validate(ticket_request)


@router.get("/", response_model=list[TicketRequestDTO])
async def list_ticket_requests(
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    user: Annotated[User, Depends(current_user)],
) -> list[TicketRequestDTO]:
    return [
        TicketRequestDTO.model_validate(ticket)
        for ticket in await unit_of_work.ticket_requests.list_by_creator(user.id)
    ]


## Estos endpoints son solo para el rol de aprobador
@router.get("/pending", response_model=list[PendingTicketRequestDTO])
async def list_pending_ticket_requests(
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    _: Annotated[User, Depends(require_approver)],
) -> list[PendingTicketRequestDTO]:
    return [
        PendingTicketRequestDTO.model_validate(ticket)
        for ticket in await ListPendingTickets(unit_of_work).list()
    ]


@router.get("/spending", response_model=SpendingSummaryDTO)
async def get_spending(
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    _: Annotated[User, Depends(require_spending_access)],
    period: str | None = None,
) -> SpendingSummaryDTO:
    period, start, end = _period_range(period)
    users = await unit_of_work.ticket_requests.spending_by_user(start, end)
    total = sum((user.total_gastado for user in users), Decimal("0.00"))
    return SpendingSummaryDTO(
        period=period,
        total_gastado=total,
        tickets_emitidos=sum(user.tickets_emitidos for user in users),
        gasto_medio_por_usuario=(
            (total / len(users)).quantize(Decimal("0.01")) if users else Decimal("0.00")
        ),
        usuarios=[UserSpendingDTO.model_validate(user) for user in users],
    )


@router.get("/spending/users/{user_id}", response_model=UserSpendingDetailDTO)
async def get_user_spending(
    user_id: UUID,
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    _: Annotated[User, Depends(require_spending_access)],
    period: str | None = None,
) -> UserSpendingDetailDTO:
    period, start, end = _period_range(period)
    user = await unit_of_work.users.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    requests = await unit_of_work.ticket_requests.spending_requests(user_id, start, end)
    return UserSpendingDetailDTO(
        period=period,
        user_id=user.id,
        nombre=user.name,
        email=user.email,
        total_gastado=sum((request.total_gastado for request in requests), Decimal("0.00")),
        tickets_emitidos=sum(request.tickets_emitidos for request in requests),
        solicitudes=[SpendingRequestDTO.model_validate(request) for request in requests],
    )


@router.get("/price-configurations", response_model=TicketPriceOverviewDTO)
async def get_ticket_price_configurations(
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    _: Annotated[User, Depends(require_accountant)],
) -> TicketPriceOverviewDTO:
    history = await unit_of_work.ticket_requests.list_price_configurations()
    current = history[0] if history else None
    return TicketPriceOverviewDTO(
        precio_unitario=current.precio_unitario if current else DEFAULT_TICKET_PRICE,
        current_configuration_id=current.id if current else None,
        historial=[TicketPriceConfigurationDTO.model_validate(item) for item in history],
    )


@router.post(
    "/price-configurations",
    response_model=TicketPriceConfigurationDTO,
    status_code=status.HTTP_201_CREATED,
)
async def set_ticket_price(
    data: TicketPriceUpdateDTO,
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    user: Annotated[User, Depends(require_accountant)],
) -> TicketPriceConfigurationDTO:
    try:
        configuration = await SetTicketPrice(unit_of_work).set(
            data.precio_unitario,
            user.id,
            user.name,
            data.expected_configuration_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    return TicketPriceConfigurationDTO.model_validate(configuration)


@router.get("/{ticket_request_id}", response_model=TicketRequestDTO)
async def get_ticket_request(
    ticket_request_id: UUID,
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    user: Annotated[User, Depends(current_user)],
) -> TicketRequestDTO:
    try:
        return TicketRequestDTO.model_validate(
            await GetTicketRequest(unit_of_work).get(ticket_request_id, user.id)
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.get("/pending/{ticket_request_id}", response_model=TicketRequestDTO)
async def get_pending_ticket_request(
    ticket_request_id: UUID,
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    _: Annotated[User, Depends(require_approver)],
) -> TicketRequestDTO:
    try:
        ticket_request = await GetTicketRequest(unit_of_work).get(ticket_request_id)
        if ticket_request.status.value != "pending":
            raise ValueError("La solicitud no está pendiente")
        return TicketRequestDTO.model_validate(ticket_request)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.post("/{ticket_request_id}/approve", response_model=TicketRequestDTO)
async def approve_ticket_request(
    ticket_request_id: UUID,
    background_tasks: BackgroundTasks,
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    user: Annotated[User, Depends(require_approver)],
) -> TicketRequestDTO:
    try:
        ticket_request = await ApproveTicketRequest(unit_of_work).approve(
            ticket_request_id, user.id
        )
        requester = await unit_of_work.users.get_by_id(ticket_request.created_by_id)
        if requester is not None:
            background_tasks.add_task(
                send_approval_email,
                requester.email,
                ticket_request,
                requester,
            )
        return TicketRequestDTO.model_validate(ticket_request)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.get("/{ticket_request_id}/print", response_class=HTMLResponse)
async def print_ticket_request(
    request: Request,
    ticket_request_id: UUID,
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    user: Annotated[User, Depends(current_user)],
) -> HTMLResponse:
    try:
        return await PrintTicketRequest(unit_of_work, HtmlTicketPrinter()).render(
            request, ticket_request_id, user
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
