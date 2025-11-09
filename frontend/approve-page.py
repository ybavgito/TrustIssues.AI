import urllib
import streamlit as st
from datetime import datetime

st.markdown("""
<style>
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="TrustIssues AI Approvals", layout="wide")

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

/* --- Navbar --- */
.navbar {
    background: linear-gradient(90deg, #0FB5A8, #056D63); /* Your brand's teal */
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
    color: white;
    margin-bottom: 25px;
}

/* --- Cards & Containers --- */
.card {
    background-color: #1f2937; /* Lighter than BG for depth */
    border-radius: 10px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    border: 1px solid #374151; /* Subtle border */
    /* NOTE: Risk colors are applied below */
}

/* --- Text & Headings --- */
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF; /* Bright white for headers */
}
p, label, .st-write, .st-markdown {
     color: #F3F4F6; /* Light gray for body text */
}

/* --- Selectbox (Sort) --- */
div[data-testid="stSelectbox"] label {
    color: #9CA3AF !important; /* Lighter label color */
}
div[data-testid="stSelectbox"] div[data-testid="stMarkdownContainer"] {
    background-color: #374151; /* Dark input BG */
    color: #F3F4F6;
    border: 1px solid #4B5563;
    border-radius: 8px;
}

/* --- Buttons --- */
.stButton > button {
    background: linear-gradient(90deg, #0FB5A8, #056D63);
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #056D63, #0FB5A8);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(5, 109, 99, 0.3);
}
.stButton > button:focus {
    box-shadow: 0 0 0 0.2rem rgba(15, 181, 168, 0.5) !important;
}

/* --- Risk/Status Card Styles --- */
.high-priority {
    background-color: rgba(244, 67, 54, 0.05); /* Faint red BG */
    border-left: 5px solid #F44336; /* Red */
}
.pending {
    background-color: rgba(255, 152, 0, 0.05); /* Faint orange BG */
    border-left: 5px solid #FF9800; /* Orange */
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="navbar">RiskLens AI - Approvals Dashboard</div>', unsafe_allow_html=True)


sort_by = st.selectbox("Sort approvals by:", ["Risk Score (high → low)", "Last Submission (recent → old)"])

if 'approvals' not in st.session_state:
    st.session_state.approvals = [
        {"case_id": "RL-2025-0045", "vendor": "ABCD Logistics", "risk_score": 72,
         "assigned_to": "alice@company.com", "status": "Awaiting Approval", "last_submission": "2025-11-07 14:20"},
        {"case_id": "RL-2025-0046", "vendor": "Dart Transport", "risk_score": 35,
         "assigned_to": "bob@company.com", "status": "Awaiting Approval", "last_submission": "2025-11-06 09:15"},
        {"case_id": "RL-2025-0047", "vendor": "Gamma Supplies", "risk_score": 18,
         "assigned_to": "charlie@company.com", "status": "Approved", "last_submission": "2025-11-05 11:00"},
         {"case_id": "RL-2025-0048", "vendor": "HackUTD Logistics", "risk_score": 78,
         "assigned_to": "charlie@company.com", "status": "Awaiting Approval", "last_submission": "2025-11-07 11:00"},
         {"case_id": "RL-2025-0049", "vendor": "Hexa Logistics", "risk_score": 62,
         "assigned_to": "charlie@company.com", "status": "Awaiting Approval", "last_submission": "2025-11-05 13:00"}
    ]

approvals = st.session_state.approvals

for a in approvals:
    a["last_submission_dt"] = datetime.strptime(a["last_submission"], "%Y-%m-%d %H:%M")

high_priority = [a for a in approvals if a["risk_score"] >= 60]
pending_approvals = [a for a in approvals if a not in high_priority]

# Sorting logic
if sort_by == "Risk Score (high → low)":
    approvals_sorted = sorted(pending_approvals, key=lambda x: x["risk_score"], reverse=True)
else:
    approvals_sorted = sorted(pending_approvals, key=lambda x: x["last_submission_dt"], reverse=True)

# --- Navigation Function ---
def navigate_to_vendor(case_id):
   st.session_state["case_id"] = case_id
   st.switch_page("frontend/pages/vendor-info.py")


# --- Corrected display_cards function for approval-page.py ---
def display_cards(data, is_high_priority=False):
    cols_per_row = 3
    for i in range(0, len(data), cols_per_row):
        cols = st.columns(cols_per_row)
        for idx, approval in enumerate(data[i:i+cols_per_row]):
            col = cols[idx]
            card_class = "high-priority" if is_high_priority else "pending"
            
            # Only display items awaiting approval
            if approval['status'] != 'Awaiting Approval':
                 continue
                 
            with col:
                # 1. Use st.container() to hold the card's content
                with st.container():
                    
                    # 2. Start the HTML card container and all its content (excluding the button)
                    st.markdown(
                        f"""
                        <div class="card {card_class}">
                            <h4>{approval['vendor']}</h4>
                            <p><b>Case ID:</b> {approval['case_id']}</p>
                            <p><b>Risk Score:</b> {approval['risk_score']}</p>
                            <p><b>Last Submission:</b> {approval['last_submission']}</p>
                            <p><b>Assigned To:</b> {approval['assigned_to']}</p>
                            <p><b>Status:</b> {approval['status']}</p>
                        """, unsafe_allow_html=True
                    )
                    
                    # 3. Render the Streamlit button. It is now logically and visually inside the card.
                    if st.button("View Details", key=f"details_{approval['case_id']}"):
                        navigate_to_vendor(approval['case_id'])

                    # 4. Close the HTML card container immediately after the button renders
                    st.markdown("</div>", unsafe_allow_html=True) 

            
# Filter only 'Awaiting Approval' for display
high_priority_display = [a for a in high_priority if a['status'] == 'Awaiting Approval']
pending_display = [a for a in approvals_sorted if a['status'] == 'Awaiting Approval']

if high_priority_display:
    st.subheader("High Priority Approvals")
    display_cards(high_priority_display, is_high_priority=True)

if pending_display:
    st.subheader("Pending Approvals")
    display_cards(pending_display, is_high_priority=False)