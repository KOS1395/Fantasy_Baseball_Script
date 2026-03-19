"""
espn.py — Fetch rostered players from ESPN Fantasy Baseball.

Uses the espn_api package to connect to a league and extract all owned player names.
"""
import logging
import unicodedata

from espn_api.baseball import League
import config

logger = logging.getLogger(__name__)


def normalize_name(name: str) -> str:
    """
    Normalize a player's name for robust matching.
    - Remove accents (Acuña -> Acuna)
    - Lowercase
    - Remove punctuation (periods, commas, hyphens)
    - Remove common suffixes (Jr, Sr, II, III)
    """
    if not name:
        return ""

    # Remove accents
    name = "".join(
        c for c in unicodedata.normalize("NFD", name) if unicodedata.category(c) != "Mn"
    )

    name = name.lower()

    # Remove punctuation
    for char in (".", ",", "-", "'"):
        name = name.replace(char, " ")

    # Remove suffixes
    parts = name.split()
    clean_parts = [p for p in parts if p not in ("jr", "sr", "ii", "iii")]

    # Rejoin with single spaces
    return " ".join(clean_parts).strip()


def get_rostered_players() -> set[str]:
    """
    Connect to the configured ESPN league and return a set of normalized names
    for all players currently on any roster.

    Returns an empty set if ESPN is not configured or an error occurs.
    """
    if not config.ESPN_LEAGUE_ID:
        logger.debug("ESPN_LEAGUE_ID not configured; skipping ownership check.")
        return set()

    logger.info(
        "Connecting to ESPN Fantasy Baseball League %s (Year: %s)…",
        config.ESPN_LEAGUE_ID,
        config.ESPN_YEAR,
    )

    kwargs = {
        "league_id": config.ESPN_LEAGUE_ID,
        "year": config.ESPN_YEAR,
    }

    if config.ESPN_S2 and config.SWID:
        kwargs["espn_s2"] = config.ESPN_S2
        kwargs["swid"] = config.SWID
        logger.debug("Using private league authentication cookies.")

    try:
        league = League(**kwargs)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to connect to ESPN league: %s", exc)
        return set()

    owned_players = set()
    try:
        for team in league.teams:
            for player in team.roster:
                norm_name = normalize_name(player.name)
                owned_players.add(norm_name)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to parse ESPN rosters: %s", exc)
        return set()

    logger.info(
        "Successfully fetched %d rostered players from %d teams.",
        len(owned_players),
        len(league.teams),
    )
    return owned_players
