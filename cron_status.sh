#!/bin/bash
#
# Cron Status Checker
#
# Shows recent cron job results and logs
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"

echo "📊 Journal AI Pipeline - Cron Status"
echo "======================================================"

# Check if logs directory exists
if [ ! -d "$LOG_DIR" ]; then
    echo "❌ No logs directory found. Cron may not have run yet."
    exit 1
fi

# Show recent daily logs
echo "📅 Recent Daily Runs:"
echo "------------------------------"
ls -la "$LOG_DIR"/cron_daily_*.log 2>/dev/null | tail -7 | while read line; do
    echo "  $line"
done

# Show latest run status
latest_log=$(ls -t "$LOG_DIR"/cron_daily_*.log 2>/dev/null | head -1)
if [ -n "$latest_log" ]; then
    echo ""
    echo "🔍 Latest Run Details:"
    echo "------------------------------"
    echo "📄 File: $(basename "$latest_log")"
    echo ""
    
    # Show success/error summary
    if grep -q "✅ Pipeline completed successfully" "$latest_log"; then
        echo "✅ Status: SUCCESS"
        events=$(grep "📅 EVENT_" "$latest_log" | wc -l)
        echo "📅 Events Created: $events"
    elif grep -q "ERROR:" "$latest_log"; then
        echo "❌ Status: FAILED"
        echo "🚨 Last Error:"
        tail -n 3 "$latest_log" | grep "ERROR:" | tail -1
    else
        echo "⚠️ Status: UNKNOWN"
    fi
    
    echo ""
    echo "📝 Latest Log Entries (last 10 lines):"
    echo "------------------------------"
    tail -n 10 "$latest_log"
else
    echo ""
    echo "❌ No daily run logs found"
fi

# Show error log if it exists
error_log="$LOG_DIR/cron_errors.log"
if [ -f "$error_log" ] && [ -s "$error_log" ]; then
    echo ""
    echo "🚨 Recent Errors:"
    echo "------------------------------"
    tail -n 5 "$error_log"
fi

# Check cron job status
echo ""
echo "⚙️ Cron Job Status:"
echo "------------------------------"
if crontab -l 2>/dev/null | grep -q "cron_daily_run.sh"; then
    echo "✅ Cron job is installed"
    echo "📋 Current cron entry:"
    crontab -l 2>/dev/null | grep "cron_daily_run.sh"
else
    echo "❌ Cron job not found"
    echo "💡 Run: crontab -e"
    echo "💡 Add: 0 7 * * * $SCRIPT_DIR/cron_daily_run.sh"
fi

echo ""
echo "🔧 Commands:"
echo "  View full log: tail -f $LOG_DIR/cron_daily_$(date +%Y-%m-%d).log"
echo "  Test script:   $SCRIPT_DIR/cron_daily_run.sh"
echo "  Edit cron:     crontab -e"