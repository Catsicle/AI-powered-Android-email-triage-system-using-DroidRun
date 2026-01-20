"""Pydantic models for email data"""

from pydantic import BaseModel, Field
from typing import List


class EmailInfo(BaseModel):
    """Raw email data extracted from Gmail."""
    Name: str = Field(description="The sender's display name")
    Email: str = Field(description="The sender's email address")
    Time: str = Field(description="The time or date the email was received")
    Subject: str = Field(description="The subject line of the email")
    Text: str = Field(description="The main body content of the email")
    IsThread: bool = Field(default=False, description="Whether this is part of an email thread")
    ThreadCount: int = Field(default=1, description="Number of messages in the thread")


class EmailList(BaseModel):
    """List of extracted emails."""
    emails: List[EmailInfo] = Field(
        description="List of extracted email information. Return EMPTY list if no unread emails exist."
    )


class CategorizedEmail(BaseModel):
    """Categorized email with metadata."""
    id: str
    sender: str
    email: str
    subject: str
    preview: str
    timestamp: str
    category: str
