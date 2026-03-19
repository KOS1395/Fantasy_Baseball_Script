# ⚾ MLB Baseball Savant — Trending Players Email App

Automatically scrapes the **Trending Players** section from [Baseball Savant](https://baseballsavant.mlb.com/) and emails you a styled digest every **Wednesday and Sunday at 12:00 PM**.

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
```

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

### 3 — Optional: Configure ESPN Fantasy Baseball Waivers

To filter the email so it *only* shows trending players that are **available on your waiver wire**, add these lines to `.env`:

```env
ESPN_LEAGUE_ID=12345678
ESPN_YEAR=2026
SWID={your-swid-cookie}
ESPN_S2=your-espn-s2-cookie...
```

*Note: `SWID` and `ESPN_S2` are only required if your league is private. You can find these by opening your ESPN Fantasy league in a browser, inspecting the page (F12), and looking under `Application` -> `Cookies`.*

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
| `scraper.py` | Fetches and processes trending players directly from the Baseball Savant API |
| `espn.py` | Connects to ESPN to fetch rostered players to filter waivers |
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

- **ESPN Filtering**: The script matches players by name. It normalizes names (removing accents, "Jr.", "II", punctuation) to ensure Baseball Savant names match ESPN rosters accurately.
- **Off-season**: Baseball Savant may show no trending players during the off-season. The app handles this gracefully and logs a warning.
- **Performance**: The scraper uses Baseball Savant's direct JSON API, which processes lightning-fast (usually under a second).
