#!/usr/bin/env python3
"""Retail sentiment fetcher — StockTwits + Reddit for a ticker.

No API keys required. Returns structured JSON with bull/bear ratios and recent posts.
Adapted from TauricResearch/TradingAgents (MIT license).

Usage:
  .venv/bin/python3 scripts/sentiment.py AAPL              # JSON output
  .venv/bin/python3 scripts/sentiment.py AAPL --md          # Markdown output
  .venv/bin/python3 scripts/sentiment.py AAPL --stocktwits  # StockTwits only
  .venv/bin/python3 scripts/sentiment.py AAPL --reddit      # Reddit only
"""
from __future__ import annotations

import argparse
import html
import http.client
import json
import logging
import re
import sys
import time
import xml.etree.ElementTree as ET
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

UA = "xiao-trading-agent/1.0"

# --- StockTwits ---

STOCKTWITS_API = "https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"


def fetch_stocktwits(ticker: str, limit: int = 30, timeout: float = 10.0) -> dict:
    url = STOCKTWITS_API.format(ticker=ticker.upper())
    req = Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except (OSError, http.client.HTTPException, json.JSONDecodeError) as exc:
        logger.warning("StockTwits fetch failed for %s: %s", ticker, exc)
        return {"source": "stocktwits", "available": False, "error": str(exc)}

    messages = data.get("messages", []) if isinstance(data, dict) else []
    if not messages:
        return {"source": "stocktwits", "available": False, "error": "no messages"}

    bullish = bearish = unlabeled = 0
    posts = []
    for m in messages[:limit]:
        entities = m.get("entities") or {}
        sentiment_obj = entities.get("sentiment") or {}
        sentiment = sentiment_obj.get("basic") if isinstance(sentiment_obj, dict) else None
        body = (m.get("body") or "").replace("\n", " ").strip()[:280]
        user = (m.get("user") or {}).get("username", "?")
        created = m.get("created_at", "")

        if sentiment == "Bullish":
            bullish += 1
        elif sentiment == "Bearish":
            bearish += 1
        else:
            unlabeled += 1

        posts.append({
            "user": user,
            "sentiment": sentiment or "none",
            "body": body,
            "created": created,
        })

    total = bullish + bearish + unlabeled
    return {
        "source": "stocktwits",
        "available": True,
        "ticker": ticker.upper(),
        "total": total,
        "bullish": bullish,
        "bearish": bearish,
        "unlabeled": unlabeled,
        "bull_pct": round(100 * bullish / total) if total else 0,
        "bear_pct": round(100 * bearish / total) if total else 0,
        "bull_bear_ratio": round(bullish / bearish, 2) if bearish > 0 else None,
        "posts": posts[:10],  # top 10 for output
    }


# --- Reddit ---

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
DEFAULT_SUBS = ("wallstreetbets", "stocks", "investing")
RSS_URL = "https://www.reddit.com/r/{sub}/search.rss?{qs}"


def _strip_html(content: str) -> str:
    if not content:
        return ""
    if "<!-- SC_OFF -->" in content and "<!-- SC_ON -->" in content:
        content = content.split("<!-- SC_OFF -->")[1].split("<!-- SC_ON -->")[0]
    text = re.sub(r"<[^>]+>", " ", content)
    return " ".join(html.unescape(text).split())


