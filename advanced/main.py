import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import os

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from birthday_loader import BirthdayLoader
from config import CSV_PATH, DRY_RUN, SMTP_HOST, SMTP_PORT, SUBJECT_TEMPLATE, TEMPLATES_DIR
from email_sender import EmailSender


def main() -> None:
    sender_email = os.getenv("BIRTHDAY_SENDER_EMAIL")
    app_password = os.getenv("BIRTHDAY_APP_PASSWORD")

    if not sender_email or not app_password:
        print("Error: BIRTHDAY_SENDER_EMAIL and BIRTHDAY_APP_PASSWORD must be set in .env")
        sys.exit(1)

    loader = BirthdayLoader(CSV_PATH)
    sender = EmailSender(
        sender_email=sender_email,
        app_password=app_password,
        templates_dir=TEMPLATES_DIR,
        smtp_host=SMTP_HOST,
        smtp_port=SMTP_PORT,
        dry_run=DRY_RUN,
    )

    df = loader.load()
    todays = loader.today_birthdays(df)

    if todays.empty:
        print("No birthdays today. Nothing to send.")
        return

    print(f"Found {len(todays)} birthday(s) for today.")

    for _, row in todays.iterrows():
        name = row["name"]
        to_addr = row["email"]
        subject = SUBJECT_TEMPLATE.format(name=name)
        body = sender.pick_template(name)
        msg = sender.build_message(to_addr, subject, body)

        try:
            sender.send(msg)
            print(f"Sent to {name} <{to_addr}>")
        except Exception as exc:
            print(f"Failed to send to {name} <{to_addr}>: {exc}")

    print("Done.")


if __name__ == "__main__":
    main()
