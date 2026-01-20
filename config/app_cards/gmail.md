"""
Gmail App Card - UI Interaction Guide for DroidRun
Package: com.google.android.gm
"""

# Gmail App Instructions

## App Package
- **Package Name**: `com.google.android.gm`
- **App Name**: Gmail

## Key UI Elements

### Main Inbox View
- **Search Bar**: Top of screen, tap to search
- **Menu Icon**: Three horizontal lines (hamburger menu) at top left
- **Compose FAB**: Circular "+" button at bottom right
- **Email List**: Scrollable list of emails/threads

### Email Thread View
- **Thread Indicators**: 
  - Look for "(2)", "(3)", etc. next to sender name = multiple messages
  - "Show message history" button = collapsed older messages
  - Multiple sender avatars = conversation thread
- **Latest Message**: Usually at the bottom (scroll down if needed)
- **Action Icons**: Archive, Delete, Mark Unread at top toolbar

### Thread Handling Best Practices
1. **Identify threads**: Check for message count indicators
2. **Focus on latest**: Always read the newest unread message
3. **Ignore history**: Don't extract old quoted/replied messages
4. **Scroll if needed**: Latest message may require scrolling down

### Search Functionality
- **Search Syntax**:
  - `is:unread` - Shows all unread emails
  - `in:trash` - Shows deleted emails
  - `in:spam` - Shows spam folder
  - `-label:trash` - Excludes trash
- **After Search**: Results show matching emails/threads

### Common Actions

#### Archive Email
1. Long press email in list to select
2. Tap Archive icon (box with down arrow) at top
3. Or swipe email left/right (if gestures enabled)

#### Delete Email
1. Long press email in list to select
2. Tap Delete icon (trash can) at top
3. Confirm if prompted

#### Restore from Trash
1. Tap menu icon (top left)
2. Scroll down, tap "Trash" or "Bin"
3. Find and select email(s)
4. Tap "Move to" icon (folder)
5. Select "Inbox"

#### Mark as Read
1. Open the email
2. Tap the menu icon (3 vertical dots) at top right
3. Select "Mark as read" from menu
4. Email will no longer appear in "is:unread" searches

#### Mark as Unread
1. Long press email to select
2. Tap "Mark as unread" icon (envelope)

### Thread-Specific Instructions

**Reading Threads:**
```
1. Open email thread
2. Check for message count indicator
3. Scroll to bottom to see latest message
4. Look for bold/unread markers on newest message
5. Extract data from latest message only
```

**Processing Threads:**
- Treat entire thread as one unit for actions
- Archiving/deleting affects whole thread
- Marking unread marks the entire thread

### Selection Mode
- **Enter**: Long press on any email
- **Multi-select**: Tap additional emails after long press
- **Exit**: Tap X or back button

### Folder Navigation
From hamburger menu:
- Inbox (default)
- Sent
- Drafts
- Spam
- Trash
- All Mail
- Custom Labels

## Common Issues

### Thread Detection
- Not all threads show count indicators
- Look for indented messages or "Show more" buttons
- Multiple sender avatars indicate thread

### Scroll Behavior
- Threads may require scrolling to see all messages
- Latest message is typically at bottom
- Use "scroll DOWN" (swipe UP) to reveal newer content

### Search Results
- Search results persist until cleared
- Back button returns to previous view
- Refresh search by tapping search bar again

## Performance Tips

1. **Use search** instead of manually scrolling through inbox
2. **Batch operations** by selecting multiple emails
3. **Check thread count** before extracting to avoid duplicates
4. **Wait for UI** to stabilize after each action (use `wait_for_stable_ui`)

## Critical Reminders

⚠️ **Thread Handling**: Always extract only the LATEST unread message in a thread, not the entire conversation history.

⚠️ **Scroll Direction**: Scroll DOWN = swipe UP (high y to low y coordinates, e.g., 2000→500)

⚠️ **Action Confirmation**: Some actions like "Delete" may require confirmation dialog - tap "OK" or "Delete" button.

⚠️ **Trash Restoration**: Must navigate to Trash folder first, cannot restore directly from Spam view.
