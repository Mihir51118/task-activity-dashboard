import json
import csv
import smtplib
import os
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv

# look for a .env file in the current directory (or parent directories)
load_dotenv()  

EMAIL_ADDRESS  = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_summary_email(to_emails, subject, plain_body, html_body, csv_path):
    msg = EmailMessage()
    msg["Subject"]  = subject
    msg["From"]     = f"TaskBot Reports <{EMAIL_ADDRESS}>"
    msg["To"]       = ", ".join(to_emails)
    msg["Reply-To"] = EMAIL_ADDRESS

    # Plain text fallback
    msg.set_content(plain_body)

    # HTML version
    msg.add_alternative(html_body, subtype="html")

    # Attach CSV
    try:
        with open(csv_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(csv_path)
            msg.add_attachment(
                file_data,
                maintype="application",
                subtype="octet-stream",
                filename=file_name
            )
            print(f"📎 Attached CSV: {file_name} — Size: {len(file_data)} bytes")
    except FileNotFoundError:
        print(f"❌ CSV not found: {csv_path}")
        return

    # Send email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Email sent to: {', '.join(to_emails)}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def generate_email_report(recipients):
    try:
        today_str = datetime.now().strftime("%Y-%m-%d")
        json_path = "data/task_data.json"
        csv_path  = f"task_{today_str}.csv"

        # Load JSON
        with open(json_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        rows = payload.get("data", payload)

        if not rows:
            print("⚠️ No task data found.")
            return

        # Write CSV
        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            headers = sorted({k for row in rows for k in row.keys()})
            writer  = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

        print(f"✅ CSV generated: {csv_path}")

        # Summary stats
        total_tasks     = len(rows)
        completed_tasks = sum(1 for t in rows if t.get("activity_status","").lower()=="completed")
        total_minutes   = sum(
            int(t.get("time_spent","0").split(":")[0])
            for t in rows if t.get("time_spent","")
        )
        total_hours     = round(total_minutes / 60, 2)

        # Email subject/body
        subject    = f"[Test] Daily Task Report — {today_str}"
        plain_body = f"""\
Daily Task Report — {today_str}

Total Tasks:     {total_tasks}
Completed Tasks: {completed_tasks}
Total Time Spent: {total_hours} hours

See attached CSV for full details.
"""

        html_body = f"""\
<html>
  <body style="font-family:Arial,sans-serif; color:#333;">
    <h2>Daily Task Report — {today_str}</h2>
    <p>Hello Team,</p>
    <ul>
      <li><b>Total Tasks:</b> {total_tasks}</li>
      <li><b>Completed Tasks:</b> {completed_tasks}</li>
      <li><b>Total Time Spent:</b> {total_hours} hours</li>
    </ul>
    <p>Please refer to the attached CSV for full task details.</p>
    <p style="color:#777;">If this lands in spam, mark it “Not Spam” to improve delivery.</p>
    <p style="font-size:0.9em; color:#888;">Regards,<br/>TaskBot</p>
  </body>
</html>
"""

        # Send email
        send_summary_email(
            to_emails  = recipients,
            subject    = subject,
            plain_body = plain_body,
            html_body  = html_body,
            csv_path   = csv_path  # Ensure csv_path is passed here
        )

    except Exception as e:
        print(f"❌ Error generating report: {e}")

# ✅ Run this script directly to test
if __name__ == "__main__":
    recipients = [
        "jaychoubisa90@gmail.com"  # ✅ Best to avoid sending to your own Gmail sender here
    ]
    generate_email_report(recipients)