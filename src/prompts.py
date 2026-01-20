"""
InboxPilot - Centralized AI Prompts
All system prompts and goal strings for DroidRun and Gemini agents
"""

import json
from typing import Dict, Any


# ============================================================================
# EMAIL CATEGORIZATION PROMPTS (Gemini)
# ============================================================================

def get_email_categorization_prompt(email_data: Dict[str, Any]) -> str:
    """
    Generate prompt for Gemini to categorize emails into 5 buckets.
    
    Args:
        email_data: Dictionary containing email data to categorize
        
    Returns:
        Formatted prompt string for Gemini
    """
    return f"""
    You are an intelligent email assistant for InboxPilot. Analyze the provided JSON of emails.
    
    Input Data:
    {json.dumps(email_data)}

    **Categorization Rules (Waterfall Priority)**
    
    1. URGENT - Requires immediate action within 24 hours
    2. DECISION - Requests approval, choice, or input
    3. CALENDAR - Meeting invites, scheduling requests
    4. SPAM - Unsolicited commercial/promotional content
    5. INFORMATION - FYI updates, no action required
    
    **Processing Order (Strict Waterfall)**
    1. Check for URGENT first
    2. Then check remaining for DECISION
    3. Categorize rest as CALENDAR/SPAM/INFORMATION
    
    **Field Extraction Requirements**
    
    For ALL categories:
    - Extract sender name, email, subject from the email
    - Extract date and time from email content (use "TBD" if not found)
    
    For CALENDAR emails:
    - "purpose": Detailed description including:
      * Meeting purpose/agenda
      * Venue/location (virtual link or physical address)
      * Who you are meeting with (attendees/organizer)
      * Example: "Discuss Q1 roadmap with Sarah Chen at Conference Room B"
    
    For NON-CALENDAR emails (Urgent/Decision/Info/Spam):
    - "summary": 1-2 sentence summary explaining "who", "what", "why"
    
    **Output Format**
    {{
        "urgent_emails": [{{"name": str, "email": str, "subject": str, "date": str, "time": str, "summary": str}}],
        "decision_emails": [{{"name": str, "email": str, "subject": str, "date": str, "time": str, "summary": str}}],
        "calendar_emails": [{{"name": str, "email": str, "subject": str, "date": str, "time": str, "purpose": str}}],
        "information_emails": [{{"name": str, "email": str, "subject": str, "date": str, "time": str, "summary": str}}],
        "spam_emails": [{{"name": str, "email": str, "subject": str, "date": str, "time": str, "summary": str}}]
    }}
    
    CRITICAL: For calendar_emails, the "purpose" field MUST include venue and attendee information.
    For all other categories, use "summary" field instead.
    """


