# Google Calendar App Instructions

## App Package
- **Package Name**: `com.google.android.calendar` or `com.android.calendar`
- **App Name**: Google Calendar

## Key UI Elements

### Main Screen
- **FAB Button**: Floating Action Button ('+' icon) at bottom right - use to create events
- **Date Navigation**: Tap dates to navigate, swipe to change months
- **View Modes**: Day, Week, Month, Schedule views available

### Event Creation Screen
- **Title Field**: "Add title" - First field at the top
- **Date/Time**: Tap to open date/time picker
- **Location Field**: "Add location" - SKIP THIS, don't use it
- **Description Field**: "Add description" or "Add note" - Use this for venue and details
- **Guests Field**: "Add guests" - AVOID unless specifically requested
- **Save Button**: Checkmark or "Save" at top right

## Best Practices

### Creating Events
1. **Always use the FAB (+) button** at bottom right to create new events
2. **Fill title first** - This is mandatory
3. **Set date and time** before other fields
4. **Skip the location field** - Add venue details to description instead
5. **Use description field** for all meeting details including venue
6. **Don't add guests** unless explicitly requested
7. **Save immediately** after filling required fields

### Field Order (Recommended)
1. Title (required)
2. Date (required)
3. Time (required)
4. **SCROLL DOWN** (swipe from y=2000 to y=500) to reveal description field
5. Description (venue + purpose + attendee info)
6. Save

### Common Gestures
- **Swipe down**: Scroll to see more fields
- **Tap date/time**: Opens picker dialog
- **Long press**: Avoid - can cause unwanted actions
- **Back button**: Cancels without saving

### CRITICAL: Scroll Direction
**To scroll DOWN (see fields below):**
- Swipe UP on screen (finger moves upward)
- Coordinates: Start at HIGHER y, end at LOWER y
- Example: `swipe(550, 2000, 550, 500)` ✅ CORRECT
- NOT: `swipe(550, 500, 550, 2000)` ❌ WRONG (scrolls up)

**To scroll UP (see fields above):**
- Swipe DOWN on screen (finger moves downward)  
- Coordinates: Start at LOWER y, end at HIGHER y
- Example: `swipe(550, 500, 550, 2000)` - scrolls up

## Important Notes

### Location Field - DO NOT USE
- **Never fill the location field** when creating events
- Location information should be included in the description
- This prevents location search and GPS-related delays
- Format: "Meeting with [Name] at [Venue]. Purpose: [Purpose]"

### Description Field - ALWAYS USE
- This is where venue information goes
- Include: attendee name, venue, and purpose
- Example: "Meeting with John Doe at Conference Room B. Purpose: Discuss Q1 goals"

### Time Format
- App supports both 12-hour (10:00 AM) and 24-hour (10:00) formats
- Use the format provided in the task

### Date Format
- Calendar picker handles various date formats
- YYYY-MM-DD is most reliable
- Select date from picker rather than typing when possible

## Troubleshooting

### If Event Creation Fails
1. Check if Calendar app is the default calendar app
2. Verify date is not in the distant past
3. Ensure time is valid (not outside 0:00-23:59)
4. Try simpler event first (title + date/time only)

### UI Timing
- **Wait 1-2 seconds** after opening app before tapping FAB
- **Wait for keyboard** to appear before typing
- **Wait for save confirmation** before exiting

### Accessibility
- Fields should be accessible by text (content-desc or text)
- If field not found by name, look for nearby text labels
- Date/time pickers may require special handling

## Performance Tips
- **Skip unnecessary fields** (location, color, reminders)
- **Don't search for locations** - adds 5-10 seconds
- **Minimize scrolling** - only scroll when needed
- **Use default settings** for notifications and reminders

## Field Identification

### By Text Content
- Title: "Add title" or "Title"
- Date: Shows current date or "Today"
- Time: Shows current time or default time
- Description: "Add description", "Add note", or "Description"
- Location: "Add location" or "Location" - **SKIP THIS**

### By Resource ID
- Save button: Usually has "save" in ID
- FAB: Usually `floating_action_button` or similar
- Title field: Often `title_edit` or `event_title`

## Example Workflow

### Successful Event Creation
```
1. Launch Google Calendar
2. Wait for app to fully load (2 seconds)
3. Tap FAB (+) button at bottom right
4. Wait for event creation screen
5. Tap "Add title" field
6. Type event title
7. Tap date field
8. Select date from picker
9. Tap time field
10. Select time from picker
11. SCROLL DOWN - swipe(550, 2000, 550, 500) to reveal description
12. Tap "Add description"
13. Type: "Meeting with [Name] at [Venue]. Purpose: [Purpose]"
14. Tap Save (checkmark at top right)
15. Wait for confirmation
16. Return to calendar view
```

### What to Avoid
- ❌ Don't tap "Add location" field
- ❌ Don't add guests unless specifically asked
- ❌ Don't change notification settings
- ❌ Don't set up recurring events unless needed
- ❌ Don't change calendar color or category

## App-Specific Quirks

### Google Calendar
- May show "Busy" status by default - ignore it
- Might suggest location autocomplete - skip it
- Can show travel time options - ignore them
- May prompt for video conferencing - decline it

### Version Differences
- Older versions: "Add note" instead of "Add description"
- Newer versions: More fields and options (ignore extras)
- Layout may vary but core flow is consistent

## Success Indicators
- ✅ Event appears in calendar grid after saving
- ✅ Event details show correctly when tapped
- ✅ App returns to main calendar view
- ✅ No error dialogs appear

## Failure Indicators
- ❌ "Required field" error
- ❌ Date/time picker doesn't close
- ❌ Save button is grayed out/disabled
- ❌ App crashes or freezes
- ❌ Event doesn't appear in calendar
