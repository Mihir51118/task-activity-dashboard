from mailer import send_summary_email

if __name__ == "__main__":
    send_summary_email(
        to_emails=["jaychoubisa90@gmail.com", "choubisamihir@gmail.com"],
        subject="Test Email",
        plain_body="This is a test.",  # plain text version
        html_body="<p>This is a test.</p>",  # HTML version
        csv_path="data/task_data.json"  # any small file path
    )
