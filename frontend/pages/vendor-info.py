import random
import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Vendor Info", layout="wide")

st.markdown("""
<style>
header {visibility:hidden;}
footer {visibility:hidden;}
.card {border-radius:10px;padding:15px;margin-bottom:20px;box-shadow: 2px 2px 10px rgba(0,0,0,0.1);}
.high-risk {background: linear-gradient(135deg,#ffcccc,#ff6666);}
.medium-risk {background: linear-gradient(135deg,#fff2cc,#ffcc66);}
.low-risk {background: linear-gradient(135deg,#ccf2ff,#66c2ff);}
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
    st.switch_page("approve-page.py") 
    st.stop()

vendor_case = next((a for a in approvals if a["case_id"]==case_id), None)
if not vendor_case:
    st.error(f"Approval case {case_id} not found. Returning to Dashboard.")
    st.switch_page("approve-page.py") 
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


def fetch_risk_factors(vendor_name):
    """
    Simulates an API call to get risk factors for a specific vendor.
    
    The weights sum up to 100%. This data would typically come from an external API.
    """
    random.seed(hash(vendor_name) % (2**32 - 1)) # Use vendor name for deterministic simulation
    
    factors = ["Financial Stability", "Security Compliance", "Service Reliability", "Operational History"]
    
    weights = [random.randint(1, 100) for _ in factors]
    total_weight = sum(weights)
    weights = [(w / total_weight) * 100 for w in weights] # Normalize to 100
    
    return pd.DataFrame({
        'Factor': factors,
        'Weight (%)': weights
    })


vendor_risk_df = fetch_risk_factors(vendor_case['vendor'])

fig = px.pie(
    vendor_risk_df,
    values='Weight (%)',
    names='Factor',
    title=f'Risk Factor Distribution for {vendor_case["vendor"]}',
    hole=.4, 
    color_discrete_sequence=px.colors.sequential.RdBu 
)

fig.update_traces(textposition='inside', textinfo='percent+label', 
                  hovertemplate="<b>%{label}</b><br>Weight: %{value:.2f}%<extra></extra>")
fig.update_layout(showlegend=True)

# Display the chart
st.plotly_chart(fig, use_container_width=True)

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
