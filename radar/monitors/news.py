"""
News monitor — uses NewsAPI (free tier) + Google News RSS fallback.

Signal classification is keyword-based; replace with an LLM call
(e.g. Claude API) for higher precision when ready.
"""
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Generator

import xml.etree.ElementTree as ET
import requests

from radar.models import Client, Signal, SignalType
from radar.monitors.base import BaseMonitor

NEWSAPI_BASE = "https://newsapi.org/v2/everything"
GNEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

# Keyword → SignalType mapping (order matters — first match wins)
KEYWORD_SIGNALS: list[tuple[list[str], SignalType]] = [
    (["general counsel", "chief legal officer", "CLO", "GC appointed", "GC named", "legal chief"], SignalType.GC_CHANGE),
    (["merger", "acquisition", "acquires", "acquired by", "takeover", "buyout", "M&A"], SignalType.MA_ACTIVITY),
    (["IPO", "initial public offering", "S-1", "going public", "direct listing"], SignalType.IPO_FILING),
    (["Series A", "Series B", "Series C", "Series D", "raised $", "funding round", "venture capital"], SignalType.FUNDING_ROUND),
    (["lawsuit", "litigation", "class action", "sued", "complaint filed", "arbitration"], SignalType.LITIGATION),
    (["SEC charges", "FTC investigation", "DOJ", "antitrust", "regulatory action", "consent decree"], SignalType.REGULATORY),
    (["CEO", "CFO", "CTO", "COO", "president", "appointed", "resigned", "steps down", "new chief"], SignalType.LEADERSHIP),
    (["bankruptcy", "Chapter 11", "Chapter 7", "insolvency", "restructuring"], SignalType.BANKRUPTCY),
]


def classify_signal(text: str) -> SignalType:
    lower = text.lower()
    for keywords, signal_type in KEYWORD_SIGNALS:
        if any(kw.lower() in lower for kw in keywords):
            return signal_type
    return SignalType.NEWS


class NewsMonitor(BaseMonitor):
    name = "news"

    def __init__(self, lookback_days: int = 3, api_key: str | None = None):
        self.lookback_days = lookback_days
        self.api_key = api_key or os.getenv("NEWS_API_KEY")

    def scan(self, clients: list[Client]) -> Generator[Signal, None, None]:
        for client in clients:
            yield from self._scan_client(client)

    def _scan_client(self, client: Client) -> Generator[Signal, None, None]:
        articles = []
        if self.api_key:
            articles = self._fetch_newsapi(client.name)
        if not articles:
            articles = self._fetch_gnews_rss(client.name)

        cutoff = datetime.now(timezone.utc) - timedelta(days=self.lookback_days)

        seen_urls: set[str] = set()
        for article in articles:
            url = article.get("url") or article.get("link", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)

            pub = article.get("publishedAt") or article.get("published", "")
            pub_dt = _parse_date(pub)
            if pub_dt and pub_dt < cutoff:
                continue

            title = article.get("title") or article.get("title", "")
            description = article.get("description") or article.get("summary", "")
            combined = f"{title} {description}"

            signal_type = classify_signal(combined)

            # Skip low-priority generic news if it's just a passing mention
            if signal_type == SignalType.NEWS and not _strong_mention(client.name, combined):
                continue

            yield Signal(
                id=None,
                client_id=client.id,
                client_name=client.name,
                signal_type=signal_type,
                headline=title[:300],
                summary=description[:1000] if description else title,
                source_url=url or None,
                source_name=article.get("source", {}).get("name") or "Google News",
                detected_at=self._now(),
                published_at=pub_dt.replace(tzinfo=None) if pub_dt else None,
            )

    def _fetch_newsapi(self, company: str) -> list[dict]:
        try:
            r = requests.get(NEWSAPI_BASE, params={
                "q": f'"{company}"',
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20,
                "apiKey": self.api_key,
            }, timeout=10)
            data = r.json()
            return data.get("articles", [])
        except Exception:
            return []

    def _fetch_gnews_rss(self, company: str) -> list[dict]:
        try:
            query = requests.utils.quote(company)
            url = GNEWS_RSS.format(query=query)
            r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            root = ET.fromstring(r.text)
            ns = {"media": "http://search.yahoo.com/mrss/"}
            items = root.findall(".//item")
            results = []
            for item in items[:20]:
                title = item.findtext("title") or ""
                link = item.findtext("link") or ""
                desc = item.findtext("description") or ""
                pub = item.findtext("pubDate") or ""
                results.append({
                    "title": title,
                    "description": desc,
                    "url": link,
                    "link": link,
                    "published": pub,
                    "source": {"name": "Google News"},
                })
            return results
        except Exception:
            return []


def _parse_date(s: str) -> datetime | None:
    if not s:
        return None
    formats = ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%a, %d %b %Y %H:%M:%S %Z"]
    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def _strong_mention(company: str, text: str) -> bool:
    """True if the company name appears as a prominent subject (not just a passing ref)."""
    name_lower = company.lower()
    text_lower = text.lower()
    words = text_lower.split()
    count = sum(1 for i in range(len(words) - 1) if name_lower in " ".join(words[i:i+4]))
    return count >= 1
