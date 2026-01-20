"""
DroidRun Integration Module
Connects the web dashboard with DroidRun email processing
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import main.py
sys.path.append(str(Path(__file__).parent.parent))

from main import CalendarEventScheduler
from droidrun import DroidAgent, DroidrunConfig


class DroidRunExecutor:
    """Executes actions queued from the web dashboard."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = DroidrunConfig.from_yaml(config_path)
        
    async def execute_action(self, email_id: str, action: str) -> bool:
        """
        Execute a single action on an email.
        
        Args:
            email_id: Email identifier
            action: Action to perform ("archive", "delete", "reply")
            
        Returns:
            True if successful, False otherwise
        """
        goal = self._build_action_goal(email_id, action)
        
        try:
            agent = DroidAgent(goal=goal, config=self.config)
            result = await agent.run()
            return result.success
        except Exception as e:
            print(f"Error executing action: {e}")
            return False
    
    def _build_action_goal(self, email_id: str, action: str) -> str:
        """Build goal string for email action."""
        if action == "archive":
            return f"""
Open Gmail app and find the email with ID {email_id}.
Select the email and tap the Archive button.
Return to inbox.
            """.strip()
        elif action == "delete":
            return f"""
Open Gmail app and find the email with ID {email_id}.
Select the email and tap the Delete button.
Confirm deletion if prompted.
Return to inbox.
            """.strip()
        elif action == "reply":
            return f"""
Open Gmail app and find the email with ID {email_id}.
Tap on the email to open it.
Tap the Reply button.
Wait for the compose screen to open.
            """.strip()
        elif action == "restore":
            return f"""
Open Gmail app.
Tap the menu icon (three horizontal lines) at the top left.
Scroll down and tap "Trash" or "Bin".
Find the email with ID {email_id} or the most recent spam email.
Long press to select the email.
Tap the "Move to" icon (usually a folder icon) at the top.
Select "Inbox" from the options.
Tap the back button to return to the main screen.
            """.strip()
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def purge_spam(self) -> bool:
        """Delete all emails in the spam category."""
        goal = """
Open Gmail app.
Navigate to the Spam folder.
Tap 'Select All' or select all visible spam emails.
Tap 'Delete Forever' or 'Empty Spam Now'.
Confirm the action if prompted.
Return to inbox.
        """.strip()
        
        try:
            agent = DroidAgent(goal=goal, config=self.config)
            result = await agent.run()
            return result.success
        except Exception as e:
            print(f"Error purging spam: {e}")
            return False


async def process_action_queue():
    """
    Main loop to process queued actions from the web dashboard.
    This should be run periodically (e.g., via cron or as a background service).
    """
    import requests
    
    executor = DroidRunExecutor()
    
    # Fetch action queue from API
    try:
        response = requests.get("http://localhost:8000/api/actions/queue")
        data = response.json()
        actions = data.get("actions", [])
        
        print(f"Processing {len(actions)} queued actions...")
        
        for idx, action_item in enumerate(actions):
            if action_item["status"] != "queued":
                continue
            
            action = action_item.get("action")
            email_id = action_item.get("emailId")
            
            print(f"Executing: {action} on {email_id}")
            
            if action == "purge_spam":
                success = await executor.purge_spam()
            else:
                success = await executor.execute_action(email_id, action)
            
            if success:
                # Mark action as completed
                requests.post(f"http://localhost:8000/api/actions/complete/{idx}")
                print(f"✓ Completed: {action}")
            else:
                print(f"✗ Failed: {action}")
        
        print("Action queue processing complete")
        
    except Exception as e:
        print(f"Error processing action queue: {e}")


if __name__ == "__main__":
    # Run the action queue processor
    asyncio.run(process_action_queue())
