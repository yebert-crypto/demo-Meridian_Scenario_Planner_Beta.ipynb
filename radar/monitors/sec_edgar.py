"""
SEC EDGAR monitor — free, no API key required.

Covers:
  - 8-K  → M&A announcements, leadership changes
  - S-1  → IPO filings
  - SC TO-T / SC 13D → tender offers / activist investors
  - DEF 14A → proxy statements (GC comp changes year-over-year → GC turnover signal)
"""
import re
import time
from datetime import datetime, timedelta
from typing import Generator

import requests

from radar.models import Client, Signal, SignalType
from radar.monitors.base import BaseMonitor

EDGAR_BASE = "https://efts.sec.gov/LATEST/search-index"
EDGAR_SEARCH = "https://efts.sec.gov/LATEST/search-index"
EDGAR_COMPANY = "https://www.sec.gov/cgi-bin/browse-edgar"
EDGAR_SUBMISSIONS = "https://data.sec.gov/submissions"

HEADERS = {"User-Agent": "Client Radar BD Monitor legal-bd@perkinscoie.com"}

# Form types and the signal they indicate
FORM_SIGNAL_MAP = {
    "8-K": SignalType.MA_ACTIVITY,       # refined by item number
    "S-1": SignalType.IPO_FILING,
    "S-1/A": SignalType.IPO_FILING,
    "SC TO-T": SignalType.MA_ACTIVITY,
    "SC 13D": SignalType.MA_ACTIVITY,
    "SC 13D/A": SignalType.MA_ACTIVITY,
    "DEF 14A": SignalType.GC_CHANGE,     # proxy — scan for GC comp
}

# 8-K items that indicate M&A or leadership changes
MA_ITEMS = {"1.01", "2.01"}             # entry into material agreement, completion of acquisition
LEADERSHIP_ITEMS = {"5.02"}             # departure/appointment of officers/directors


class SecEdgarMonitor(BaseMonitor):
    name = "sec_edgar"

    def __init__(self, lookback_days: int = 7):
        self.lookback_days = lookback_days

    def scan(self, clients: list[Client]) -> Generator[Signal, None, None]:
        # Only public companies have tickers / CIK lookups
        public = [c for c in clients if c.ticker]
        for client in public:
            cik = self._get_cik(client.ticker)
            if not cik:
                continue
            time.sleep(0.15)  # EDGAR rate limit: ~10 req/sec
            yield from self._scan_client(client, cik)

    def _get_cik(self, ticker: str) -> str | None:
        try:
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?company=&CIK={ticker}&type=&dateb=&owner=include&count=1&search_text=&action=getcompany&output=atom"
            r = requests.get(url, headers=HEADERS, timeout=10)
            match = re.search(r"CIK=(\d+)", r.text)
            return match.group(1).zfill(10) if match else None
        except Exception:
            return None

    def _scan_client(self, client: Client, cik: str) -> Generator[Signal, None, None]:
        try:
            r = requests.get(
                f"{EDGAR_SUBMISSIONS}/CIK{cik}.json",
                headers=HEADERS, timeout=15,
            )
            data = r.json()
        except Exception:
            return

        filings = data.get("filings", {}).get("recent", {})
        forms = filings.get("form", [])
        dates = filings.get("filingDate", [])
        accessions = filings.get("accessionNumber", [])
        descriptions = filings.get("primaryDocDescription", [])

        cutoff = datetime.utcnow() - timedelta(days=self.lookback_days)

        for form, date_str, accession, desc in zip(forms, dates, accessions, descriptions):
            if form not in FORM_SIGNAL_MAP:
                continue
            try:
                filed = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue
            if filed < cutoff:
                break  # filings are newest-first

            signal_type = FORM_SIGNAL_MAP[form]
            headline, summary = self._describe_filing(form, client.name, accession, desc)

            yield Signal(
                id=None,
                client_id=client.id,
                client_name=client.name,
                signal_type=signal_type,
                headline=headline,
                summary=summary,
                source_url=f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-','')}/{accession}-index.htm",
                source_name="SEC EDGAR",
                detected_at=self._now(),
                published_at=filed,
            )

    def _describe_filing(self, form: str, company: str, accession: str, desc: str) -> tuple[str, str]:
        templates = {
            "8-K": (
                f"{company} filed 8-K with SEC",
                f"Current report (8-K) filed. May indicate material agreement, M&A, or leadership change. Review items disclosed.",
            ),
            "S-1": (
                f"{company} filed S-1 IPO registration",
                f"Initial S-1 registration statement filed with SEC — company is pursuing an IPO. Significant legal engagement opportunity.",
            ),
            "S-1/A": (
                f"{company} amended S-1 IPO registration",
                f"Amended S-1 filing — IPO process ongoing.",
            ),
            "SC TO-T": (
                f"Tender offer filed targeting {company}",
                f"SC TO-T indicates a third-party tender offer for {company} shares. M&A activity confirmed.",
            ),
            "SC 13D": (
                f"Activist investor disclosed stake in {company}",
                f"Schedule 13D filed — investor acquired >5% stake and may push for strategic changes including M&A.",
            ),
            "SC 13D/A": (
                f"Activist investor amended 13D stake in {company}",
                f"Amended Schedule 13D — activist position updated. Monitor for board pressure or M&A push.",
            ),
            "DEF 14A": (
                f"{company} filed annual proxy statement",
                f"Proxy statement filed. Review named executive officers section for General Counsel changes year-over-year.",
            ),
        }
        headline, summary = templates.get(form, (f"{company} filed {form}", f"SEC filing: {form}"))
        return headline, summary
