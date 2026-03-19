# ⚾ MLB Reddit Hype & Statcast Emailer

Automatically scans **r/fantasybaseball** for the most hyped players on the waiver wire and emails you a styled digest every **Wednesday and Sunday at 12:00 PM**.

This script connects to the MLB Stats API to fetch all active players, filters out anyone currently rostered in your ESPN Fantasy Baseball league, and then uses a **Regex Fuzzy-Matching Engine** to count how many times available players are mentioned on Reddit (even catching spelling mistakes or using nicknames like "CES" and "Ohtani").

Finally, it cross-references the top 15 hyped players with **Baseball Savant's Trending Data**, attaching Statcast trend arrows to anyone visibly heating up (or cooling down) under the hood.

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
This prints the full HTML to a `preview.html` file so you can open it directly in your browser without filling up your inbox!

### Start the automatic scheduler (Wed & Sun at 7 PM)

```bash
python main.py --schedule
```

Keep this running in the background (or set it up as a Windows Scheduled Task / startup script).

---

## 📁 Project Files

| File | Purpose |
|---|---|
| `main.py` | Entry point — orchestrates APIs, filtering, and email delivery |
| `reddit.py` | Searches the last 4 days of "Anything Goes" threads on Reddit and counts mentions |
| `aliases.py` | Handles custom nicknames ("J-Rod", "Elly") and blocks common last names |
| `mlb_stats.py` | Fetches the master roster of all active MLB players |
| `scraper.py` | Fetches trending players directly from the Baseball Savant API for context symbols |
| `espn.py` | Connects to ESPN to fetch rostered players |
| `emailer.py` | HTML email builder + SMTP sender |
| `scheduler.py` | APScheduler cron trigger (Wed & Sun 7 PM) |
| `config.py` | Loads settings from `.env` |

---

## ⚠️ Notes

- **Smart Scraping**: The script uses `regex` fuzzy string matching. It tolerates up to 1 typo for any player alias longer than 5 letters (e.g. matching "Otani" to "Ohtani") without bleeding into unintended words.
- **Off-season Statcast**: Baseball Savant may have little to no trending players during the off-season. If a player is hyped on Reddit but has no Statcast arrow next to their name, it just means they aren't currently shifting metrics on Baseball Savant.
