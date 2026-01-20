# InboxPilot - AI Agent Instructions

## Project Overview
**InboxPilot** is an automated Android email triage system using DroidRun framework and Google Gemini AI agents. The system monitors Gmail, categorizes emails into 5 buckets (Urgent, Info, Calendar, Spam, Decisions), and provides a web dashboard for user review and action execution.

**Tagline**: Automated Android Email Triage & Decision Dashboard

**Core Tech Stack**: DroidRun 0.4.22, Python 3.11, Google Gemini 2.0/2.5, Pydantic, Phoenix tracing

## MVP Architecture

### System Components
1. **Automation Engine (DroidRun on Android)**
   - Periodic Gmail checks at set intervals
   - Content extraction (sender, subject, preview text)
   - Local categorization into 5 buckets
   - Syncs JSON payloads to web backend

2. **Web Dashboard**
   - Summary view ("Morning Briefing" style counts)
   - Read-only lists for Urgent/Info/Calendar/Spam
   - Interactive "Decisions" tab with action cards
   - Spam purge functionality

3. **Feedback Loop**
   - Action queue in database
   - DroidRun executes user decisions on device

### Email Categories
- **Urgent**: Time-sensitive emails (keywords: "ASAP", "Payment Failed", family contacts)
- **Info**: Newsletters, receipts, notifications
- **Calendar**: Meeting invites, scheduling requests
- **Spam**: Suspicious emails, promos not caught by Gmail (keywords: "Lottery", "Verify")
- **Decisions**: Action-required emails ("Do you want to...", "Please confirm", approvals)

### JSON Data Structure
**Calendar emails** have dedicated fields for meeting logistics:
```json
{
  "id": "calendar_0",
  "name": "Aron Aron",
  "email": "aron@example.com",
  "subject": "Project Kickoff",
  "date": "2026-01-27",
  "time": "10:00 AM",
  "purpose": "Discuss timeline with Sarah Chen at Conference Room B",
  "category": "calendar"
}
```

**Non-calendar emails** (Urgent/Info/Spam/Decisions) use standard fields:
```json
{
  "id": "urgent_0",
  "name": "John Smith",
  "email": "john@example.com",
  "subject": "Payment Failed",
  "date": "2026-01-18",
  "time": "3:45 PM",
  "summary": "Credit card charge declined, action required within 24 hours",
  "category": "urgent"
}
```

**Critical field usage**:
- `purpose` (calendar only): Must include meeting purpose, venue/location, and attendees
- `summary` (non-calendar): 1-2 sentence description explaining who/what/why
- All categories extract `date` and `time` from email content (use "TBD" if not found)

### Data Flow
1. DroidRun wakes device → Opens Gmail app
2. Scrapes unread emails → Extracts context
3. Categorizes via LLM/rules → Validates with Pydantic models
4. Sends JSON to web backend → Stores in database
5. User reviews dashboard → Makes decisions
6. DroidRun fetches action queue → Executes on device (archive/delete/reply)

## Critical Development Patterns

### 1. Config Management
**DroidRun uses YAML config, not direct LLM instantiation.** Never create `GoogleGenAI()` objects directly:
```python
# ✗ OLD WAY (don't use)
llm = GoogleGenAI(model_name="gemini-2.0-flash", api_key=api_key)
agent = DroidAgent(goal=goal, llms=llm)

# ✓ CORRECT (config-based)
config = DroidrunConfig.from_yaml("config.yaml")  # Contains llm_profiles
agent = DroidAgent(goal=goal, config=config)  # Automatically uses configured LLMs
```

**Config attributes**: Use `max_steps` not `maxsteps` (common typo), `after_sleep_action` for delays, `save_trajectory` values: `"action"`, `"step"`, or `"never"`

### 2. Agent Goal Formatting
Goals must include **explicit UI coordinates for scroll gestures** (counterintuitive y-axis):
```python
# Scroll DOWN to reveal more content = swipe UP (high y to low y)
goal = """
3. SCROLL DOWN to see older emails - swipe from y=2000 to y=500
"""
```

**Gmail-specific patterns**:
- Opening inbox: "Open Gmail app and navigate to Inbox"
- Email selection: Include sender + subject for precise targeting
- Batch actions: "Select all emails in [category], then tap Delete/Archive"

### 3. App Cards System
Located in [config/app_cards/](config/app_cards/), automatically injected into agent prompts when app is active:
- `app_cards.json`: Maps package names to markdown files
  - `com.google.android.gm` → `gmail.md` (Gmail app instructions)
  - `com.google.android.calendar` → `calendar.md` (Calendar app instructions)
- Enable with `agent.app_cards.enabled: true` and `mode: local` in config
- **No code changes needed** - DroidRun handles injection automatically

**Creating Gmail app card**:
- Document email list UI patterns (swipe gestures, selection checkboxes)
- Include action menu locations (archive, delete, mark read)
- Define search/filter interaction patterns

### 4. Error Handling & Statistics
All processing uses try-catch with detailed logging and stats tracking:
```python
# Pattern used throughout - adapt for email triage
try:
    result = await agent.run()
    if result.success:
        self.emails_processed += 1
        categorized_data = parse_result(result)
    else:
        logger.error(f"Failed: {result.reason}")
        self.errors += 1
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    self.errors += 1
```

**MVP-specific tracking**:
- Count emails per category (Urgent/Info/Calendar/Spam/Decisions)
- Track action execution success rate
- Log categorization confidence scores

### 5. Logging Convention
Use Python `logging` module with structured levels, never bare `print()`:
```python
logger.info("✓ Success message")
logger.error("✗ Error message")
logger.warning("⚠ Warning message")
```

