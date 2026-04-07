# Day 32 — Birthday Email Bot: Course Exercise Description

## Original exercise

Build an automated birthday-email sender. The program:

1. Reads a `birthdays.csv` file containing columns: `name`, `email`, `year`, `month`, `day`.
2. Compares each row's `month` and `day` against today's date (using Python's `datetime` module).
3. If today is someone's birthday, selects one of several `letter_templates/letter_X.txt` files at random.
4. Replaces the `[NAME]` placeholder in the template with the person's name.
5. Sends the personalised email via SMTP (Gmail) using Python's `smtplib` and `ssl` modules.

## Concepts covered

- `datetime.date.today()` — get today's date
- `pandas` — reading and filtering CSV data
- `random.choice()` — picking a random item from a list
- `pathlib.Path` — cross-platform file paths
- `smtplib.SMTP` + `ssl.create_default_context()` — sending email over TLS
- `email.message.EmailMessage` — building a properly-structured email object
- `python-dotenv` / `os.getenv()` — loading secrets from a `.env` file
- Defensive validation: checking for missing CSV columns, skipping malformed rows
- Dry-run flag — preview without actually sending

## Course source

100 Days of Code: The Complete Python Pro Bootcamp by Dr. Angela Yu (Udemy).
Day 32 project.
