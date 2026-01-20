#!/usr/bin/env python3
"""
Email Reader Module
Extracts and categorizes emails from Gmail using DroidRun
MUST be called from web server - cannot be run standalone
"""

import asyncio
import json
import os
from typing import List, Dict, Optional
from pathlib import Path

from droidrun import DroidAgent
import google.generativeai as genai

from src.models import EmailInfo, EmailList
from src.utils import get_droidrun_config, get_llm, setup_logger
from src.prompts import (
    get_extract_next_email_goal,
    get_archive_email_goal,
    get_detailed_email_categorization_prompt
)

# Check if module is being imported by web server
if not os.getenv("INBOXPILOT_WEBAPP_MODE"):
    raise RuntimeError(
        "This module cannot be run directly. "
        "It must be called through the web server API. "
        "Set INBOXPILOT_WEBAPP_MODE=1 to enable."
    )

logger = setup_logger(__name__)


class EmailReader:
    """Handles automated email extraction and categorization from Gmail."""
    
    def __init__(self, config_path: Optional[str] = None, data_dir: str = "data"):
        """
        Initialize the email reader.
        
        Args:
            config_path: Optional path to custom config.yaml file
            data_dir: Directory to store JSON data files
        """
        # Resolve paths relative to project root
        project_root = Path(__file__).parent.parent.parent
        if config_path:
            self.config_path = str(Path(config_path))
        else:
            self.config_path = str(project_root / "config.yaml")
        
        # Resolve data_dir relative to project root if not absolute
        if Path(data_dir).is_absolute():
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = project_root / data_dir
        self.data_dir.mkdir(exist_ok=True)
        
        self.processed_count = 0
        self.extracted_file = self.data_dir / "extracted_email_threads.json"
        self.processed_file = self.data_dir / "processed_emails.json"
    
    def _validate_api_key(self):
        """Validate that Gemini API key is configured."""
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable"
            )
        genai.configure(api_key=api_key)
    
    def categorize_emails_with_gemini(self, email_data: Dict) -> Dict:
        """
        Categorizes emails using Gemini 2.0 Flash with strict waterfall logic.
        
        Args:
            email_data: Dictionary containing email data to categorize
            
        Returns:
            categorized emails in 5 buckets:
            - urgent_emails
            - decision_emails  
            - calendar_emails
            - information_emails
            - spam_emails
        """
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.1  # Low temp for consistent results
            }
        )

        prompt = get_detailed_email_categorization_prompt(email_data)

        try:
            response = model.generate_content(prompt)
            categorized = json.loads(response.text)
            logger.info(f"✓ Categorized {sum(len(v) for v in categorized.values())} emails")
            return categorized
        except Exception as e:
            logger.error(f"Categorization failed: {e}")
            return {
                "urgent_emails": [],
                "decision_emails": [],
                "calendar_emails": [],
                "information_emails": [],
                "spam_emails": []
            }
    
    async def extract_next_email(self) -> tuple[bool, Optional[EmailInfo]]:
        """
        Extract data from the next unread email, handling threads.
        
        Returns:
            Tuple of (success: bool, email: Optional[EmailInfo])
        """
        logger.info("📧 Extracting next email...")
        
        goal = get_extract_next_email_goal()
        config = get_droidrun_config(max_steps=50, config_path=self.config_path)
        
        agent = DroidAgent(
            goal=goal,
            config=config,
            llms=get_llm(),
            output_model=EmailList
        )
        
        result = await agent.run()
        
        if not result.success:
            logger.warning(f"Agent stopped: {result.reason}")
            return False, None
        
        if result.structured_output:
            email_data: EmailList = result.structured_output
            
            # Check if inbox is empty
            if not email_data.emails:
                logger.info("🎉 No more unread emails!")
                return False, None
            
            email = email_data.emails[0]
            thread_info = f" (Thread: {email.ThreadCount} messages)" if email.IsThread else ""
            logger.info(f"✓ Extracted: {email.Subject}{thread_info}")
            return True, email
        
        logger.error("No structured data returned")
        return False, None
    
    async def delete_email(self, email_subject: str):
        """
        Delete the email from the main inbox view (for spam).
        
        Args:
            email_subject: Subject line of email to delete
        """
        logger.info(f"🗑️  Deleting spam email: {email_subject[:50]}...")
        
        goal = f"""
Navigate to Gmail inbox and delete the email with subject: "{email_subject}"

1. If you are not in the main Gmail inbox, tap the back arrow until you reach the inbox
2. Find the email with subject "{email_subject}" in the inbox list
3. Long-press the email to select it
4. Tap the delete/trash icon in the action bar at the top
5. Confirm the deletion if prompted
6. Return to the main inbox view
"""
        config = get_droidrun_config(max_steps=20, config_path=self.config_path)
        
        agent = DroidAgent(
            goal=goal,
            config=config,
            llms=get_llm(),
            output_model=None
        )
        
        result = await agent.run()
        if result.success:
            logger.info("✓ Email deleted")
        else:
            logger.warning(f"⚠️  Failed to delete: {result.reason}")
    
    async def archive_email(self, category: str, email_subject: str):
        """
        Archive the email from the main inbox view.
        Skips archiving for Urgent and Decision categories.
        
        Args:
            category: Email category (Urgent, Decision, etc.)
            email_subject: Subject line of email to archive
        """
        # Don't archive urgent or decision emails - keep them in inbox
        if category in ["Urgent", "Decision"]:
            logger.info(f"⏭️  Skipping archive for {category} - keeping in inbox")
            return
        
        # Delete spam emails instead of archiving
        if category == "Spam":
            await self.delete_email(email_subject)
            return
        
        logger.info(f"📥 Archiving email: {email_subject[:50]}...")
        
        goal = get_archive_email_goal(email_subject)
        config = get_droidrun_config(max_steps=15, config_path=self.config_path)
        
        agent = DroidAgent(
            goal=goal,
            config=config,
            llms=get_llm(),
            output_model=None
        )
        
        result = await agent.run()
        if result.success:
            logger.info("✓ Email archived")
        else:
            logger.warning(f"⚠️  Failed to archive: {result.reason}")
    
    def is_email_processed(self, subject: str, sender_email: str) -> bool:
        """Check if email was already processed."""
        if self.extracted_file.exists():
            try:
                with open(self.extracted_file, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    for email in data:
                        if email.get("Subject") == subject and email.get("Email") == sender_email:
                            return True
            except:
                pass
        return False
    
    def save_raw_emails(self, email_list: List[EmailInfo]):
        """Save raw extracted emails to JSON."""
        if self.extracted_file.exists():
            with open(self.extracted_file, "r", encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = []
                except json.JSONDecodeError:
                    data = []
        else:
            data = []
        
        # Convert Pydantic models to dicts
        new_emails = [email.model_dump() for email in email_list]
        data.extend(new_emails)
        
        with open(self.extracted_file, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved {len(new_emails)} raw email(s) to {self.extracted_file}")
    
    def save_categorized_emails(self, categorized: Dict):
        """Append categorized emails to processed_emails.json for the dashboard."""
        # Load existing data
        if self.processed_file.exists():
            with open(self.processed_file, "r", encoding='utf-8') as f:
                try:
                    dashboard_data = json.load(f)
                    # Ensure all keys exist
                    for key in ["urgent", "decisions", "calendar", "info", "spam"]:
                        if key not in dashboard_data:
                            dashboard_data[key] = []
                except json.JSONDecodeError:
                    dashboard_data = {
                        "urgent": [],
                        "decisions": [],
                        "calendar": [],
                        "info": [],
                        "spam": []
                    }
        else:
            dashboard_data = {
                "urgent": [],
                "decisions": [],
                "calendar": [],
                "info": [],
                "spam": []
            }
        
        # Map categorized data to dashboard format
        for email in categorized.get("urgent_emails", []):
            dashboard_data["urgent"].append({
                "id": f"urgent_{len(dashboard_data['urgent'])}",
                "name": email.get("name", "Unknown"),
                "email": email.get("email", ""),
                "subject": email.get("subject", "No Subject"),
                "date": email.get("date", "TBD"),
                "time": email.get("time", "TBD"),
                "summary": email.get("summary", ""),
                "category": "urgent"
            })
        
        for email in categorized.get("decision_emails", []):
            dashboard_data["decisions"].append({
                "id": f"decision_{len(dashboard_data['decisions'])}",
                "name": email.get("name", "Unknown"),
                "email": email.get("email", ""),
                "subject": email.get("subject", "No Subject"),
                "date": email.get("date", "TBD"),
                "time": email.get("time", "TBD"),
                "summary": email.get("summary", ""),
                "category": "decisions"
            })
        
        for email in categorized.get("calendar_emails", []):
            dashboard_data["calendar"].append({
                "id": f"calendar_{len(dashboard_data['calendar'])}",
                "name": email.get("name", "Unknown"),
                "email": email.get("email", ""),
                "subject": email.get("subject", "No Subject"),
                "date": email.get("date", "TBD"),
                "time": email.get("time", "TBD"),
                "purpose": email.get("purpose", "Meeting details not specified"),
                "category": "calendar"
            })
        
        for email in categorized.get("information_emails", []):
            dashboard_data["info"].append({
                "id": f"info_{len(dashboard_data['info'])}",
                "name": email.get("name", "Unknown"),
                "email": email.get("email", ""),
                "subject": email.get("subject", "No Subject"),
                "date": email.get("date", "TBD"),
                "time": email.get("time", "TBD"),
                "summary": email.get("summary", ""),
                "category": "info"
            })
        
        for email in categorized.get("spam_emails", []):
            dashboard_data["spam"].append({
                "id": f"spam_{len(dashboard_data['spam'])}",
                "name": email.get("name", "Unknown"),
                "email": email.get("email", ""),
                "subject": email.get("subject", "No Subject"),
                "date": email.get("date", "TBD"),
                "time": email.get("time", "TBD"),
                "summary": email.get("summary", "Unsolicited content"),
                "category": "spam"
            })
        
        with open(self.processed_file, "w", encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
        
        total = sum(len(v) for v in dashboard_data.values())
        logger.info(f"💾 Saved {total} categorized email(s) to {self.processed_file}")
    
    async def process_emails(self, max_emails: Optional[int] = None) -> Dict[str, int]:
        """
        Main email processing loop.
        
        Args:
            max_emails: Optional limit on number of emails to process
            
        Returns:
            Dictionary with processing statistics
        """
        logger.info("="*60)
        logger.info("InboxPilot - Email Triage Engine")
        logger.info("="*60)
        
        self._validate_api_key()
        self.processed_count = 0
        
        # Process emails one by one
        consecutive_failures = 0
        max_consecutive_failures = 3  # Stop after 3 consecutive extraction failures
        
        while True:
            if max_emails and self.processed_count >= max_emails:
                logger.info(f"Reached limit of {max_emails} emails")
                break
            
            success, email = await self.extract_next_email()
            
            if not success and not email:
                consecutive_failures += 1
                logger.warning(f"⚠️  Extraction failed ({consecutive_failures}/{max_consecutive_failures})")
                
                if consecutive_failures >= max_consecutive_failures:
                    logger.error("❌ Too many consecutive extraction failures, stopping")
                    break
                
                # Continue to try next email despite failure
                logger.info("🔄 Attempting to continue with next email...")
                await asyncio.sleep(2)  # Brief pause before retry
                continue
            
            if not email:
                logger.info("✅ No more unread emails found")
                break
            
            # Reset failure counter on successful extraction
            consecutive_failures = 0
            
            # Skip if already processed
            if self.is_email_processed(email.Subject, email.Email):
                logger.info("⏭️  Email already processed, skipping...")
                await self.archive_email("Info", email.Subject)
                continue
            
            # Save raw email
            self.save_raw_emails([email])
            
            # Categorize with Gemini
            email_dict = {"emails": [email.model_dump()]}
            categorized = self.categorize_emails_with_gemini(email_dict)
            
            # Save categorized data for dashboard
            self.save_categorized_emails(categorized)
            
            # Determine category
            primary_category = None
            if categorized.get("urgent_emails"):
                primary_category = "Urgent"
            elif categorized.get("decision_emails"):
                primary_category = "Decision"
            elif categorized.get("calendar_emails"):
                primary_category = "Calendar"
            elif categorized.get("spam_emails"):
                primary_category = "Spam"
            elif categorized.get("information_emails"):
                primary_category = "Info"
            
            if primary_category:
                logger.info(f"📋 Category: {primary_category}")
            
            # Archive if not urgent/decision
            await self.archive_email(primary_category or "Info", email.Subject)
            
            self.processed_count += 1
            logger.info(f"Processed {self.processed_count} email(s)\n")
        
        logger.info("="*60)
        logger.info(f"Session Complete: {self.processed_count} emails processed")
        logger.info("="*60)
        
        return {"processed": self.processed_count}


# Export for API usage
def create_email_reader(config_path: Optional[str] = None, data_dir: str = "data") -> EmailReader:
    """
    Factory function to create EmailReader instance.
    
    Args:
        config_path: Optional path to custom config.yaml file
        data_dir: Directory to store JSON data files
        
    Returns:
        Configured EmailReader instance
    """
    return EmailReader(config_path=config_path, data_dir=data_dir)
