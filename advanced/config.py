from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
CSV_PATH = INPUT_DIR / "birthdays.csv"
TEMPLATES_DIR = INPUT_DIR / "letter_templates"

# Email / SMTP
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SUBJECT_TEMPLATE = "Happy Birthday, {name}!"

# Behavior
DRY_RUN = False
