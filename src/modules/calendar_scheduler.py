#!/usr/bin/env python3
"""
Calendar Scheduler Module
Automatically creates calendar events from JSON data on Android devices
MUST be called from web server - cannot be run standalone
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from droidrun import DroidAgent

from src.models import CalendarEvent
from src.utils import get_droidrun_config, setup_logger
from src.prompts import get_calendar_event_goal, get_close_calendar_goal

# Check if module is being imported by web server
if not os.getenv("INBOXPILOT_WEBAPP_MODE"):
    raise RuntimeError(
        "This module cannot be run directly. "
        "It must be called through the web server API. "
        "Set INBOXPILOT_WEBAPP_MODE=1 to enable."
    )

logger = setup_logger(__name__)


class CalendarScheduler:
    """Handles automated scheduling of calendar events."""
    
    def __init__(self, config_path: Optional[str] = None, data_dir: str = "data"):
        """
        Initialize the calendar event scheduler.
        
        Args:
            config_path: Optional path to custom config.yaml file
            data_dir: Directory containing JSON data files
        """
        # Resolve paths relative to project root
        project_root = Path(__file__).parent.parent.parent
        if config_path:
            self.config_path = str(Path(config_path))
        else:
            self.config_path = str(project_root / "config.yaml")
        
        self.config = get_droidrun_config(max_steps=30, config_path=self.config_path)
        
        # Resolve data_dir relative to project root if not absolute
        if Path(data_dir).is_absolute():
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = project_root / data_dir
        
        self.events_processed = 0
        self.events_succeeded = 0
        self.events_failed = 0
    
    def _validate_api_key(self):
        """Validate that Google API key is configured."""
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable"
            )
    
    def load_events_from_json(self, json_path: Optional[str] = None) -> List[CalendarEvent]:
        """
        Load calendar events from JSON file.
        
        Args:
            json_path: Optional path to specific JSON file
            
        Returns:
            List of validated CalendarEvent objects
        """
        calendar_events = []
        
        if json_path:
            json_path = Path(json_path)
            with open(json_path, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded events from: {json_path}")
            
            # Check if it's processed_emails.json format (with calendar key)
            if "calendar" in data:
                calendar_events = data["calendar"]
            elif "calendar_emails" in data:
                calendar_events = data["calendar_emails"]
            else:
                calendar_events = []
        else:
            # Try loading from processed_emails.json first
            processed_path = self.data_dir / "processed_emails.json"
            if processed_path.exists():
                with open(processed_path, 'r') as f:
                    data = json.load(f)
                calendar_events = data.get("calendar", [])
                logger.info(f"Loaded {len(calendar_events)} events from {processed_path}")
            else:
                logger.warning("No calendar events found")
                calendar_events = []
        
        # Validate events
        events = [CalendarEvent(**event) for event in calendar_events]
        logger.info(f"Loaded and validated {len(events)} events")
        return events
    
    async def schedule_event(self, event: CalendarEvent) -> bool:
        """
        Schedule a single calendar event.
        
        Args:
            event: Calendar event to schedule
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Scheduling: {event.subject} on {event.date} at {event.time}")
        
        try:
            goal = get_calendar_event_goal(
                title=event.subject,
                date=event.date,
                time=event.time,
                description=event.purpose
            )
            
            agent = DroidAgent(
                goal=goal,
                config=self.config,
            )
            
            result = await agent.run()
            
            if result.success:
                logger.info(f"✓ Successfully scheduled: {event.subject}")
                return True
            else:
                logger.error(f"✗ Failed to schedule: {event.subject} - {result.reason}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error scheduling {event.subject}: {str(e)}")
            return False
    
    async def schedule_all_events(
        self, 
        events: List[CalendarEvent],
        delay_between_events: float = 2.0
    ) -> Dict[str, int]:
        """
        Schedule all calendar events sequentially.
        
        Args:
            events: List of calendar events to schedule
            delay_between_events: Delay in seconds between events
            
        Returns:
            Dictionary with success/failure counts
        """
        logger.info(f"Starting to schedule {len(events)} events...")
        
        for idx, event in enumerate(events, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Event {idx}/{len(events)}")
            logger.info(f"{'='*60}")
            
            success = await self.schedule_event(event)
            
            self.events_processed += 1
            if success:
                self.events_succeeded += 1
            else:
                self.events_failed += 1
            
            # Delay between events to allow UI to settle
            if idx < len(events):
                await asyncio.sleep(delay_between_events)
        
        return self.get_stats()
    
    async def close_calendar_app(self):
        """Close the Google Calendar app."""
        logger.info("Closing Google Calendar app...")
        
        goal = get_close_calendar_goal()
        
        close_agent = DroidAgent(
            goal=goal,
            config=self.config,
        )
        await close_agent.run()
        logger.info("✓ Calendar app closed")
    
    def get_stats(self) -> Dict[str, int]:
        """Get scheduling statistics."""
        return {
            "total": self.events_processed,
            "succeeded": self.events_succeeded,
            "failed": self.events_failed
        }
    
    def print_summary(self):
        """Print execution summary."""
        stats = self.get_stats()
        logger.info(f"\n{'='*60}")
        logger.info("SCHEDULING SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total Events: {stats['total']}")
        logger.info(f"Succeeded: {stats['succeeded']}")
        logger.info(f"Failed: {stats['failed']}")
        if stats['total'] > 0:
            logger.info(f"Success Rate: {(stats['succeeded']/stats['total']*100):.1f}%")
        logger.info(f"{'='*60}\n")
    
    async def run(self, json_path: Optional[str] = None, delay: float = 1.5) -> Dict[str, int]:
        """
        Main execution function.
        
        Args:
            json_path: Optional path to JSON file with events
            delay: Delay between events in seconds
            
        Returns:
            Dictionary with execution statistics
        """
        self._validate_api_key()
        
        # Load events
        events = self.load_events_from_json(json_path)
        
        if not events:
            logger.warning("No events to schedule")
            return {"total": 0, "succeeded": 0, "failed": 0}
        
        # Schedule all events
        stats = await self.schedule_all_events(events, delay_between_events=delay)
        
        # Print summary
        self.print_summary()
        
        # Close Calendar app
        await self.close_calendar_app()
        
        return stats


# Export for API usage
def create_calendar_scheduler(config_path: Optional[str] = None, data_dir: str = "data") -> CalendarScheduler:
    """
    Factory function to create CalendarScheduler instance.
    
    Args:
        config_path: Optional path to custom config.yaml file
        data_dir: Directory containing JSON data files
        
    Returns:
        Configured CalendarScheduler instance
    """
    return CalendarScheduler(config_path=config_path, data_dir=data_dir)
