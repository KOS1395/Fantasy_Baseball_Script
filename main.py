"""
main.py — Entry point for the MLB Baseball Savant Trending Players Email App.

Usage:
  python main.py              # Scrape now and send email immediately
  python main.py --dry-run    # Scrape now, print HTML to console (no email sent)
  python main.py --schedule   # Start the scheduler (Wed & Sun at 7 PM)
"""
import argparse
import logging
import sys

# Force UTF-8 encoding for stdout on Windows to support emojis
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("main")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MLB Reddit Hype + Baseball Savant — Email Digest"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scrape players and print the HTML email to stdout instead of sending.",
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Start the scheduler (sends email Wed & Sun at 7 PM).",
    )
    args = parser.parse_args()

    if args.schedule:
        logger.info("Starting scheduler mode…")
        from scheduler import start_scheduler
        start_scheduler()
        return

    # One-shot mode (with or without --dry-run)
    from mlb_stats import get_active_mlb_players
    from espn import get_rostered_players, normalize_name
    from reddit import get_reddit_hype_scores
    from scraper import scrape_trending_players
    from emailer import send_email

    # 1. Fetch MLB Universe
    all_players = get_active_mlb_players()
    if not all_players:
        logger.error("Failed to load MLB player universe. Exiting.")
        return

    # 2. Fetch ESPN Rosters
    rostered_names = get_rostered_players()
    if rostered_names:
        logger.info("Will filter out %d players currently rostered in ESPN.", len(rostered_names))

    # 3. Filter available players
    available_players = []
    for p in all_players:
        if normalize_name(p["name"]) not in rostered_names:
            available_players.append(p)
    logger.info("%d players available on waiver wire.", len(available_players))

    # 4. Fetch Reddit Hype Scores (4-day window)
    available_names = [p["name"] for p in available_players]
    hype_scores = get_reddit_hype_scores(available_names)

    # 5. Filter to players with hype and sort
    hyped_players = []
    for p in available_players:
        score = hype_scores.get(p["name"], 0)
        if score > 0:
            p["hype_score"] = score
            hyped_players.append(p)

    hyped_players.sort(key=lambda x: x["hype_score"], reverse=True)
    top_15 = hyped_players[:15]

    if not top_15:
        logger.warning("No available players are being hyped on Reddit right now.")
        if args.dry_run:
            send_email([], dry_run=True)
        return

    # 6. Fetch Baseball Savant Context
    logger.info("Fetching Baseball Savant list to append trend contexts…")
    savant_players = scrape_trending_players(owned_players=set())
    savant_map = {normalize_name(p["name"]): p for p in savant_players}

    # 7. Merge Context
    for p in top_15:
        p["profile_url"] = f"https://baseballsavant.mlb.com/savant-player/{p['player_id']}"
        norm_name = normalize_name(p["name"])
        if norm_name in savant_map:
            s_data = savant_map[norm_name]
            p["trend_dir"] = s_data["trend_dir"]
            p["trend_pct"] = s_data["trend_pct"]
            p["stat_label"] = s_data["stat_label"]
        else:
            p["trend_dir"] = None
            p["trend_pct"] = ""
            p["stat_label"] = f"Pos: {p['position']}"

    logger.info("Final Top %d Hyped Players:", len(top_15))
    for i, p in enumerate(top_15, 1):
        trend = f"({p['trend_dir']} {p['trend_pct']})" if p['trend_dir'] else ""
        # Removed emoji from the terminal logger to prevent Windows UnicodeEncodeError
        logger.info("  #%-2d %-25s HYPE: %-3s %s", i, p["name"], p["hype_score"], trend)

    # 8. Send Email
    send_email(top_15, dry_run=args.dry_run)
    if not args.dry_run:
        logger.info("✅ Email sent successfully!")


if __name__ == "__main__":
    main()
