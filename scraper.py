"""
scraper.py — Fetch trending players from the Baseball Savant JSON API.

Uses a direct HTTP call instead of a headless browser — fast and reliable.

Each returned player dict has:
    name        str   "Shohei Ohtani"
    trend_dir   str   "up" | "down"
    trend_pct   str   "+3%" | "-8%"
    stat_label  str   "Home Runs" | "Strikeouts" | ...
    profile_url str   "https://baseballsavant.mlb.com/savant-player/660271"
    player_id   str   "660271"
    team        str   "LAD"
    position    str   "RF" | "RHP" | ...
"""
import re
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

API_URL = "https://baseballsavant.mlb.com/savant/api/v1/trending-players"

# Map position -> default stat label shown on Baseball Savant cards
PITCHER_POSITIONS = {"RHP", "LHP", "SP", "RP", "P"}

def _stat_label(pos: str) -> str:
    """Return the default trending stat label based on position."""
    if pos.upper() in PITCHER_POSITIONS:
        return "Strikeouts"
    return "Home Runs"


def _parse_trend(trend_str: str) -> tuple[str, str]:
    """Parse '↑ 3%' or '↓ -8%' into (direction, pct_string)."""
    m = re.search(r"([↑↓▲▼])\s*(\d+%?)", trend_str)
    if m:
        arrow, pct = m.group(1), m.group(2)
        direction = "up" if arrow in ("↑", "▲") else "down"
        pct_str = pct if "%" in pct else f"{pct}%"
        sign = "+" if direction == "up" else "-"
        return direction, f"{sign}{pct_str}"
    return "unknown", "N/A"


def scrape_trending_players(timeout_s: int = 10) -> list[dict[str, Any]]:
    """
    Fetch trending players from the Baseball Savant API.
    Returns a list of player dicts in trending order.
    """
    logger.info("Fetching trending players from %s", API_URL)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://baseballsavant.mlb.com/",
        "Accept": "application/json",
    }

    try:
        resp = requests.get(API_URL, headers=headers, timeout=timeout_s)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        logger.error("Failed to fetch trending players: %s", exc)
        return []

    players: list[dict[str, Any]] = []
    for entry in data:
        player_id = str(entry.get("id", "unknown"))
        name = entry.get("name") or f"{entry.get('first', '')} {entry.get('last', '')}".strip()
        pos = entry.get("pos", "")
        team = entry.get("parent_team", "")
        trend_raw = entry.get("trend", "")
        trend_dir, trend_pct = _parse_trend(trend_raw)

        players.append({
            "name": name or "Unknown Player",
            "trend_dir": trend_dir,
            "trend_pct": trend_pct,
            "stat_label": _stat_label(pos),
            "profile_url": f"https://baseballsavant.mlb.com/savant-player/{player_id}",
            "player_id": player_id,
            "team": team,
            "position": pos,
        })

    logger.info("Found %d trending players.", len(players))
    return players
