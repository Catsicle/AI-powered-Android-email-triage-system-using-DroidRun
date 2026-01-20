# InboxPilot Web Dashboard

Modern web dashboard for InboxPilot - Automated Android Email Triage System.

## Design System: Obsidian Professional

- **Theme**: Deep Dark Mode for eye comfort and data legibility
- **Palette**:
  - Backgrounds: Matte Black (#121212), Dark Charcoal (#1E1E1E)
  - Text: Primary White (#FFFFFF), Cool Grey (#A0A0A0)
  - Accents: Electric Blue, Amber, Desaturated Red, Emerald Green
- **Typography**: Inter (clean sans-serif), Roboto Mono (timestamps/IDs)

## Tech Stack

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Integration**: DroidRun automation engine
- **Data**: JSON files (processed_emails.json, extracted_email_threads.json)

## Features

### 1. Dashboard (Command Center)
- 5 Key Metric Cards (Urgent, Decisions, Calendar, Info, Spam)
- Real-time sync indicator
- Quick action buttons

### 2. Decision Console
- Interactive action cards for emails requiring decisions
- Optimistic UI updates
- Actions: Archive, Delete, Reply
- Toast notifications for queued actions

### 3. Spam Quarantine
- High-density table view
- Bulk "Purge All" functionality
- Individual restore capability
- Confirmation dialogs for destructive actions

### 4. Read-Only Views
- **Urgent**: Alert-style cards with amber left border
- **Calendar**: Chronological timeline view
- **Info**: Collapsed accordion list

## Project Structure

```
web/
├── app/
│   ├── page.tsx          # Main app with view routing
│   ├── layout.tsx        # Root layout with metadata
│   └── globals.css       # Tailwind + custom styles
├── components/
│   ├── Dashboard.tsx     # Command center HUD
│   ├── DecisionConsole.tsx
│   ├── SpamQuarantine.tsx
│   ├── UrgentView.tsx
│   ├── InfoView.tsx
│   ├── CalendarView.tsx
│   ├── Sidebar.tsx       # Vertical navigation
│   ├── Header.tsx        # Sync indicator
│   ├── MetricCard.tsx    # Stat cards
│   └── Toast.tsx         # Notifications
├── types/
│   └── index.ts          # TypeScript interfaces
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js

api/
├── main.py               # FastAPI backend
├── droidrun_executor.py  # DroidRun integration
└── requirements.txt
```

## Setup & Installation

### 1. Frontend Setup

```bash
cd web

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 2. Backend Setup

```bash
cd api

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
python main.py
```

The API will be available at `http://localhost:8000`

### 3. DroidRun Integration

The backend automatically reads from these JSON files in the project root:
- `processed_emails.json` - Processed and categorized emails
- `extracted_email_threads.json` - Raw scraped email data

## API Endpoints

### GET /api/emails
Returns categorized email data:
```json
{
  "urgent": [...],
  "info": [...],
  "calendar": [...],
  "spam": [...],
  "decisions": [...],
  "lastSync": "2026-01-19T10:30:00"
}
```

### POST /api/actions
Queue an action for DroidRun:
```json
{
  "emailId": "email_123",
  "action": "archive" // or "delete", "reply"
}
```

### POST /api/actions/purge-spam
Queue bulk deletion of all spam emails.

### GET /api/actions/queue
Get pending actions for DroidRun to execute.

### GET /api/stats
Get email statistics and counts by category.

## DroidRun Execution Flow

1. **User Action**: User clicks Archive/Delete/Reply on dashboard
2. **API Queue**: Action is queued in FastAPI backend
3. **Executor Fetch**: `droidrun_executor.py` polls for queued actions
4. **Agent Execute**: DroidRun agent performs UI interactions on Android
5. **Status Update**: Action marked as completed

### Running the Executor

```bash
# Process action queue once
python api/droidrun_executor.py

# Or run periodically via cron
*/5 * * * * cd /path/to/Hackathon && python api/droidrun_executor.py
```

## Data Structure

The backend expects pre-categorized email data from DroidRun in `processed_emails.json`:

```json
{
  "urgent": [...],
  "info": [...],
  "calendar": [...],
  "spam": [...],
  "decisions": [...]
}
```

Each email object should contain:
- `id`: Unique identifier
- `sender`: Email sender name/address
- `subject`: Email subject line
- `preview`: Email body preview or description
- `timestamp`: When the email was received
- `category`: Pre-assigned category (optional, uses parent key)
- `read`: Boolean flag (optional)

Categorization is handled by DroidRun using LLM-based classification before syncing to the backend.

## Development

### Frontend

```bash
cd web

# Development mode with hot reload
npm run dev

# Production build
npm run build
npm start

# Linting
npm run lint
```

### Backend

```bash
cd api

# Development with auto-reload
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Environment Variables

Create `.env.local` in the `web/` directory:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For the backend, ensure these are set:
```bash
GOOGLE_API_KEY=your-google-api-key
GEMINI_API_KEY=your-gemini-api-key
```

## Empty State Handling

- **All Caught Up**: Shows when Decisions queue is empty
- **No Spam**: Shows when Spam quarantine is empty
- **No Items**: Graceful handling for each category

## Toast Notifications

Non-intrusive bottom-center toasts appear when:
- Action is queued (Archive/Delete/Reply)
- Spam is purged
- Email is restored from spam

Auto-dismiss after 3 seconds.

## Responsive Design

- Desktop-first design (optimized for 1920x1080+)
- Sidebar collapses on smaller screens
- Card layouts stack on mobile
- Touch-friendly buttons and interactions

## Performance

- Optimistic UI updates for instant feedback
- Polling every 30 seconds for email updates
- Minimal re-renders with React best practices
- Tailwind CSS for minimal bundle size

## Future Enhancements

1. **Real-time Sync**: WebSocket connection instead of polling
2. **LLM Categorization**: Replace rule-based logic with Gemini API
3. **Email Preview Modal**: Full email content viewing
4. **Search & Filter**: Find emails across categories
5. **Action History**: Log of executed actions
6. **Multi-device Support**: Manage multiple Android devices
7. **Push Notifications**: Alert for urgent emails
8. **Dark/Light Theme Toggle**: User preference

## Contributing

When adding new features:
1. Update TypeScript types in `types/index.ts`
2. Add API endpoints in `api/main.py`
3. Create React components following existing patterns
4. Use Tailwind utility classes (avoid custom CSS)
5. Maintain Obsidian Professional design system colors

## License

Part of the InboxPilot project.
