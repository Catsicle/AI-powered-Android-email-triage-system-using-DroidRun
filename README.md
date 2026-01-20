# InboxPilot - Automated Email Triage System

Automated Android email triage using DroidRun + Gemini AI with modern web dashboard.

## Overview

InboxPilot is a complete email management system that:
1. **Scrapes** unread emails from Gmail (Android + DroidRun)
2. **Categorizes** them using Gemini AI (Urgent/Decisions/Calendar/Spam/Info)
3. **Takes actions** automatically (archive/delete based on category)
4. **Displays** results in a sleek web dashboard for user review

## Features

-  **Email Scraping**: DroidRun extracts emails from Gmail app
-  **AI Categorization**: Gemini 2.5 Flash with waterfall logic
-  **Auto Actions**: Archive info/calendar, **delete spam**, keep urgent/decisions in inbox
-  **Retry Logic**: Continues processing even if individual email extraction fails
-  **Web Dashboard**: Next.js + Obsidian Professional dark theme
-  **Decision Console**: Interactive UI for user approvals
-  **Spam Quarantine**: Bulk purge with restore capability
-  **Real-time Sync**: Dashboard polls backend every 30 seconds

## Project Structure

```
├── src/                          # 🆕 Modular Architecture
│   ├── modules/
│   │   ├── email_reader.py      # Email extraction & categorization
│   │   └── calendar_scheduler.py # Calendar automation
│   ├── models/                   # Pydantic models
│   ├── utils/                    # Config loaders & helpers
│   └── prompts.py                # AI prompt templates
├── web/                          # Next.js Frontend
│   ├── app/, components/, types/
│   └── package.json
├── api/                          # FastAPI Backend
│   ├── main.py
│   ├── routes/                   # API endpoints
│   └── droidrun_executor.py      # Action execution

```

## Prerequisites

### System Requirements
- Python 3.11.x (using pyenv)
- Android device with ADB enabled
- Google Calendar app installed on device

### Python Environment
```bash
# Using pyenv
pyenv install 3.11.14
pyenv virtualenv 3.11.14 droidrun-11
pyenv activate droidrun-11
```

### Dependencies
```bash
pip install droidrun
pip install llama-index-llms-google-genai
pip install pydantic
```

## Configuration

### 1. Set Environment Variables
```bash
export GOOGLE_API_KEY="your-google-api-key-here"
# OR
export GEMINI_API_KEY="your-google-api-key-here"
```

### 2. Configure DroidRun
The `config.yaml` file contains comprehensive DroidRun settings:

**Key Settings:**
- **Agent Configuration**: 30 max steps, vision enabled
- **LLM Profiles**: Google Gemini models for different agents
- **Logging**: Action-level trajectory saving with GIFs
- **Tracing**: Phoenix tracing enabled for debugging
- **Device**: Auto-detect Android device

### 3. Device Setup
```bash
# Enable ADB debugging on Android device
# CQuick Start

### 1. Run Email Scraping Engine
```bash
# Activate environment
pyenv activate droidrun-11

# Ensure device is connected
adb devices

# Run email triage (scrapes Gmail, categorizes, takes actions)
python inboxpilot_engine.py
```

**Features:**
- Processes all unread emails with automatic retry on failures 
- Saves categorized data to `processed_emails.json`
- **Archives**: Info and Calendar emails
- **Deletes**: Spam emails permanently
- **Keeps in Inbox**: Urgent and Decision emails for user attention

### 2. Start Web Dashboard

**Terminal 1: Backend API**
```bash
cd api
python main.py
# → http://localhost:8000
```

**Terminal 2: Frontend**
```bash
cd web
npm run dev
# → http://localhost:3000
```

### 3. (Optional) Execute User Actions
```bash
# Process action queue from dashboard decisions
python api/droidrun_executor.py
# Run the automation
python main.py
```

```python
events = scheduler.load_events_from_json("path/to/events.json")
```

**JSON Format:**
```json
{
  "calendar_emails": [
    {
      "name": "John Doe",
      "email": "john@example.com",
      "subject": "Project Meeting",
      "venue": "Conference Room A",
      "Date": "2026-01-20",
      "Time": "10:00 AM",
      "Purpose": "Discuss Q1 goals"
    }
  ]
}
```

## Code Structure

### Main Components

#### `CalendarEventScheduler`
Main automation class with the following methods:

- `__init__()`: Initialize with optional config path
- `load_events_from_json()`: Load and validate events
- `schedule_event()`: Schedule a single event
- `schedule_all_events()`: Batch process all events
- `get_stats()`: Get execution statistics
- `print_summary()`: Print execution report

#### `CalendarEvent`
Pydantic model for event validation:
```python
class CalendarEvent(BaseModel):
    name: str
    email: Optional[str]
    subject: str
    venue: str
    Date: str  # YYYY-MM-DD
    Time: str  # 12-hour format
    Purpose: str
```

