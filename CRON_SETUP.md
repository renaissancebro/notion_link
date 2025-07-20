# Cron Job Setup - Daily Journal AI Pipeline

This guide helps you set up automatic daily execution of your Journal AI Pipeline using cron.

## 🎯 What It Does

**Evening Planning Workflow**:
1. **7:00 PM CT**: Cron triggers the pipeline when you're active
2. **Extract**: Today's journal entries from Notion
3. **Process**: AI analyzes entries and creates tomorrow's plan
4. **Create**: Calendar events for tomorrow based on insights
5. **Log**: Results for monitoring and debugging

## 🚀 Quick Setup

### 1. Test the Script First
```bash
# Test the cron script manually
./cron_daily_run.sh

# Check if it created a log file
ls -la logs/cron_daily_*.log
```

### 2. Install the Cron Job
```bash
# Open cron editor
crontab -e

# Add this line (runs daily at 7:00 PM Central Time)
0 19 * * * /Users/joshuafreeman/Desktop/agent_projects/agents/planning_agent/cron_daily_run.sh

# Save and exit (:wq in vim)
```

### 3. Verify Installation
```bash
# Check if cron job is installed
crontab -l

# Monitor status
./cron_status.sh
```

## ⏰ Cron Schedule Options

```bash
# Daily at 7:00 PM (recommended)
0 19 * * *

# Daily at 8:00 PM
0 20 * * *

# Weekdays only at 7:00 PM
0 19 * * 1-5

# Twice daily (lunch planning + evening review)
0 12,19 * * *
```

## 📊 Monitoring & Logs

### View Status
```bash
# Quick status check
./cron_status.sh

# View today's log in real-time
tail -f logs/cron_daily_$(date +%Y-%m-%d).log

# Check error log
cat logs/cron_errors.log
```

### Log Files
- `logs/cron_daily_YYYY-MM-DD.log` - Daily execution logs
- `logs/cron_errors.log` - Error summary
- Each log includes:
  - Timestamp for each step
  - Events created with details
  - Token usage statistics
  - Success/failure status

## 🔧 Troubleshooting

### Common Issues

**1. Cron job not running**
```bash
# Check if cron service is running (macOS)
sudo launchctl list | grep cron

# Check system cron logs
grep CRON /var/log/system.log
```

**2. Python path issues**
```bash
# Test Python availability in cron environment
* * * * * /usr/bin/which python3 >> /tmp/cron_test.log 2>&1

# Or specify full path in script
/usr/local/bin/python3 run.py
```

**3. Permission issues**
```bash
# Make script executable
chmod +x cron_daily_run.sh

# Check file permissions
ls -la cron_daily_run.sh
```

**4. Environment variables**
```bash
# Cron has minimal environment
# The script handles this by:
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"
```

## 🛡️ Security Considerations

✅ **Protected**:
- Script runs in your user context (not root)
- All credentials remain in protected files
- Logs don't contain sensitive data
- Virtual environment isolation

⚠️ **Best Practices**:
- Keep cron script in secure directory
- Monitor logs regularly
- Set up log rotation if needed
- Test script changes manually first

## 📱 Notification Setup (Optional)

Add notification when pipeline completes:

```bash
# macOS notification
./cron_daily_run.sh && osascript -e 'display notification "Journal AI Pipeline completed successfully" with title "Daily Planning Ready"'

# Email notification (requires mail setup)
./cron_daily_run.sh && echo "Daily planning completed at $(date)" | mail -s "Journal AI Pipeline" your@email.com
```

## 🎛️ Advanced Configuration

### Custom Time Zones
The script automatically uses your system timezone. For different zones:
```bash
# Run at 7 AM EST regardless of system timezone
0 12 * * * TZ=America/New_York /path/to/cron_daily_run.sh
```

### Multiple Profiles
Run different configurations:
```bash
# Morning planning
0 7 * * * /path/to/cron_daily_run.sh

# Evening review
0 18 * * * TASK_TYPE=reflection /path/to/cron_daily_run.sh
```

### Backup Strategy
```bash
# Weekly backup of logs
0 0 * * 0 tar -czf logs/backup_$(date +%Y%m%d).tar.gz logs/cron_daily_*.log
```

## 📈 Expected Results

**Successful Daily Run**:
- 3-5 calendar events created for today
- Based on yesterday's journal insights
- Events include focus time, breaks, specific tasks
- All timed for Central Time zone
- Logged with timestamps and details

**Example Output**:
```
[2025-07-21 19:00:01 CT] Starting Daily Journal AI Pipeline
[2025-07-21 19:00:15 CT] ✅ Pipeline completed successfully: 4 events created, 1247 tokens used
[2025-07-21 19:00:15 CT] 📅 EVENT_1: Deep Work: Notion Integration at 2025-07-22T09:00:00
[2025-07-21 19:00:15 CT] 📅 EVENT_2: Code Review Session at 2025-07-22T11:00:00
[2025-07-21 19:00:15 CT] 📅 EVENT_3: Lunch Break at 2025-07-22T12:00:00
[2025-07-21 19:00:15 CT] 📅 EVENT_4: Documentation Update at 2025-07-22T14:00:00
```

Your calendar will be automatically populated each evening with tomorrow's AI-generated, insight-driven time blocks!