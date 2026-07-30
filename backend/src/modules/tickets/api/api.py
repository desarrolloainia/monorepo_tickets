from collections.abc import AsyncIterator
from os import getenv
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from modules.tickets.api.dtos import TicketCreateDTO, TicketDTO
from modules.tickets.application.approve_ticket import ApproveTicket
from modules.tickets.application.create_ticket import CreateTicket
from modules.tickets.application.delete_ticket import DeleteTicket
from modules.tickets.application.get_ticket_by_id import GetTicketById
from modules.tickets.application.list_tickets import ListTickets
from modules.tickets.infrastructure.escpos.ticket_printer import EscposNetworkTicketPrinter
from modules.auth.dependencies import current_user
from modules.users.api.dependencies import require_approver
from modules.users.domain.entities.users import User
from shared.database import get_db
from shared.uow import UnitOfWork

router = APIRouter(prefix="/tickets", tags=["tickets"])


async def get_uow(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AsyncIterator[UnitOfWork]:
    yield UnitOfWork(db)


def get_ticket_printer() -> EscposNetworkTicketPrinter:
    host = getenv("TICKET_PRINTER_HOST")
    if not host:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TICKET_PRINTER_HOST is required to approve tickets",
        )
    return EscposNetworkTicketPrinter(host, int(getenv("TICKET_PRINTER_PORT", "9100")))


@router.get("/", response_model=list[TicketDTO])
async def list_tickets(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    user: Annotated[User, Depends(current_user)],
):
    return await ListTickets(uow).list(user.id)


@router.post("/", response_model=TicketDTO, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket: TicketCreateDTO,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    user: Annotated[User, Depends(current_user)],
):
    return await CreateTicket(uow).create(ticket, user.id)


@router.patch("/{ticket_id}/approve", response_model=TicketDTO)
async def approve_ticket(
    ticket_id: UUID,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    user: Annotated[User, Depends(require_approver)],
    printer: Annotated[EscposNetworkTicketPrinter, Depends(get_ticket_printer)],
):
    try:
        return await ApproveTicket(uow, printer).approve(ticket_id, user.id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.get("/{ticket_id}", response_model=TicketDTO)
async def get_ticket(
    ticket_id: UUID,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    user: Annotated[User, Depends(current_user)],
):
    try:
        return await GetTicketById(uow).get_by_id(ticket_id, user.id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: UUID,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    user: Annotated[User, Depends(current_user)],
) -> None:
    try:
        await DeleteTicket(uow).delete(ticket_id, user.id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
