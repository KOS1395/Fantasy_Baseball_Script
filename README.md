# ⚾ MLB Baseball Savant — Trending Players Email App

Automatically scrapes the **Trending Players** section from [Baseball Savant](https://baseballsavant.mlb.com/) and emails you a styled digest every **Wednesday and Sunday at 7:00 PM**.

---

## 📋 Requirements

- Python 3.11+
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) enabled

---

## 🚀 Setup

### 1 — Install dependencies

```bash
cd mlb-trending-emailer
pip install -r requirements.txt
playwright install chromium
```

> `playwright install chromium` downloads the headless browser (~120 MB, one-time).

---

### 2 — Configure your credentials

```bash
copy .env.example .env
```

Open `.env` and fill in:

```env
SMTP_USER=you@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx   # Gmail App Password (16 chars)
EMAIL_TO=you@gmail.com              # recipient (can be same address)
```

> **How to get a Gmail App Password:**  
> Google Account → Security → 2-Step Verification → App Passwords → create one for "Mail".

---

## ▶️ Usage

### Send an email right now

```bash
python main.py
```

### Preview the email without sending (no credentials needed)

```bash
python main.py --dry-run
```
This prints the full HTML to your terminal so you can inspect it.

### Start the automatic scheduler (Wed & Sun at 7 PM)

```bash
python main.py --schedule
```

Keep this running in the background (or set it up as a Windows Scheduled Task / startup script).

---

## 📁 Project Files

| File | Purpose |
|---|---|
| `main.py` | Entry point — CLI with `--dry-run` and `--schedule` flags |
| `scraper.py` | Playwright scraper for Baseball Savant trending players |
| `emailer.py` | HTML email builder + SMTP sender |
| `scheduler.py` | APScheduler cron trigger (Wed & Sun 7 PM) |
| `config.py` | Loads settings from `.env` |
| `.env` | Your private credentials (do **not** commit this) |
| `.env.example` | Template for `.env` |

---

## 🔧 Customization

| Setting | `.env` key | Default |
|---|---|---|
| Schedule days | `SCHEDULE_DAYS` | `wed,sun` |
| Schedule time | `SCHEDULE_HOUR` / `SCHEDULE_MINUTE` | `19` / `0` |
| SMTP provider | `SMTP_HOST` / `SMTP_PORT` | Gmail / 587 |
| Multiple recipients | `EMAIL_TO` | comma-separated |

---

## ⚠️ Notes

- **Off-season**: Baseball Savant may show no trending players during the off-season. The app handles this gracefully and logs a warning.
- **Rate limiting**: The scraper adds a 3-second wait after page load to let all JavaScript render before parsing.
- **Headless browser**: Playwright runs without opening a visible window.
