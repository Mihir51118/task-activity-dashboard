import json
import csv
import smtplib
import os
from email.message import EmailMessage
from datetime import datetime

# 📧 Send summary email to multiple recipients
def send_summary_email(to_emails, subject, html_body, csv_path):
    EMAIL_ADDRESS = "choubisamihir@gmail.com"
    EMAIL_PASSWORD = "yjwy ejle ugvf nxgj"  # App‑specific Gmail password

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = ", ".join(to_emails)  # Multiple recipients

    # Fallback text version
    msg.set_content("Your task report is attached. Please open the email in an HTML‑supported email client.")

    # Add HTML body
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
    except FileNotFoundError:
        print(f"❌ CSV file not found: {csv_path}")
        return

    # Send the email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Email sent to: {', '.join(to_emails)}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# 📝 Generate and send daily task report
def generate_email_report(recipients):
    try:
        today_str = datetime.now().strftime("%Y-%m-%d")
        json_path = "data/task_data.json"
        csv_path = f"task_{today_str}.csv"

        # Load task data
        with open(json_path, "r") as f:
            task_data = json.load(f)

        if not task_data:
            print("⚠️ No task data found.")
            return

        # Write CSV
        with open(csv_path, "w", newline="") as csvfile:
            headers = task_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for row in task_data:
                writer.writerow(row)

        print(f"✅ CSV generated: {csv_path}")

        # Generate summary stats
        total_tasks = len(task_data)
        completed_tasks = sum(1 for task in task_data if task.get("activity_status") == "Completed")
        total_minutes = sum(int(task.get("time_spent_minutes", 0)) for task in task_data)
        total_hours = round(total_minutes / 60, 2)

        # HTML Email Body
        html_body = f"""\
<html>
  <body style="font-family:Arial,sans-serif; color:#333;">
    <h2 style="color:#2E86C1;">📅 Daily Task Report — {today_str}</h2>
    <p>Here is your task summary:</p>
    <table style="border-collapse:collapse; width:100%; max-width:600px;">
      <tr>
        <th style="background:#f2f2f2; padding:8px; border:1px solid #ddd;">Metric</th>
        <th style="background:#f2f2f2; padding:8px; border:1px solid #ddd;">Value</th>
      </tr>
      <tr>
        <td style="padding:8px; border:1px solid #ddd;">Total Tasks</td>
        <td style="padding:8px; border:1px solid #ddd;">{total_tasks}</td>
      </tr>
      <tr>
        <td style="padding:8px; border:1px solid #ddd;">Completed Tasks</td>
        <td style="padding:8px; border:1px solid #ddd;">{completed_tasks}</td>
      </tr>
      <tr>
        <td style="padding:8px; border:1px solid #ddd;">Total Time Spent</td>
        <td style="padding:8px; border:1px solid #ddd;">{total_hours} hours</td>
      </tr>
    </table>
    <p style="margin-top:20px;">📎 Attached: <strong>{os.path.basename(csv_path)}</strong></p>
    <p style="color:#555; font-size:0.9em;">Regards,<br/>TaskBot</p>
  </body>
</html>
"""

        subject = f"📊 Daily Task Report - {today_str}"

        # Send email to all recipients
        send_summary_email(
            to_emails=recipients,
            subject=subject,
            html_body=html_body,
            csv_path=csv_path
        )

    except Exception as e:
        print(f"❌ Error generating report: {e}")

# 🧪 Run with your specified email addresses
if __name__ == "__main__":
    recipients = [
        "jaychoubisa90@gmail.com",
        "choubisamihir@gmail.com",
        "thanushthan124@gmail.com"
    ]
    generate_email_report(recipients)
