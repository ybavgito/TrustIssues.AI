import random
import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Vendor Info", layout="wide")

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
.high-risk {
    background-color: rgba(244, 67, 54, 0.05); /* Faint red BG */
    border-left: 5px solid #F44336; /* Red */
}
.medium-risk {
    background-color: rgba(255, 152, 0, 0.05); /* Faint orange BG */
    border-left: 5px solid #FF9800; /* Orange */
}
.low-risk {
    background-color: rgba(76, 175, 80, 0.05); /* Faint green BG */
    border-left: 5px solid #4CAF50; /* Green */
}

/* --- Alerts (Info) --- */
.stAlert {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)


if 'approvals' not in st.session_state:
    st.session_state.approvals = [
        {"case_id": "RL-2025-0045", "vendor": "ABCD Logistics", "risk_score": 72,
         "assigned_to": "alice@company.com", "status": "Awaiting Approval", "last_submission": "2025-11-07 14:20"},
        {"case_id": "RL-2025-0046", "vendor": "Dart Transport", "risk_score": 35,
         "assigned_to": "bob@company.com", "status": "Awaiting Approval", "last_submission": "2025-11-06 09:15"},
        {"case_id": "RL-2025-0047", "vendor": "Gamma Supplies", "risk_score": 18,
         "assigned_to": "charlie@company.com", "status": "Awaiting Approval", "last_submission": "2025-11-05 11:00"},
        {"case_id": "RL-2025-0048", "vendor": "HackUTD Logistics", "risk_score": 78,
         "assigned_to": "charlie@company.com", "status": "Awaiting Approval", "last_submission": "2025-11-07 11:00"},
        {"case_id": "RL-2025-0049", "vendor": "Hexa Logistics", "risk_score": 62,
         "assigned_to": "charlie@company.com", "status": "Awaiting Approval", "last_submission": "2025-11-05 13:00"}
    ]

approvals = st.session_state.approvals


case_id = st.session_state.get("case_id")

if not case_id:
    st.warning("No approval case selected. Returning to Approval Dashboard.")
    st.switch_page("pages/approvals.py") 
    st.stop()

vendor_case = next((a for a in approvals if a["case_id"]==case_id), None)
if not vendor_case:
    st.error(f"Approval case {case_id} not found. Returning to Dashboard.")
    st.switch_page("pages/approvals.py") 
    st.stop()

if "last_submission_dt" not in vendor_case:
    vendor_case["last_submission_dt"] = datetime.strptime(vendor_case["last_submission"], "%Y-%m-%d %H:%M")

def risk_category(score):
    if score>=60: return "High Risk", "high-risk"
    elif score>=30: return "Medium Risk", "medium-risk"
    else: return "Low Risk", "low-risk"

risk_label, css_class = risk_category(vendor_case["risk_score"])


st.markdown(f"<h2>Approval Details: {vendor_case['case_id']}</h2>", unsafe_allow_html=True)

st.markdown(f"<div class='card {css_class}'>", unsafe_allow_html=True)
st.markdown(f"<h3>{vendor_case['vendor']}</h3>", unsafe_allow_html=True)
st.markdown(f"<p><b>Case ID:</b> {vendor_case['case_id']}</p>", unsafe_allow_html=True)
st.markdown(f"<p><b>Risk Score:</b> {vendor_case['risk_score']} ({risk_label})</p>", unsafe_allow_html=True)
st.markdown(f"<p><b>Assigned To:</b> {vendor_case['assigned_to']}</p>", unsafe_allow_html=True)
st.markdown(f"<p><b>Status:</b> {vendor_case['status']}</p>", unsafe_allow_html=True)
st.markdown(f"<p><b>Last Submission:</b> {vendor_case['last_submission']}</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

def update_status(case_id, new_status):
    """Updates the status in st.session_state and reruns."""
    for case in st.session_state.approvals:
        if case["case_id"] == case_id:
            case["status"] = new_status
            break
    st.rerun() 

st.subheader("Decision")
col1, col2 = st.columns([1,1])

if vendor_case['status'] == 'Awaiting Approval':
    if col1.button("Approve", key="approve_btn", type="primary"):
        update_status(case_id, "Approved")
        
    if col2.button("Reject", key="reject_btn"):
        update_status(case_id, "Rejected")
else:
    st.info(f"This case has already been **{vendor_case['status']}**.")


st.markdown("---")
