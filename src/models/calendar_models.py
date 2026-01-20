"""Pydantic models for calendar event data"""

from pydantic import BaseModel, Field


class CalendarEvent(BaseModel):
    """Pydantic model for calendar event data validation."""
    name: str = Field(description="Contact name for the meeting")
    email: str = Field(description="Email address")
    subject: str = Field(description="Event title/subject")
    date: str = Field(description="Event date in YYYY-MM-DD format")
    time: str = Field(description="Event time")
    purpose: str = Field(description="Meeting purpose/description")
