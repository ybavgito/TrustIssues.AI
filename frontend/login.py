import streamlit as st

def login_page():
    st.set_page_config(layout="centered", page_title="Eye-Popping Login")

    # --- CSS ---
    st.markdown("""
        <style>
        /* --- Google Font --- */
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

        /* --- Base Theme --- */
        html, body, [class*="st-emotion-cache"] {
            font-family: 'Montserrat', sans-serif;
        }
        
        .stApp {
            background: linear-gradient(135deg, #111827, #1f2937); /* Dark slate gradient */
            color: #F3F4F6; /* Light primary text for legibility */
        }

        /* --- Hide Streamlit Chrome --- */
        #MainMenu { visibility: hidden; }
        header { visibility: hidden; }
        footer { visibility: hidden; }
        div[data-testid="stSidebarNav"] { display: none; } /* Hide sidebar for login page */

        /* --- Hide "Press Enter" helper text --- */
        div[data-testid="stTextInput"] label > div:nth-of-type(2),
        div[data-testid="stPasswordInput"] label > div:nth-of-type(2) {
            display: none;
        }

        /* --- Login Container (mimics .card) --- */
        /* This targets the container holding the form */
        .st-emotion-cache-1pxazr7 { 
            background-color: #1f2937; /* Lighter than BG for depth */
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid #374151; /* Subtle border */
            max-width: 500px;
            margin: 50px auto;
        }

        /* --- Text & Headings --- */
        h1 {
            color: #FFFFFF; /* Bright white for header */
            text-align: center;
            margin-bottom: 30px;
            text-shadow: none;
        }
        h3, p, label, .st-write, .st-markdown, .st-emotion-cache-vk336y label {
             color: #F3F4F6 !important; /* Light gray for body text */
        }

        /* --- Inputs (Text, Password) --- */
        div[data-testid="stTextInput"] label,
        div[data-testid="stPasswordInput"] label {
            color: #9CA3AF !important; /* Lighter label color */
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stPasswordInput"] input {
            background-color: #374151; /* Dark input BG */
            color: #F3F4F6;
            border: 1px solid #4B5563;
            border-radius: 8px;
        }
        
        /* --- Login Button --- */
        div[data-testid="stFormSubmitButton"] > button {
            width: 100%;
            background: linear-gradient(90deg, #0FB5A8, #056D63);
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            padding: 12px 20px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            margin-top: 20px;
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            background: linear-gradient(90deg, #056D63, #0FB5A8);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(5, 109, 99, 0.3);
        }
        div[data-testid="stFormSubmitButton"] > button:focus {
            box-shadow: 0 0 0 0.2rem rgba(15, 181, 168, 0.5) !important;
        }
        
        /* --- Alerts (Success/Error) --- */
        .stAlert {
            border-radius: 8px;
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
                # --- Dummy Authentication ---
                if username == "admin" and password == "password123":
                    st.success("Login Successful! Redirecting...")
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")

# --- Main App Logic ---
if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        st.success("You are logged in!")
        st.write("This is your super secret main app content.")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()
    else:
        login_page()