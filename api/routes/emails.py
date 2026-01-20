"""Email-related API endpoints"""

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import json
from pathlib import Path
from datetime import datetime

router = APIRouter(prefix="/api", tags=["emails"])

# Paths to JSON data files
DATA_DIR = Path(__file__).parent.parent.parent / "data"
PROCESSED_EMAILS_PATH = DATA_DIR / "processed_emails.json"
EXTRACTED_EMAILS_PATH = DATA_DIR / "extracted_email_threads.json"


# Pydantic Models
class Email(BaseModel):
    id: str
    sender: str
    subject: str
    preview: str
    timestamp: str
    category: str
    read: bool = False


class EmailData(BaseModel):
    urgent: List[Email]
    info: List[Email]
    calendar: List[Email]
    spam: List[Email]
    decisions: List[Email]
    lastSync: str


class TriggerEmailReaderRequest(BaseModel):
    max_emails: int = None  # Optional limit


class TriggerCategorizerRequest(BaseModel):
    pass  # No parameters needed


def load_json_data() -> dict:
    """Load pre-categorized email data from JSON files."""
    try:
        if PROCESSED_EMAILS_PATH.exists():
            with open(PROCESSED_EMAILS_PATH, 'r') as f:
                return json.load(f)
        elif EXTRACTED_EMAILS_PATH.exists():
            with open(EXTRACTED_EMAILS_PATH, 'r') as f:
                return json.load(f)
        else:
            # Return empty structure for development
            return {
                "urgent": [],
                "info": [],
                "calendar": [],
                "spam": [],
                "decisions": []
            }
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        return {
            "urgent": [],
            "info": [],
            "calendar": [],
            "spam": [],
            "decisions": []
        }


def parse_emails(raw_data: dict) -> EmailData:
    """
    Parse pre-categorized email data from DroidRun output.
    Assumes data is already categorized into buckets.
    """
    categorized = {
        "urgent": [],
        "info": [],
        "calendar": [],
        "spam": [],
        "decisions": []
    }
    
    # Process pre-categorized data
    for category in ["urgent", "info", "calendar", "spam", "decisions"]:
        if category in raw_data:
            for idx, email_data in enumerate(raw_data[category]):
                # Map backend fields to frontend fields
                email = Email(
                    id=email_data.get("id", f"{category}_{idx}"),
                    sender=email_data.get("name", email_data.get("sender", "Unknown")),
                    subject=email_data.get("subject", "No Subject"),
                    preview=email_data.get("summary", email_data.get("purpose", email_data.get("preview", ""))),
                    timestamp=f"{email_data.get('date', 'TBD')} {email_data.get('time', '')}".strip(),
                    category=category,
                    read=email_data.get("read", False)
                )
                categorized[category].append(email)
    
    return EmailData(
        urgent=categorized["urgent"],
        info=categorized["info"],
        calendar=categorized["calendar"],
        spam=categorized["spam"],
        decisions=categorized["decisions"],
        lastSync=datetime.now().isoformat()
    )


@router.get("/emails", response_model=EmailData)
def get_emails():
    """Get pre-categorized email data from DroidRun."""
    try:
        raw_data = load_json_data()
        parsed_data = parse_emails(raw_data)
        return parsed_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
def get_stats():
    """Get email statistics."""
    data = load_json_data()
    parsed = parse_emails(data)
    
    return {
        "total_emails": sum([
            len(parsed.urgent),
            len(parsed.info),
            len(parsed.calendar),
            len(parsed.spam),
            len(parsed.decisions)
        ]),
        "by_category": {
            "urgent": len(parsed.urgent),
            "info": len(parsed.info),
            "calendar": len(parsed.calendar),
            "spam": len(parsed.spam),
            "decisions": len(parsed.decisions)
        }
    }


@router.post("/emails/scan")
async def trigger_email_reader(request: TriggerEmailReaderRequest):
    """
    Trigger the email reader to scan Gmail inbox.
    This endpoint starts the DroidRun email extraction process.
    """
    # Set environment variable to allow module import
    os.environ["INBOXPILOT_WEBAPP_MODE"] = "1"
    
    try:
        # Import here to avoid circular dependencies and allow environment check
        from src.modules import create_email_reader
        
        reader = create_email_reader(data_dir="data")
        
        # Run email processing (async)
        import asyncio
        stats = await reader.process_emails(max_emails=request.max_emails)
        
        return {
            "success": True,
            "message": f"Email scan completed. Processed {stats['processed']} emails.",
            "stats": stats
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Email scan failed: {str(e)}",
            "stats": {"processed": 0, "errors": 1}
        }


@router.post("/emails/recategorize")
async def trigger_email_categorizer(request: TriggerCategorizerRequest):
    """
    Trigger email recategorization.
    Reprocesses emails in extracted_email_threads.json without running DroidRun.
    """
    # Set environment variable to allow module import
    os.environ["INBOXPILOT_WEBAPP_MODE"] = "1"
    
    try:
        # Import here to avoid circular dependencies
        from src.modules import create_email_categorizer
        
        categorizer = create_email_categorizer(data_dir="data")
        stats = categorizer.reprocess_emails()
        
        return {
            "success": True,
            "message": f"Recategorization completed. Processed {stats['total']} emails.",
            "stats": stats
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Recategorization failed: {str(e)}",
            "stats": {"total": 0, "errors": 1}
        }
