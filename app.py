"""
Meridian — Client Intelligence Monitor
Perkins Coie Business Development

Run with:  streamlit run app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from meridian import db
from meridian.models import SignalType, SIGNAL_COLOR
from meridian.scanner import run_scan

st.set_page_config(
    page_title="Client Intelligence | Perkins Coie BD",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Init DB and auto-seed demo data on first run ---
db.init_db()
if not db.get_clients():
    from meridian.seed_clients import seed
    from meridian.seed_signals import seed_demo_signals
    seed()
    seed_demo_signals()

# --- Styles ---
st.markdown("""
<style>
    .signal-card {
        border-left: 4px solid #ccc;
        padding: 12px 16px;
        margin-bottom: 10px;
        border-radius: 4px;
        background: #1e1e2e;
    }
    .signal-headline { font-size: 1.0rem; font-weight: 600; margin-bottom: 4px; }
    .signal-meta { font-size: 0.78rem; color: #aaa; }
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .priority-1 { background: #e74c3c22; color: #e74c3c; border: 1px solid #e74c3c44; }
    .priority-2 { background: #e67e2222; color: #e67e22; border: 1px solid #e67e2244; }
    .priority-3 { background: #3498db22; color: #3498db; border: 1px solid #3498db44; }
    .priority-4 { background: #7f8c8d22; color: #7f8c8d; border: 1px solid #7f8c8d44; }
</style>
""", unsafe_allow_html=True)


# === SIDEBAR ===
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Perkins_Coie_logo.svg/320px-Perkins_Coie_logo.svg.png", width=180)
    st.markdown("## ⚖️ Meridian")
    st.caption("Client Intelligence Monitor")
    st.divider()

    # Scan controls
    st.markdown("### Scan Controls")
    lookback = st.slider("Lookback window (days)", 1, 30, 7)
    if st.button("🔍 Run Scan Now", use_container_width=True, type="primary"):
        with st.spinner("Scanning monitors…"):
            result = run_scan(lookback_days=lookback)
        st.success(f"Found **{result['new_signals']}** new signals across {result['clients']} clients.")

    st.divider()

    # Filters
    st.markdown("### Filters")
    clients = db.get_clients()
    client_names = ["All Clients"] + [c.name for c in clients]
    selected_client_name = st.selectbox("Client", client_names)
    selected_client = next((c for c in clients if c.name == selected_client_name), None)

    all_signal_types = list(SignalType)
    selected_types = st.multiselect(
        "Signal Types",
        options=[t.value for t in all_signal_types],
        default=[t.value for t in all_signal_types],
    )
    selected_type_enums = [t for t in all_signal_types if t.value in selected_types]

    show_dismissed = st.checkbox("Show dismissed", value=False)
    st.divider()

    unread = db.get_unread_count()
    st.metric("Unread Signals", unread)

    if st.button("Seed Sample Clients", use_container_width=True):
        from meridian.seed_clients import seed
        seed()
        st.success("Sample clients loaded.")
        st.rerun()


# === MAIN PANEL ===
col_title, col_stats = st.columns([3, 1])
with col_title:
    st.title("Client Intelligence Feed")
    st.caption(f"Last refreshed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")

# Fetch signals
signals = db.get_signals(
    client_id=selected_client.id if selected_client else None,
    signal_types=selected_type_enums if selected_type_enums else None,
    include_dismissed=show_dismissed,
    limit=300,
)

# --- Summary metrics ---
counts = db.get_signal_counts()
total = sum(counts.values())

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Signals", total)
m2.metric("GC Changes", counts.get(SignalType.GC_CHANGE.value, 0))
m3.metric("M&A Activity", counts.get(SignalType.MA_ACTIVITY.value, 0))
m4.metric("IPO Filings", counts.get(SignalType.IPO_FILING.value, 0))
m5.metric("Funding Rounds", counts.get(SignalType.FUNDING_ROUND.value, 0))

st.divider()

# --- Chart + Feed layout ---
chart_col, feed_col = st.columns([1, 2])

with chart_col:
    st.subheader("Signal Breakdown")
    if counts:
        df_chart = pd.DataFrame([
            {"Type": k, "Count": v, "Color": SIGNAL_COLOR.get(SignalType(k), "#7f8c8d")}
            for k, v in counts.items()
        ]).sort_values("Count", ascending=False)
        fig = px.bar(
            df_chart, x="Count", y="Type", orientation="h",
            color="Type",
            color_discrete_map={row["Type"]: row["Color"] for _, row in df_chart.iterrows()},
        )
        fig.update_layout(showlegend=False, height=350, margin=dict(l=0, r=0, t=10, b=0),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#ccc")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No signals yet — run a scan.")

    # Client leaderboard
    if signals:
        st.subheader("Top Clients by Signal Volume")
        from collections import Counter
        client_counts = Counter(s.client_name for s in signals)
        df_clients = pd.DataFrame(client_counts.most_common(10), columns=["Client", "Signals"])
        st.dataframe(df_clients, hide_index=True, use_container_width=True)

with feed_col:
    st.subheader(f"Signal Feed {'— ' + selected_client_name if selected_client else ''}")

    if not signals:
        st.info("No signals match your filters. Try running a scan or adjusting filters.")
    else:
        for sig in signals:
            color = SIGNAL_COLOR.get(sig.signal_type, "#7f8c8d")
            priority_class = f"priority-{sig.priority}"
            pub_str = sig.published_at.strftime("%b %d, %Y") if sig.published_at else "—"
            unread_dot = "🔵 " if not sig.is_read else ""

            st.markdown(f"""
<div class="signal-card" style="border-left-color: {color};">
  <div class="signal-headline">{unread_dot}{sig.headline}</div>
  <div style="margin: 4px 0;">
    <span class="badge {priority_class}">{sig.signal_type.value}</span>
    <span class="badge" style="background:#ffffff11;color:#ccc;border:1px solid #ffffff22">{sig.client_name}</span>
  </div>
  <div class="signal-meta">{sig.summary[:200]}{"…" if len(sig.summary) > 200 else ""}</div>
  <div class="signal-meta" style="margin-top:6px;">
    📰 {sig.source_name} &nbsp;|&nbsp; 📅 {pub_str}
    {f'&nbsp;|&nbsp; <a href="{sig.source_url}" target="_blank" style="color:#5dade2">View source ↗</a>' if sig.source_url else ''}
  </div>
</div>
""", unsafe_allow_html=True)

            action_cols = st.columns([1, 1, 4])
            with action_cols[0]:
                if st.button("Mark read", key=f"read_{sig.id}", use_container_width=True):
                    db.mark_read(sig.id)
                    st.rerun()
            with action_cols[1]:
                if st.button("Dismiss", key=f"dismiss_{sig.id}", use_container_width=True):
                    db.mark_dismissed(sig.id)
                    st.rerun()
