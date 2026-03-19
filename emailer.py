"""
emailer.py — Build and send a rich HTML email with trending MLB players.
"""
import smtplib
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from jinja2 import Environment, BaseLoader

import config

logger = logging.getLogger(__name__)

# ── Inline Jinja2 HTML template ───────────────────────────────────────────────
_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>⚾ MLB Trending Players</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

  body {
    margin: 0; padding: 0;
    background: #0a0e1a;
    font-family: 'Inter', Arial, sans-serif;
    color: #e2e8f0;
  }
  .wrapper {
    max-width: 680px;
    margin: 0 auto;
    background: #0a0e1a;
  }

  /* ─── Header ─── */
  .header {
    background: linear-gradient(135deg, #1a2540 0%, #0f1e3a 50%, #1a1030 100%);
    padding: 40px 32px 32px;
    text-align: center;
    border-bottom: 2px solid #2a3a5e;
  }
  .header-badge {
    display: inline-block;
    background: linear-gradient(90deg, #c41e3a, #e8503a);
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 20px;
    margin-bottom: 14px;
  }
  .header h1 {
    margin: 0 0 8px;
    font-size: 32px;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: -0.5px;
  }
  .header .subtitle {
    color: #7fa4cc;
    font-size: 14px;
    margin: 0;
  }
  .header .date-line {
    margin-top: 10px;
    font-size: 12px;
    color: #4a6fa5;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  /* ─── Body ─── */
  .body {
    padding: 28px 24px;
  }
  .section-title {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4a6fa5;
    margin: 0 0 16px;
  }

  /* ─── Player Card ─── */
  .player-card {
    background: linear-gradient(135deg, #121a2e 0%, #171f38 100%);
    border: 1px solid #1e2d4d;
    border-radius: 12px;
    margin-bottom: 14px;
    overflow: hidden;
  }
  .player-card:hover { border-color: #2a4070; }
  .card-inner {
    display: table;
    width: 100%;
    padding: 18px 20px;
    box-sizing: border-box;
  }
  .card-rank {
    display: table-cell;
    width: 36px;
    vertical-align: middle;
    font-size: 13px;
    font-weight: 700;
    color: #2e4268;
    white-space: nowrap;
  }
  .card-avatar {
    display: table-cell;
    width: 54px;
    vertical-align: middle;
    padding-right: 14px;
  }
  .avatar-img {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, #1e3050, #2a4578);
    display: block;
    overflow: hidden;
  }
  .avatar-img img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
  }
  .card-info {
    display: table-cell;
    vertical-align: middle;
  }
  .player-name {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 3px;
    text-decoration: none;
  }
  .player-name a {
    color: #ffffff;
    text-decoration: none;
  }
  .player-name a:hover { color: #7fa4cc; }
  .stat-label {
    font-size: 12px;
    color: #5a7aa8;
    margin: 0;
    font-weight: 600;
  }
  .card-trend {
    display: table-cell;
    vertical-align: middle;
    text-align: right;
    white-space: nowrap;
  }
  .trend-badge {
    display: inline-block;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 14px;
    font-weight: 700;
    font-family: monospace;
    margin-bottom: 4px;
  }
  .hype-badge {
    display: inline-block;
    background: rgba(255, 69, 0, 0.15); /* Reddit orangeish */
    color: #ff4500;
    border: 1px solid rgba(255, 69, 0, 0.3);
    border-radius: 8px;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: 700;
    font-family: monospace;
    margin-left: 6px;
  }
  .trend-up {
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    border: 1px solid rgba(74, 222, 128, 0.3);
  }
  .trend-down {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(248, 113, 113, 0.3);
  }
  .trend-unknown {
    background: rgba(100, 116, 139, 0.15);
    color: #94a3b8;
    border: 1px solid rgba(148, 163, 184, 0.3);
  }
  .trend-arrow {
    margin-right: 4px;
  }

  /* ─── Divider ─── */
  .divider {
    border: 0;
    border-top: 1px solid #1a2540;
    margin: 24px 0;
  }

  /* ─── Empty state ─── */
  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #4a6fa5;
    font-size: 14px;
  }

  /* ─── CTA ─── */
  .cta-btn {
    display: block;
    width: 200px;
    margin: 0 auto;
    background: linear-gradient(90deg, #c41e3a, #e8503a);
    color: #ffffff !important;
    text-decoration: none;
    font-weight: 700;
    font-size: 14px;
    padding: 13px 24px;
    border-radius: 8px;
    text-align: center;
    letter-spacing: 0.5px;
  }

  /* ─── Footer ─── */
  .footer {
    padding: 24px 32px;
    text-align: center;
    border-top: 1px solid #141e32;
  }
  .footer p {
    margin: 4px 0;
    font-size: 11px;
    color: #2e4268;
  }
  .footer a { color: #3d5a8a; text-decoration: none; }
</style>
</head>
<body>
<div class="wrapper">

  <!-- Header -->
  <div class="header">
    <div class="header-badge">⚾ Baseball Savant</div>
    <h1>Trending Players</h1>
    <p class="subtitle">This week's hottest names on Statcast</p>
    <div class="date-line">{{ date_str }}</div>
  </div>

  <!-- Body -->
  <div class="body">
    <p class="section-title">🔥 Top Trending — {{ players|length }} Players</p>

    {% if players %}
      {% for player in players %}
      <div class="player-card">
        <div class="card-inner">
          <div class="card-rank">#{{ loop.index }}</div>
          <div class="card-avatar">
            <div class="avatar-img">
              <img
                src="https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_48,q_auto:best/v1/people/{{ player.player_id }}/headshot/67/current"
                alt="{{ player.name }}"
              />
            </div>
          </div>
          <div class="card-info">
            <div class="player-name">
              <a href="{{ player.profile_url }}" target="_blank">{{ player.name }}</a>
            </div>
            <p class="stat-label">{{ player.stat_label }}</p>
          </div>
          <div class="card-trend">
            {% if player.trend_dir == 'up' %}
            <div class="trend-badge trend-up">
              <span class="trend-arrow">↑</span>{{ player.trend_pct }}
            </div>
            {% elif player.trend_dir == 'down' %}
            <div class="trend-badge trend-down">
              <span class="trend-arrow">↓</span>{{ player.trend_pct }}
            </div>
            {% else %}
            <div class="trend-badge trend-unknown">—</div>
            {% endif %}

            {% if player.hype_score > 0 %}
            <div class="hype-badge">
              💬 {{ player.hype_score }}
            </div>
            {% endif %}
          </div>
        </div>
      </div>
      {% endfor %}
    {% else %}
      <div class="empty-state">
        ⚾ No trending players found this week.<br/>
        The season may be between games — check back soon!
      </div>
    {% endif %}

    <hr class="divider" />

    <div style="text-align:center; margin-bottom:28px;">
      <a class="cta-btn" href="https://baseballsavant.mlb.com/" target="_blank">
        View Full Dashboard →
      </a>
    </div>
  </div>

  <!-- Footer -->
  <div class="footer">
    <p>Data sourced from <a href="https://baseballsavant.mlb.com">Baseball Savant / MLB Statcast</a></p>
    <p>Sent automatically on Wednesday &amp; Sunday at 7:00 PM</p>
    <p style="margin-top:8px; color:#1e2d4d;">
      To stop receiving these emails, simply disable the scheduler.
    </p>
  </div>

</div>
</body>
</html>
""".strip()


def build_html(players: list[dict[str, Any]]) -> str:
    """Render the Jinja2 HTML template with player data."""
    env = Environment(loader=BaseLoader())
    tmpl = env.from_string(_EMAIL_TEMPLATE)
    now = datetime.now()
    # %-d is Linux-only; use this portable approach for day without leading zero
    today = now.strftime("%A, %B ") + str(now.day) + now.strftime(", %Y")
    return tmpl.render(players=players, date_str=today)


def send_email(players: list[dict[str, Any]], dry_run: bool = False) -> None:
    """Build and send (or print) the trending players email."""
    html_body = build_html(players)
    now = datetime.now()
    subject = f"⚾ MLB Trending Players — {now.strftime('%B ')} {now.day}, {now.strftime('%Y')}"

    if dry_run:
        print("\n" + "=" * 60)
        print(f"DRY RUN — Would send: '{subject}'")
        print(f"TO: {', '.join(config.EMAIL_TO) if config.EMAIL_TO else 'Not Configured'}")
        print("=" * 60)
        print(html_body)
        print("=" * 60 + "\n")
        return

    if not config.SMTP_USER or not config.SMTP_PASSWORD:
        raise EnvironmentError(
            "Missing SMTP_USER or SMTP_PASSWORD. "
            "Please copy .env.example to .env and configure your credentials."
        )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.EMAIL_FROM
    msg["To"] = ", ".join(config.EMAIL_TO)

    # Plain-text fallback
    plain_lines = [f"MLB Trending Players — {now.strftime('%B ')}{now.day}, {now.year}", ""]
    for i, p in enumerate(players, 1):
        arrow = "↑" if p["trend_dir"] == "up" else ("↓" if p["trend_dir"] == "down" else "—")
        hype = f" [Reddit Hype: {p['hype_score']}]" if p.get("hype_score", 0) > 0 else ""
        plain_lines.append(f"#{i}  {p['name']}  {arrow} {p['trend_pct']}  |  {p['stat_label']}{hype}")
        plain_lines.append(f"    {p['profile_url']}")
    plain_lines += ["", "View full dashboard: https://baseballsavant.mlb.com/"]
    plain_body = "\n".join(plain_lines)

    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    logger.info("Connecting to %s:%s…", config.SMTP_HOST, config.SMTP_PORT)
    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.sendmail(config.EMAIL_FROM, config.EMAIL_TO, msg.as_string())

    logger.info("Email sent to: %s", ", ".join(config.EMAIL_TO))
