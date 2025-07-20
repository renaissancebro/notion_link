# Journal AI Pipeline

A Python-based system that extracts journal entries from Notion, processes them through AI, and integrates with Google Calendar for intelligent daily planning.

## Features

- **Notion Integration**: Extracts journal content from Notion databases
- **Smart Content Filtering**: Separates user-written content from template text
- **AI Processing**: Formats journal data for OpenAI consumption
- **Calendar Integration**: Prepares data for Google Calendar scheduling
- **Content Organization**: Categorizes entries by sections (Built Today, Goals, etc.)

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

## Core Components

### `journal_extractor.py`
Extracts and organizes journal content from Notion:
- `JournalExtractor.get_journal_entry()` - Get entry for specific date
- `JournalExtractor.format_for_openai()` - Format for AI processing
- `JournalExtractor.extract_for_calendar_planning()` - Extract scheduling data

### `ai_pipeline.py`
Complete pipeline for AI processing:
- `AIPipeline.run_full_pipeline()` - Full extraction → AI → calendar flow
- `AIPipeline.prepare_ai_prompt()` - Generate structured prompts
- Ready for OpenAI and Google Calendar integration

### `notion_fetcher.py`
Core Notion API integration:
- Database queries and content retrieval
- Edit detection and content filtering
- Debug tools for troubleshooting

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
```

**⚠️ SECURITY WARNING**: 
- Copy `.env.sample` to `.env` and add your real tokens
- Never commit `.env` to version control
- The `.gitignore` file protects your credentials

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Usage Examples

```python
# Extract today's journal for AI
from journal_extractor import get_today_journal_for_ai
data = get_today_journal_for_ai()

# Run full pipeline
from ai_pipeline import AIPipeline
pipeline = AIPipeline()
result = pipeline.run_full_pipeline()

# Get calendar planning data
from journal_extractor import get_calendar_planning_data
calendar_data = get_calendar_planning_data(days=7)
```

## Next Steps

1. Add OpenAI API integration to `ai_pipeline.py`
2. Add Google Calendar API integration
3. Replace placeholder responses with real API calls

Built for entrepreneurs who want to transform their journal reflections into actionable daily planning.