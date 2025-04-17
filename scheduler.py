from apscheduler.schedulers.blocking import BlockingScheduler
from mailer import generate_email_report
import json
import os

# Load scheduled time from config/email_time.json
def load_email_time():
    config_path = "config/email_time.json"
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                data = json.load(f)
                hour = int(data.get("hour", 18))
                minute = int(data.get("minute", 0))
                return hour, minute
    except Exception as e:
        print(f"⚠️ Error loading email time config: {e}")

    # Fallback default time
    return 18, 0

# Initialize scheduler
scheduler = BlockingScheduler()
hour, minute = load_email_time()

@scheduler.scheduled_job('cron', hour=hour, minute=minute)
def daily_task_summary():
    print(f"⏰ Sending daily email at {hour:02d}:{minute:02d} ...")
    generate_email_report()

print(f"✅ Scheduler started — Daily email scheduled at {hour:02d}:{minute:02d}")
scheduler.start()
