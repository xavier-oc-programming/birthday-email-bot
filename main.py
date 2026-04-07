# main.py
from __future__ import annotations

import os
import random
import smtplib
import ssl
from datetime import date
from email.message import EmailMessage
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# ---------------------------- CONFIG ---------------------------- #

# Load environment variables from a local .env file (if present)
load_dotenv()

BASE_DIR = Path(__file__).parent
CSV_PATH = BASE_DIR / "birthdays.csv"
TEMPLATES_DIR = BASE_DIR / "letter_templates"  # contains letter_1.txt, letter_2.txt, ...

# Non-secret config can have safe defaults
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# Secrets must be provided via environment variables (no defaults)
# SENDER comes from .env / environment
SENDER_EMAIL = os.getenv("BIRTHDAY_SENDER_EMAIL")
SENDER_APP_PASSWORD = os.getenv("BIRTHDAY_APP_PASSWORD")

if not SENDER_EMAIL or not SENDER_APP_PASSWORD:
    raise ValueError("Missing sender email or app password. Set them in your .env file.")

# Preview mode: if True, print emails instead of sending
DRY_RUN = False

# ---------------------------- DATA LOADING ---------------------------- #

def load_birthdays(csv_path: Path) -> pd.DataFrame:
    """Read the CSV, coerce numeric columns, and drop invalid rows."""
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]

    required = {"name", "email", "year", "month", "day"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing expected columns: {missing}")

    # Convert to numbers; invalid entries become NaN
    df["month"] = pd.to_numeric(df["month"], errors="coerce")
    df["day"] = pd.to_numeric(df["day"], errors="coerce")

    # Identify rows missing any key fields
    bad = df[df[["name", "email", "month", "day"]].isna().any(axis=1)]
    if not bad.empty:
        print(f"Skipping {len(bad)} invalid row(s):")
        print(bad[["name", "email", "year", "month", "day"]])

    # Drop invalid rows and normalize types/whitespace
    df = df.dropna(subset=["name", "email", "month", "day"]).copy()
    df["name"] = df["name"].astype(str).str.strip()
    df["email"] = df["email"].astype(str).str.strip()
    df["month"] = df["month"].astype(int)
    df["day"] = df["day"].astype(int)
    return df


def today_birthdays(df: pd.DataFrame) -> pd.DataFrame:
    t = date.today()
    return df[(df["month"] == t.month) & (df["day"] == t.day)].copy()

# ---------------------------- TEMPLATING ---------------------------- #

def pick_template_text(name: str) -> str:
    templates = list(TEMPLATES_DIR.glob("letter_*.txt"))
    if not templates:
        raise FileNotFoundError(
            f"No templates found in {TEMPLATES_DIR}. Add files like 'letter_1.txt'."
        )
    chosen = random.choice(templates)
    text = chosen.read_text(encoding="utf-8")
    return text.replace("[NAME]", name)

# ---------------------------- EMAIL BUILD/SEND ---------------------------- #

def build_email(to_addr: str, subject: str, body: str) -> EmailMessage:
    """
    Build a plain-text email.

    SENDER (From): taken from SENDER_EMAIL (.env)
    RECEIVER (To): taken from CSV row (row['email'])
    """
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL        # sender from .env
    msg["To"] = to_addr               # receiver from CSV
    msg["Subject"] = subject
    msg.set_content(body)
    return msg


def send_email(msg: EmailMessage) -> None:
    """Send an EmailMessage via SMTP with TLS."""
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.send_message(msg)

# ---------------------------- MAIN ---------------------------- #

def main():
    df = load_birthdays(CSV_PATH)
    todays = today_birthdays(df)

    if todays.empty:
        print("No birthdays today. Nothing to send.")
        return

    print(f"Found {len(todays)} birthday(s) for today.")
    for _, row in todays.iterrows():
        # RECEIVER email is extracted from the CSV here:
        name = str(row["name"]).strip()
        receiver_email = str(row["email"]).strip()   # receiver from CSV
        subject = f"Happy Birthday, {name}!"
        body = pick_template_text(name)

        msg = build_email(receiver_email, subject, body)

        if DRY_RUN:
            print("\n--- DRY RUN ---")
            print("From:", SENDER_EMAIL)               # from .env
            print("To:", receiver_email)               # from CSV
            print("Subject:", subject)
            print(body)
            print("--- END ---")
        else:
            try:
                send_email(msg)
                print(f"Sent to {name} <{receiver_email}>")
            except Exception as e:
                print(f"Failed to send to {name} <{receiver_email}>: {e}")

    print("Done.")


if __name__ == "__main__":
    main()
