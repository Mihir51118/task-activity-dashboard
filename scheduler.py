from apscheduler.schedulers.blocking import BlockingScheduler
from mailer import generate_email_report
from fetch_data import fetch_task_data
import json
import os

# ─── Helpers ────────────────────────────────────────────────────────────────

def load_email_time():
    """Read hour/minute from config/email_time.json (defaults to 18:00)."""
    config_path = "config/email_time.json"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            data = json.load(f)
            return int(data.get("hour", 18)), int(data.get("minute", 0))
    return 18, 0

def load_recipients():
    """Read list of emails from config/recipients.json (empty if missing)."""
    rec_path = "config/recipients.json"
    if os.path.exists(rec_path):
        with open(rec_path, "r") as f:
            return json.load(f)
    return []

def send_daily_report():
    """Fetch new data, then generate & send the report to all recipients."""
    # 1️⃣ Fetch fresh data into data/task_data.json
    print("⏰ Fetching fresh task data...")
    fetch_task_data()

    # 2️⃣ Load recipients
    recipients = load_recipients()
    if not recipients:
        print("⚠️ No recipients configured. Skipping email.")
        return

    # 3️⃣ Generate & send
    print(f"⏰ Sending daily report to: {', '.join(recipients)}")
    generate_email_report(recipients)

# ─── Scheduler Setup ────────────────────────────────────────────────────────

if __name__ == "__main__":
    hour, minute = load_email_time()
    scheduler = BlockingScheduler()
    scheduler.add_job(send_daily_report, "cron", hour=hour, minute=minute, id="daily_email", replace_existing=True)

    print(f"✅ Scheduler started — will send email daily at {hour:02d}:{minute:02d}")
    scheduler.start()