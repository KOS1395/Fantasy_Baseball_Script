"""
reddit.py — Fetch the daily stickied thread from r/fantasybaseball
and count mentions of specific players to calculate a 'Hype Score'.
"""
import logging
import re
from typing import Any

import requests

logger = logging.getLogger(__name__)


def _extract_all_comments(data: Any, comments_list: list[str]) -> None:
    """
    Recursively extract the 'body' text from all comments and replies
    in a Reddit JSON listing.
    """
    if isinstance(data, dict):
        if "body" in data:
            comments_list.append(data["body"])
        
        # If there are replies, it's usually a dictionary representing another Listing
        if "replies" in data and isinstance(data["replies"], dict):
            _extract_all_comments(data["replies"], comments_list)
        elif "children" in data:
            _extract_all_comments(data["children"], comments_list)
        elif "data" in data:
            _extract_all_comments(data["data"], comments_list)

    elif isinstance(data, list):
        for item in data:
            _extract_all_comments(item, comments_list)


def get_reddit_hype_scores(player_names: list[str]) -> dict[str, int]:
    """
    Fetch the stickied thread from r/fantasybaseball.
    Extract all comments.
    Count how many comments mention each player's last name.
    
    Returns:
        dict: Mapping of player full name to number of mentions (Hype Score).
    """
    if not player_names:
        return {}

    logger.info("Fetching r/fantasybaseball daily stickied thread…")

    headers = {
        "User-Agent": "MLB-Trending-Emailer/1.0"
    }
    url = "https://www.reddit.com/r/fantasybaseball/about/sticky.json"

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        thread_data = resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to fetch Reddit thread: %s", exc)
        return {name: 0 for name in player_names}

    if not thread_data or len(thread_data) < 2:
        logger.error("Unexpected Reddit JSON structure.")
        return {name: 0 for name in player_names}

    # Extract title just for logging
    try:
        title = thread_data[0]["data"]["children"][0]["data"]["title"]
        logger.info("Scanning thread: %s", title)
    except (KeyError, IndexError):
        logger.info("Scanning stickied thread...")

    # Extract all comment bodies
    all_comments: list[str] = []
    _extract_all_comments(thread_data[1], all_comments)
    logger.info("Extracted %d comments/replies.", len(all_comments))

    hype_scores: dict[str, int] = {}

    for full_name in player_names:
        # Split into parts. Usually ["Shohei", "Ohtani"]
        parts = full_name.split()
        if len(parts) >= 2:
            # Match by last name.
            # E.g., if parts are ["Ronald", "Acuña", "Jr."], last name is "Acuña"
            last_name = parts[1].strip(".,'")
            
            # For common short names like "Pena" or "Smith", searching just the last name
            # might yield false positives, but since we are only searching for players
            # ALREADY trending on Baseball Savant, the risk is much lower.
            search_regex = re.compile(rf"\b{re.escape(last_name)}\b", re.IGNORECASE)
        else:
            search_regex = re.compile(rf"\b{re.escape(full_name)}\b", re.IGNORECASE)

        count = 0
        for comment in all_comments:
            if search_regex.search(comment):
                count += 1
                
        hype_scores[full_name] = count

    return hype_scores
