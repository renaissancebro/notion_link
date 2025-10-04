# Explicit Plan Scheduling Guide

## Overview

The system now supports **direct plan scheduling** - you write your explicit daily plan with times at the end of each day, and the system schedules it directly to your Google Calendar. No AI inference needed!

## How It Works

### Your Workflow

1. **End of Day**: In your Notion journal entry, add a planning section
2. **Write Your Plan**: List tomorrow's tasks with specific times
3. **Run Pipeline**: System extracts and schedules your plan to calendar
4. **Next Morning**: Wake up to your pre-planned day

### Example Journal Entry

```
## Daily Reflection

[Your usual journal content here...]

## Plan for Tomorrow

9:00-10:30: Deep work on accounting system
11:00-12:00: Internship applications and resume updates
2pm-4pm: Customer discovery calls
4:00: Code review and PR cleanup (1 hour)
5:30-6:30: Study React hooks documentation
```

## Supported Time Formats

### Time Ranges
- `9:00-10:30: Task description`
- `2pm-4pm: Another task`
- `14:00-15:30: Task in 24-hour format`
- `8:30-9:00 Morning standup` (with or without colon after time)

### Single Time with Duration
- `14:00: Review PRs (1 hour)`
- `3pm: Team sync (30 minutes)`
- `9:00 (2 hours): Deep work session`

### Time Interpretation
- **With AM/PM**: Uses explicit time (2pm = 14:00)
- **Without AM/PM**:
  - Hours 8-23: Treated literally
  - Hours 1-7: Assumed PM (4:00 becomes 16:00)
  - This matches typical work hours

## Planning Section Triggers

The system looks for these keywords to identify your planning section:
- "tomorrow"
- "next day"
- "plan for"
- "schedule"
- "to do"
- "tasks for"

**Examples:**
- "## Plan for Tomorrow"
- "## Tomorrow's Schedule"
- "## Tasks for Next Day"
- "## To Do Tomorrow"

## What Happens Behind the Scenes

1. **Extraction**: System parses your time-based entries
2. **Validation**: AI checks for conflicts with existing calendar
3. **Scheduling**: Creates Google Calendar events with your exact times
4. **Conflict Detection**: Warns you if tasks overlap with existing meetings

## Fallback to AI Inference

If you don't provide an explicit plan, the system falls back to the original AI-based planning:
- Analyzes your journal entries
- Infers action items and priorities
- Suggests time blocks based on context
- Uses smart gap-filling around existing calendar events

## Testing Your Setup

Run this command to test the time parser:
```bash
python test_explicit_plan.py
```

## Tips for Success

1. **Be Specific**: Include exact times or durations
2. **Use Clear Headers**: Include planning keywords in section titles
3. **Check Conflicts**: Review existing calendar before planning
4. **Iterate**: System improves as you use it consistently

## Benefits Over AI Inference

- ✅ **Faster**: No complex AI processing needed
- ✅ **Cheaper**: Less OpenAI API usage
- ✅ **More Accurate**: Uses your exact intentions
- ✅ **More Control**: You decide the schedule, not the AI
- ✅ **Better for Routines**: Perfect for established workflows

## Example Output

When you run the pipeline with an explicit plan:
```
🚀 Starting AI Pipeline...
==================================================
🔍 Extracting journal data from Notion...
✅ Extracted journal data: {'total_entries': 3, ...}
📋 Found explicit plan with 5 items
✅ Using explicit plan from journal
📝 Preparing AI prompt for: daily_planning
🤖 Processing with OpenAI...
📅 Creating Google Calendar events...
✅ Created 5 calendar events
==================================================
✅ Pipeline complete!
```

## Advanced Features

### Priority Importance System
You can still use importance markers in your tasks:
```
9:00-10:30: [HIGH] Deep work on critical feature
2pm-3pm: [LOW] Email catch-up
```

### Custom Durations
If not specified, defaults:
- Regular tasks: 1 hour
- Quick items with "review", "check": 30 minutes
- Deep work sessions: Minimum 1 hour

### Template Integration
The system filters out your Notion template keywords automatically, so you can keep your existing template structure.