## Developer Workflows

### Environment Setup
```bash
# Python env (must be 3.11.x)
pyenv activate droidrun-11

# API key (required before running)
export GOOGLE_API_KEY="your-key"  # or GEMINI_API_KEY

# Device setup (first time only)
adb devices  # Verif (MVP: email triage cycle)
python main.py

# Test categorization logic
# Create test emails in processed_emails.json or extracted_email_threads.json

# Test app cards loading
python test_app_cards.py  # Validates card configuration

# Debug with trajectories (edit config.yaml)
config.logging.save_trajectory = "action"
config.logging.trajectory_gifs = true  # Generates animated GIFs in trajectories/
```

### Debugging Failed Email Processing
1. Check trajectories in `trajectories/TIMESTAMP_ID/` folders (action logs + screenshots)
2. Verify app card loaded: `grep "App card" trajectories/*/log.txt`
3. Check scroll coordinates in goal string (y-axis direction is critical)
4. Validate categorization logic: Review JSON output for misclassified emails
5. Enable Phoenix tracing: `tracing.enabled: true` in config for step visualization

### Testing Email Categories
Create test cases for each bucket:
- **Urgent**: Emails with "URGENT", "ASAP", "Payment Failed"
- **Spam**: Emails with "Lottery", "Verify your account", suspicious senders
- **Decisions**: Emails with "Please confirm", "Do you want", "Approve"
- **Calendar**: Emails with "Meeting", "Schedule", ".ics attachments"
- **Info**: Everything else (newsletters, receipts, notifications)
Email Categories
1. Update categorization logic (rule-based or LLM prompt)
2. Add Pydantic model for new category in [main.py](main.py)
3. Update JSON schema for web backend sync
4. Add category to dashboard UI

### Changing Categorization Logic
**Rule-based approach**:
```python
if any(keyword in subject.lower() for keyword in ["asap", "urgent", "payment failed"]):
    category = "Urgent"
elif any(keyword in sender.lower() for keyword in ["lottery", "verify"]):
    category = "Spam"
```

**LLM-based approach**:
- Update agent goal with category definitions
- Use structured output LLM profile (gemini-2.0-flash, temp=0.0)
- Validate output against Pydantic schema

### Changing LLM Models
Edit [config.yaml](config.yaml) `llm_profiles` section - different agents use different models:
- Manager: Higher reasoning (gemini-2.5-pro) for complex email analysis
- Executor: Fast execution (gemini-2.0-flash) for UI interactions
- Structured Output: Deterministic (gemini-2.0-flash, temp=0.0) for categorization
- TMVP User Flow Example
1. **Capture**: DroidRun scans inbox → Identifies 50 unread emails
2. **Sort**: Categorizes 15 as Spam, 5 as Urgent, 10 as Decisions, 20 as Info
3. **Sync**: Sends JSON payload to web backend
4. **Review**: User opens dashboard
   - Checks "Spam" (15 emails) → Hits "Empty Spam"
   - Notes "Urgent" (5 emails)
   - Opens "Decisions" (10 emails) → Takes actions
5. **Execute**: DroidRun fetches action queue → Performs deletions/archives on device

## Key Files Reference
- [main.py](main.py): Email triage orchestrator with Pydantic validation and OOP design
- [processed_emails.json](processed_emails.json): Processed email data (categorized output)
- [extracted_email_threads.json](extracted_email_threads.json): Raw scraped email threads
- [config.yaml](config.yaml): DroidRun v4 config with multi-agent LLM profiles
- [config/app_cards/](config/app_cards/): App-specific UI instructions (Gmail, Calendar)
- [setup.sh](setup.sh): Automated environment verification script
- [IMPROVEMENTS.md](IMPROVEMENTS.md): Before/after comparison showing evolution from procedural to OOP

## Common Pitfalls
- ❌ Creating LLM objects manually (use config-based approach)
- ❌ Using `maxsteps` instead of `max_steps` in config
- ❌ Wrong scroll direction (DOWN = swipe UP, use high→low y coordinates)
- ❌ Forgetting to enable app cards or using wrong mode (Gmail app card critical for MVP)
- ❌ Missing API key environment variable (both `GOOGLE_API_KEY` and `GEMINI_API_KEY` are checked)
- ❌ Not handling Gmail's infinite scroll when processing large inboxes
- ❌ Assuming email order is chronological (Gmail uses "importance" sorting)
- ❌ Missing confidence thresholds for Spam categorization (false positives are costly
- `agent.max_steps`: Max actions per event (default 20)
- `agent.after_sleep_action`: Wait time between actions in seconds (default 1.0)
- `delay_between_events`: Delay between processing events (in `schedule_all_events()`)

## Key Files Reference
- [main.py](main.py): Complete scheduler with Pydantic validation and OOP design
- [config.yaml](config.yaml): DroidRun v4 config with multi-agent LLM profiles
- [config/app_cards/calendar.md](config/app_cards/calendar.md): Google Calendar UI guidance
- [setup.sh](setup.sh): Automated environment verification script
- [IMPROVEMENTS.md](IMPROVEMENTS.md): Before/after comparison showing evolution from procedural to OOP

## Common Pitfalls
- ❌ Creating LLM objects manually (use config-based approach)
- ❌ Using `maxsteps` instead of `max_steps` in config
- ❌ Wrong scroll direction (DOWN = swipe UP, use high→low y coordinates)
- ❌ Forgetting to enable app cards or using wrong mode
- ❌ Missing API key environment variable (both `GOOGLE_API_KEY` and `GEMINI_API_KEY` are checked)
