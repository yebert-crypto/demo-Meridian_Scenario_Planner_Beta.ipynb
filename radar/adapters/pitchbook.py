"""
Pitchbook adapter — plug in your API key when access is granted.

Covers: M&A, funding rounds, company profiles, investor activity.
Docs: https://docs.pitchbook.com (requires vendor access)
"""
import os
from datetime import datetime, timedelta
from typing import Generator

import requests

from radar.models import Client, Signal, SignalType
from radar.monitors.base import BaseMonitor

PITCHBOOK_BASE = os.getenv("PITCHBOOK_API_URL", "https://api.pitchbook.com/v1")


class PitchbookMonitor(BaseMonitor):
    name = "pitchbook"

    def __init__(self, api_key: str | None = None, lookback_days: int = 7):
        self.api_key = api_key or os.getenv("PITCHBOOK_API_KEY")
        self.lookback_days = lookback_days

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def scan(self, clients: list[Client]) -> Generator[Signal, None, None]:
        if not self.is_configured:
            return
        for client in clients:
            yield from self._scan_deals(client)
            yield from self._scan_funding(client)

    def _scan_deals(self, client: Client) -> Generator[Signal, None, None]:
        """Query Pitchbook M&A deals API."""
        # TODO: replace with actual Pitchbook endpoint once docs are available
        # Example endpoint shape (confirm with Pitchbook):
        # GET /v1/deals?company={name}&dealType=ma&fromDate={date}
        params = {
            "company": client.name,
            "dealType": "ma",
            "fromDate": (datetime.utcnow() - timedelta(days=self.lookback_days)).strftime("%Y-%m-%d"),
        }
        try:
            r = requests.get(
                f"{PITCHBOOK_BASE}/deals",
                headers={"X-API-Key": self.api_key},
                params=params,
                timeout=15,
            )
            r.raise_for_status()
            for deal in r.json().get("data", []):
                yield Signal(
                    id=None,
                    client_id=client.id,
                    client_name=client.name,
                    signal_type=SignalType.MA_ACTIVITY,
                    headline=f"{client.name}: {deal.get('dealType', 'Deal')} — {deal.get('targetName', 'undisclosed')}",
                    summary=deal.get("description", "M&A deal detected via Pitchbook."),
                    source_url=deal.get("url"),
                    source_name="Pitchbook",
                    detected_at=self._now(),
                    published_at=_parse(deal.get("announcedDate")),
                )
        except Exception:
            pass

    def _scan_funding(self, client: Client) -> Generator[Signal, None, None]:
        """Query Pitchbook funding rounds API."""
        params = {
            "company": client.name,
            "fromDate": (datetime.utcnow() - timedelta(days=self.lookback_days)).strftime("%Y-%m-%d"),
        }
        try:
            r = requests.get(
                f"{PITCHBOOK_BASE}/funding-rounds",
                headers={"X-API-Key": self.api_key},
                params=params,
                timeout=15,
            )
            r.raise_for_status()
            for round_ in r.json().get("data", []):
                amount = round_.get("dealSize", "undisclosed")
                yield Signal(
                    id=None,
                    client_id=client.id,
                    client_name=client.name,
                    signal_type=SignalType.FUNDING_ROUND,
                    headline=f"{client.name} raised {amount} — {round_.get('roundType', 'funding round')}",
                    summary=round_.get("description", "Funding round detected via Pitchbook."),
                    source_url=round_.get("url"),
                    source_name="Pitchbook",
                    detected_at=self._now(),
                    published_at=_parse(round_.get("closedDate")),
                )
        except Exception:
            pass


def _parse(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        return None
