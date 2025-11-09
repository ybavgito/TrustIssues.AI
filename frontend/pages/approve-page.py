import urllib
import streamlit as st
from datetime import datetime

st.markdown("""
<style>
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="RiskLens AI Approvals", layout="wide")

st.markdown("""
<style>
/* --- 0. CRITICAL STREAMLIT OVERRIDES --- */

/* Remove default padding/margin on Streamlit containers in the column */
div[data-testid*="stVerticalBlock"] > div:first-child > div:nth-child(2) {
    margin-bottom: 0px !important;
    padding-bottom: 0px !important;
}

/* --- 1. GENERAL LAYOUT (Dark Mode) --- */
body {
    /* Dark background gradient */
    background: linear-gradient(to right, #121212, #1e1e1e);
    color: #f0f0f0; /* Default text color for dark mode */
}
.navbar {
    /* Retain original accent color for a striking title bar */
    background: linear-gradient(90deg, #0FB5A8, #056D63);
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
    color: white;
    margin-bottom: 25px;
}
h3 {
    color: #f0f0f0; /* Ensure Streamlit subheaders are visible */
}

/* --- 2. PREMIUM CARD STYLES --- */
.card {
    /* Card background: Darker shade of gray for depth */
    background-color: #2a2a2a; 
    border-radius: 16px;      /* Softer, more premium corner radius */
    padding: 25px;            /* Increased padding for an airy feel */
    margin-bottom: 30px;      /* Generous bottom margin to separate cards */
    
    /* Deep, soft, multi-layer shadow for a "floating" effect */
    box-shadow: 
        0 10px 30px rgba(0, 0, 0, 0.3), /* Deeper shadow on dark background */
        0 4px 8px rgba(0, 0, 0, 0.2); 
    
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); /* Smooth, premium transition */
    cursor: pointer;
    border: 1px solid #444444; /* Subtle separation border */
}

/* Hover effect: Card lifts and shadow deepens */
.card:hover {
    transform: translateY(-8px); 
    box-shadow: 
        0 20px 40px rgba(0, 0, 0, 0.5),
        0 8px 16px rgba(0, 0, 0, 0.3); 
}

/* --- 3. PRIORITY COLOR SCHEME (Mauve/Teal) --- */

/* High Priority: Mauve/Crimson for urgency */
.high-priority {
    background: linear-gradient(135deg, #302638, #3e284a); /* Dark Mauve gradient */
    border-left: 8px solid #cc4499; /* Bright Mauve/Pink bar */
}

/* Pending: Deep Teal for standard action items */
.pending {
    background: linear-gradient(135deg, #243635, #2c4240); /* Deep Teal gradient */
    border-left: 8px solid #009688; /* Strong Teal bar */
}

/* --- 4. CONTENT TYPOGRAPHY --- */

.card h4 {
    color: #ffffff; /* White title for contrast */
    font-size: 1.5em;
    margin-top: 0;
    margin-bottom: 15px;
    padding-bottom: 8px;
    border-bottom: 1px solid #444444; /* Darker separator line */
}
.card p {
    color: #cccccc; /* Light gray body text */
    font-size: 0.95em;
    line-height: 1.8;
    margin-bottom: 5px;
}
.card p b {
    color: #eeeeee; /* Brighter label text */
    display: inline-block;
    min-width: 120px; 
    font-weight: 600;
}

/* --- 5. BUTTON INTEGRATION (The Fix for Visual Placement) --- */

/* Targets the Streamlit button element within the card area */
/* This selector is complex but necessary for Streamlit specificity */
.card + div > div > div > button {
    /* Button appearance */
    background-color: #0FB5A8; 
    color: white;
    font-weight: bold;
    border-radius: 8px;
    padding: 10px 15px;
    width: 100%; /* Make button span the width of the card interior */
}

/* Remove surrounding margins that push the button outside */
.card + div {
    /* Adjusts the space between the card's closing DIV and the button's container */
    margin-top: -15px !important; 
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

/* Ensure button text is readable */
.card + div > div > div > button p {
    color: white !important;
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

   st.switch_page("pages/vendor-info.py")


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