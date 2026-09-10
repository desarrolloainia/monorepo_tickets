import re
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

MADRID = ZoneInfo("Europe/Madrid")


def date_range(
    period: str | None = None, desde: date | None = None, hasta: date | None = None
) -> tuple[str, datetime, datetime]:
    if desde is not None or hasta is not None:
        if period is not None or desde is None or hasta is None or desde > hasta:
            raise ValueError("Indique Desde y Hasta en orden, sin combinar con period.")
        end = hasta + timedelta(days=1)
        label = f"{desde}/{hasta}"
    else:
        period = period if period is not None else datetime.now(MADRID).strftime("%Y-%m")
        if re.fullmatch(r"\d{4}", period):
            desde = date(int(period), 1, 1)
            end = date(desde.year + 1, 1, 1)
        elif re.fullmatch(r"\d{4}-\d{2}", period):
            desde = date(int(period[:4]), int(period[5:]), 1)
            end = date(desde.year + (desde.month == 12), desde.month % 12 + 1, 1)
        else:
            raise ValueError("Periodo inválido. Use YYYY o YYYY-MM.")
        label = period
    return (
        label,
        datetime.combine(desde, time.min, MADRID).astimezone(UTC),
        datetime.combine(end, time.min, MADRID).astimezone(UTC),
    )


def effective_dates(start: datetime, end: datetime) -> dict[str, date]:
    return {
        "desde": start.astimezone(MADRID).date(),
        "hasta": end.astimezone(MADRID).date() - timedelta(days=1),
    }