def get_detailed_email_categorization_prompt(email_data: Dict[str, Any]) -> str:
    """
    Extended categorization prompt with detailed rules (used in inboxpilot_engine).
    
    Args:
        email_data: Dictionary containing email data to categorize
        
    Returns:
        Formatted prompt string for Gemini with detailed categorization rules
    """
    return f"""
    You are an intelligent email assistant for InboxPilot. Analyze the provided JSON of emails.
    
    Input Data:
    {json.dumps(email_data)}

    **Categorization Rules (Waterfall Priority)**
    
    1. URGENT
       - Requires immediate action within 24 hours
       - Keywords: "Emergency", "ASAP", "Critical", "Urgent", "Payment Failed"
       - Explicit deadlines or high-priority crises
    
    2. DECISION
       - Requests specific input, approval, or choice
       - Direct questions: "Do you approve?", "Which option?"
       - Requires Yes/No response
       - If urgent + decision → tag as URGENT
    
    3. CALENDAR
       - Meeting invitations, scheduling requests
       - Contains dates, times, or calendar invites (.ics)
       - Keywords: "meeting", "schedule", "appointment"
    
    4. INFORMATION
       - Passive updates for awareness only
       - Newsletters, receipts, FYI notes, status reports
       - No action required
    
    5. SPAM
       - Unsolicited commercial/promotional content
       - Marketing emails, cold sales, irrelevant content
       - Has "unsubscribe" links
    
    **Processing Order (Strict Waterfall)**
    1. Check for URGENT first
    2. Then check remaining for DECISION
    3. Categorize rest as CALENDAR/SPAM/INFORMATION
    
    **Field Extraction Requirements**
    
    For ALL categories:
    - Extract sender name, email, subject from the email
    - Extract date and time from email content (use "TBD" if not found)
    
    For CALENDAR emails:
    - "purpose": Detailed description including:
      * Meeting purpose/agenda
      * Venue/location (virtual link or physical address)
      * Who you are meeting with (attendees/organizer)
      * Example: "Discuss Q1 roadmap with Sarah Chen at Conference Room B"
    
    For NON-CALENDAR emails (Urgent/Decision/Info/Spam):
    - "summary": 1-2 sentence summary explaining "who", "what", "why"
      - DO NOT just copy subject line or email text
      - Be clear and concise
    
    **Output Format**
    {{
        "urgent_emails": [{{"name": str, "email": str, "subject": str, "date": str, "time": str, "summary": str}}],
        "decision_emails": [{{"name": str, "email": str, "subject": str, "date": str, "time": str, "summary": str}}],
        "calendar_emails": [{{"name": str, "email": str, "subject": str, "date": str, "time": str, "purpose": str}}],
        "information_emails": [{{"name": str, "email": str, "subject": str, "date": str, "time": str, "summary": str}}],
        "spam_emails": [{{"name": str, "email": str, "subject": str, "date": str, "time": str, "summary": str}}]
    }}
    
    CRITICAL: For calendar_emails, the "purpose" field MUST include venue and attendee information.
    For all other categories, use "summary" field instead.
    """


# ============================================================================
# EMAIL EXTRACTION GOALS (DroidRun)
# ============================================================================

def get_extract_next_email_goal() -> str:
    """
    Goal for DroidRun agent to extract the next unread email from Gmail.
    Handles email threads and returns structured EmailList data.
    
    Returns:
        Goal string for DroidRun agent
    """
    return """
    0. OPEN Gmail app (package: com.google.android.gm):
       - Ensure you open the official Gmail app (com.google.android.gm)
       - Wait for the app to fully load
       - If you're not in the main inbox, navigate to "Primary" or "Inbox"
    
    1. SEARCH for unread emails:
       - Tap the search bar at the top of Gmail
       - Type the text: is:unread with clear: True
       - Press Enter or tap the search button to execute the search
       - Wait for search results to load
    
    2. SELECT the first email:
       - Look at the search results list
       - IF the list is empty (no results), return an EMPTY 'EmailList' and STOP
       - Tap the first/top email in the results to open it
       - Opening the email will automatically mark it as read
    
    3. CHECK if this is a thread (multiple emails in one conversation):
       - Look for text like "(2)", "(3)", etc. next to the sender name
       - Look for "Show message history" or multiple message blocks
       - If it's a thread, focus on the LATEST/MOST RECENT message in the thread
    
    4. EXTRACT the following data from the LATEST message only. If missing, use "Unknown":
       - Name: Sender display name (from the most recent message)
       - Email: Sender email address (in < > brackets)
       - Subject: Email subject line (from the thread)
       - Time: Timestamp of the most recent message (usually top right)
       - Text: Main email body content of the LATEST message only (not the entire thread history)
    
    5. IMPORTANT: 
       - For threads, only extract the newest unread message, not old messages
       - Look for the message that is currently unread/bold
       - Ignore quoted text or previous messages in the thread
    
    6. Return the extracted data.
    
    NOTE: We'll archive the email from the main inbox after categorization.
    """.strip()


def get_archive_email_goal(email_subject: str) -> str:
    """
    Goal for DroidRun agent to archive an email from the Gmail inbox.
    
    Args:
        email_subject: Subject line of the email to archive
        
    Returns:
        Goal string for DroidRun agent
    """
    return f"""
    Archive the email from the inbox:
    1. Make sure you're in the main inbox view (not search)
    2. Scroll through the inbox to find the email with subject: "{email_subject}"
    3. Long press on that email to select it
    4. Tap the Archive icon (box with down arrow) at the top toolbar
    5. Wait for the email to be archived and disappear
    
    This removes the email from inbox but keeps it searchable in "All Mail".
    """.strip()


