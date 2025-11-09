"""
TrustIssues.AI - Main Application Entry Point
Redirects to login page
"""
import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Page config
st.set_page_config(
    page_title="TrustIssues.AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Check if user is logged in
if not st.session_state.get('logged_in'):
    # Redirect to login
    st.switch_page("pages/login.py")
    st.rerun()
else:
    # Redirect to appropriate dashboard based on role
    if st.session_state.get('role') == 'admin':
        st.switch_page("pages/admin_dashboard.py")
        st.rerun()
    else:
        st.switch_page("pages/vendor_dashboard.py")
        st.rerun()

