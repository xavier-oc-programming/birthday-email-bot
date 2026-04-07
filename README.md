# Birthday Email Bot

Checks a CSV for today's birthdays and sends personalised emails via Gmail SMTP.

---

## Table of Contents

1. [Quick start](#1-quick-start)
2. [Builds comparison](#2-builds-comparison)
3. [Usage](#3-usage)
4. [GitHub Actions automation](#4-github-actions-automation)
5. [Data flow](#5-data-flow)
6. [Features](#6-features)
7. [Navigation flow](#7-navigation-flow)
8. [Architecture](#8-architecture)
9. [Module reference](#9-module-reference)
10. [Configuration reference](#10-configuration-reference)
11. [Data schema](#11-data-schema)
12. [Environment variables](#12-environment-variables)
13. [Design decisions](#13-design-decisions)
14. [Course context](#14-course-context)
15. [Dependencies](#15-dependencies)

---

## 1. Quick start

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your Gmail address and app password
python menu.py         # select 1 (original) or 2 (advanced), or run directly:
python original/main.py
python advanced/main.py
```

> **Gmail app password**: Go to Google Account → Security → 2-Step Verification → App passwords. Generate one for "Mail".

---

## 2. Builds comparison

| Feature | Original | Advanced |
|---|---|---|
| Read birthdays CSV | Yes | Yes |
| Filter to today's date | Yes | Yes |
| Random letter template | Yes | Yes |
| Send via Gmail SMTP | Yes | Yes |
| Dry-run / preview mode | Yes (`DRY_RUN` flag) | Yes (`DRY_RUN` in config.py) |
| OOP structure | No (functions) | Yes (`BirthdayLoader`, `EmailSender`) |
| Centralised config | No (constants scattered) | Yes (`config.py`) |
| Credentials via `.env` | Yes | Yes |
| Input files in `input/` | No | Yes |
| Separated data-loading logic | No | Yes (`BirthdayLoader`) |
| Separated sending logic | No | Yes (`EmailSender`) |
| GitHub Actions daily schedule | No | Yes (`.github/workflows/birthday_email.yml`) |

---

## 3. Usage

### Original build

```bash
python original/main.py
```

Set `DRY_RUN = True` at line 37 of `original/main.py` to preview emails without sending.

### Advanced build

```bash
python advanced/main.py
```

Set `DRY_RUN = True` in `advanced/config.py` to preview without sending.

### Example terminal output

```
Found 1 birthday(s) for today.
Sent to Adam <testingpythonxavier@yahoo.com>
Done.
```

Dry-run output:

```
Found 1 birthday(s) for today.

--- DRY RUN ---
From: youraddress@gmail.com
To: testingpythonxavier@yahoo.com
Subject: Happy Birthday, Adam!
Dear Adam,

Happy birthday! Have a wonderful time today and eat lots of cake!
...
--- END ---
Done.
```

---

## 4. GitHub Actions automation

The workflow at [.github/workflows/birthday_email.yml](.github/workflows/birthday_email.yml) runs the advanced build automatically every day at **08:00 UTC**. You can also trigger it manually from the **Actions** tab in GitHub.

### Setup

1. Push this repo to GitHub.
2. Go to **Settings → Secrets and variables → Actions** and add two repository secrets:

   | Secret name | Value |
   |---|---|
   | `BIRTHDAY_SENDER_EMAIL` | Your Gmail address |
   | `BIRTHDAY_APP_PASSWORD` | Your 16-character Gmail App Password |

3. Enable the workflow under the **Actions** tab if it is not already active.

That's it — GitHub runs `python advanced/main.py` daily. No local machine needs to be running.

### Changing the schedule

Edit the `cron` line in the workflow file. The format is standard cron (`minute hour day month weekday`):

```yaml
- cron: "0 8 * * *"   # 08:00 UTC daily
```

Use [crontab.guru](https://crontab.guru) to build a custom schedule.

### Manual trigger

Open the **Actions** tab → **Birthday Email** → **Run workflow** to fire it immediately without waiting for the schedule.

---

## 5. Data flow

**Input:** `birthdays.csv` — rows with `name`, `email`, `year`, `month`, `day`

**Load:** pandas reads CSV → strips whitespace → coerces numeric types → drops malformed rows → returns clean DataFrame

**Filter:** compare `month` + `day` columns against `datetime.date.today()` → subset DataFrame of today's people

**Template:** `glob("letter_*.txt")` → `random.choice()` → read file → `.replace("[NAME]", name)` → rendered body string

**Send:** `EmailMessage` built with From/To/Subject/body → `smtplib.SMTP` opens STARTTLS session → `server.login()` → `server.send_message(msg)`

---

## 6. Features

### Both builds

**Birthday detection.** Reads `birthdays.csv` and checks whether any person's `month` and `day` match today. Year is stored but not used for filtering — the bot fires every year.

**Random personalised templates.** Picks one of any number of `letter_*.txt` files at random and replaces the `[NAME]` placeholder with the recipient's name.

**Gmail SMTP sending.** Connects to `smtp.gmail.com:587`, upgrades to TLS via STARTTLS, authenticates with a Gmail app password, and sends a plain-text `EmailMessage`.

**Dry-run mode.** When `DRY_RUN = True`, the email is printed to the terminal instead of sent — safe for testing.

**Malformed-row handling.** Rows missing `name`, `email`, `month`, or `day` are reported and skipped rather than crashing the run.

### Advanced build only

**OOP separation.** `BirthdayLoader` owns all CSV logic; `EmailSender` owns all email logic. `main.py` wires them together but contains no data-loading or SMTP details.

**Centralised config.** Every constant (paths, SMTP host/port, subject template, dry-run flag) lives in `config.py`. Nothing is hardcoded in module files.

**Structured input directory.** CSV and templates live under `advanced/input/` so the advanced build is fully self-contained and does not share mutable files with the original build.

---

## 7. Navigation flow

### a) Terminal menu tree

```
menu.py
├── 1 → original/main.py   (subprocess.run, cwd=original/)
├── 2 → advanced/main.py   (subprocess.run, cwd=advanced/)
└── q → exit
     (any other input) → "Invalid choice. Try again." → re-display menu
```

### b) Execution flow

```
Start
  │
  ▼
Load .env → read BIRTHDAY_SENDER_EMAIL + BIRTHDAY_APP_PASSWORD
  │
  ├── Missing credentials → print error → exit(1)
  │
  ▼
BirthdayLoader.load()
  │
  ├── CSV not found → raise FileNotFoundError
  ├── Missing columns → raise ValueError
  └── Malformed rows → print warning, skip row
  │
  ▼
BirthdayLoader.today_birthdays(df)
  │
  ├── No matches → print "No birthdays today." → exit cleanly
  │
  ▼
For each birthday person:
  │
  ▼
EmailSender.pick_template(name)
  │
  ├── No templates found → raise FileNotFoundError
  │
  ▼
EmailSender.build_message(to_addr, subject, body)
  │
  ▼
EmailSender.send(msg)
  │
  ├── DRY_RUN=True → print email to terminal
  ├── SMTP success → print "Sent to {name}"
  └── SMTP error → print "Failed to send to {name}: {error}" → continue loop
  │
  ▼
Print "Done." → exit cleanly
```

---

## 8. Architecture

```
birthday-email-bot/
├── .github/
│   └── workflows/
│       └── birthday_email.yml  # daily cron + manual-trigger workflow
├── menu.py                     # interactive launcher, while True menu
├── art.py                      # LOGO ASCII art
├── requirements.txt            # pip dependencies + Python version note
├── .env.example                # credential placeholders (committed)
├── .env                        # real credentials (gitignored)
├── .gitignore
├── README.md
│
├── docs/
│   └── COURSE_NOTES.md         # original exercise description
│
├── original/                   # verbatim course files
│   ├── main.py                 # single-file script (functions only)
│   ├── birthdays.csv           # input data
│   └── letter_templates/
│       ├── letter_1.txt
│       ├── letter_2.txt
│       └── letter_3.txt
│
└── advanced/                   # OOP refactor
    ├── config.py               # all constants in one place
    ├── birthday_loader.py      # BirthdayLoader — CSV read + date filter
    ├── email_sender.py         # EmailSender — template + SMTP send
    ├── main.py                 # orchestrator: wires loader + sender
    └── input/                  # curated project files (committed)
        ├── birthdays.csv
        └── letter_templates/
            ├── letter_1.txt
            ├── letter_2.txt
            └── letter_3.txt
```

---

## 9. Module reference

### `BirthdayLoader` (`advanced/birthday_loader.py`)

| Method | Returns | Description |
|---|---|---|
| `__init__(csv_path)` | — | Stores path to the CSV file |
| `load()` | `pd.DataFrame` | Reads CSV, validates columns, coerces types, drops malformed rows |
| `today_birthdays(df)` | `pd.DataFrame` | Filters df to rows matching today's month and day |

### `EmailSender` (`advanced/email_sender.py`)

| Method | Returns | Description |
|---|---|---|
| `__init__(sender_email, app_password, templates_dir, smtp_host, smtp_port, dry_run)` | — | Stores all connection and behaviour config |
| `pick_template(name)` | `str` | Chooses a random letter_*.txt, replaces [NAME], returns body |
| `build_message(to_addr, subject, body)` | `EmailMessage` | Constructs a plain-text EmailMessage with From/To/Subject |
| `send(msg)` | `None` | Sends via SMTP STARTTLS, or prints in dry_run mode |

---

## 10. Configuration reference

(`advanced/config.py`)

| Constant | Default | Description |
|---|---|---|
| `BASE_DIR` | `Path(__file__).parent` | Root of the `advanced/` directory |
| `INPUT_DIR` | `BASE_DIR / "input"` | Directory containing CSV and templates |
| `CSV_PATH` | `INPUT_DIR / "birthdays.csv"` | Path to the birthday CSV |
| `TEMPLATES_DIR` | `INPUT_DIR / "letter_templates"` | Directory containing letter_*.txt files |
| `SMTP_HOST` | `"smtp.gmail.com"` | SMTP server hostname |
| `SMTP_PORT` | `587` | SMTP port (STARTTLS) |
| `SUBJECT_TEMPLATE` | `"Happy Birthday, {name}!"` | Email subject, formatted with recipient name |
| `DRY_RUN` | `False` | If True, print emails instead of sending |

---

## 11. Data schema

### `birthdays.csv`

```
name,email,year,month,day
Adam,adam@example.com,1990,4,7
Sara,sara@example.com,1985,12,25
```

| Column | Type | Required | Notes |
|---|---|---|---|
| name | string | Yes | Recipient's name; replaces [NAME] in template |
| email | string | Yes | Recipient email address |
| year | integer | No | Birth year; stored but not used for filtering |
| month | integer | Yes | 1–12 |
| day | integer | Yes | 1–31 |

### `letter_templates/letter_N.txt`

Plain text file. Use `[NAME]` as a placeholder — it is replaced at runtime.

```
Dear [NAME],

Happy birthday! Have a wonderful day.

With love,
Xavier
```

### Email message (runtime, not persisted)

```
From: youraddress@gmail.com
To: adam@example.com
Subject: Happy Birthday, Adam!

Dear Adam,

Happy birthday! Have a wonderful day.
...
```

---

## 12. Environment variables

Copy `.env.example` to `.env` and fill in values.

| Variable | Required | Description |
|---|---|---|
| `BIRTHDAY_SENDER_EMAIL` | Yes | Gmail address that sends the emails |
| `BIRTHDAY_APP_PASSWORD` | Yes | Gmail App Password (16 chars, no spaces) |
| `SMTP_HOST` | No | SMTP host (default: `smtp.gmail.com`) |
| `SMTP_PORT` | No | SMTP port (default: `587`) |

---

## 13. Design decisions

**`config.py` — zero magic numbers.** Every constant is defined once. Changing the SMTP host or subject format means editing one line, not hunting through multiple files.

**Separate `BirthdayLoader` and `EmailSender` modules.** Each class is independently testable. You can test CSV loading with a mock file without needing SMTP credentials, and you can test email building without touching any CSV.

**Credentials via `.env`, never hardcoded.** Secrets stored in source code get leaked in version control. `.env` keeps them out of git entirely.

**`.env.example` committed, `.env` gitignored.** Documents exactly which variables are required without ever exposing real values. Onboarding is one `cp` command.

**`Path(__file__).parent` for all file paths.** The script works correctly regardless of what directory it is invoked from — including when launched via `menu.py`'s `subprocess.run`.

**Pure-logic modules raise exceptions instead of `sys.exit()`.** `BirthdayLoader` and `EmailSender` raise standard exceptions so `main.py` can decide how to handle errors (log and continue vs. abort). A module that calls `sys.exit()` is untestable and inflexible.

**`sys.path.insert` pattern in `advanced/main.py`.** Makes sibling imports (`from birthday_loader import ...`) work both when run directly and when launched via `subprocess.run` from `menu.py`.

**`subprocess.run` + `cwd=` in `menu.py`.** Setting the working directory to the script's parent means relative imports and `Path(__file__).parent` resolve correctly inside each build.

**`while True` in `menu.py` instead of recursion.** Recursion grows the call stack indefinitely. `while True` loops forever with constant stack depth.

**Console cleared before every menu render.** Prevents the menu from cluttering the terminal with previous output, giving a clean UX on every iteration.

**`advanced/input/` committed, no output directory.** Curated input files (CSV, templates) belong in version control — they are the configuration of the program. This bot produces no output files; emails are sent, not written to disk.

**Per-recipient try/except.** A failed send to one person does not abort the remaining recipients. The loop continues and reports each failure individually.

**GitHub Actions for scheduling, not cron.** Using `schedule: cron` in a workflow means no server or local machine needs to stay running. Secrets are stored as encrypted repository secrets and injected as environment variables at runtime — the `.env` file is never needed in CI.

---

## 14. Course context

Built as Day 32 of 100 Days of Code by Dr. Angela Yu.

**Concepts covered in the original build:**
- `datetime.date.today()` for date-based logic
- `pandas` for reading and filtering CSV data
- `random.choice()` for randomisation
- `pathlib.Path` for cross-platform file handling
- `smtplib` + `ssl` for sending email over TLS
- `email.message.EmailMessage` for constructing well-formed emails
- `python-dotenv` + `os.getenv()` for secret management
- Defensive validation: missing columns, malformed rows

**The advanced build extends into:**
- Object-oriented design: separating data loading from email sending
- Single-responsibility principle: each class does one thing
- Centralised configuration via `config.py`
- Clean exception propagation instead of `sys.exit()` in modules
- GitHub Actions: automated daily scheduling via `schedule: cron`, secrets injected as environment variables

See [docs/COURSE_NOTES.md](docs/COURSE_NOTES.md) for the full concept breakdown.

---

## 15. Dependencies

| Module | Used in | Purpose |
|---|---|---|
| `pandas` | both builds | Read and filter CSV data |
| `python-dotenv` | both builds | Load `.env` file into environment |
| `smtplib` | both builds | SMTP connection and sending (stdlib) |
| `ssl` | both builds | TLS context for SMTP (stdlib) |
| `email.message` | both builds | Build structured EmailMessage objects (stdlib) |
| `random` | both builds | Pick a random letter template (stdlib) |
| `pathlib` | both builds | Cross-platform file paths (stdlib) |
| `datetime` | both builds | Get today's date for birthday matching (stdlib) |
| `os` | both builds | Read env vars, detect OS for clear command (stdlib) |
| `subprocess` | `menu.py` | Launch builds as subprocesses (stdlib) |
| `sys` | `menu.py`, advanced | Path manipulation, exit (stdlib) |
