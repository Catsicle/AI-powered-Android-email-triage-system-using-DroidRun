"""Action-related API endpoints (archive, delete, restore, etc.)"""

import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path

router = APIRouter(prefix="/api", tags=["actions"])

# Paths to JSON data files
DATA_DIR = Path(__file__).parent.parent.parent / "data"
PROCESSED_EMAILS_PATH = DATA_DIR / "processed_emails.json"

# Action queue storage (in production, use a database)
action_queue = []


# Pydantic Models
class ActionRequest(BaseModel):
    emailId: str
    action: str  # "archive", "delete", "reply"


class RestoreRequest(BaseModel):
    emailId: str


@router.post("/actions")
def queue_action(action: ActionRequest):
    """Queue an action for DroidRun to execute."""
    action_queue.append({
        "emailId": action.emailId,
        "action": action.action,
        "timestamp": datetime.now().isoformat(),
        "status": "queued"
    })
    return {
        "success": True,
        "message": f"Action '{action.action}' queued for email {action.emailId}"
    }


@router.get("/actions/queue")
def get_action_queue():
    """Get pending actions for DroidRun to execute."""
    return {"actions": action_queue}


@router.post("/actions/purge-spam")
def purge_spam():
    """Queue deletion of all spam emails."""
    action_queue.append({
        "action": "purge_spam",
        "timestamp": datetime.now().isoformat(),
        "status": "queued"
    })
    return {"success": True, "message": "Spam purge queued"}


@router.post("/actions/restore")
def restore_email(request: RestoreRequest):
    """Restore an email from spam/trash to inbox."""
    email_id = request.emailId
    action_queue.append({
        "emailId": email_id,
        "action": "restore",
        "timestamp": datetime.now().isoformat(),
        "status": "queued"
    })
    
    # Also remove from spam list in processed_emails.json
    try:
        if PROCESSED_EMAILS_PATH.exists():
            with open(PROCESSED_EMAILS_PATH, 'r') as f:
                data = json.load(f)
            
            if "spam" in data:
                data["spam"] = [email for email in data["spam"] if email.get("id") != email_id]
                
            with open(PROCESSED_EMAILS_PATH, "w") as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error updating processed_emails.json: {e}")
    
    return {"success": True, "message": f"Restore queued for email {email_id}"}


@router.post("/actions/complete/{action_id}")
def complete_action(action_id: int):
    """Mark an action as completed by DroidRun."""
    if action_id < len(action_queue):
        action_queue[action_id]["status"] = "completed"
        return {"success": True, "message": "Action marked as completed"}
    raise HTTPException(status_code=404, detail="Action not found")


@router.get("/actions/stats")
def get_action_stats():
    """Get action queue statistics."""
    return {
        "total_actions": len(action_queue),
        "queued": len([a for a in action_queue if a["status"] == "queued"]),
        "completed": len([a for a in action_queue if a["status"] == "completed"])
    }
