"""
config.py — Load and validate environment variables from .env
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _get_or_empty(key: str) -> str:
    return os.getenv(key, "")


# SMTP / Gmail
SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = _get_or_empty("SMTP_USER")
SMTP_PASSWORD: str = _get_or_empty("SMTP_PASSWORD")

# Email addresses
EMAIL_FROM: str = os.getenv("EMAIL_FROM", SMTP_USER)
EMAIL_TO: list[str] = [
    addr.strip()
    for addr in _get_or_empty("EMAIL_TO").split(",")
    if addr.strip()
]

# Scheduler — default: Wednesday & Sunday at 19:00
SCHEDULE_DAYS: str = os.getenv("SCHEDULE_DAYS", "wed,sun")
SCHEDULE_HOUR: int = int(os.getenv("SCHEDULE_HOUR", "19"))
SCHEDULE_MINUTE: int = int(os.getenv("SCHEDULE_MINUTE", "0"))

# Baseball Savant
SAVANT_URL: str = "https://baseballsavant.mlb.com/"

# ESPN Fantasy Baseball
ESPN_LEAGUE_ID: str = _get_or_empty("ESPN_LEAGUE_ID")
ESPN_YEAR: int = int(os.getenv("ESPN_YEAR", "2026"))
ESPN_S2: str = _get_or_empty("ESPN_S2")
SWID: str = _get_or_empty("SWID")
