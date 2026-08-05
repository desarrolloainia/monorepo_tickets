import logging
import smtplib
from collections.abc import Sequence
from email.message import EmailMessage
from pathlib import Path
from typing import ClassVar

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from modules.tickets.domain.entities.ticket import TicketRequest
from modules.users.domain.entities.users import User

logger = logging.getLogger(__name__)


class SmtpSettings(BaseSettings):
    host: str = Field(min_length=1, validation_alias="SMTP_HOST")
    port: int = Field(default=25, ge=1, le=65535, validation_alias="SMTP_PORT")
    from_address: str = Field(min_length=1, validation_alias="SMTP_FROM")

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


templates = Environment(
    loader=FileSystemLoader(Path(__file__).parent.parent / "template"),
    autoescape=select_autoescape(["html"]),
    undefined=StrictUndefined,
)


def render_ticket_email(
    template_name: str,
    ticket_request: TicketRequest,
    requester: User,
    *,
    reception_url: str = "",
) -> str:
    return templates.get_template(template_name).render(
        cantidad=ticket_request.cantidad,
        nombre_persona=requester.name,
        email_persona=requester.email,
        codigo_solicitud=str(ticket_request.id),
        fecha_solicitud=ticket_request.fecha_creacion,
        reception_url=reception_url,
    )


def _message(from_address: str, recipient: str, subject: str, text: str, html: str) -> EmailMessage:
    message = EmailMessage()
    message["From"] = from_address
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(text)
    message.add_alternative(html, subtype="html")
    return message


def _send(
    recipients: Sequence[str],
    subject: str,
    text: str,
    html: str,
) -> None:
    settings = SmtpSettings()  # pyright: ignore[reportCallIssue]
    with smtplib.SMTP(settings.host, settings.port, timeout=10) as server:
        for recipient in recipients:
            try:
                _ = server.send_message(
                    _message(settings.from_address, recipient, subject, text, html)
                )
            except Exception:
                logger.exception("No se pudo enviar el correo de tickets a %s", recipient)


def send_reception_emails(
    recipients: Sequence[str],
    ticket_request: TicketRequest,
    requester: User,
    reception_url: str,
) -> None:
    try:
        html = render_ticket_email(
            "recepcion_mensaje.html",
            ticket_request,
            requester,
            reception_url=reception_url,
        )
        _send(
            recipients,
            "Nueva solicitud de tickets",
            f"{requester.name} ha solicitado {ticket_request.cantidad} tickets.",
            html,
        )
    except Exception:
        logger.exception("No se pudieron enviar los avisos de la solicitud %s", ticket_request.id)


def send_approval_email(
    recipient: str,
    ticket_request: TicketRequest,
    requester: User,
) -> None:
    try:
        html = render_ticket_email("aprobado_ticket.html", ticket_request, requester)
        _send(
            [recipient],
            "Tus tickets están preparados",
            f"Tu solicitud de {ticket_request.cantidad} tickets ha sido aprobada.",
            html,
        )
    except Exception:
        logger.exception("No se pudo enviar el aviso de aprobación %s", ticket_request.id)
