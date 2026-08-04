from datetime import UTC, datetime
from decimal import Decimal

from fastapi import Request

from modules.tickets.domain.entities.ticket_printer import PrintableTicket
from modules.tickets.infrastructure.html_ticket_printer import HtmlTicketPrinter


def test_html_printer_groups_twelve_tickets_into_eleven_and_one() -> None:
    tickets = [
        PrintableTicket("User", f"2607-{index:06d}", datetime.now(UTC), Decimal("5.50"))
        for index in range(1, 13)
    ]
    request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})

    printer = HtmlTicketPrinter()
    html = bytes(printer.render(request, tickets, "User", False).body).decode()
    printable_html = bytes(printer.render(request, tickets, "User", True).body).decode()

    assert html.count('<section class="sheet">') == 2
    assert html.count('class="label firma-label"') == 2
    assert html.count('class="label empty"') == 10
    assert all(ticket.codigo in html for ticket in tickets)
    assert "<body onload=" not in html
    assert "window.print()" not in html
    assert printable_html.index("JsBarcode('.barcode').init()") < printable_html.index(
        "window.print()"
    )
