# Clean Up Your Crontab

Looking at your current cron setup, there are formatting issues that need fixing:

## 🐛 Current Issues

1. **Line breaks**: The Journal AI Pipeline entry is split across multiple lines
2. **Numbers**: Leading numbers (1, 2, 3, 4) should be removed
3. **Extra spaces**: Some entries have extra whitespace

## ✅ Clean Crontab Format

Here's what your crontab should look like (clean, no line numbers):

```bash
# Journal AI Pipeline - Evening Planning (7 PM Daily)
0 19 * * * /Users/joshuafreeman/Desktop/agent_projects/agents/planning_agent/cron_daily_run.sh >> /Users/joshuafreeman/Desktop/agent_projects/agents/planning_agent/logs/cron.log 2>&1

# Federal Register Monitor (Every 30 minutes)
*/30 * * * * /Users/joshuafreeman/Desktop/incubator/prototypes/federal_register/venv/bin/python /Users/joshuafreeman/Desktop/incubator/prototypes/federal_register/main.py >> /Users/joshuafreeman/Desktop/incubator/prototypes/federal_register/cron.log 2>&1

# Practice Regulations Alert (Every 3 hours)
0 */3 * * * /Users/joshuafreeman/Desktop/practice_regulations/venv/bin/python /Users/joshuafreeman/Desktop/practice_regulations/reg_alert.py >> /Users/joshuafreeman/Desktop/practice_regulations/cron.log 2>&1

# AI Scraper (Monthly - 3rd day, 4th month?)
* * 3 4 * /Users/joshuafreeman/Desktop/incubator/ai-scraper-skeleton/run_all.sh >> /Users/joshuafreeman/Desktop/incubator/ai-scraper-skeleton/logs/cron.log 2>&1

# Hacker News Crawler (Every minute - very frequent!)
* * * * * /Users/joshuafreeman/Desktop/webbots/hacker_news_crawler/run_crawler.sh >> /Users/joshuafreeman/Desktop/webbots/hacker_news_crawler/logs/hn.log 2>&1

# News Bot (Daily at 1 PM)
0 13 * * * /Users/joshuafreeman/Desktop/webbots/async_news_bot_v3/run_bot.sh >> /Users/joshuafreeman/Desktop/webbots/async_news_bot_v3/bot.log 2>&1
```

## 🔧 How to Fix

1. **Clear and rebuild**:
   ```bash
   # Save current crontab as backup
   crontab -l > ~/crontab_backup.txt
   
   # Clear current crontab
   crontab -r
   
   # Edit fresh crontab
   crontab -e
   ```

2. **Copy the clean format above** (without the code block markers)

3. **Verify it worked**:
   ```bash
   crontab -l
   ```

## 📊 Your Automation Schedule

Once fixed, your automation will run:

- **Every minute**: Hacker News Crawler
- **Every 30 min**: Federal Register Monitor  
- **Every 3 hours**: Practice Regulations
- **Daily 1 PM**: News Bot
- **Daily 7 PM**: Journal AI Pipeline ← Your new addition!
- **Monthly**: AI Scraper (April 3rd?)

## ⚠️ Quick Note

Your Hacker News Crawler runs **every minute** - that's very frequent! Make sure that's intentional and not overloading the server.

After cleaning up the format, all your automation projects will run smoothly! 🤖