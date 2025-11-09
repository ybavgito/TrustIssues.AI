import streamlit as st

def login_page():
    st.set_page_config(layout="centered", page_title="Eye-Popping Login")

    # --- CSS ---
    st.markdown("""
        <style>
        /* --- NEW: Hide "Press Enter to submit form" --- */
        /* This targets the helper text in text_input and password_input */
        div[data-testid="stTextInput"] label > div:nth-of-type(2),
        div[data-testid="stPasswordInput"] label > div:nth-of-type(2) {
            display: none;
        }
        
        /* --- Hide default Streamlit navigation --- */
        #MainMenu { visibility: hidden; }
        header { visibility: hidden; }
        footer { visibility: hidden; }
        div[data-testid="stSidebarNav"] { display: none; }
        
        /* --- Your eye-popping styles from before --- */
        
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

        html, body, [class*="st-emotion-cache"] {
            font-family: 'Montserrat', sans-serif;
            color: #ffffff;
        }

        .stApp {
            background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .st-emotion-cache-1pxazr7 {
            background-color: rgba(0, 0, 0, 0.4);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            max-width: 500px;
            margin: 50px auto;
        }

        h1 {
            color: #f0f2f6;
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
        }

        .st-emotion-cache-v06ymw, .st-emotion-cache-1xw8zd0 {
            background-color: rgba(255, 255, 255, 0.1);
            color: #e0e0e0;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            padding: 10px 15px;
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
        }

        .st-emotion-cache-v06ymw:focus, .st-emotion-cache-1xw8zd0:focus {
            border-color: #fdbb2d;
            box-shadow: 0 0 0 0.2rem rgba(253, 187, 45, 0.25);
        }

        .st-emotion-cache-vk336y button {
            width: 100%;
            padding: 12px 20px;
            border-radius: 8px;
            border: none;
            background-image: linear-gradient(to right, #fdbb2d 0%, #22c1c3 100%);
            color: white;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            margin-top: 20px;
        }

        .st-emotion-cache-vk336y button:hover {
            background-image: linear-gradient(to right, #22c1c3 0%, #fdbb2d 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }

        .st-emotion-cache-nahz7x, .st-emotion-cache-1l02zvs {
            border-radius: 8px;
            padding: 10px;
            margin-top: 20px;
        }

        .st-emotion-cache-vk336y label {
            color: #e0e0e0 !important;
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
                    st.experimental_rerun()
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
            st.experimental_rerun()
    else:
        login_page()