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
from src.state_manager import StateManager

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
                import uuid
                from datetime import datetime
                
                uploads_dir = Path("uploads")
                uploads_dir.mkdir(exist_ok=True)
                
                # Create unique filename to prevent overwrites
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                file_extension = Path(uploaded_file.name).suffix
                file_stem = Path(uploaded_file.name).stem
                unique_filename = f"{timestamp}_{unique_id}_{file_stem}{file_extension}"
                
                save_path = uploads_dir / unique_filename
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                submission_id = db.record_submission(
                    uploaded_file.name,  # Keep original name for display
                    str(save_path),  # But save with unique path
                    submitted_by=st.session_state.get('user_email')
                )
                st.session_state.setdefault("recent_submission_ids", []).append(submission_id)
                
                st.success("✅ Submitted! Check 'My Submissions' tab")

with tab2:
    st.markdown("### Your Submissions")
    
    submissions = db.get_recent_submissions(limit=20, submitted_by=st.session_state.get('user_email'))
    state_manager = StateManager()
    
    if submissions:
        for submission in submissions:
            with st.expander(f"📄 {submission['original_filename']}"):
                st.write(f"**Submitted:** {submission.get('submitted_at', '—')}")
                st.write(f"**Status:** {submission.get('status', 'uploaded').replace('_', ' ').title()}")
                if submission.get("vendor_name"):
                    st.write(f"**Detected Company:** {submission['vendor_name']}")
                if submission.get("risk_level"):
                    st.write(f"**Risk Level:** {submission['risk_level'].upper()} ({submission.get('risk_score', '—')})")
                
                # Load and display access recommendation if available
                if submission.get("session_id"):
                    try:
                        state = state_manager.load_state(submission['session_id'])
                        if state and state.access_recommendation:
                            st.markdown("---")
                            st.markdown("### ✅ Access Level Granted")
                            
                            access_level = state.access_recommendation.access_level
                            access_color = {
                                'standard': '#10b981',
                                'read_only': '#f59e0b',
                                'restricted': '#ef4444'
                            }.get(access_level, '#6366f1')
                            
                            st.markdown(f"""
                            <div style="background: #f0fdf4; border-left: 4px solid {access_color}; padding: 15px; border-radius: 6px; margin: 10px 0;">
                                <div style="margin-bottom: 12px;">
                                    <strong style="color: #065f46; font-size: 16px;">Access Level: {access_level.upper().replace('_', ' ')}</strong>
                                </div>
                                <div style="font-size: 14px; color: #111827; line-height: 1.8;">
                                    <div style="margin-bottom: 8px;">
                                        <strong>Permissions:</strong> {', '.join(state.access_recommendation.permissions)}
                                    </div>
                                    <div style="margin-bottom: 8px;">
                                        <strong>Restrictions:</strong> {', '.join(state.access_recommendation.restrictions) if state.access_recommendation.restrictions else 'None'}
                                    </div>
                                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #e5e7eb;">
                                        <strong>Justification:</strong> {state.access_recommendation.justification}
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    except:
                        pass  # If state doesn't exist or can't be loaded, skip
    else:
        st.info("📭 No submissions yet. Upload a document to get started!")
