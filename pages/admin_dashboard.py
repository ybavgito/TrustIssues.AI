"""
TrustIssues.AI - Admin Dashboard
Stats overview and navigation to approvals
"""
import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from styles.app_styles import get_base_css, COLORS
from src import db

# Auth check
if not st.session_state.get('logged_in') or st.session_state.get('role') != 'admin':
    st.switch_page("pages/login.py")

st.set_page_config(
    page_title="Admin Dashboard - TrustIssues.AI",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(get_base_css(), unsafe_allow_html=True)

# Hide navigation
st.markdown("""
<style>
[data-testid="stSidebarNav"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-bar">
    <h1>🔐 Admin Dashboard</h1>
    <p>System overview and statistics</p>
</div>
""", unsafe_allow_html=True)

# Logout button in corner
col1, col2, col3 = st.columns([5, 1, 1])
with col3:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/login.py")
        st.rerun()

st.markdown("---")

# Get stats from database
stats = db.get_stats()

# Main stats display
st.markdown("### 📊 System Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Submissions",
        value=stats['total'],
        help="All vendor submissions"
    )

with col2:
    st.metric(
        label="Pending Review",
        value=stats['pending_review'],
        delta="Awaiting decision",
        help="Submissions that need human review"
    )

with col3:
    st.metric(
        label="Approved",
        value=stats['approved'],
        delta="✅",
        help="Approved vendors"
    )

with col4:
    if stats['avg_risk'] is not None:
        st.metric(
            label="Average Risk Score",
            value=f"{stats['avg_risk']:.0f}/100",
            help="Average risk across all submissions"
        )
    else:
        st.metric(
            label="Average Risk Score",
            value="N/A"
        )

st.markdown("---")

# Recent submissions preview
st.markdown("### 📋 Recent Submissions")

recent = db.get_recent_submissions(limit=5)

if recent:
    for submission in recent:
        with st.expander(f"📄 {submission['vendor_name'] or submission['original_filename']} - {submission['status'].replace('_', ' ').title()}"):
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.write(f"**File:** {submission['original_filename']}")
                st.write(f"**Submitted by:** {submission['submitted_by'] or 'Unknown'}")
            
            with col_b:
                st.write(f"**Status:** {submission['status'].replace('_', ' ').title()}")
                if submission['risk_score'] is not None:
                    risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(submission['risk_level'], '⚪')
                    st.write(f"**Risk:** {risk_emoji} {submission['risk_level'].upper()} ({submission['risk_score']})")
            
            with col_c:
                st.write(f"**Submitted:** {submission['submitted_at']}")
                if submission['processed_at']:
                    st.write(f"**Processed:** {submission['processed_at']}")
else:
    st.info("No submissions yet")

st.markdown("---")

# Main action button
st.markdown("### 🎯 Next Actions")

col_action1, col_action2 = st.columns(2)

with col_action1:
    if st.button("📋 Review Pending Submissions", type="primary", use_container_width=True):
        st.switch_page("pages/approvals.py")
        st.rerun()

with col_action2:
    st.info(f"**{stats['pending_review']} submissions** awaiting your review")
