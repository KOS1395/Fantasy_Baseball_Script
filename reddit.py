"""
reddit.py — Fetch the daily stickied thread from r/fantasybaseball
and count mentions of specific players to calculate a 'Hype Score'.
"""
import logging
import regex as re
import time
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


import time

def get_reddit_hype_scores(player_names: list[str]) -> dict[str, int]:
    """
    Find recent 'Anything Goes' threads (past 4 days).
    Extract all comments.
    Count how many comments mention each player's last name.
    """
    if not player_names:
        return {}

    logger.info("Fetching r/fantasybaseball recent Anything Goes threads (past 96h)…")

    headers = {"User-Agent": "MLB-Trending-Emailer/1.0"}
    search_url = "https://www.reddit.com/r/fantasybaseball/search.json?q=Anything+Goes&restrict_sr=on&sort=new&t=week"

    try:
        resp = requests.get(search_url, headers=headers, timeout=10)
        resp.raise_for_status()
        search_data = resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to fetch Reddit search results: %s", exc)
        return {name: 0 for name in player_names}

    posts = search_data.get("data", {}).get("children", [])
    if not posts:
        logger.warning("No Anything Goes threads found in the past week.")
        return {name: 0 for name in player_names}

    # Filter threads created within the last 96 hours
    current_time = time.time()
    recent_threads = []
    max_age_seconds = 4 * 24 * 3600

    for p in posts:
        post_data = p.get("data", {})
        created_utc = post_data.get("created_utc", 0)
        if current_time - created_utc <= max_age_seconds:
            recent_threads.append(post_data)

    logger.info("Found %d threads matching criteria. Fetching comments…", len(recent_threads))

    all_comments: list[str] = []

    for thread in recent_threads:
        permalink = thread.get("permalink", "")
        if not permalink:
            continue
        
        thread_url = f"https://www.reddit.com{permalink}.json"
        try:
            r = requests.get(thread_url, headers=headers, timeout=10)
            if r.status_code == 200:
                thread_data = r.json()
                if len(thread_data) >= 2:
                    _extract_all_comments(thread_data[1], all_comments)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to fetch comments for thread %s: %s", permalink, exc)
        
        # Be nice to Reddit
        time.sleep(1)

    from aliases import get_search_terms

    logger.info("Extracted %d comments/replies across %d threads.", len(all_comments), len(recent_threads))

    hype_scores: dict[str, int] = {}

    # Pre-compile the regexes for all players for maximum scanning speed
    player_patterns = {}
    for full_name in player_names:
        terms = get_search_terms(full_name)
        # Create a robust regex: (?e)\b(?:(?:Shohei Ohtani){e<=1}|(?:Shohei){e<=1}|Ohtani)\b
        regex_terms = []
        for t in terms:
            escaped_t = re.escape(t)
            # Only allow typos (1 edit distance) if the alias is longer than 5 characters
            # to prevent matching completely different short words (like CES matching CAT)
            if len(t) > 5:
                regex_terms.append(f"(?:{escaped_t}){{e<=1}}")
            else:
                regex_terms.append(escaped_t)
                
        # (?e) enables fuzzy matching mode in the `regex` library
        pattern_str = rf"(?e)\b(?:{'|'.join(regex_terms)})\b"
        player_patterns[full_name] = re.compile(pattern_str, re.IGNORECASE)

    logger.info("Scanning comments for %d players with smart nickname aliases...", len(player_names))
    
    for full_name, search_regex in player_patterns.items():
        count = 0
        for comment in all_comments:
            if search_regex.search(comment):
                count += 1
                
        hype_scores[full_name] = count

    return hype_scores
