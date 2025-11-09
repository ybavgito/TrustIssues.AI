"""
TrustIssues.AI - Connected Frontend
This version actually connects to the backend agent system
"""
import streamlit as st
import sys
from pathlib import Path
import tempfile
import os

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agent import RiskLensAgent
from src.state_manager import StateManager
from src.models import AgentState
from src.industry_config import detect_industry, get_industry_profile

# Page config
st.set_page_config(page_title="TrustIssues.AI - Vendor Onboarding", layout="wide")

# Hide Streamlit header
st.markdown("""
<style>
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Custom CSS
# Custom CSS
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
.form-container {
    background-color: #1f2937; /* Lighter than BG for depth */
    border-radius: 10px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    border: 1px solid #374151; /* Subtle border */
}

/* --- Text & Headings --- */
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF; /* Bright white for headers */
}
p, label, .st-write, .st-markdown {
     color: #F3F4F6; /* Light gray for body text */
}

/* --- Inputs (File Uploader) --- */
div[data-testid="stFileUploader"] label {
    color: #9CA3AF !important; /* Lighter label color */
}

/* --- Buttons --- */
.stButton > button, div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(90deg, #0FB5A8, #056D63);
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    transition: all 0.3s ease;
}
.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
    background: linear-gradient(90deg, #056D63, #0FB5A8);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(5, 109, 99, 0.3);
}
.stButton > button:focus, div[data-testid="stFormSubmitButton"] > button:focus {
    box-shadow: 0 0 0 0.2rem rgba(15, 181, 168, 0.5) !important;
}

/* --- Tabs --- */
.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    color: #9CA3AF;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: #1f2937;
    color: #FFFFFF;
    border-radius: 8px 8px 0 0;
}

/* --- Risk/Decision Boxes --- */
.risk-box, .decision-box {
    padding: 20px;
    border-radius: 8px;
    border-left-width: 5px;
    border-left-style: solid;
    margin-bottom: 10px;
}
/* Risk Box Colors */
.risk-box-high { 
    background-color: rgba(244, 67, 54, 0.05); 
    border-left-color: #F44336; 
}
.risk-box-medium { 
    background-color: rgba(255, 152, 0, 0.05); 
    border-left-color: #FF9800; 
}
.risk-box-low { 
    background-color: rgba(76, 175, 80, 0.05); 
    border-left-color: #4CAF50; 
}
/* Risk Box Header Colors */
.risk-box-high h2 { color: #F44336; }
.risk-box-medium h2 { color: #FF9800; }
.risk-box-low h2 { color: #4CAF50; }

/* Decision Box Colors */
.decision-box-approved { 
    background-color: rgba(76, 175, 80, 0.05); 
    border-left-color: #4CAF50; 
}
.decision-box-rejected { 
    background-color: rgba(244, 67, 54, 0.05); 
    border-left-color: #F44336; 
}
.decision-box-request_more_info { 
    background-color: rgba(255, 152, 0, 0.05); 
    border-left-color: #FF9800; 
}

/* --- Status Box (from original file) --- */
.status-box {
    background: linear-gradient(135deg, #1a2a1a, #1f3a1f);
    border-left: 4px solid #4caf50;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize backend components
@st.cache_resource
def get_agent_system():
    """Initialize agent system (cached)"""
    state_manager = StateManager()
    agent = RiskLensAgent(state_manager)
    return agent, state_manager

# Main title
st.markdown('<div class="navbar">🛡️ TrustIssues.AI - Vendor Onboarding</div>', unsafe_allow_html=True)

# Initialize agent system
agent, state_manager = get_agent_system()

# Tabs
tab1, tab2, tab3 = st.tabs(["📤 Submit Vendor", "📊 View Results", "📋 Recent Sessions"])

with tab1:
    st.subheader("Submit New Vendor for Analysis")
    
    uploaded_file = st.file_uploader(
        "Upload Vendor PDF Document",
        type="pdf",
        help="Upload a PDF containing vendor information"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        if st.button("🚀 Process Vendor", type="primary", use_container_width=True):
            with st.spinner("🤖 Processing vendor with AI agents..."):
                try:
                    # Process with backend agent system
                    state = agent.run(tmp_path)
                    
                    # Store in session state
                    st.session_state['last_state'] = state
                    st.session_state['last_session_id'] = state.session_id
                    
                    st.success(f"✅ Processing complete! Session ID: {state.session_id}")
                    st.balloons()
                    
                    # Show quick results
                    if state.company_info:
                        st.markdown("### 📋 Extracted Information")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Company:** {state.company_info.company_name}")
                            st.write(f"**Country:** {state.company_info.country}")
                        with col2:
                            st.write(f"**Business Type:** {state.company_info.business_type}")
                            st.write(f"**Registration:** {state.company_info.registration_number}")
                    
                    if state.risk_score:
                        st.markdown("### 📊 Risk Assessment")
                        risk_level = state.risk_score.risk_level.upper()
                        risk_color = {
                            "LOW": "🟢",
                            "MEDIUM": "🟡",
                            "HIGH": "🔴"
                        }.get(risk_level, "⚪")
                        
                        st.metric(
                            "Risk Score",
                            f"{risk_level} ({state.risk_score.total_score}/100)",
                            delta=f"{risk_color} {risk_level} RISK"
                        )
                    
                    # Switch to results tab
                    st.info("💡 Switch to 'View Results' tab to see full analysis")
                    
                except Exception as e:
                    st.error(f"❌ Error processing vendor: {str(e)}")
                    st.exception(e)
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("View Processing Results")
    
    # Check if we have a recent session
    if 'last_session_id' in st.session_state:
        session_id = st.session_state['last_session_id']
        state = state_manager.load_state(session_id)
        
        if state:
            # Display full results
            st.markdown(f"**Session ID:** `{session_id}`")
            
            # Company Info
            if state.company_info:
                st.markdown("### 📋 Company Information")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Name:** {state.company_info.company_name}")
                    st.write(f"**Country:** {state.company_info.country}")
                with col2:
                    st.write(f"**Business Type:** {state.company_info.business_type}")
                    st.write(f"**Registration:** {state.company_info.registration_number}")
                with col3:
                    if state.company_info.incorporation_date:
                        st.write(f"**Incorporated:** {state.company_info.incorporation_date}")
            
            # Risk Assessment
            if state.risk_score:
                st.markdown("### 📊 Risk Assessment")
                
                risk_level = state.risk_score.risk_level.upper()
                risk_level_class = {
                    "LOW": "low",
                    "MEDIUM": "medium",
                    "HIGH": "high"
                }.get(risk_level, "medium") # default to medium
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"""
                    <div class="risk-box risk-box-{risk_level_class}">
                        <h2 style="margin: 0;">{state.risk_score.total_score}/100</h2>
                        <p style="margin: 5px 0 0 0; font-weight: bold;">
                            {risk_level} RISK
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if state.risk_score.score_breakdown:
                        st.write("**Score Breakdown:**")
                        for factor, score in state.risk_score.score_breakdown.items():
                            color = "#4caf50" if score > 0 else "#f44336"
                            st.write(f"- {factor.replace('_', ' ').title()}: <span style='color: {color};'>{'+' if score > 0 else ''}{score}</span>", unsafe_allow_html=True)
            
            # Risk Explanation
            if state.risk_explanation:
                st.markdown("### 🧠 AI Risk Analysis")
                st.write(f"**Summary:** {state.risk_explanation.summary}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Key Factors:**")
                    for factor in state.risk_explanation.key_factors:
                        st.write(f"- {factor}")
                with col2:
                    st.write("**Uncertainties:**")
                    for unknown in state.risk_explanation.unknowns:
                        st.write(f"- {unknown}")
                
                st.write(f"**Recommendation:** {state.risk_explanation.recommendation}")
            
            # Human Decision
            if state.requires_human_review:
                st.markdown("### 👤 Human Review Required")
                
                if state.human_decision:
                    decision_class = f"decision-box-{state.human_decision}"
                    
                    st.markdown(f"""
                    <div class="decision-box {decision_class}">
                        <strong>Decision:</strong> {state.human_decision.upper().replace('_', ' ')}
                        {f'<br><strong>Notes:</strong> {state.human_notes}' if state.human_notes else ''}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("⏳ Awaiting human decision")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✅ Approve", use_container_width=True):
                            state.human_decision = "approved"
                            state_manager.save_state(state)
                            # Continue workflow
                            agent.run(state.pdf_path, state.session_id)
                            st.rerun()
                    with col2:
                        if st.button("❌ Reject", use_container_width=True):
                            state.human_decision = "rejected"
                            state_manager.save_state(state)
                            st.rerun()
                    with col3:
                        if st.button("❓ Request More Info", use_container_width=True):
                            state.human_decision = "request_more_info"
                            state_manager.save_state(state)
                            st.rerun()
            
            # Access Recommendation
            if state.access_recommendation:
                st.markdown("### 🔐 Access Recommendation")
                st.write(f"**Level:** {state.access_recommendation.level.upper()}")
                st.write("**Permissions:**")
                for perm in state.access_recommendation.permissions:
                    st.write(f"- ✅ {perm}")
                st.write("**Restrictions:**")
                for restriction in state.access_recommendation.restrictions:
                    st.write(f"- 🚫 {restriction}")
        else:
            st.warning("No results found for this session")
    else:
        st.info("👆 Upload and process a vendor in the 'Submit Vendor' tab first")

with tab3:
    st.subheader("Recent Processing Sessions")
    
    # List recent sessions
    state_dir = Path("state")
    if state_dir.exists():
        state_files = sorted(
            state_dir.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:10]  # Show last 10
        
        if state_files:
            for state_file in state_files:
                try:
                    state = state_manager.load_state(state_file.stem)
                    if state:
                        with st.expander(f"📄 {state_file.stem} - {state.company_info.company_name if state.company_info else 'Unknown'}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Session ID:** {state.session_id}")
                                if state.risk_score:
                                    st.write(f"**Risk Score:** {state.risk_score.total_score}/100 ({state.risk_score.risk_level.upper()})")
                            with col2:
                                st.write(f"**Status:** {'✅ Complete' if state.workflow_complete else '⏳ Processing'}")
                                if state.human_decision:
                                    st.write(f"**Decision:** {state.human_decision.upper()}")
                            
                            if st.button(f"View Details", key=f"view_{state.session_id}"):
                                st.session_state['last_session_id'] = state.session_id
                                st.rerun()
                except:
                    continue
        else:
            st.info("No processing sessions found")
    else:
        st.info("No state directory found")

