"""
TrustIssues.AI - Vendor Dashboard
Clean, simple interface for vendors
"""
import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from styles.app_styles import get_base_css, COLORS
from src import db

# Auth check
if not st.session_state.get('logged_in') or st.session_state.get('role') != 'vendor':
    st.switch_page("pages/login.py")

st.set_page_config(
    page_title="Vendor Dashboard - TrustIssues.AI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(get_base_css(), unsafe_allow_html=True)

# No additional styling needed - using design system

# Header
st.markdown(f"""
<div class="header-bar">
    <h1>📦 Vendor Dashboard</h1>
    <p>Welcome, {st.session_state.get('user_email', 'Vendor')}</p>
</div>
""", unsafe_allow_html=True)

# Logout button below header
col1, col2, col3 = st.columns([3, 1, 1])
with col3:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/login.py")
        st.rerun()

st.markdown("---")

# Initialize
# Tabs
tab1, tab2 = st.tabs(["📤 Upload Document", "📊 My Submissions"])

with tab1:
    st.markdown("### Upload Company Document")
    st.write("Upload your company information PDF for automated verification.")
    
    uploaded_file = st.file_uploader(
        "Choose PDF file",
        type="pdf",
        help="Company registration, profile, or certification"
    )
    
    if uploaded_file:
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.info(f"📄 **{uploaded_file.name}** ({len(uploaded_file.getvalue())/1024:.1f} KB)")
        with col_b:
            if st.button("🚀 Submit", type="primary", use_container_width=True):
                uploads_dir = Path("uploads")
                uploads_dir.mkdir(exist_ok=True)
                
                save_path = uploads_dir / uploaded_file.name
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                submission_id = db.record_submission(
                    uploaded_file.name,
                    str(save_path),
                    submitted_by=st.session_state.get('user_email')
                )
                st.session_state.setdefault("recent_submission_ids", []).append(submission_id)
                
                st.success("✅ Submitted! Check 'My Submissions' tab")
                st.balloons()

with tab2:
    st.markdown("### Your Submissions")
    
    submissions = db.get_recent_submissions(limit=20, submitted_by=st.session_state.get('user_email'))
    
    if submissions:
        for submission in submissions:
            with st.expander(f"📄 {submission['original_filename']}"):
                st.write(f"**Submitted:** {submission.get('submitted_at', '—')}")
                st.write(f"**Status:** {submission.get('status', 'uploaded').replace('_', ' ').title()}")
                if submission.get("vendor_name"):
                    st.write(f"**Detected Company:** {submission['vendor_name']}")
                if submission.get("risk_level"):
                    st.write(f"**Risk Level:** {submission['risk_level'].upper()} ({submission.get('risk_score', '—')})")
                if submission.get("session_id"):
                    if st.button("Open Live Visualization", key=f"viz_{submission['submission_id']}"):
                        st.session_state['selected_session_id'] = submission['session_id']
                        st.switch_page("pages/live_agent_visualization.py")
    else:
        st.info("📭 No submissions yet. Upload a document to get started!")
