"""
Quantegrity Security Monitoring Dashboard
Real-time security event monitoring and analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from security_manager import security_manager
from shared_state import shared_state

# Page configuration
st.set_page_config(
    page_title="Quantegrity Security Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for security dashboard
st.markdown("""
<style>
    .security-header {
        font-size: 3rem;
        text-align: center;
        color: #DC143C;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .alert-critical {
        background: linear-gradient(135deg, #FF0000 0%, #8B0000 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        border-left: 5px solid #8B0000;
    }
    .alert-high {
        background: linear-gradient(135deg, #FF4500 0%, #FF6347 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        border-left: 5px solid #8B0000;
    }
    .alert-medium {
        background: linear-gradient(135deg, #FFA500 0%, #FFD700 100%);
        padding: 1rem;
        border-radius: 10px;
        color: #333;
        margin: 0.5rem 0;
        border-left: 5px solid #FF8C00;
    }
    .alert-low {
        background: linear-gradient(135deg, #90EE90 0%, #98FB98 100%);
        padding: 1rem;
        border-radius: 10px;
        color: #333;
        margin: 0.5rem 0;
        border-left: 5px solid #32CD32;
    }
    .secure-status {
        background: linear-gradient(135deg, #00FF00 0%, #32CD32 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="security-header">🛡️ Quantegrity Security Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Real-Time Security Monitoring & Threat Analysis</p>', unsafe_allow_html=True)

# Refresh button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔄 Refresh Security Status", use_container_width=True):
        st.rerun()

# Get security status
security_status = security_manager.get_security_status()

# ============================================================================
# SECTION 1: Overall Security Metrics
# ============================================================================

st.markdown("## 📊 System Security Overview")

# Display overall security level
overall_level = security_status.get('overall_level', 'UNKNOWN')

if overall_level == "SECURE":
    st.markdown(f'<div class="secure-status">🟢 SYSTEM SECURE - All metrics normal</div>', unsafe_allow_html=True)
elif overall_level == "LOW":
    st.warning("🟡 LOW THREAT LEVEL - Minor anomalies detected")
elif overall_level == "MEDIUM":
    st.warning("🟠 MEDIUM THREAT LEVEL - Concerning patterns detected")
elif overall_level == "HIGH":
    st.error("🔴 HIGH THREAT LEVEL - Security threshold exceeded")
else:  # CRITICAL
    st.error("🚨 CRITICAL THREAT LEVEL - Immediate action required!")

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Security Events</div>
        <div class="metric-value">{security_status.get('total_events', 0)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Threat Score</div>
        <div class="metric-value">{security_status.get('threat_score', 0)}/100</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Active Sessions</div>
        <div class="metric-value">{security_status.get('seo_ah_sessions', 0)}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    avg_ber = security_status.get('avg_ber', 0.0)
    ber_color = "#00FF00" if avg_ber < 0.05 else "#FFA500" if avg_ber < 0.11 else "#FF0000"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Average BER</div>
        <div class="metric-value" style="color: {ber_color}">{avg_ber:.2%}</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# SECTION 2: Threat Level Distribution
# ============================================================================

st.markdown("## 🎯 Threat Level Distribution")

threat_counts = security_status.get('threat_counts', {})

# Create pie chart
if sum(threat_counts.values()) > 0:
    fig = go.Figure(data=[go.Pie(
        labels=list(threat_counts.keys()),
        values=list(threat_counts.values()),
        marker=dict(colors=['#00FF00', '#90EE90', '#FFA500', '#FF4500', '#8B0000']),
        hole=0.4
    )])
    fig.update_layout(
        title="Security Events by Threat Level",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("✅ No security events recorded yet")

# ============================================================================
# SECTION 3: Recent High-Priority Events
# ============================================================================

st.markdown("## ⚠️ Recent High-Priority Events")

high_priority = security_status.get('high_priority_events', [])

if high_priority:
    for event in high_priority:
        threat_level = event.get('threat_level', 'UNKNOWN')
        css_class = f"alert-{threat_level.lower()}"

        st.markdown(f"""
        <div class="{css_class}">
            <strong>{event.get('event_type', 'UNKNOWN')}</strong> - {threat_level}
            <br><small>Source: {event.get('source', 'unknown')} | Time: {event.get('timestamp', 'N/A')}</small>
            <br>{event.get('description', 'No description')}
        </div>
        """, unsafe_allow_html=True)
else:
    st.success("✅ No high-priority security events")

# ============================================================================
# SECTION 4: Error Correction Statistics
# ============================================================================

st.markdown("## 🔧 Error Correction Statistics")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Total Error Corrections",
        security_status.get('total_error_corrections', 0)
    )

with col2:
    avg_ber = security_status.get('avg_ber', 0.0)
    ber_status = "Excellent" if avg_ber < 0.01 else "Good" if avg_ber < 0.05 else "Fair" if avg_ber < 0.11 else "Poor"
    st.metric(
        "Average BER",
        f"{avg_ber:.4f}",
        delta=ber_status,
        delta_color="normal" if avg_ber < 0.11 else "inverse"
    )

# Get error correction history
ec_stats_list = shared_state.get_error_correction_stats()

if ec_stats_list:
    # Convert to DataFrame
    ec_df = pd.DataFrame([
        {
            'Timestamp': s.timestamp,
            'Voter ID': s.voter_id,
            'Original BER': s.original_ber,
            'Key Length (Before)': s.key_length_before,
            'Key Length (After)': s.key_length_after,
            'Success': '✅' if s.success else '❌'
        }
        for s in ec_stats_list[:20]  # Last 20
    ])

    st.dataframe(ec_df, use_container_width=True)

    # BER trend chart
    if len(ec_stats_list) > 1:
        ber_data = pd.DataFrame([
            {'Timestamp': s.timestamp, 'BER': s.original_ber}
            for s in ec_stats_list
        ])
        fig = px.line(ber_data, x='Timestamp', y='BER', title='BER Trend Over Time')
        fig.add_hline(y=0.11, line_dash="dash", line_color="red", annotation_text="Security Threshold (11%)")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No error correction statistics available yet")

# ============================================================================
# SECTION 5: All Security Events Log
# ============================================================================

st.markdown("## 📜 Complete Security Event Log")

# Filters
col1, col2 = st.columns(2)

with col1:
    filter_level = st.selectbox(
        "Filter by Threat Level",
        ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW", "NONE"]
    )

with col2:
    limit = st.slider("Number of events to show", 10, 100, 50)

# Get events
if filter_level == "All":
    events = shared_state.get_security_events(limit)
else:
    events = shared_state.get_security_events_by_threat_level(filter_level)[:limit]

if events:
    # Convert to DataFrame
    events_df = pd.DataFrame([
        {
            'Time': e.timestamp,
            'Type': e.event_type,
            'Threat Level': e.threat_level,
            'Source': e.source,
            'Description': e.description
        }
        for e in events
    ])

    st.dataframe(events_df, use_container_width=True)

    # Export option
    if st.button("📥 Export Security Log (CSV)"):
        csv = events_df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            "security_log.csv",
            "text/csv",
            key='download-csv'
        )
else:
    st.info("No security events match the selected filters")

# ============================================================================
# SECTION 6: System Actions
# ============================================================================

st.markdown("## 🔧 System Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🧹 Cleanup Expired Sessions", use_container_width=True):
        security_manager.cleanup_expired_sessions()
        st.success("✅ Expired sessions cleaned up")
        st.rerun()

with col2:
    if st.button("🔄 Reset IDS History (Testing)", use_container_width=True):
        security_manager.reset_ids_history()
        st.success("✅ IDS history reset")
        st.rerun()

with col3:
    st.markdown(f"""
    **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """)

# Footer
st.markdown("---")
st.markdown("""
<p style="text-align: center; color: #666;">
    🛡️ Quantegrity Security Dashboard | Real-time monitoring with quantum-enhanced security
</p>
""", unsafe_allow_html=True)
