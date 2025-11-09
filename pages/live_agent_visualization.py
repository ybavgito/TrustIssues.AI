"""
TrustIssues.AI - Live Agent Visualization
Clean, professional real-time monitoring
"""
import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv
import plotly.graph_objects as go
import plotly.express as px

load_dotenv()
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from styles.app_styles import get_base_css, COLORS
from src.state_manager import StateManager

st.set_page_config(
    page_title="Live Visualization - TrustIssues.AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(get_base_css(), unsafe_allow_html=True)

# Hide navigation and compact layout
st.markdown("""
<style>
[data-testid="stSidebarNav"] {
    display: none !important;
}
.main .block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    padding: 0;
}
.stTabs [data-baseweb="tab"] {
    padding: 8px 16px;
    font-size: 13px;
}
.stMetric {
    padding: 8px;
}
</style>
""", unsafe_allow_html=True)

# Initialize
state_manager = StateManager()
from src import db

# Sidebar
with st.sidebar:
    st.markdown("### 🤖 Session Selector")
    
    state_dir = Path("state")
    if state_dir.exists():
        sessions = sorted(
            state_dir.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:15]
        
        if sessions:
            options = [f.stem for f in sessions]
            # Pre-select if coming from approvals
            default_idx = 0
            if 'selected_session_id' in st.session_state:
                try:
                    default_idx = options.index(st.session_state['selected_session_id'])
                except ValueError:
                    pass
            
            selected = st.selectbox("Select Session", options, index=default_idx)
            
            if selected:
                st.session_state['selected_session_id'] = selected
            
            st.markdown("---")
            auto_refresh = st.toggle("🔄 Auto-refresh (5s)")
            
            if auto_refresh:
                import time
                time.sleep(5)
                st.rerun()
    else:
            st.info("No sessions found")
    
            st.markdown("---")
    
    # Show current submission info if available
    if 'current_submission_id' in st.session_state:
        submission_id = st.session_state['current_submission_id']
        st.markdown(f"**Submission ID:** `{submission_id[:8]}...`")
        st.markdown("---")
    
    if st.button("⬅️ Back to Approvals", use_container_width=True):
        st.switch_page("pages/approvals.py")
        st.rerun()

# Compact header
st.markdown("""
<div style="padding: 8px 0; margin-bottom: 8px;">
    <h2 style="margin: 0; font-size: 20px;">🤖 Live Agent Visualization</h2>
</div>
""", unsafe_allow_html=True)

# Check if we need to start processing
if 'process_pdf_path' in st.session_state:
    pdf_path = st.session_state['process_pdf_path']
    submission_id = st.session_state.get('current_submission_id')
    
    # Professional header for live processing
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h2 style="color: white; margin: 0;">🚀 Live AI Agent Processing</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">Watch every step as the multi-agent system analyzes the vendor in real-time</p>
        </div>
    """, unsafe_allow_html=True)

    # Create containers for live feed
    import threading
    import time
    
    # Live activity feed container
    activity_feed = st.empty()
    status_box = st.empty()
    
    # Initialize tracking
    if 'processing_started' not in st.session_state:
        st.session_state['processing_started'] = True
        st.session_state['agent_session_id'] = None
        
        # Start processing in background thread
        def run_agent():
            from src.agent import RiskLensAgent
            from src.state_manager import StateManager
            
            state_manager = StateManager()
            agent = RiskLensAgent(state_manager)
            state = agent.run(pdf_path)
            
            # Update database
            db.update_after_processing(
                pdf_path,
                state.session_id,
                state.company_info.company_name if state.company_info else None,
                state.risk_score.total_score if state.risk_score else None,
                state.risk_score.risk_level if state.risk_score else None
            )
            
            st.session_state['agent_session_id'] = state.session_id
            st.session_state['processing_complete'] = True
        
        thread = threading.Thread(target=run_agent, daemon=True)
        thread.start()
        st.session_state['agent_thread'] = thread
    
    # Poll for state file updates
    state_dir = Path("state")
    if state_dir.exists():
        sessions = sorted(
            state_dir.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if sessions:
            # Get the most recent session (likely ours)
            latest_session = sessions[0].stem
            state = state_manager.load_state(latest_session)
            
            if state:
                # Compact single-page layout - no scrolling
                # Top row: Status + Quick Metrics
                status_col, metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns([2, 1, 1, 1, 1])
                
                with status_col:
                    if state.requires_human_review and not state.human_decision:
                        # Show paused state when awaiting human review
                        st.markdown("""
                        <div style="background: #ffc107; padding: 8px 12px; border-radius: 6px; color: white; font-weight: 600; font-size: 14px;">
                            ⏸️ PAUSED: Awaiting Human Review
                        </div>
                        """, unsafe_allow_html=True)
                    elif state.current_agent:
                        agent_colors = {
                            'coordinator': '#2563eb',
                            'extractor': '#10b981', 
                            'verifier': '#f59e0b',
                            'risk_analyst': '#ef4444'
                        }
                        agent_color = agent_colors.get(state.current_agent, '#6366f1')
                        st.markdown(f"""
                        <div style="background: {agent_color}; padding: 8px 12px; border-radius: 6px; color: white; font-weight: 600; font-size: 14px;">
                            🤖 ACTIVE: {state.current_agent.upper().replace('_', ' ')}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="background: #6b7280; padding: 8px 12px; border-radius: 6px; color: white; font-weight: 600; font-size: 14px;">
                            ⏳ Initializing...
                        </div>
                        """, unsafe_allow_html=True)

                with metrics_col1:
                    st.metric("Steps", len(state.agent_decisions) if state.agent_decisions else 0)
                with metrics_col2:
                    if state.company_info:
                        st.metric("Company", state.company_info.company_name[:15] + "..." if len(state.company_info.company_name) > 15 else state.company_info.company_name)
                with metrics_col3:
                    if state.risk_score:
                        st.metric("Risk", f"{state.risk_score.total_score}/100", delta=state.risk_score.risk_level.upper())
                with metrics_col4:
                    # Three-state system: Processing → Awaiting Review → Complete
                    if state.workflow_complete or state.human_decision:
                        status = "Complete"
                        status_delta = "✅ Done"
                    elif state.requires_human_review and not state.human_decision:
                        status = "Awaiting Review"
                        status_delta = "⏸️ Paused"
                    else:
                        status = "Processing"
                        status_delta = "🔄 Active"
                    st.metric("Status", status, delta=status_delta)
                
                # Main content in tabs for compactness
                tab1, tab2, tab3, tab4 = st.tabs(["📋 Activity", "✅ Results", "💬 Messages", "📊 Details"])
                
                with tab1:
                    # Compact activity timeline
                    if state.agent_decisions:
                        for i, decision in enumerate(state.agent_decisions[-3:], 1):  # Show last 3 only
                            agent_colors = {
                                'coordinator': '#2563eb',
                                'extractor': '#10b981', 
                                'verifier': '#f59e0b',
                                'risk_analyst': '#ef4444'
                            }
                            agent_color = agent_colors.get(decision.agent_id, '#6366f1')
                            
                            with st.expander(f"Step {len(state.agent_decisions) - 3 + i}: {decision.agent_id.upper().replace('_', ' ')}", expanded=False):
                                reasoning_text = decision.reasoning[:200] + "..." if len(decision.reasoning) > 200 else decision.reasoning
                                st.markdown(f"""
                                <div style="background: #f9fafb; padding: 10px; border-left: 3px solid {agent_color}; border-radius: 4px; font-size: 12px; line-height: 1.5;">
                                    {reasoning_text.replace(chr(10), '<br>')}
                                </div>
                                """, unsafe_allow_html=True)
                                if decision.tool_calls:
                                    tools = [tool.get('function', 'unknown').replace('_', ' ').title() if isinstance(tool, dict) else str(tool).replace('_', ' ').title() for tool in decision.tool_calls]
                                    st.caption(f"🔧 Tools: {', '.join(tools)}")
                
                with tab2:
                    # Show prominent message when processing completes
                    if state.requires_human_review and not state.human_decision:
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <h3 style="color: white; margin: 0 0 10px 0;">✅ AI Processing Complete</h3>
                            <p style="color: rgba(255,255,255,0.95); margin: 0;">All analysis is complete. Review the results below and make your decision.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Compact results in grid
                    res_col1, res_col2 = st.columns(2)
                    
                    with res_col1:
                        if state.company_info:
                            st.markdown(f"""
                            <div style="background: #f0fdf4; border-left: 3px solid #10b981; padding: 10px; border-radius: 6px; margin-bottom: 8px;">
                                <strong style="color: #065f46; font-size: 13px;">✅ Company</strong>
                                <div style="font-size: 11px; color: #111827; margin-top: 4px; line-height: 1.4;">
                                    <div><strong>Name:</strong> {state.company_info.company_name}</div>
                                    <div><strong>Reg:</strong> {state.company_info.registration_number}</div>
                                    {f'<div><strong>Country:</strong> {state.company_info.country}</div>' if state.company_info.country else ''}
                                </div>
                                </div>
                            """, unsafe_allow_html=True)

                        if state.registry_result:
                            is_match = state.registry_result.match
                            status_icon = "✅" if is_match else "❌"
                            status_color = "#10b981" if is_match else "#ef4444"
                            bg_color = "#f0fdf4" if is_match else "#fef2f2"
                            st.markdown(f"""
                            <div style="background: {bg_color}; border-left: 3px solid {status_color}; padding: 10px; border-radius: 6px; margin-bottom: 8px;">
                                <strong style="color: #065f46; font-size: 13px;">🔍 Registry</strong>
                                <div style="font-size: 11px; color: #111827; margin-top: 4px;">
                                    <div>{status_icon} {state.registry_result.status.title() if state.registry_result.status else 'Not Found'}</div>
                                    <div>Confidence: {state.registry_result.confidence:.0%}</div>
                                </div>
                                </div>
                                """, unsafe_allow_html=True)

                    with res_col2:
                        if state.sanctions_result:
                            is_match = state.sanctions_result.match
                            status_color = "#ef4444" if is_match else "#10b981"
                            bg_color = "#fef2f2" if is_match else "#f0fdf4"
                            status_icon = "⚠️" if is_match else "✅"
                            st.markdown(f"""
                            <div style="background: {bg_color}; border-left: 3px solid {status_color}; padding: 10px; border-radius: 6px; margin-bottom: 8px;">
                                <strong style="color: #991b1b; font-size: 13px;">🚨 Sanctions</strong>
                                <div style="font-size: 11px; color: #111827; margin-top: 4px;">
                                    <div>{status_icon} {'MATCH' if is_match else 'Clear'}</div>
                                    {f'<div>Match: {state.sanctions_result.match_score:.0%}</div>' if state.sanctions_result.match_score > 0 else ''}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        if state.risk_score:
                            risk_level = state.risk_score.risk_level
                            risk_colors = {
                                'low': {'bg': '#f0fdf4', 'border': '#10b981', 'text': '#065f46'},
                                'medium': {'bg': '#fffbeb', 'border': '#f59e0b', 'text': '#92400e'},
                                'high': {'bg': '#fef2f2', 'border': '#ef4444', 'text': '#991b1b'}
                            }
                            colors = risk_colors.get(risk_level, risk_colors['medium'])
                            risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(risk_level, '⚪')
                            st.markdown(f"""
                            <div style="background: {colors['bg']}; border-left: 3px solid {colors['border']}; padding: 10px; border-radius: 6px; margin-bottom: 8px;">
                                <strong style="color: {colors['text']}; font-size: 13px;">{risk_emoji} Risk</strong>
                                <div style="font-size: 11px; color: #111827; margin-top: 4px;">
                                    <div><strong>{risk_level.upper()}</strong> - {state.risk_score.total_score}/100</div>
        </div>
        </div>
                            """, unsafe_allow_html=True)
    
                with tab3:
                    if state.agent_messages:
                        for msg in state.agent_messages[-5:]:
                            priority_icon = "🔴" if msg.priority == "high" else "💬"
                            st.markdown(f"""
                            <div style="background: #f9fafb; padding: 8px; border-radius: 4px; margin-bottom: 6px; border-left: 2px solid #2563eb; font-size: 11px;">
                                <strong style="color: #2563eb;">{priority_icon} {msg.sender.upper()} → {msg.receiver.upper()}</strong>
                                <div style="color: #374151; margin-top: 2px;">{msg.content[:100] + '...' if len(msg.content) > 100 else msg.content}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No messages")
                
                with tab4:
                    # Full details in compact format
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        if state.company_info:
                            st.markdown("**Company Details:**")
                            st.text(f"Name: {state.company_info.company_name}")
                            st.text(f"Registration: {state.company_info.registration_number}")
                            if state.company_info.country:
                                st.text(f"Country: {state.company_info.country}")
                            if state.company_info.address:
                                st.text(f"Address: {state.company_info.address}")
                    
                    with detail_col2:
                        if state.risk_explanation:
                            st.markdown("**Risk Explanation:**")
                            st.text(state.risk_explanation.explanation[:300] + "..." if len(state.risk_explanation.explanation) > 300 else state.risk_explanation.explanation)
                
                # Human Review Section - Prominent at bottom
                if state.requires_human_review and not state.human_decision:
                    st.markdown("---")
                    # Make human review section very prominent
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); padding: 25px; border-radius: 10px; margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                        <h2 style="color: white; margin: 0 0 10px 0;">⚠️ Human Review Required</h2>
                        <p style="color: rgba(255,255,255,0.95); margin: 0; font-size: 16px;">AI processing is complete. Your decision is required to proceed.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if state.review_reason:
                        st.markdown(f"""
                        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                            <strong>Review Reason:</strong> {state.review_reason}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Review decision buttons
                    review_col1, review_col2, review_col3, review_col4 = st.columns([1, 1, 1, 3])
                    
                    with review_col1:
                        if st.button("✅ Approve", type="primary", use_container_width=True, key="human_approve"):
                            # Update state with human decision
                            state.human_decision = "approved"
                            state_manager.save_state(state)
                            
                            # Continue processing - generate access recommendation
                            from src.agent import RiskLensAgent
                            agent = RiskLensAgent(state_manager)
                            
                            # Resume workflow to generate access recommendation
                            if state.risk_score and not state.access_recommendation:
                                from src.tools.access_recommender import AccessRecommender
                                access_recommender = AccessRecommender()
                                result = access_recommender.recommend_access(
                                    state.risk_score,
                                    state.human_decision,
                                    state.human_notes
                                )
                                if result.success:
                                    from src.models import AccessRecommendation
                                    state.access_recommendation = AccessRecommendation(**result.data)
                                    state.workflow_complete = True
                                    state_manager.save_state(state)
                            
                            # Update database
                            if 'current_submission_id' in st.session_state:
                                db.mark_submission_status(st.session_state['current_submission_id'], 'approved')
                            
                            st.success("✅ Approved! Generating access recommendation...")
                            st.balloons()
                            st.rerun()
                    
                    with review_col2:
                        if st.button("❌ Reject", use_container_width=True, key="human_reject"):
                            state.human_decision = "rejected"
                            state.workflow_complete = True
                            state_manager.save_state(state)
                            
                            # Update database
                            if 'current_submission_id' in st.session_state:
                                db.mark_submission_status(st.session_state['current_submission_id'], 'rejected')
                            
                            st.warning("❌ Rejected")
                            st.rerun()
                    
                    with review_col3:
                        if st.button("📋 Request Info", use_container_width=True, key="human_request_info"):
                            state.human_decision = "request_more_info"
                            state.workflow_complete = True
                            state_manager.save_state(state)
                            st.info("📋 More information requested")
                            st.rerun()
                    
                    # Notes input
                    notes = st.text_area("Additional Notes (Optional)", key="human_notes", height=80)
                    if notes:
                        state.human_notes = notes
                        state_manager.save_state(state)
                
                # Show access recommendation if available
                if state.access_recommendation:
                    st.markdown("---")
                    st.markdown("### ✅ Access Recommendation")
                    access_level = state.access_recommendation.access_level
                    access_color = {
                        'standard': '#10b981',
                        'read_only': '#f59e0b',
                        'restricted': '#ef4444'
                    }.get(access_level, '#6366f1')
                    
                    st.markdown(f"""
                    <div style="background: #f0fdf4; border-left: 4px solid {access_color}; padding: 12px; border-radius: 6px;">
                        <strong style="color: #065f46; font-size: 14px;">Access Level: {access_level.upper().replace('_', ' ')}</strong>
                        <div style="font-size: 12px; color: #111827; margin-top: 6px;">
                            <div><strong>Permissions:</strong> {', '.join(state.access_recommendation.permissions)}</div>
                            <div><strong>Restrictions:</strong> {', '.join(state.access_recommendation.restrictions) if state.access_recommendation.restrictions else 'None'}</div>
                            <div style="margin-top: 6px;"><strong>Justification:</strong> {state.access_recommendation.justification}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Check if processing is complete (requires_human_review means AI processing is done)
                if state.requires_human_review:
                    # AI processing is complete, now awaiting human review
                    if state.human_decision:
                        # Human has made a decision
                        status_box.success("✅ Processing Complete! Final results shown below.")
                        # Clean up processing state
                        st.session_state['selected_session_id'] = latest_session
                        if 'processing_started' in st.session_state:
                            del st.session_state['processing_started']
                        if 'agent_thread' in st.session_state:
                            del st.session_state['agent_thread']
                        if 'processing_complete' in st.session_state:
                            del st.session_state['processing_complete']
                        if 'process_pdf_path' in st.session_state:
                            del st.session_state['process_pdf_path']
                        time.sleep(2)
                        st.rerun()
                    else:
                        # AI processing done, awaiting human review
                        status_box.warning("⏸️ AI Processing Complete - Awaiting Human Review")
                        # Clean up processing state but keep session selected
                        st.session_state['selected_session_id'] = latest_session
                        if 'processing_started' in st.session_state:
                            del st.session_state['processing_started']
                        if 'agent_thread' in st.session_state:
                            del st.session_state['agent_thread']
                        if 'processing_complete' in st.session_state:
                            del st.session_state['processing_complete']
                        if 'process_pdf_path' in st.session_state:
                            del st.session_state['process_pdf_path']
                        # Don't auto-refresh when awaiting review - let user interact
                        time.sleep(3)
                        st.rerun()
                else:
                    # Still processing
                    status_box.info("🔄 Processing... Auto-refreshing every 2 seconds")
                    time.sleep(2)
                    st.rerun()
    
    # Fallback status
    if not state_dir.exists() or not sessions:
        status_box.warning("⏳ Initializing agents... Please wait")
        time.sleep(2)
        st.rerun()

# Main content
if 'selected_session_id' in st.session_state:
    session_id = st.session_state['selected_session_id']
    state = state_manager.load_state(session_id)
    
    if state:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Company",
                state.company_info.company_name if state.company_info else "Processing"
            )
        
        with col2:
            if state.risk_score:
                st.metric(
                    "Risk Level",
                    state.risk_score.risk_level.upper(),
                    delta=f"{state.risk_score.total_score}/100"
                )
        
        with col3:
            agent_count = len(state.agent_decisions) if state.agent_decisions else 0
            st.metric("Agent Actions", agent_count)
        
        with col4:
            # Three-state system: Processing → Awaiting Review → Complete
            if state.workflow_complete or state.human_decision:
                status = "Complete"
                status_delta = "✅ Done"
            elif state.requires_human_review and not state.human_decision:
                status = "Awaiting Review"
                status_delta = "⏸️ Paused"
            else:
                status = "Processing"
                status_delta = "🔄 Active"
            st.metric("Status", status, delta=status_delta)
        
        # Pipeline - Show accurate agent workflow stages
        st.markdown("### 🔄 Agent Pipeline")
        
        # Map completed_steps to agent stages
        step_to_agent = {
            'extract_from_pdf': 'extractor',
            'search_registry': 'verifier',
            'check_sanctions': 'verifier',
            'compute_risk': 'risk_analyst',
            'explain_risk': 'risk_analyst'
        }
        
        # Determine which agents have completed work
        completed_agents = set()
        for step in state.completed_steps:
            agent = step_to_agent.get(step)
            if agent:
                completed_agents.add(agent)
        
        stages = [
            ("coordinator", "Coordinator"),
            ("extractor", "Extractor"),
            ("verifier", "Verifier"),
            ("risk_analyst", "Risk Analyst")
        ]
        
        current_agent = state.current_agent if state.current_agent else None
        
        cols = st.columns(len(stages))
        for i, (agent_id, stage_name) in enumerate(stages):
            with cols[i]:
                if agent_id in completed_agents:
                    st.success(f"✓ {stage_name}")
                elif agent_id == current_agent:
                    st.warning(f"⚡ {stage_name}")
                elif state.requires_human_review and not state.human_decision:
                    # Show paused state
                    st.info(f"⏸️ {stage_name}")
                else:
                    st.info(f"○ {stage_name}")
        
        # Show paused indicator if awaiting human review
        if state.requires_human_review and not state.human_decision:
            st.markdown("""
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; border-radius: 6px; margin-top: 10px;">
                <strong>⏸️ Workflow Paused</strong> - Awaiting human review decision
            </div>
            """, unsafe_allow_html=True)
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["🧠 Agent Decisions", "📊 Risk Analysis", "📈 Timeline"])
        
        with tab1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if state.agent_decisions:
                for decision in reversed(state.agent_decisions[-5:]):
                    with st.expander(f"{decision.agent_id.title()} - {decision.timestamp.strftime('%H:%M:%S')}"):
                        st.markdown(f"**Reasoning:** {decision.reasoning}")
                        if decision.action:
                            st.info(f"**Action:** {decision.action}")
            else:
                st.info("No decisions yet")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            if state.risk_score:
                col_a, col_b = st.columns([1, 1])
                
                with col_a:
                    # Gauge chart
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=state.risk_score.total_score,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Risk Score"},
                        gauge={
                            'axis': {'range': [None, 100]},
                            'steps': [
                                {'range': [0, 40], 'color': "lightgreen"},
                                {'range': [40, 70], 'color': "yellow"},
                                {'range': [70, 100], 'color': "lightcoral"}
                            ],
                            'threshold': {'line': {'color': "red", 'width': 4}, 'value': 70}
                        }
                    ))
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_b:
                    if state.risk_score.breakdown:
                        st.markdown("#### Risk Factors")
                        for factor, score in state.risk_score.breakdown.items():
                            st.write(f"**{factor.replace('_', ' ').title()}:** {score}")
                
                if state.risk_explanation:
                    st.markdown("#### AI Analysis")
                    st.write(state.risk_explanation.summary)
                    
                    col_c, col_d = st.columns(2)
                    with col_c:
                        st.markdown("**Key Factors:**")
                        for f in state.risk_explanation.key_factors:
                            st.write(f"• {f}")
                    with col_d:
                        st.markdown("**Uncertainties:**")
                        for u in state.risk_explanation.unknowns:
                            st.write(f"• {u}")
            else:
                st.info("Risk assessment not complete")
        
        with tab3:
            if state.agent_decisions:
                # Create timeline data
                timeline_data = []
                for d in state.agent_decisions:
                    timeline_data.append({
                        'Agent': d.agent_id.replace('_', ' ').title(),
                        'Time': d.timestamp,
                        'Action': d.action or 'Reasoning'
                    })
                
                fig = px.scatter(
                    timeline_data,
                    x='Time',
                    y='Agent',
                    color='Agent',
                    hover_data=['Action'],
                    title="Agent Activity Timeline"
                )
                fig.update_traces(marker=dict(size=12))
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No timeline data yet")
        
        # Human Review Section - Prominent
        if state.requires_human_review and not state.human_decision:
            st.markdown("---")
            # Make human review section very prominent
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); padding: 25px; border-radius: 10px; margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                <h2 style="color: white; margin: 0 0 10px 0;">⚠️ Human Review Required</h2>
                <p style="color: rgba(255,255,255,0.95); margin: 0; font-size: 16px;">AI processing is complete. Your decision is required to proceed.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if state.review_reason:
                st.markdown(f"""
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                    <strong>Review Reason:</strong> {state.review_reason}
                </div>
                """, unsafe_allow_html=True)
            
            # Review decision buttons
            review_col1, review_col2, review_col3, review_col4 = st.columns([1, 1, 1, 3])
            
            with review_col1:
                if st.button("✅ Approve", type="primary", use_container_width=True, key="human_approve_main"):
                    # Update state with human decision
                    state.human_decision = "approved"
                    state_manager.save_state(state)
                    
                    # Continue processing - generate access recommendation
                    from src.agent import RiskLensAgent
                    agent = RiskLensAgent(state_manager)
                    
                    # Resume workflow to generate access recommendation
                    if state.risk_score and not state.access_recommendation:
                        from src.tools.access_recommender import AccessRecommender
                        access_recommender = AccessRecommender()
                        result = access_recommender.recommend_access(
                            state.risk_score,
                            state.human_decision,
                            state.human_notes
                        )
                        if result.success:
                            from src.models import AccessRecommendation
                            state.access_recommendation = AccessRecommendation(**result.data)
                            state.workflow_complete = True
                            state_manager.save_state(state)
                    
                    # Update database
                    if 'current_submission_id' in st.session_state:
                        db.mark_submission_status(st.session_state['current_submission_id'], 'approved')
                    
                    st.success("✅ Approved! Generating access recommendation...")
                    st.balloons()
                    st.rerun()
            
            with review_col2:
                if st.button("❌ Reject", use_container_width=True, key="human_reject_main"):
                    state.human_decision = "rejected"
                    state.workflow_complete = True
                    state_manager.save_state(state)
                    
                    # Update database
                    if 'current_submission_id' in st.session_state:
                        db.mark_submission_status(st.session_state['current_submission_id'], 'rejected')
                    
                    st.warning("❌ Rejected")
                    st.rerun()
            
            with review_col3:
                if st.button("📋 Request Info", use_container_width=True, key="human_request_info_main"):
                    state.human_decision = "request_more_info"
                    state.workflow_complete = True
                    state_manager.save_state(state)
                    st.info("📋 More information requested")
                    st.rerun()
            
            # Notes input
            notes = st.text_area("Additional Notes (Optional)", key="human_notes_main", height=80)
            if notes:
                state.human_notes = notes
                state_manager.save_state(state)
        
        # Show access recommendation if available
        if state.access_recommendation:
            st.markdown("---")
            st.markdown("### ✅ Access Recommendation")
            access_level = state.access_recommendation.access_level
            access_color = {
                'standard': '#10b981',
                'read_only': '#f59e0b',
                'restricted': '#ef4444'
            }.get(access_level, '#6366f1')
            
            st.markdown(f"""
            <div style="background: #f0fdf4; border-left: 4px solid {access_color}; padding: 12px; border-radius: 6px;">
                <strong style="color: #065f46; font-size: 14px;">Access Level: {access_level.upper().replace('_', ' ')}</strong>
                <div style="font-size: 12px; color: #111827; margin-top: 6px;">
                    <div><strong>Permissions:</strong> {', '.join(state.access_recommendation.permissions)}</div>
                    <div><strong>Restrictions:</strong> {', '.join(state.access_recommendation.restrictions) if state.access_recommendation.restrictions else 'None'}</div>
                    <div style="margin-top: 6px;"><strong>Justification:</strong> {state.access_recommendation.justification}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.error("Could not load session")
else:
    st.info("👈 Select a session from the sidebar")
