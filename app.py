"""
Client Radar — BD Intelligence Monitor
Perkins Coie Business Development

Run with:  streamlit run app.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
from datetime import datetime

from radar import db
from radar.models import SignalType, SIGNAL_COLOR
from radar.scanner import run_scan

st.set_page_config(
    page_title="Client Radar | Perkins Coie BD",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Auto-seed on first run
db.init_db()
if not db.get_clients():
    from radar.seed_clients import seed
    from radar.seed_signals import seed_demo_signals
    seed()
    seed_demo_signals()

st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #0d0d1a; }
  [data-testid="stSidebar"] { background: #12122a; }

  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    white-space: nowrap;
  }
  .card {
    background: #16213e;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
    border-left: 5px solid #ccc;
    transition: background 0.2s;
  }
  .card:hover { background: #1a2a50; }
  .card-headline {
    font-size: 1.0rem;
    font-weight: 700;
    color: #f0f0f0;
    margin-bottom: 6px;
    line-height: 1.4;
  }
  .card-summary {
    font-size: 0.85rem;
    color: #b0b8cc;
    line-height: 1.6;
    margin-bottom: 8px;
  }
  .card-insight {
    font-size: 0.82rem;
    color: #7ec8e3;
    font-style: italic;
    margin-bottom: 8px;
  }
  .card-meta {
    font-size: 0.75rem;
    color: #666;
  }
  .card-meta a { color: #5dade2; text-decoration: none; }
  .unread-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #5dade2;
    margin-right: 6px;
    vertical-align: middle;
  }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📡 Client Radar")
    st.caption("Perkins Coie BD Intelligence")
    st.divider()

    st.markdown("### 🔍 Run Scan")
    lookback = st.slider("Days to look back", 1, 30, 7)
    if st.button("Scan Now", use_container_width=True, type="primary"):
        with st.spinner("Scanning..."):
            result = run_scan(lookback_days=lookback)
        if result["new_signals"]:
            st.success(f"**{result['new_signals']}** new signals found")
        else:
            st.info("No new signals")

    st.divider()
    st.markdown("### Filters")

    clients = db.get_clients()
    client_options = ["All Clients"] + [c.name for c in clients]
    selected_client_name = st.selectbox("Client", client_options)
    selected_client = next((c for c in clients if c.name == selected_client_name), None)

    priority_filter = st.multiselect(
        "Signal Priority",
        ["🔴 High (GC Change, M&A, IPO)", "🟠 Medium (Funding, Regulatory)", "🟡 Lower (Leadership, News)"],
        default=["🔴 High (GC Change, M&A, IPO)", "🟠 Medium (Funding, Regulatory)"],
    )
    show_dismissed = st.checkbox("Show dismissed", value=False)

    priority_map = {
        "🔴 High (GC Change, M&A, IPO)": [1],
        "🟠 Medium (Funding, Regulatory)": [2],
        "🟡 Lower (Leadership, News)": [3, 4],
    }
    allowed_priorities = []
    for label in priority_filter:
        allowed_priorities.extend(priority_map[label])

    st.divider()
    unread = db.get_unread_count()
    st.metric("Unread", unread)


# ── HEADER ─────────────────────────────────────────────────
st.markdown("## 📡 Client Radar")
st.caption(f"Perkins Coie Business Development &nbsp;·&nbsp; {datetime.utcnow().strftime('%b %d, %Y %H:%M UTC')}")

# ── METRICS ────────────────────────────────────────────────
counts = db.get_signal_counts()
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Signals", sum(counts.values()))
m2.metric("🔴 GC Changes", counts.get(SignalType.GC_CHANGE.value, 0))
m3.metric("🔴 M&A", counts.get(SignalType.MA_ACTIVITY.value, 0))
m4.metric("🔴 IPOs", counts.get(SignalType.IPO_FILING.value, 0))
m5.metric("🟠 Funding", counts.get(SignalType.FUNDING_ROUND.value, 0))

st.divider()

# ── SIGNAL FEED ────────────────────────────────────────────
signals = db.get_signals(
    client_id=selected_client.id if selected_client else None,
    include_dismissed=show_dismissed,
    limit=300,
)
signals = [s for s in signals if s.priority in allowed_priorities]

# View toggle
view = st.radio("View", ["Cards", "Table"], horizontal=True, label_visibility="collapsed")

if not signals:
    st.info("No signals yet. Hit **Scan Now** in the sidebar.")

elif view == "Table":
    rows = []
    for s in signals:
        summary_parts = s.summary.split("\n\n💼 ")
        summary = summary_parts[0]
        insight = summary_parts[1] if len(summary_parts) > 1 else ""
        rows.append({
            "Client": s.client_name,
            "Signal": s.signal_type.value,
            "What's happening": summary,
            "BD Insight": insight,
            "Date": s.published_at.strftime("%b %d") if s.published_at else "—",
            "Source": s.source_name,
            "URL": s.source_url or "",
        })
    df = pd.DataFrame(rows)
    st.dataframe(
        df[["Client", "Signal", "What's happening", "BD Insight", "Date", "Source"]],
        use_container_width=True,
        hide_index=True,
        height=600,
    )

else:
    for sig in signals:
        color = SIGNAL_COLOR.get(sig.signal_type, "#7f8c8d")
        pub_str = sig.published_at.strftime("%b %d, %Y") if sig.published_at else "—"
        unread_html = '<span class="unread-dot"></span>' if not sig.is_read else ""

        summary_parts = sig.summary.split("\n\n💼 ")
        summary_text = summary_parts[0]
        bd_insight = summary_parts[1] if len(summary_parts) > 1 else ""

        source_link = (
            f'<a href="{sig.source_url}" target="_blank">{sig.source_name} ↗</a>'
            if sig.source_url else sig.source_name
        )

        st.markdown(f"""
<div class="card" style="border-left-color:{color}">
  <div class="card-headline">{unread_html}{sig.headline}</div>
  <span class="badge" style="background:{color}22;color:{color};border:1px solid {color}44">{sig.signal_type.value}</span>
  <span class="badge" style="background:#ffffff0d;color:#aaa;border:1px solid #ffffff1a;margin-left:4px">{sig.client_name}</span>
  <br><br>
  <div class="card-summary">{summary_text}</div>
  {"<div class='card-insight'>💼 " + bd_insight + "</div>" if bd_insight else ""}
  <div class="card-meta">📰 {source_link} &nbsp;·&nbsp; 📅 {pub_str}</div>
</div>
""", unsafe_allow_html=True)

        col1, col2, _ = st.columns([1, 1, 6])
        with col1:
            if st.button("✓ Read", key=f"r{sig.id}", use_container_width=True):
                db.mark_read(sig.id)
                st.rerun()
        with col2:
            if st.button("✕ Dismiss", key=f"d{sig.id}", use_container_width=True):
                db.mark_dismissed(sig.id)
                st.rerun()
