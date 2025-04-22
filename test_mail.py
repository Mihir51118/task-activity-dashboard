from mailer import send_summary_email
from datetime import datetime

if __name__ == "__main__":
    today_str = datetime.now().strftime("%Y-%m-%d")
    subject = f"📅 Task Activity Report — {today_str} (Test Email)"
    html_body = f"""
    <html>
    <body>
        <p>Dear Team,</p>
        <p>This is a <b>test email</b> from the Task Activity Dashboard system, sent on <b>{today_str}</b>.</p>
        <p>Please find the attached sample data file for your reference.</p>
        <p>If you have any questions or did not expect this email, please contact the administrator.</p>
        <br>
        <p>Best regards,<br>
        Task Activity Dashboard Bot</p>
    </body>
    </html>
    """
    send_summary_email(
        ["jaychoubisa90@gmail.com", "choubisamihir@gmail.com"],
        subject,
        html_body,
        "data/task_data.json"
    )
