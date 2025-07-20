#!/bin/bash
#
# Daily Journal AI Pipeline Runner
# 
# This script runs the complete journal processing pipeline:
# 1. Extracts yesterday's journal entries from Notion
# 2. Processes them through AI for insights
# 3. Creates calendar events for today
#
# Usage: ./cron_daily_run.sh
# Cron: 0 7 * * * /path/to/cron_daily_run.sh
#

# Set script directory and change to it
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set up environment
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# Logging setup
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/cron_daily_$(date +%Y-%m-%d).log"
ERROR_LOG="$LOG_DIR/cron_errors.log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] $1" | tee -a "$LOG_FILE"
}

# Function to log errors
log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] ERROR: $1" | tee -a "$LOG_FILE" >> "$ERROR_LOG"
}

# Start logging
log "Starting Daily Journal AI Pipeline"
log "Working directory: $SCRIPT_DIR"

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    log "Activating virtual environment"
    source venv/bin/activate
else
    log "No virtual environment found - using system Python"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    log_error ".env file not found - pipeline cannot run without API keys"
    exit 1
fi

# Check if credentials files exist
if [ ! -f "credentials.json" ]; then
    log_error "Google Calendar credentials.json not found"
    exit 1
fi

# Run the daily pipeline
# Strategy: Use yesterday's journal to plan today's calendar events
log "Running daily pipeline: yesterday's journal → today's calendar"

# Calculate dates
yesterday=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)
today=$(date +%Y-%m-%d)

log "Processing journal from $yesterday to create events for $today"

# Run the pipeline with error handling
python_output=$(python -c "
import sys
import os
from datetime import date, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from pipeline import JournalAIPipeline
    
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    
    # Initialize pipeline
    pipeline = JournalAIPipeline()
    
    # Run full pipeline using yesterday's data for today's calendar
    result = pipeline.run_full_pipeline(yesterday, 'daily_planning')
    
    if result.get('status') == 'error':
        print(f'PIPELINE_ERROR: {result.get(\"message\")}')
        sys.exit(1)
    
    # Extract results
    calendar_result = result.get('calendar_result', {})
    ai_response = result.get('ai_response', {})
    
    events_created = calendar_result.get('events_created', 0)
    ai_tokens = ai_response.get('tokens_used', 0)
    
    print(f'PIPELINE_SUCCESS: {events_created} events created, {ai_tokens} tokens used')
    
    # Log individual events
    for i, event in enumerate(calendar_result.get('events', []), 1):
        title = event.get('title', 'Unknown')
        start = event.get('start', 'Unknown')
        print(f'EVENT_{i}: {title} at {start}')
    
except Exception as e:
    print(f'PIPELINE_ERROR: {str(e)}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
" 2>&1)

# Parse Python output
if echo "$python_output" | grep -q "PIPELINE_SUCCESS"; then
    # Extract success details
    success_line=$(echo "$python_output" | grep "PIPELINE_SUCCESS")
    log "✅ Pipeline completed successfully: $success_line"
    
    # Log created events
    echo "$python_output" | grep "EVENT_" | while read event_line; do
        log "📅 $event_line"
    done
    
    log "Daily pipeline completed successfully"
    exit 0
    
elif echo "$python_output" | grep -q "PIPELINE_ERROR"; then
    # Extract error details
    error_line=$(echo "$python_output" | grep "PIPELINE_ERROR" | head -1)
    log_error "Pipeline failed: $error_line"
    log_error "Full output: $python_output"
    exit 1
    
else
    log_error "Unexpected pipeline output: $python_output"
    exit 1
fi