# Your Build Blocks Setup Guide

## ✅ System Configured for Your Format

The planning agent now understands your **"Build Blocks (Tomorrow's System)"** format perfectly!

## How It Works with Your Journal

### Your Current Format
```
## 📅 Build Blocks (Tomorrow's System)

*(Estimate time + set anchor order)*

Task — X min

Meet with Chris 2 hours
accounting homework 1 hour
python homework 1 hour
internship applications 1 hour + SEO 30 min
```

### What Happens

1. **System Detects** "Build Blocks" or "Tomorrow's System" section
2. **Parses Tasks** with duration estimates:
   - `Meet with Chris 2 hours` → 120 minutes
   - `accounting homework 1 hour` → 60 minutes
   - `python homework 1 hour` → 60 minutes
   - `internship applications 1 hour + SEO 30 min` → 60 minutes

3. **Schedules Sequentially** starting at 8:00 AM:
   - 08:00-10:00: Meet with Chris
   - 10:00-11:00: accounting homework
   - 11:00-12:00: python homework
   - 12:00-13:00: internship applications

4. **Creates Google Calendar Events** automatically

## Supported Duration Formats

All of these work:
- ✅ `Task 2 hours`
- ✅ `Task 1 hour`
- ✅ `Task 30 min`
- ✅ `Task 30 minutes`
- ✅ `Task — 1 hour` (with dash)
- ✅ `Task 90 min`

The `+ SEO 30 min` part is ignored (only first duration is used).

## Running the Pipeline

```bash
# Process today's journal and schedule tomorrow
python run.py

# Test the system components
python run.py test

# Test the Build Blocks parser specifically
python test_build_blocks.py
```

## What Gets Created

From your Build Blocks section, the system creates:

**Google Calendar Events:**
- Title: Exact task name from your list
- Start/End: Sequential time blocks starting at 8am
- Description: Auto-generated from task name
- Date: Tomorrow (or specified date)

## Smart Features Still Active

Even though you provide explicit durations, the system still:

- ✅ **Checks for conflicts** with existing calendar events
- ✅ **Validates timing** to ensure no overlaps
- ✅ **Respects existing meetings** in your calendar
- ✅ **Warns about scheduling issues** if any arise

## Customization Options

### Change Start Time
Edit `src/notion/extractor.py` line 159:
```python
def _schedule_build_blocks(self, plan_items, start_hour=8):  # Change 8 to your preferred hour
```

### Change Default Duration
If task has no duration, defaults to 60 minutes. Change in `_parse_time_entry()` method.

## Example Output

When you run the pipeline:

```
🚀 Starting AI Pipeline...
==================================================
🔍 Extracting journal data from Notion...
✅ Extracted journal data: {'total_entries': 3, ...}
📋 Found explicit plan with 4 items
✅ Using explicit plan from journal
📝 Preparing AI prompt for: daily_planning
🤖 Processing with OpenAI...
📅 Creating Google Calendar events...
✅ Created 4 calendar events
==================================================
✅ Pipeline complete!
```

## Your Complete Workflow

### Every Night (End of Day):
1. Reflect on your day in Notion journal
2. Fill out "Build Blocks (Tomorrow's System)" section
3. List tasks with time estimates

### System Runs (Automated or Manual):
```bash
python run.py
```

### Next Morning:
- Open Google Calendar
- See your planned day already scheduled
- Adjust as needed based on reality

## Tips for Your Format

1. **Be Realistic**: Your time estimates become your actual schedule
2. **Include Breaks**: Add `lunch break 1 hour` or `rest 30 min` as tasks
3. **Anchor Tasks**: Put your meeting with Chris first (it has a fixed time)
4. **Buffer Time**: Consider adding flex blocks between major tasks
5. **Consistency**: Keep the same format each day for best results

## Testing Your Setup

Run this to verify everything works:
```bash
python test_build_blocks.py
```

Expected output:
```
✅ Found 4 scheduled tasks:

1. 08:00-10:00: Meet with Chris
2. 10:00-11:00: accounting homework
3. 11:00-12:00: python homework
4. 12:00-13:00: internship applications
```

## Troubleshooting

**Issue**: Tasks not being parsed
- ✅ Check section header includes "Build Blocks" or "Tomorrow's System"
- ✅ Ensure duration format is: `Task [number] [hour/min]`
- ✅ Remove bullet points or checkboxes

**Issue**: Wrong times scheduled
- ✅ Default starts at 8am - change `start_hour` parameter if needed
- ✅ Tasks scheduled sequentially - first task starts at 8am

**Issue**: Some tasks missing
- ✅ Check if duration is specified (e.g., "1 hour" or "30 min")
- ✅ Make sure no template keywords in task name
- ✅ Verify task is in the Build Blocks section

## Next Steps

Your system is ready! Just:
1. Fill out Build Blocks section each night
2. Run `python run.py` before bed or as a cron job
3. Wake up to a planned day

The system falls back to AI-based planning if you don't fill out Build Blocks on a given day.
