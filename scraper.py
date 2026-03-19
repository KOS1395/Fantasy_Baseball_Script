"""
scraper.py — Scrape trending players from Baseball Savant using Playwright.

The Baseball Savant homepage renders trending player cards via JavaScript.
We launch a headless Chromium browser, wait for the cards to appear, then
parse them with BeautifulSoup.

Each returned player dict has:
    name        str   "Shohei Ohtani"
    trend_dir   str   "up" | "down"
    trend_pct   str   "+5%" | "-2%"
    stat_label  str   "Home Runs - 2025"
    profile_url str   "https://baseballsavant.mlb.com/savant-player/660271"
    player_id   str   "660271"
"""
import re
import logging
from typing import Any

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from bs4 import BeautifulSoup

from config import SAVANT_URL

logger = logging.getLogger(__name__)


def _parse_trend_card(card_soup) -> dict[str, Any] | None:
    """Parse a single trending player card element."""
    try:
        # The card is wrapped in an <a> tag pointing to the player profile
        anchor = card_soup if card_soup.name == "a" else card_soup.find("a")
        if not anchor:
            return None

        href = anchor.get("href", "")
        profile_url = href if href.startswith("http") else f"https://baseballsavant.mlb.com{href}"

        # Extract player ID from URL
        player_id_match = re.search(r"/savant-player/(\d+)", profile_url)
        player_id = player_id_match.group(1) if player_id_match else "unknown"

        # All text content inside the card
        raw_text = anchor.get_text(separator="\n", strip=True)
        lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]

        # Parse name — look for "Firstname Lastname Home Runs" pattern
        name = None
        stat_label = None
        trend_dir = "unknown"
        trend_pct = "N/A"

        for i, line in enumerate(lines):
            # Trend indicator line: "Trending ↑ +5%" or "Trending ↓ -2%"
            # CSS arrows may also render as plain text "up" / "down" etc.
            trend_match = re.search(
                r"Trending\s*([↑↓▲▼]|up|down)\s*([+-]?\d+%?)",
                line,
                re.IGNORECASE,
            )
            if trend_match:
                arrow = trend_match.group(1)
                pct = trend_match.group(2)
                trend_dir = "up" if arrow in ("↑", "▲", "up") else "down"
                trend_pct = pct if "%" in pct else f"{pct}%"

            # "TRENDING PLAYER" label — the line before it often has direction
            if "TRENDING PLAYER" in line.upper():
                continue

            # Stat label: "Home Runs - 2025" pattern
            stat_match = re.search(r"(.+?)\s*-\s*(20\d{2})", line)
            if stat_match and not name:
                stat_label = line

        # Name extraction: look for lines that appear to be a player name
        # (2–4 words, title-cased, no digits, before the stat label)
        name_candidates = []
        for line in lines:
            if re.match(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}$", line):
                name_candidates.append(line)

        if name_candidates:
            # Prefer the longest clean match that isn't "Trending Player"
            for cand in sorted(name_candidates, key=len, reverse=True):
                if "Trending" not in cand and "Player" not in cand:
                    name = cand
                    break

        # Fall back: first plausible name from raw text
        if not name:
            # Try splitting the raw text looking for a "FirstName LastName Stat" run
            joined = " ".join(lines)
            fallback = re.search(
                r"([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,3})\s+(?:Home Runs|Strikeouts|ERA|AVG|OBP|SLG|WHIP|Pitching)",
                joined,
            )
            name = fallback.group(1) if fallback else "Unknown Player"

        if not stat_label:
            # Try generic label from text
            lbl_match = re.search(
                r"((?:Home Runs|Strikeouts|ERA|AVG|OBP|SLG|WHIP|Batting|Pitching|[A-Za-z ]+)\s*-\s*20\d{2})",
                " ".join(lines),
            )
            stat_label = lbl_match.group(1) if lbl_match else "—"

        return {
            "name": name,
            "trend_dir": trend_dir,
            "trend_pct": trend_pct,
            "stat_label": stat_label,
            "profile_url": profile_url,
            "player_id": player_id,
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to parse player card: %s", exc)
        return None


def scrape_trending_players(timeout_ms: int = 30_000) -> list[dict[str, Any]]:
    """
    Launch headless Chromium, load Baseball Savant, and return a list of
    trending player dicts.
    """
    logger.info("Launching headless browser…")
    players: list[dict[str, Any]] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        try:
            logger.info("Navigating to %s", SAVANT_URL)
            page.goto(SAVANT_URL, wait_until="domcontentloaded", timeout=timeout_ms)

            # Wait for the trending player section to render
            try:
                page.wait_for_selector(
                    "a[href*='/savant-player/']",
                    timeout=timeout_ms,
                    state="attached",
                )
            except PWTimeout:
                logger.warning("Timed out waiting for player links; parsing what's available.")

            # Extra pause to let React / Svelte components finish rendering
            page.wait_for_timeout(3000)

            html = page.content()
        finally:
            browser.close()

    logger.info("Parsing page HTML…")
    soup = BeautifulSoup(html, "lxml")

    # Strategy 1: find all anchor tags linking to savant-player profiles
    anchors = soup.find_all("a", href=re.compile(r"/savant-player/\d+"))

    # Deduplicate by player_id while preserving order
    seen_ids: set[str] = set()
    for anchor in anchors:
        # Only look at anchors that have some meaningful text (not bare icons)
        text = anchor.get_text(strip=True)
        if len(text) < 10:
            continue
        result = _parse_trend_card(anchor)
        if result and result["player_id"] not in seen_ids:
            seen_ids.add(result["player_id"])
            players.append(result)

    logger.info("Found %d trending players.", len(players))
    return players
