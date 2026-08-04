from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse

from modules.auth.dependencies import current_user, get_uow
from modules.tickets.api.dtos import (
    PendingTicketRequestDTO,
    TicketRequestCreateDTO,
    TicketRequestDTO,
)
from modules.tickets.application.approve_ticket_request import ApproveTicketRequest
from modules.tickets.application.create_ticket_request import CreateTicketRequest
from modules.tickets.application.get_ticket_request import GetTicketRequest
from modules.tickets.application.list_pending_tickets import ListPendingTickets
from modules.tickets.application.print_ticket_request import PrintTicketRequest
from modules.tickets.infrastructure.html_ticket_printer import HtmlTicketPrinter
from modules.users.api.dependencies import require_approver
from modules.users.domain.entities.users import User
from shared.uow import UnitOfWork

router = APIRouter(prefix="/tickets", tags=["tickets"])


# Estos endpoints para los empleados
@router.post("/", response_model=TicketRequestDTO, status_code=status.HTTP_201_CREATED)
async def create_ticket_request(
    data: TicketRequestCreateDTO,
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    user: Annotated[User, Depends(current_user)],
) -> TicketRequestDTO:
    return TicketRequestDTO.model_validate(
        await CreateTicketRequest(unit_of_work).create(data.cantidad, user.id)
    )


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
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    user: Annotated[User, Depends(require_approver)],
) -> TicketRequestDTO:
    try:
        ticket_request = await ApproveTicketRequest(unit_of_work).approve(
            ticket_request_id, user.id
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
