"""Print today's date using UTC by default."""

from datetime import date, datetime, timezone

__all__ = ["current_date", "print_current_date"]


def current_date(now: datetime | date | None = None) -> date:
    """Return the UTC date; injected naive datetimes are interpreted as UTC."""
    if now is None:
        return datetime.now(timezone.utc).date()
    if isinstance(now, datetime):
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        return now.astimezone(timezone.utc).date()
    if isinstance(now, date):
        return now
    raise TypeError("now must be a datetime, date, or None")


def print_current_date(now: datetime | date | None = None) -> None:
    """Print a single ISO 8601 date followed by a newline."""
    print(current_date(now).isoformat(timespec="seconds"))
