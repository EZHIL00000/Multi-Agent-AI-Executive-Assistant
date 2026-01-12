"""Tools package for the Personal Assistant."""

from src.tools.calendar_tools import (
    create_calendar_event,
    delete_calendar_event,
    get_available_time_slots,
    list_upcoming_events,
    update_calendar_event,
)
from src.tools.email_tools import (
    draft_email,
    search_emails,
    send_email,
)
from src.tools.google_auth import get_google_services

__all__ = [
    # Calendar tools
    "create_calendar_event",
    "delete_calendar_event",
    "get_available_time_slots",
    "list_upcoming_events",
    "update_calendar_event",
    # Email tools
    "draft_email",
    "search_emails",
    "send_email",
    # Auth
    "get_google_services",
]
