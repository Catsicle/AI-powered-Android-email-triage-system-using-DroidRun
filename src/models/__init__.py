"""Data models for InboxPilot"""

from .email_models import EmailInfo, EmailList, CategorizedEmail
from .calendar_models import CalendarEvent

__all__ = [
    'EmailInfo',
    'EmailList',
    'CategorizedEmail',
    'CalendarEvent',
]
