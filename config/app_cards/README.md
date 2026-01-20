# App Cards Configuration

This directory contains app-specific instruction cards for DroidRun agents.

## Structure

```
config/app_cards/
├── app_cards.json      # Package name → markdown file mapping
└── calendar.md         # Google Calendar app instructions
```

## How It Works

1. **DroidRun detects the active app** by its package name
2. **Looks up the package** in `app_cards.json`
3. **Loads the corresponding markdown file** (e.g., `calendar.md`)
4. **Injects instructions** into the agent's system prompt

## Current App Cards

### Google Calendar (`calendar.md`)
- **Package Names**: 
  - `com.google.android.calendar` (Google Calendar)
  - `com.android.calendar` (AOSP Calendar)
- **Purpose**: Guide agents on creating calendar events
- **Key Instructions**:
  - Skip location field (use description instead)
  - Don't add guests unless requested
  - Proper field order and timing
  - UI element identification

## Benefits

✅ **App-specific guidance** - Agents know app quirks and best practices  
✅ **Improved success rate** - Reduces trial-and-error  
✅ **Faster execution** - Agents follow optimal workflows  
✅ **Consistent behavior** - Same approach across all events  

## Usage

App cards are automatically loaded when:
- `agent.app_cards.enabled = true` in config.yaml
- Agent is interacting with a recognized app
- Corresponding card exists in this directory

No code changes needed - DroidRun handles it automatically!

## Adding New App Cards

1. **Get the package name**:
   ```bash
   adb shell dumpsys window | grep -i mCurrentFocus
   ```

2. **Create markdown file** (e.g., `gmail.md`)

3. **Add mapping** to `app_cards.json`:
   ```json
   {
     "com.google.android.gm": "gmail.md"
   }
   ```

4. **Write instructions** following the calendar.md template

## Configuration

In `config.yaml`:
```yaml
agent:
  app_cards:
    enabled: true              # Enable app cards
    mode: local                # Use local markdown files
    app_cards_dir: config/app_cards  # This directory
```

## Best Practices

- **Be specific** about UI elements and their locations
- **Include workarounds** for common issues
- **Mention what to avoid** (e.g., skip location field)
- **Provide examples** of successful workflows
- **Document version differences** if applicable

## Troubleshooting

If app cards aren't being used:
1. Check `enabled: true` in config.yaml
2. Verify package name in app_cards.json matches actual app
3. Ensure markdown file exists and is readable
4. Check DroidRun logs for card loading messages
