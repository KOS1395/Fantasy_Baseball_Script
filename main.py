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
        description="MLB Baseball Savant Trending Players — Email Digest"
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
    from scraper import scrape_trending_players
    from emailer import send_email

    logger.info("Scraping trending players from Baseball Savant…")
    players = scrape_trending_players()

    if not players:
        logger.warning(
            "No trending players were found. "
            "The site may be loading slowly or the off-season is active."
        )
        if args.dry_run:
            send_email([], dry_run=True)
        return

    logger.info("Scraped %d trending players.", len(players))
    for p in players:
        arrow = "↑" if p["trend_dir"] == "up" else ("↓" if p["trend_dir"] == "down" else "—")
        logger.info("  %s  %s %s  |  %s", p["name"], arrow, p["trend_pct"], p["stat_label"])

    send_email(players, dry_run=args.dry_run)
    if not args.dry_run:
        logger.info("✅ Email sent successfully!")


if __name__ == "__main__":
    main()
