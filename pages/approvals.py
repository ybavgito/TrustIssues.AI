"""
TrustIssues.AI - Approvals Page
Review client submissions, process with AI, and approve/reject
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
from src.agent import RiskLensAgent
from src.state_manager import StateManager

# Auth check
if not st.session_state.get('logged_in') or st.session_state.get('role') != 'admin':
    st.switch_page("pages/login.py")

st.set_page_config(
    page_title="Approvals - TrustIssues.AI",
    page_icon="📋",
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
    <h1>📋 Pending Approvals</h1>
    <p>Review and process client submissions</p>
</div>
""", unsafe_allow_html=True)

# Navigation buttons
col1, col2, col3 = st.columns([4, 1, 1])
with col2:
    if st.button("🏠 Dashboard", use_container_width=True):
        st.switch_page("pages/admin_dashboard.py")
        st.rerun()
with col3:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/login.py")
        st.rerun()

st.markdown("---")

# Get pending submissions
pending_submissions = db.get_pending_submissions()

if not pending_submissions:
    st.info("🎉 No pending submissions! All caught up.")
    if st.button("⬅️ Back to Dashboard"):
        st.switch_page("pages/admin_dashboard.py")
else:
    st.markdown(f"### {len(pending_submissions)} Submission(s) Awaiting Review")
    
    # Display submissions as cards
    for submission in pending_submissions:
        with st.container():
            # Card styling
            risk_color = COLORS['warning'] if submission['risk_level'] == 'medium' else (
                COLORS['danger'] if submission['risk_level'] == 'high' else COLORS['success']
            ) if submission['risk_level'] else COLORS['text_secondary']
            
            st.markdown(f"""
            <div style="
                background: white;
                border-left: 4px solid {risk_color};
                padding: 20px;
                border-radius: 8px;
                margin: 15px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <h3 style="margin: 0 0 10px 0;">{submission['vendor_name'] or submission['original_filename']}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**File:** {submission['original_filename']}")
                st.write(f"**Submitted by:** {submission['submitted_by'] or 'Unknown'}")
            
            with col2:
                st.write(f"**Submitted:** {submission['submitted_at']}")
                st.write(f"**Status:** {submission['status'].replace('_', ' ').title()}")
            
            with col3:
                if submission['risk_score'] is not None:
                    risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(submission['risk_level'], '⚪')
                    st.write(f"**Risk Level:** {risk_emoji} {submission['risk_level'].upper()}")
                    st.write(f"**Risk Score:** {submission['risk_score']}/100")
                else:
                    st.write("**Risk:** Not processed yet")
            
            with col4:
                # Action buttons
                if submission['session_id']:
                    # Already processed - show visualization
                    if st.button("🤖 View Live Visualization", key=f"viz_{submission['submission_id']}", use_container_width=True):
                        st.session_state['selected_session_id'] = submission['session_id']
                        st.session_state['current_submission_id'] = submission['submission_id']
                        st.switch_page("pages/live_agent_visualization.py")
                        st.rerun()
                else:
                    # Not processed yet - offer to process
                    if st.button("🚀 Process with AI Agents", key=f"process_{submission['submission_id']}", type="primary", use_container_width=True):
                        # Store processing info and immediately redirect to live viz
                        st.session_state['process_pdf_path'] = submission['pdf_path']
                        st.session_state['current_submission_id'] = submission['submission_id']
                        st.switch_page("pages/live_agent_visualization.py")
                        st.rerun()
            
            # Approval/rejection buttons if processed
            if submission['session_id'] and submission['status'] == 'pending_review':
                col_a, col_b, col_c = st.columns([1, 1, 4])
                
                with col_a:
                    if st.button("✅ Approve", key=f"approve_{submission['submission_id']}", use_container_width=True):
                        db.mark_submission_status(submission['submission_id'], 'approved')
                        st.success("✅ Approved!")
                        st.rerun()
                
                with col_b:
                    if st.button("❌ Reject", key=f"reject_{submission['submission_id']}", use_container_width=True):
                        db.mark_submission_status(submission['submission_id'], 'rejected')
                        st.warning("❌ Rejected")
                        st.rerun()
            
            st.markdown("---")
