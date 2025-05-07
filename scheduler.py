import os
import json
from apscheduler.schedulers.blocking import BlockingScheduler
from mailer import generate_email_report
from fetch_data import fetch_task_data

# ─── Helpers ────────────────────────────────────────────────────────────────

CONFIG_DIR = "config"
EMAIL_TIME_PATH = os.path.join(CONFIG_DIR, "email_time.json")
RECIPIENTS_PATH = os.path.join(CONFIG_DIR, "recipients.json")


def load_email_time():
    """Read hour/minute from config/email_time.json (defaults to 18:00)."""
    if os.path.exists(EMAIL_TIME_PATH):
        with open(EMAIL_TIME_PATH, "r") as f:
            data = json.load(f)
            return int(data.get("hour", 18)), int(data.get("minute", 0))
    return 18, 0


def load_recipients():
    """Read list of emails from config/recipients.json (empty if missing)."""
    if os.path.exists(RECIPIENTS_PATH):
        with open(RECIPIENTS_PATH, "r") as f:
            return json.load(f)
    return []


def save_recipients(recipients):
    """Persist the recipients list to config/recipients.json."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(RECIPIENTS_PATH, "w") as f:
        json.dump(recipients, f, indent=2)
    print(f"✅ Saved {len(recipients)} recipient(s) to {RECIPIENTS_PATH}")


def add_recipient(email):
    """Add a new email address to the recipients list (no duplicates)."""
    recips = load_recipients()
    if email in recips:
        print(f"⚠️  {email} is already in recipients.")
        return
    recips.append(email)
    save_recipients(recips)
    print(f"✅ Added {email} to recipients.")


def remove_recipient(email):
    """Remove an email address from the recipients list."""
    recips = load_recipients()
    if email not in recips:
        print(f"⚠️  {email} not found in recipients.")
        return
    recips.remove(email)
    save_recipients(recips)
    print(f"✅ Removed {email} from recipients.")


def send_daily_report():
    """Fetch fresh data, then generate & send the report to all recipients."""
    print("⏰ Fetching fresh task data...")
    fetch_task_data()

    recipients = load_recipients()
    if not recipients:
        print("⚠️ No recipients configured. Skipping email.")
        return

    print(f"⏰ Sending daily report to: {', '.join(recipients)}")
    generate_email_report(recipients)


# ─── Scheduler & CLI ────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Example CLI usage:
    #   python script.py add user@example.com
    #   python script.py remove user@example.com
    #   python script.py run

    import sys
    if len(sys.argv) >= 3 and sys.argv[1] == "add":
        add_recipient(sys.argv[2])
        sys.exit(0)
    if len(sys.argv) >= 3 and sys.argv[1] == "remove":
        remove_recipient(sys.argv[2])
        sys.exit(0)

    # Otherwise, start the scheduler to run daily
    hour, minute = load_email_time()
    scheduler = BlockingScheduler()
    scheduler.add_job(
        send_daily_report,
        trigger="cron",
        hour=hour,
        minute=minute,
        id="daily_email",
        replace_existing=True,
    )

    print(f"✅ Scheduler started — will send email daily at {hour:02d}:{minute:02d}")
    scheduler.start()
