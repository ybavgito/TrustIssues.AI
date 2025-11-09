import random
import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Vendor Info", layout="wide")

st.markdown("""
<style>
/* --- 1. UNIVERSAL STYLES (For Consistency) --- */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

/* Solid Black Body Background for Dark Mode */
.stApp {
    background: #000000; /* Pure Black Background */
    background-image: none; /* Ensure no old gradient image interferes */
}

html, body, [class*="st-emotion-cache"] {
    font-family: 'Montserrat', sans-serif;
    color: #ffffff; 
}

/* Hide default Streamlit elements */
#MainMenu { visibility: hidden; }
header { visibility: hidden; }
footer { visibility: hidden; }
div[data-testid="stSidebarNav"] { display: none; }


/* Header Text (Ensure visibility) */
h1, h2, h4 {
    /* Set h1, h2, h4 to the desired dark color */
    color: #ffffff !important; /* Deep Charcoal Black */
    text-shadow: 1px 1px 3px rgba(255, 255, 255, 0.2); /* Lighter shadow for dark text */
}

h3 {
    /* Set h3 to a light color (white/near-white) */
    color: #f0f0f6 !important; /* Near-white/light gray */
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5); /* Darker shadow for light text */
}
/* --- 2. CARD STYLES (Premium Dark Look) --- */

.card {
    /* Base Card Appearance */
    background-color: #2a2a2a; 
    border-radius: 16px;      
    padding: 25px;            
    margin-bottom: 30px;      
    
    /* Premium Shadow */
    box-shadow: 
        0 10px 30px rgba(0, 0, 0, 0.3), 
        0 4px 8px rgba(0, 0, 0, 0.2); 
    
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); 
    border: 1px solid #444444; 
}
.card:hover {
    transform: translateY(-4px); /* Slight lift on hover */
    box-shadow: 
        0 15px 35px rgba(0, 0, 0, 0.4),
        0 6px 12px rgba(0, 0, 0, 0.25); 
}

/* Content inside the card */
.card p {
    color: #cccccc; 
    font-size: 0.95em;
    line-height: 1.8;
}
.card p b {
    color: #eeeeee; 
    font-weight: 600;
}


/* --- 3. RISK COLOR SCHEMES (High Contrast) --- */

/* High Risk: Deep Red/Mauve */
.high-risk {
    background: linear-gradient(135deg, #302638, #3e284a); /* Dark Mauve gradient */
    border-left: 8px solid #cc4499; /* Bright Mauve bar */
}

/* Medium Risk: Gold/Orange */
.medium-risk {
    background: linear-gradient(135deg, #3d3420, #4a3e20); /* Dark Bronze gradient */
    border-left: 8px solid #ffcc66; /* Bright Gold bar */
}

/* Low Risk: Deep Teal/Green */
.low-risk {
    background: linear-gradient(135deg, #243635, #2c4240); /* Deep Teal gradient */
    border-left: 8px solid #009688; /* Strong Teal bar */
}
            
            /* --- BUTTON COLOR ENHANCEMENTS --- */

/* Primary Button (Approve) - SOLID TEAL */
div[data-testid="stButton"] button[kind="primary"] {
    /* Use solid teal color */
    background-color: #0FB5A8 !important; 
    background-image: none !important; /* IMPORTANT: Removes the gradient */
    border: 1px solid #056D63;
    color: white !important;
    font-weight: bold;
    box-shadow: 0 4px 10px rgba(15, 181, 168, 0.4); /* Teal shadow */
    transition: all 0.3s ease;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    background-color: #056D63 !important; /* Darker teal on hover */
    transform: translateY(-2px);
}

/* Secondary Button (Reject) - UNCHANGED (Deep Red/Mauve) */
div[data-testid="stButton"] button:not([kind="primary"]) {
    background-color: #A32E2E !important; 
    border: 1px solid #CC4499; 
    color: white !important;
    font-weight: bold;
    box-shadow: 0 2px 5px rgba(163, 46, 46, 0.4);
}
div[data-testid="stButton"] button:not([kind="primary"]):hover {
    background-color: #C73838 !important; 
    transform: translateY(-2px);
}


div[data-testid="stInfo"] {
    /* Set outer container border and spacing */
    border-left: 5px solid #0FB5A8; 
    border-radius: 8px;
    padding: 0 !important; /* Reset outer padding */
    margin-top: 20px;
    /* Ensure outer text color is light */
    color: #f0f0f0 !important;
}

div[data-testid="stInfo"] > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) {
    background-color: #2a2a2a !important; /* FORCES DARK BACKGROUND */
    border-radius: 8px; /* Maintain inner rounding */
    padding: 15px; 
}

div[data-testid="stInfo"] p {
    color: #f0f0f0 !important;
    margin-bottom: 0 !important;
                 
div[data-testid*="stPlotlyChart"],
div[data-testid*="stDeckGlChart"],
div[data-testid*="stVegaLiteChart"] {
    background-color: #2a2a2a; 
    border-radius: 16px;
    padding: 20px;
    margin-top: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    border: 1px solid #444444; 
}

/* --- NEW RECOMMENDATION BOX STYLE --- */
.recommendation-box {
    background-color: #000000; /* Pure Black */
    color: white;              /* White Text */
    border-radius: 12px;
    padding: 20px 25px;
    margin-top: 30px;
    margin-bottom: 30px;
    box-shadow: 0 4px 15px rgba(255, 255, 255, 0.1); /* Subtle white shadow */
}

/* Ensure the h2 inside is white and overrides the dark h2 rule */
.recommendation-box h2 {
    color: white !important;
    text-shadow: none !important;
    margin: 0; /* Remove default margin */
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
    st.switch_page("pages/approve-page.py") 
    st.stop()

vendor_case = next((a for a in approvals if a["case_id"]==case_id), None)
if not vendor_case:
    st.error(f"Approval case {case_id} not found. Returning to Dashboard.")
    st.switch_page("pages/approve-page.py") 
    st.stop()

if "last_submission_dt" not in vendor_case:
    vendor_case["last_submission_dt"] = datetime.strptime(vendor_case["last_submission"], "%Y-%m-%d %H:%M")

def risk_category(score):
    if score>=60: return "High Risk", "high-risk"
    elif score>=30: return "Medium Risk", "medium-risk"
    else: return "Low Risk", "low-risk"

risk_label, css_class = risk_category(vendor_case["risk_score"])


st.markdown(f"<h2>Approval Details: {vendor_case['case_id']}</h2>", unsafe_allow_html=True)

card_html = f"""
<div class='card {css_class}'>
    <h3>{vendor_case['vendor']}</h3>
    <p><b>Case ID:</b> {vendor_case['case_id']}</p>
    <p><b>Risk Score:</b> {vendor_case['risk_score']} ({risk_label})</p>
    <p><b>Assigned To:</b> {vendor_case['assigned_to']}</p>
    <p><b>Status:</b> {vendor_case['status']}</p>
    <p><b>Last Submission:</b> {vendor_case['last_submission']}</p>
</div>
"""
st.markdown(card_html, unsafe_allow_html=True)

def update_status(case_id, new_status):
    """Updates the status in st.session_state and reruns."""
    for case in st.session_state.approvals:
        if case["case_id"] == case_id:
            case["status"] = new_status
            break
    st.rerun() 

st.markdown(
    f"""
    <div class='recommendation-box'>
        <h2>Recommendation for {vendor_case['vendor']}</h2>
        <p>Lorem Ipsum</p>
    </div>
    """, 
    unsafe_allow_html=True
)

def fetch_risk_factors(vendor_name):
    """
    Simulates an API call to get risk factors for a specific vendor.
    
    The weights sum up to 100%. This data would typically come from an external API.
    """
    random.seed(hash(vendor_name) % (2**32 - 1)) 
    
    factors = ["Financial Stability", "Security Compliance", "Service Reliability", "Operational History"]
    
    weights = [random.randint(1, 100) for _ in factors]
    total_weight = sum(weights)
    weights = [(w / total_weight) * 100 for w in weights] 
    
    return pd.DataFrame({
        'Factor': factors,
        'Weight (%)': weights
    })


vendor_risk_df = fetch_risk_factors(vendor_case['vendor'])

st.markdown(f"<h2>Risk Factor Distribution for {vendor_case['vendor']}</h2>", unsafe_allow_html=True)
import plotly.express as px

custom_colors = ['#cc4499', '#009688', '#ffcc66', '#fdbb2d', '#2196f3'] 

fig = px.pie(
    vendor_risk_df,
    values='Weight (%)',
    names='Factor',
    title=" ",
    hole=.4, 
    color_discrete_sequence=custom_colors 
)

fig.update_traces(
    textposition='inside', 
    textinfo='percent+label', 
    marker=dict(line=dict(color='#2a2a2a', width=2)),
    hovertemplate="<b>%{label}</b><br>Weight: %{value:.2f}%<extra></extra>"
)

fig.update_layout(
    plot_bgcolor='#2a2a2a', 
    paper_bgcolor='#2a2a2a',
    title_font_color='white',
    title_font_size=20,
    title_x=0.5, # Keep the centering logic
    showlegend=True,
    legend=dict(
        font=dict(color='white'),
        orientation="h",
        yanchor="bottom",
        y=-0.1,
        xanchor="center",
        x=0.5
    ),
    margin=dict(t=10, b=50, l=10, r=10) # Reduce top margin since we added a separate header
)

st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns([1,1])


if vendor_case['status'] == 'Awaiting Approval':
    
    col1, col2 = st.columns([1,1]) 

    if col1.button("Approve", key=f"approve_btn_{vendor_case['case_id']}", type="primary", use_container_width=True):
        update_status(case_id, "Approved")
        st.rerun()

    if col2.button("Reject", key=f"reject_btn_{vendor_case['case_id']}", use_container_width=True):
        update_status(case_id, "Rejected")
        st.rerun()

else:
    st.info(f"This case has been **{vendor_case['status']}**.")
st.markdown("---")