# ============================================================================
# CALENDAR SCHEDULING GOALS (DroidRun)
# ============================================================================

def get_calendar_event_goal(
    title: str,
    date: str,
    time: str,
    description: str
) -> str:
    """
    Goal for DroidRun agent to create a calendar event in Google Calendar.
    
    Args:
        title: Event title/subject
        date: Event date (YYYY-MM-DD format)
        time: Event time (e.g., "10:00 AM")
        description: Event description/purpose
        
    Returns:
        Goal string for DroidRun agent
    """
    return f"""
Open the Google Calendar app and schedule the following event:

Event Details:
- Title: {title}
- Date & Time: {date} at {time}
- Description: {description}

Execution Steps:
1. Launch the 'Google Calendar' app
2. Tap the '+' (Create/Add) button at the bottom right
3. Select 'Event' from the options
4. In the 'Add title' field, type: "{title}"
5. Set the date to "{date}"
6. Set the time to "{time}"
7. SCROLL DOWN to find the description field - swipe from bottom to top (e.g., from y=2000 to y=500)
8. Tap 'Add description' and type: "{description}"
9. Tap the 'Save' button
10. Return to the main calendar view

IMPORTANT: To scroll DOWN (see more fields below), swipe UP on screen: from higher y-coordinate to lower y-coordinate (e.g., 550,2000 -> 550,500).

Important Notes:
- Do NOT add any guests to this event
- Do NOT add a location - the venue is included in the description
- Ensure all fields are filled accurately
- Wait for UI to stabilize between actions
    """.strip()


def get_close_calendar_goal() -> str:
    """
    Goal for DroidRun agent to close Google Calendar app.
    
    Returns:
        Goal string for DroidRun agent
    """
    return "Close the Google Calendar app and return to home screen"


# ============================================================================
# EMAIL ACTION GOALS (DroidRun - from Web Dashboard)
# ============================================================================

def get_archive_email_by_id_goal(email_id: str) -> str:
    """
    Goal to archive a specific email by ID.
    
    Args:
        email_id: Email identifier
        
    Returns:
        Goal string for DroidRun agent
    """
    return f"""
Open Gmail app (package: com.google.android.gm) and find the email with ID {email_id}.
Select the email and tap the Archive button.
Return to inbox.
    """.strip()


def get_delete_email_goal(email_id: str) -> str:
    """
    Goal to delete a specific email by ID.
    
    Args:
        email_id: Email identifier
        
    Returns:
        Goal string for DroidRun agent
    """
    return f"""
Open Gmail app (package: com.google.android.gm) and find the email with ID {email_id}.
Select the email and tap the Delete button.
Confirm deletion if prompted.
Return to inbox.
    """.strip()


def get_reply_email_goal(email_id: str) -> str:
    """
    Goal to open reply interface for a specific email.
    
    Args:
        email_id: Email identifier
        
    Returns:
        Goal string for DroidRun agent
    """
    return f"""
Open Gmail app (package: com.google.android.gm) and find the email with ID {email_id}.
Tap on the email to open it.
Tap the Reply button.
Wait for the compose screen to open.
    """.strip()


def get_restore_email_goal(email_id: str) -> str:
    """
    Goal to restore an email from trash/spam to inbox.
    
    Args:
        email_id: Email identifier
        
    Returns:
        Goal string for DroidRun agent
    """
    return f"""
Open Gmail app (package: com.google.android.gm).
Tap the menu icon (three horizontal lines) at the top left.
Scroll down and tap "Trash" or "Bin".
Find the email with ID {email_id} or the most recent spam email.
Long press to select the email.
Tap the "Move to" icon (usually a folder icon) at the top.
Select "Inbox" from the options.
Tap the back button to return to the main screen.
    """.strip()


def get_purge_spam_goal() -> str:
    """
    Goal to delete all emails in Gmail spam folder.
    
    Returns:
        Goal string for DroidRun agent
    """
    return """
Open Gmail app (package: com.google.android.gm).
Navigate to the Spam folder.
Tap 'Select All' or select all visible spam emails.
Tap 'Delete Forever' or 'Empty Spam Now'.
Confirm the action if prompted.
Return to inbox.
    """.strip()
