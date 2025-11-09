"""
TrustIssues.AI - Login Page
Clean, professional design with working login
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

st.set_page_config(
    page_title="Login - TrustIssues.AI",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Apply consistent styling
st.markdown(get_base_css(), unsafe_allow_html=True)

# Additional login-specific CSS
st.markdown(f"""
<style>
.login-container {{
    max-width: 400px;
    margin: 60px auto;
}}

.logo {{
    text-align: center;
    font-size: 48px;
    margin-bottom: 8px;
}}

.app-title {{
    text-align: center;
    font-size: 24px;
    font-weight: 600;
    color: {COLORS['text']};
    margin-bottom: 8px;
}}

.app-subtitle {{
    text-align: center;
    font-size: 14px;
    color: {COLORS['text_secondary']};
    margin-bottom: 32px;
}}
</style>
""", unsafe_allow_html=True)

# Logo and title
st.markdown('<div class="logo">🛡️</div>', unsafe_allow_html=True)
st.markdown('<div class="app-title">TrustIssues.AI</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Agentic Vendor Onboarding</div>', unsafe_allow_html=True)

# Role selection with clean buttons
st.markdown("### Select Role")
col1, col2 = st.columns(2)

# Initialize role state
if 'login_role' not in st.session_state:
    st.session_state['login_role'] = 'vendor'

with col1:
    if st.button(
        "📦 Vendor/Client", 
        use_container_width=True,
        type="primary" if st.session_state.get('login_role') == 'vendor' else "secondary"
    ):
        st.session_state['login_role'] = 'vendor'
        st.rerun()

with col2:
    if st.button(
        "🔐 Admin",
        use_container_width=True,
        type="primary" if st.session_state.get('login_role') == 'admin' else "secondary"
    ):
        st.session_state['login_role'] = 'admin'
        st.rerun()

st.markdown("---")

# Login form based on role
role = st.session_state.get('login_role', 'vendor')

if role == 'vendor':
    st.markdown("### 📦 Vendor Login")
    
    email = st.text_input("Email", value="vendor@company.com", key="v_email")
    password = st.text_input("Password", type="password", value="demo", key="v_pass")
    
    if st.button("Login", type="primary", use_container_width=True, key="v_login"):
        if email and password:
            st.session_state['logged_in'] = True
            st.session_state['role'] = 'vendor'
            st.session_state['user_email'] = email
            st.success("✅ Login successful!")
            st.balloons()
            st.switch_page("pages/vendor_dashboard.py")
            st.rerun()
        else:
            st.error("❌ Please enter email and password")

else:
    st.markdown("### 🔐 Admin Login")
    
    email = st.text_input("Email", value="admin@trustissues.ai", key="a_email")
    password = st.text_input("Password", type="password", value="admin", key="a_pass")
    
    if st.button("Login", type="primary", use_container_width=True, key="a_login"):
        if email and password:
            st.session_state['logged_in'] = True
            st.session_state['role'] = 'admin'
            st.session_state['user_email'] = email
            st.success("✅ Login successful!")
            st.balloons()
            st.switch_page("pages/admin_dashboard.py")
            st.rerun()
        else:
            st.error("❌ Please enter email and password")

st.markdown("---")
with st.expander("ℹ️ Demo Info"):
    st.caption("Any email and password will work for demo purposes")
    st.caption("Default credentials are pre-filled - just click Login!")
