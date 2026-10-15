"""Print the current UTC date and time to whole seconds."""

from datetime import date, datetime, time, timezone

__all__ = ["current_date", "print_current_date"]


def _current_datetime(now: datetime | date | None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if isinstance(now, datetime):
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        return now.astimezone(timezone.utc)
    if isinstance(now, date):
        return datetime.combine(now, time.min, tzinfo=timezone.utc)
    raise TypeError("now must be a datetime, date, or None")


def current_date(now: datetime | date | None = None) -> date:
    """Return the UTC date; injected naive datetimes are interpreted as UTC."""
    return _current_datetime(now).date()


def print_current_date(now: datetime | date | None = None) -> None:
    """Print an ISO 8601 UTC timestamp to seconds, followed by a newline."""
    print(_current_datetime(now).isoformat(timespec="seconds"))
