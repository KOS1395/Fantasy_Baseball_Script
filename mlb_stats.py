"""
mlb_stats.py — Fetch the roster of all active MLB players from the official API.
"""
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

MLB_STATS_API_URL = "https://statsapi.mlb.com/api/v1/sports/1/players?season=2026"


def get_active_mlb_players(timeout_s: int = 15) -> list[dict[str, Any]]:
    """
    Fetch all active MLB players for the current season.
    Returns a list of dicts:
    [
        {
            "player_id": "660271",
            "name": "Shohei Ohtani",
            "position": "TWP",
            "team": "LAD" # Note: team is not available on this endpoint, we will leave blank
        },
        ...
    ]
    """
    logger.info("Fetching active MLB players from MLB Stats API…")

    headers = {
        "User-Agent": "MLB-Trending-Emailer/1.0"
    }

    try:
        resp = requests.get(MLB_STATS_API_URL, headers=headers, timeout=timeout_s)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to fetch MLB players: %s", exc)
        return []

    people = data.get("people", [])
    if not people:
        logger.warning("MLB API returned successfully but found 0 players.")
        return []

    players: list[dict[str, Any]] = []
    for p in people:
        # Some players might not be active, but the endpoint should filter for active
        players.append({
            "player_id": str(p.get("id")),
            "name": p.get("fullName", "Unknown Player"),
            "position": p.get("primaryPosition", {}).get("abbreviation", "UNK"),
            "player_first_last": f"{p.get('firstName', '')} {p.get('lastName', '')}".strip()
        })

    logger.info("Found %d active MLB players.", len(players))
    return players
