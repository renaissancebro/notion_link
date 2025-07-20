# Project Structure

Clean, organized codebase with 3 main concerns:

```
📁 planning_agent/
├── 🚀 run.py                    # Main entry point
├── 📄 main.py                   # Legacy compatibility
├── 📋 README.md                 # Documentation
├── 📜 LICENSE                   # MIT License
├── 📦 requirements.txt          # Dependencies
├── 🔒 .env.sample              # Environment template
├── 🚫 .gitignore               # Git ignore rules
│
├── 📁 src/                      # Main source code
│   ├── 🔧 pipeline.py          # Main orchestrator
│   │
│   ├── 📁 notion/              # Notion integration
│   │   ├── fetcher.py          # Raw API calls
│   │   └── extractor.py        # Content extraction & filtering
│   │
│   ├── 📁 ai/                  # AI processing
│   │   └── processor.py        # OpenAI integration & prompts
│   │
│   └── 📁 calendar_api/        # Calendar integration
│       └── integration.py      # Google Calendar API
│
├── 📁 config/                  # Configuration files
│   ├── GOOGLE_CALENDAR_SETUP.md
│   └── Notion_API_Tests.postman_collection.json
│
└── 📁 tests/                   # Testing & utilities
    ├── test_components.py      # Comprehensive tests
    ├── test_individual.py      # Individual component tests
    ├── print_content.py        # Content viewer
    └── show_content.py         # Detailed content analysis
```

## Usage

**New Clean Interface:**
```bash
python run.py                    # Run full pipeline
python run.py help              # Show usage help
python run.py test              # Test all components
python run.py extract today     # Extract journal data only
```

**Legacy Support:**
```bash
python main.py search           # Old search command still works
```

## 3 Main Concerns

1. **📊 Notion** (`src/notion/`) - Journal data extraction
2. **🤖 AI** (`src/ai/`) - OpenAI processing & prompt generation  
3. **📅 Calendar** (`src/calendar_api/`) - Google Calendar integration

Each concern is cleanly separated with clear interfaces.