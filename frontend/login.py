import streamlit as st
import time

# Authentication Mock Data
USER_CREDENTIALS = {
    "adminuser": {"password": "adminpassword", "role": "admin"},
    "vendoruser": {"password": "vendorpassword", "role": "vendor"},
}

ADMIN_PAGE = "pages/approve-page.py"
VENDOR_PAGE = "pages/vendor.py"

def login_page():
    st.set_page_config(layout="centered", page_title="Eye-Popping Login")

    # --- CSS ---
    st.markdown("""
<style>
/* --- FONT AND BASE TYPOGRAPHY --- */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

html, body, [class*="st-emotion-cache"] {
    font-family: 'Montserrat', sans-serif;
    color: #ffffff; /* Default text color for the background */
}

/* --- STREAMLIT OVERRIDES (Hide Defaults) --- */
#MainMenu { visibility: hidden; }
header { visibility: hidden; }
footer { visibility: hidden; }
div[data-testid="stSidebarNav"] { display: none; }

/* Hide helper text ("Press Enter to submit form") in input fields */
div[data-testid="stTextInput"] label > div:nth-of-type(2),
div[data-testid="stPasswordInput"] label > div:nth-of-type(2) {
    display: none;
}

/* --- BACKGROUND & ANIMATION (From Login Page) --- */
.stApp {
    /* Eye-popping background gradient */
    background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* --- GLOBAL FORM/CONTAINER STYLES (Targeting the centered login form container) --- */
/* Note: We use the most generic cache selector for the container if possible */
.login-container, 
/* Specific targeting for the central block where content sits (from login page) */
div[data-testid="stVerticalBlock"] > div > div:nth-child(2) {
    background-color: rgba(0, 0, 0, 0.4);
    padding: 40px;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    max-width: 500px;
    margin: 50px auto;
}

/* Reset for the main app pages where content is wide */
.stApp > header + div {
    max-width: none !important; /* Allow content to span full width */
}

/* --- INPUT FIELDS (Text/Password) --- */
div[data-testid="stTextInput"] > div > div, 
div[data-testid="stPasswordInput"] > div > div {
    background-color: rgba(255, 255, 255, 0.1);
    color: #e0e0e0;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    padding: 10px 15px;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
}

div[data-testid="stTextInput"] > div > div:focus-within, 
div[data-testid="stPasswordInput"] > div > div:focus-within {
    border-color: #fdbb2d;
    box-shadow: 0 0 0 0.2rem rgba(253, 187, 45, 0.25);
}

div[data-testid="stForm"] label {
     color: #e0e0e0 !important; /* Ensure form labels are white */
}


/* --- BUTTONS (Login Button, etc.) --- */
div[data-testid="stFormSubmitButton"] button, 
div[data-testid="stButton"] button {
    width: 100%;
    padding: 12px 20px;
    border-radius: 8px;
    border: none;
    /* Gradient for primary action buttons */
    background-image: linear-gradient(to right, #fdbb2d 0%, #22c1c3 100%);
    color: white;
    font-size: 1.1em;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    margin-top: 20px;
}

div[data-testid="stFormSubmitButton"] button:hover, 
div[data-testid="stButton"] button:hover {
    background-image: linear-gradient(to right, #22c1c3 0%, #fdbb2d 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}


/* --- HEADERS --- */
h1 {
    color: #f0f2f6;
    text-align: center;
    margin-bottom: 30px;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
}
h2, h3, h4 {
    color: #f0f0f6; /* Ensure all headers are visible white */
    text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
}


/* --- INFO/SUCCESS/ERROR BOXES (Alerts) --- */
div[data-testid="stAlert"] {
    border-radius: 8px;
    padding: 10px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

    # --- Login Form ---
    st.title("Welcome Back! 👋")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("login_form", clear_on_submit=False):
            st.subheader("Sign In")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button("Login")

            if submitted:
                
                user_info = USER_CREDENTIALS.get(username)

                if user_info and user_info["password"] == password:
                    # 1. Set Session State variables
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = user_info["role"]

                    st.success(f"Login Successful! Redirecting as {user_info['role']}...")
                    time.sleep(1) # Visual delay for the user

                    # 2. Perform Role-Based Redirection
                    if st.session_state["role"] == "admin":
                        st.switch_page(ADMIN_PAGE) # Redirect to pages/approve-page.py
                    elif st.session_state["role"] == "vendor":
                        st.switch_page(VENDOR_PAGE) # Redirect to pages/vendor.py
                    # st.switch_page stops execution
                else:
                    st.error("Invalid Username or Password")

if __name__ == "__main__":

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

        st.session_state["role"] = None 
    if st.session_state["logged_in"]:
        
        role = st.session_state["role"]

        if role == "admin":
            st.switch_page(ADMIN_PAGE)
        elif role == "vendor":
            st.switch_page(VENDOR_PAGE)
        else:
            st.error("Invalid session state. Logging out.")
            st.session_state["logged_in"] = False
            st.rerun()

    else:
        login_page()