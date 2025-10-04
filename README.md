# Journal AI Pipeline

A Python-based system that extracts journal entries from Notion and automatically schedules them to Google Calendar. **Now with Build Blocks support - write your plan with durations and it schedules automatically!**

## Features

- **Notion Integration**: Extracts journal content from Notion databases with smart content filtering
- **Explicit Plan Scheduling**: Write your daily plan with times at end of day - system schedules it directly to calendar
- **AI Processing**: OpenAI GPT-4 analysis of journal entries for actionable insights (when explicit plan not provided)
- **Google Calendar Integration**: Automatically creates time-blocked calendar events while respecting existing meetings
- **Smart Content Filtering**: Separates user-written content from template text
- **Free-Window Scheduling**: Detects current calendar gaps and only proposes plan blocks that fit available windows
- **Flexible Time Formats**: Supports 9:00-10:30, 2pm-4pm, 14:00 (1 hour), and more
- **Multi-date Support**: Process any date range and create events for future dates
- **Central Time Zone**: Configured for America/Chicago timezone
- **Secure OAuth2**: Protected credential management with comprehensive .gitignore

## Quick Start

1. **Setup Environment**:
   ```bash
   pip install -r requirements.txt
   cp .env.sample .env
   # Add your API keys to .env (see .env.sample for format)
   ```

   ⚠️ **Security Note**: Never commit your `.env` file to git - it contains sensitive API keys!

2. **Test the System**:
   ```bash
   python run.py test          # Test all components
   python run.py extract       # View extracted content
   ```

3. **Run the Pipeline**:
   ```bash
   python run.py               # Full AI pipeline for today
   python run.py help          # Show all usage options
   ```

   The planner will pull today’s journal, look at tomorrow’s calendar, and only schedule tasks into free windows.

## Architecture

Clean 3-concern separation in `src/` folder:

### 📊 **Notion** (`src/notion/`)
- **fetcher.py** - Raw Notion API calls and database queries
- **extractor.py** - Content extraction, filtering, and AI formatting

### 🤖 **AI** (`src/ai/`) 
- **processor.py** - OpenAI integration and structured prompt generation

### 📅 **Calendar** (`src/calendar_api/`)
- **integration.py** - Google Calendar API, free-window detection, and conflict-aware event creation

### 🔧 **Pipeline** (`src/pipeline.py`)
- **JournalAIPipeline** - Main orchestrator connecting all 3 concerns

## Testing

- `test_components.py` - Comprehensive test suite
- `test_individual.py` - Test individual components
- `print_content.py` - Clean content viewer
- `show_content.py` - Detailed content analysis

## Configuration

Create `.env` file with:
```
NOTION_TOKEN=your_notion_integration_token
DATABASE_ID=your_notion_database_id
OPENAI_API_KEY=your_openai_api_key
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
```

**🔒 SECURITY SETUP**:
1. Download OAuth2 credentials from Google Cloud Console → Save as any filename
2. Run `python setup_calendar.py` to automatically:
   - Rename credentials to standard `credentials.json`
   - Complete OAuth2 flow for calendar access
   - Update `.env` with proper settings
3. Your credentials are protected by comprehensive `.gitignore`

**⚠️ SECURITY WARNING**: 
- Never commit `.env`, `credentials.json`, or `token.json` to version control
- All sensitive files are automatically protected by `.gitignore`

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Workflow

**Your Daily Process:**

1. **End of Day**: In your Notion journal, fill out your Build Blocks section:
   ```
   ## 📅 Build Blocks (Tomorrow's System)

   Meet with Chris 2 hours
   accounting homework 1 hour
   python homework 1 hour
   internship applications 1 hour + SEO 30 min
   ```

2. **System Runs**: Pipeline extracts your plan and schedules sequentially to Google Calendar
   - Meet with Chris: 08:00-10:00
   - accounting homework: 10:00-11:00
   - python homework: 11:00-12:00
   - internship applications: 12:00-13:00

3. **Next Morning**: Wake up to your pre-planned day already on your calendar

**Command Line:**
```bash
python run.py                         # Today's full pipeline
python run.py run 2025-07-19         # Specific date
python run.py run today reflection   # Different AI task type
python run.py extract yesterday      # Extract data only
```

**Python API:**
```python
# New clean interface
from src.pipeline import JournalAIPipeline

pipeline = JournalAIPipeline()
result = pipeline.run_full_pipeline()

# Individual components
from src.notion.extractor import JournalExtractor
extractor = JournalExtractor()
data = extractor.get_journal_entry()
```

## Supported Time Formats

### Build Blocks Format (Your Setup)
Tasks are scheduled sequentially starting at 8:00 AM:
- `Task 2 hours` → 08:00-10:00
- `Task 30 min` → 10:00-10:30
- `Task — 1 hour` → 10:30-11:30

**Supported duration formats:**
- `Task X hours` or `Task X hour`
- `Task X min` or `Task X minutes`
- `Task — X hours` (with dash separator)

### Alternative Formats (Also Supported)
- **Time ranges**: `9:00-10:30: Task`, `2pm-4pm: Task`
- **Single time with duration**: `14:00: Task (1 hour)`

**Keywords that trigger planning mode:**
- "build blocks", "tomorrow's system" (your format)
- "tomorrow", "next day", "plan for", "schedule", "to do", "tasks for"

## Live Example

**Real Test Results** (Yesterday → Tomorrow):
```bash
python run.py
# ✅ Extracted: Builder's edge journal from 2025-10-04 (and recent context)
# 🤖 AI Processing: Generated a JSON schedule with split focus blocks
# 📅 Calendar: 0 new events created (existing calendar already covered every free window; warnings logged instead)
```

## Understanding the Output

- **AI Prompt Preview**: `result['ai_prompt']` (or the console output) shows the structured prompt sent to GPT, including free windows and action-item estimates.
- **Validation Warnings**: When the calendar is already full, the pipeline reports skipped blocks and unscheduled tasks instead of forcing conflicts.
- **Logs**: Nightly runs append to `logs/cron_daily_<date>.log`, capturing the same warnings plus a list of unscheduled items for quick follow-up.

## System Status

✅ **Fully Operational**:
- Notion extraction working
- OpenAI GPT-4 integration active  
- Google Calendar gap-aware scheduling active
- Central Time timezone configured
- OAuth2 security implemented
- Complete pipeline: Journal → AI → Calendar

Built for entrepreneurs who want to transform their journal reflections into actionable daily planning.