def fetch_reddit(ticker: str, limit_per_sub: int = 5, timeout: float = 10.0) -> dict:
    all_posts = []
    sub_results = {}

    for i, sub in enumerate(DEFAULT_SUBS):
        if i > 0:
            time.sleep(1.0)  # rate limit
        qs = urlencode({
            "q": ticker, "restrict_sr": "on",
            "sort": "new", "t": "week", "limit": limit_per_sub,
        })
        url = RSS_URL.format(sub=sub, qs=qs)
        req = Request(url, headers={"User-Agent": UA})
        try:
            with urlopen(req, timeout=timeout) as resp:
                root = ET.fromstring(resp.read())
        except (OSError, http.client.HTTPException, ET.ParseError, HTTPError) as exc:
            logger.warning("Reddit fetch failed for r/%s: %s", sub, exc)
            sub_results[sub] = 0
            continue

        posts = []
        for entry in root.findall("atom:entry", ATOM_NS)[:limit_per_sub]:
            title_el = entry.find("atom:title", ATOM_NS)
            content_el = entry.find("atom:content", ATOM_NS)
            published_el = entry.find("atom:published", ATOM_NS)
            title = (title_el.text if title_el is not None else "") or ""
            body = _strip_html(content_el.text if content_el is not None else "")[:240]
            published = (published_el.text if published_el is not None else "") or ""
            posts.append({
                "subreddit": sub,
                "title": title,
                "body": body,
                "published": published[:10],
            })
        sub_results[sub] = len(posts)
        all_posts.extend(posts)

    return {
        "source": "reddit",
        "available": len(all_posts) > 0,
        "ticker": ticker.upper(),
        "total_posts": len(all_posts),
        "subreddits": sub_results,
        "posts": all_posts[:15],  # top 15
    }


# --- Combined output ---

def to_markdown(st: dict, rd: dict) -> str:
    lines = [f"## Retail Sentiment: {st.get('ticker', '?')}", ""]

    if st.get("available"):
        ratio_str = f" (ratio {st['bull_bear_ratio']})" if st.get("bull_bear_ratio") else ""
        lines.extend([
            "### StockTwits",
            f"Bullish: {st['bullish']} ({st['bull_pct']}%) | "
            f"Bearish: {st['bearish']} ({st['bear_pct']}%) | "
            f"Unlabeled: {st['unlabeled']} | Total: {st['total']}{ratio_str}",
            "",
        ])
        for p in st.get("posts", [])[:5]:
            tag = f"[{p['sentiment']}]" if p["sentiment"] != "none" else "[—]"
            lines.append(f"- {tag} @{p['user']}: {p['body'][:120]}")
        lines.append("")
    else:
        lines.extend(["### StockTwits", f"Unavailable: {st.get('error', 'unknown')}", ""])

    if rd.get("available"):
        subs = ", ".join(f"r/{s}: {c}" for s, c in rd.get("subreddits", {}).items())
        lines.extend([
            "### Reddit (past 7 days)",
            f"Total: {rd['total_posts']} posts ({subs})",
            "",
        ])
        for p in rd.get("posts", [])[:5]:
            lines.append(f"- r/{p['subreddit']} [{p['published']}]: {p['title'][:120]}")
        lines.append("")
    else:
        lines.extend(["### Reddit", "No posts found in past 7 days", ""])

    # Divergence check
    if st.get("available") and st.get("bull_pct", 50) > 65:
        lines.append("**⚠️ StockTwits skews heavily bullish — check for retail hype divergence from fundamentals**")
    elif st.get("available") and st.get("bear_pct", 50) > 65:
        lines.append("**⚠️ StockTwits skews heavily bearish — contrarian signal if fundamentals intact**")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Fetch retail sentiment (StockTwits + Reddit)")
    parser.add_argument("ticker", help="Stock ticker symbol")
    parser.add_argument("--md", action="store_true", help="Markdown output")
    parser.add_argument("--stocktwits", action="store_true", help="StockTwits only")
    parser.add_argument("--reddit", action="store_true", help="Reddit only")
    args = parser.parse_args()

    both = not args.stocktwits and not args.reddit

    st = fetch_stocktwits(args.ticker) if (both or args.stocktwits) else {"available": False}
    rd = fetch_reddit(args.ticker) if (both or args.reddit) else {"available": False}

    if args.md:
        print(to_markdown(st, rd))
    else:
        output = {}
        if st.get("available") is not None and (both or args.stocktwits):
            output["stocktwits"] = st
        if rd.get("available") is not None and (both or args.reddit):
            output["reddit"] = rd
        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
