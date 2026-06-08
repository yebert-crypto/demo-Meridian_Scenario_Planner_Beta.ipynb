"""
Orchestrates all monitors and writes signals to the database.
Called by the scheduler or manually from the dashboard.
"""
import logging
from datetime import datetime

from meridian import db
from meridian.adapters.pitchbook import PitchbookMonitor
from meridian.monitors.news import NewsMonitor
from meridian.monitors.sec_edgar import SecEdgarMonitor

log = logging.getLogger(__name__)


def run_scan(lookback_days: int = 7) -> dict:
    """Run all monitors. Returns summary counts."""
    db.init_db()
    clients = db.get_clients(active_only=True)
    if not clients:
        return {"clients": 0, "new_signals": 0, "errors": 0}

    monitors = [
        SecEdgarMonitor(lookback_days=lookback_days),
        NewsMonitor(lookback_days=lookback_days),
        PitchbookMonitor(lookback_days=lookback_days),  # no-op if API key not set
    ]

    new_count = 0
    error_count = 0

    for monitor in monitors:
        try:
            for signal in monitor.scan(clients):
                result = db.insert_signal(signal)
                if result:
                    new_count += 1
                    log.info("New signal [%s] %s — %s", signal.signal_type.value, signal.client_name, signal.headline[:60])
        except Exception as e:
            log.error("Monitor %s failed: %s", monitor.name, e)
            error_count += 1

    return {
        "clients": len(clients),
        "new_signals": new_count,
        "errors": error_count,
        "scanned_at": datetime.utcnow().isoformat(),
    }
