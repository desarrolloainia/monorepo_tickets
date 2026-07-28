import asyncio

from escpos.printer import Network

from modules.tickets.domain.entities.ticket import Ticket


class EscposNetworkTicketPrinter:
    def __init__(self, host: str, port: int = 9100) -> None:
        self.host = host
        self.port = port

    async def print_ticket(self, ticket: Ticket) -> None:
        await asyncio.to_thread(self._print_ticket, ticket)

    def _print_ticket(self, ticket: Ticket) -> None:
        printer = Network(self.host, self.port)
        try:
            printer.text(
                f"Ticket: {ticket.codigo}\n"
                f"Nombre: {ticket.nombre}\n"
                f"{ticket.description}\n"
                f"Cantidad: {ticket.cantidad}\n\n"
            )
            printer.qr(ticket.codigo_qr)
            printer.cut()
        finally:
            printer.close()
