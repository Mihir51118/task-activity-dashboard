from mailer import send_summary_email

if __name__ == "__main__":
    send_summary_email(
        ["jaychoubisa90@gmail.com","choubisamihir@gmail.com"],
        "Test Email",
        "<p>This is a test.</p>",
        "data/task_data.json"  # any small file path
    )
