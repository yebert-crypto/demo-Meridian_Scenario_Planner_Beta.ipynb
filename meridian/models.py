from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class SignalType(str, Enum):
    GC_CHANGE = "GC / CLO Change"
    MA_ACTIVITY = "M&A Activity"
    FUNDING_ROUND = "Funding Round"
    IPO_FILING = "IPO / S-1 Filing"
    LITIGATION = "Litigation"
    REGULATORY = "Regulatory Action"
    LEADERSHIP = "Leadership Change"
    BANKRUPTCY = "Bankruptcy"
    NEWS = "General News"


SIGNAL_PRIORITY = {
    SignalType.GC_CHANGE: 1,
    SignalType.MA_ACTIVITY: 1,
    SignalType.IPO_FILING: 1,
    SignalType.BANKRUPTCY: 1,
    SignalType.FUNDING_ROUND: 2,
    SignalType.REGULATORY: 2,
    SignalType.LITIGATION: 2,
    SignalType.LEADERSHIP: 3,
    SignalType.NEWS: 4,
}

SIGNAL_COLOR = {
    SignalType.GC_CHANGE: "#e74c3c",
    SignalType.MA_ACTIVITY: "#8e44ad",
    SignalType.IPO_FILING: "#2980b9",
    SignalType.BANKRUPTCY: "#c0392b",
    SignalType.FUNDING_ROUND: "#27ae60",
    SignalType.REGULATORY: "#e67e22",
    SignalType.LITIGATION: "#d35400",
    SignalType.LEADERSHIP: "#16a085",
    SignalType.NEWS: "#7f8c8d",
}


@dataclass
class Client:
    id: int
    name: str
    ticker: Optional[str] = None        # NYSE/NASDAQ ticker for public companies
    domain: Optional[str] = None        # e.g. "microsoft.com"
    industry: Optional[str] = None
    relationship_partner: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None


@dataclass
class Signal:
    id: Optional[int]
    client_id: int
    client_name: str
    signal_type: SignalType
    headline: str
    summary: str
    source_url: Optional[str]
    source_name: str
    detected_at: datetime
    published_at: Optional[datetime] = None
    is_read: bool = False
    is_dismissed: bool = False
    priority: int = field(init=False)

    def __post_init__(self):
        self.priority = SIGNAL_PRIORITY.get(self.signal_type, 4)
