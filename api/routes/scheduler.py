"""Calendar scheduler API endpoints"""

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api", tags=["scheduler"])


# Pydantic Models
class ScheduleEventsRequest(BaseModel):
    json_path: Optional[str] = None  # Optional path to JSON file
    delay: float = 1.5  # Delay between events in seconds


@router.post("/scheduler/run")
async def run_calendar_scheduler(request: ScheduleEventsRequest):
    """
    Trigger the calendar scheduler to create events from calendar emails.
    This endpoint starts the DroidRun calendar event creation process.
    """
    # Set environment variable to allow module import
    os.environ["INBOXPILOT_WEBAPP_MODE"] = "1"
    
    try:
        # Import here to avoid circular dependencies and allow environment check
        from src.modules import create_calendar_scheduler
        
        scheduler = create_calendar_scheduler(data_dir="data")
        
        # Run calendar scheduling (async)
        stats = await scheduler.run(
            json_path=request.json_path,
            delay=request.delay
        )
        
        return {
            "success": True,
            "message": f"Calendar scheduling completed. Processed {stats['total']} events.",
            "stats": stats
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Calendar scheduling failed: {str(e)}",
            "stats": {"total": 0, "succeeded": 0, "failed": 1}
        }


@router.get("/scheduler/status")
def get_scheduler_status():
    """Get current scheduler status."""
    # In a production system, this would check if scheduler is currently running
    return {
        "status": "idle",
        "message": "Scheduler is ready to process calendar events"
    }
