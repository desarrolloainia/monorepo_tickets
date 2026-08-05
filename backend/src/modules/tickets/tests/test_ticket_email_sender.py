from __future__ import annotations

from datetime import UTC, datetime
from email.message import EmailMessage
from typing import ClassVar

import pytest

from modules.tickets.domain.entities.ticket import TicketRequest
from modules.tickets.infrastructure.ticket_email_sender import (
    render_ticket_email,
    send_approval_email,
    send_reception_emails,
)
from modules.users.domain.entities.users import User


class FakeSmtp:
    messages: ClassVar[list[EmailMessage]] = []
    connection: ClassVar[tuple[str, int, int] | None] = None
    failed_recipient: ClassVar[str | None] = None

    def __init__(self, host: str, port: int, timeout: int) -> None:
        type(self).connection = (host, port, timeout)

    def __enter__(self) -> FakeSmtp:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def send_message(self, message: EmailMessage) -> None:
        if message["To"] == self.failed_recipient:
            raise OSError("SMTP no disponible")
        self.messages.append(message)


@pytest.fixture(autouse=True)
def smtp_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    FakeSmtp.messages = []
    FakeSmtp.connection = None
    FakeSmtp.failed_recipient = None
    monkeypatch.setenv("SMTP_HOST", "smtp.internal")
    monkeypatch.setenv("SMTP_PORT", "2525")
    monkeypatch.setenv("SMTP_FROM", "tickets@example.com")
    monkeypatch.setattr("smtplib.SMTP", FakeSmtp)


def ticket_data() -> tuple[TicketRequest, User]:
    requester = User("oid", "ana@example.com", "Ana")
    request = TicketRequest(11, requester.id, datetime(2026, 8, 4, 10, 30, tzinfo=UTC))
    return request, requester


def test_renders_both_ticket_email_templates() -> None:
    request, requester = ticket_data()

    reception = render_ticket_email(
        "recepcion_mensaje.html",
        request,
        requester,
        reception_url="https://tickets.example.com/recepcion",
    )
    approved = render_ticket_email("aprobado_ticket.html", request, requester)

    for html in (reception, approved):
        assert requester.name in html
        assert requester.email in html
        assert str(request.id) in html
        assert "11" in html
    assert 'href="https://tickets.example.com/recepcion"' in reception
    assert "Solicitud aprobada" in approved


def test_sends_individual_messages_and_continues_after_recipient_failure() -> None:
    request, requester = ticket_data()
    FakeSmtp.failed_recipient = "failed@example.com"

    send_reception_emails(
        ["failed@example.com", "approver@example.com"],
        request,
        requester,
        "https://tickets.example.com/recepcion",
    )
    send_approval_email(requester.email, request, requester)

    assert FakeSmtp.connection == ("smtp.internal", 2525, 10)
    assert [message["To"] for message in FakeSmtp.messages] == [
        "approver@example.com",
        requester.email,
    ]
    assert all(message["From"] == "tickets@example.com" for message in FakeSmtp.messages)
    assert all(message.get_body(preferencelist=("html",)) for message in FakeSmtp.messages)
