#!/usr/bin/env python3
"""
Email Categorizer Module
Reprocesses extracted emails for testing categorization without DroidRun
MUST be called from web server - cannot be run standalone
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional

import google.generativeai as genai

from src.utils import setup_logger
from src.prompts import get_email_categorization_prompt

# Check if module is being imported by web server
if not os.getenv("INBOXPILOT_WEBAPP_MODE"):
    raise RuntimeError(
        "This module cannot be run directly. "
        "It must be called through the web server API. "
        "Set INBOXPILOT_WEBAPP_MODE=1 to enable."
    )

logger = setup_logger(__name__)


class EmailCategorizer:
    """Handles email categorization using Gemini LLM."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the email categorizer.
        
        Args:
            data_dir: Directory containing JSON data files
        """
        # Resolve data_dir relative to project root if not absolute
        project_root = Path(__file__).parent.parent.parent
        if Path(data_dir).is_absolute():
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = project_root / data_dir
        
        self.extracted_file = self.data_dir / "extracted_email_threads.json"
        self.processed_file = self.data_dir / "processed_emails.json"
        self._validate_api_key()
    
    def _validate_api_key(self):
        """Validate that Gemini API key is configured."""
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable"
            )
        genai.configure(api_key=api_key)
    
    def categorize_emails_with_gemini(self, email_data: dict) -> dict:
        """
        Categorizes emails using Gemini 2.0 Flash.
        
        Args:
            email_data: Dictionary containing email data to categorize
            
        Returns:
            Dictionary with categorized emails in 5 buckets
        """
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )

        prompt = get_email_categorization_prompt(email_data)

        try:
            response = model.generate_content(prompt)
            categorized = json.loads(response.text)
            logger.info(f"✓ Categorized successfully")
            return categorized
        except Exception as e:
            logger.error(f"✗ Categorization failed: {e}")
            return {
                "urgent_emails": [],
                "decision_emails": [],
                "calendar_emails": [],
                "information_emails": [],
                "spam_emails": []
            }
    
    def reprocess_emails(self) -> Dict[str, int]:
        """
        Load extracted emails and recategorize them.
        
        Returns:
            Dictionary with statistics per category
        """
        # Load raw emails
        if not self.extracted_file.exists():
            logger.error(f"{self.extracted_file} not found")
            return {
                "urgent": 0,
                "decisions": 0,
                "calendar": 0,
                "info": 0,
                "spam": 0,
                "total": 0
            }
        
        with open(self.extracted_file, "r") as f:
            raw_emails = json.load(f)
        
        logger.info(f"Loaded {len(raw_emails)} raw emails")
        
        # Initialize dashboard data
        dashboard_data = {
            "urgent": [],
            "decisions": [],
            "calendar": [],
            "info": [],
            "spam": []
        }
        
        # Process each email
        for idx, email in enumerate(raw_emails):
            if email.get("Name") == "Unknown" or email.get("Subject") == "Unknown":
                logger.info(f"Skipping email {idx+1} - incomplete data")
                continue
            
            logger.info(f"\nProcessing email {idx+1}/{len(raw_emails)}: {email.get('Subject')}")
            
            # Create email structure for Gemini
            email_for_gemini = {"emails": [email]}
            
            # Categorize
            categorized = self.categorize_emails_with_gemini(email_for_gemini)
            
            # Add to dashboard data
            for gemini_email in categorized.get("urgent_emails", []):
                dashboard_data["urgent"].append({
                    "id": f"urgent_{len(dashboard_data['urgent'])}_{idx}",
                    "name": gemini_email.get("name", email.get("Name", "Unknown")),
                    "email": gemini_email.get("email", email.get("Email", "")),
                    "subject": gemini_email.get("subject", email.get("Subject", "")),
                    "date": gemini_email.get("date", "TBD"),
                    "time": gemini_email.get("time", "TBD"),
                    "summary": gemini_email.get("summary", ""),
                    "category": "urgent"
                })
            
            for gemini_email in categorized.get("decision_emails", []):
                dashboard_data["decisions"].append({
                    "id": f"decision_{len(dashboard_data['decisions'])}_{idx}",
                    "name": gemini_email.get("name", email.get("Name", "Unknown")),
                    "email": gemini_email.get("email", email.get("Email", "")),
                    "subject": gemini_email.get("subject", email.get("Subject", "")),
                    "date": gemini_email.get("date", "TBD"),
                    "time": gemini_email.get("time", "TBD"),
                    "summary": gemini_email.get("summary", ""),
                    "category": "decisions"
                })
            
            for gemini_email in categorized.get("calendar_emails", []):
                dashboard_data["calendar"].append({
                    "id": f"calendar_{len(dashboard_data['calendar'])}_{idx}",
                    "name": gemini_email.get("name", email.get("Name", "Unknown")),
                    "email": gemini_email.get("email", email.get("Email", "")),
                    "subject": gemini_email.get("subject", email.get("Subject", "")),
                    "date": gemini_email.get("date", "TBD"),
                    "time": gemini_email.get("time", "TBD"),
                    "purpose": gemini_email.get("purpose", "Meeting details not specified"),
                    "category": "calendar"
                })
            
            for gemini_email in categorized.get("information_emails", []):
                dashboard_data["info"].append({
                    "id": f"info_{len(dashboard_data['info'])}_{idx}",
                    "name": gemini_email.get("name", email.get("Name", "Unknown")),
                    "email": gemini_email.get("email", email.get("Email", "")),
                    "subject": gemini_email.get("subject", email.get("Subject", "")),
                    "date": gemini_email.get("date", "TBD"),
                    "time": gemini_email.get("time", "TBD"),
                    "summary": gemini_email.get("summary", ""),
                    "category": "info"
                })
            
            for gemini_email in categorized.get("spam_emails", []):
                dashboard_data["spam"].append({
                    "id": f"spam_{len(dashboard_data['spam'])}_{idx}",
                    "name": gemini_email.get("name", email.get("Name", "Unknown")),
                    "email": gemini_email.get("email", email.get("Email", "")),
                    "subject": gemini_email.get("subject", email.get("Subject", "")),
                    "date": gemini_email.get("date", "TBD"),
                    "time": gemini_email.get("time", "TBD"),
                    "summary": gemini_email.get("summary", "Unsolicited content"),
                    "category": "spam"
                })
        
        # Save to processed_emails.json
        with open(self.processed_file, "w", encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
        
        stats = {
            "urgent": len(dashboard_data['urgent']),
            "decisions": len(dashboard_data['decisions']),
            "calendar": len(dashboard_data['calendar']),
            "info": len(dashboard_data['info']),
            "spam": len(dashboard_data['spam']),
            "total": sum(len(v) for v in dashboard_data.values())
        }
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Reprocessing Complete!")
        logger.info(f"{'='*60}")
        logger.info(f"Total emails categorized: {stats['total']}")
        logger.info(f"  - Urgent: {stats['urgent']}")
        logger.info(f"  - Decisions: {stats['decisions']}")
        logger.info(f"  - Calendar: {stats['calendar']}")
        logger.info(f"  - Info: {stats['info']}")
        logger.info(f"  - Spam: {stats['spam']}")
        logger.info(f"{'='*60}")
        
        return stats


# Export for API usage
def create_email_categorizer(data_dir: str = "data") -> EmailCategorizer:
    """
    Factory function to create EmailCategorizer instance.
    
    Args:
        data_dir: Directory containing JSON data files
        
    Returns:
        Configured EmailCategorizer instance
    """
    return EmailCategorizer(data_dir=data_dir)
