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

# Header with prominent back navigation
col_back, col_title = st.columns([1, 6])
with col_back:
    if st.button("⬅️ Back", key="header_back", use_container_width=True, type="secondary"):
        # Navigate back based on where user came from
        if 'current_submission_id' in st.session_state:
            st.switch_page("pages/approvals.py")
        else:
            st.switch_page("pages/admin_dashboard.py")
        st.rerun()
with col_title:
    st.markdown("""
    <div style="padding: 8px 0; margin-bottom: 8px;">
        <h2 style="margin: 0; font-size: 20px;">🤖 Live Agent Visualization</h2>
    </div>
    """, unsafe_allow_html=True)

# CRITICAL: Check if decision was just made (before checking process_pdf_path)
# This prevents restarting agent when approve/reject is clicked
if 'decision_just_made' in st.session_state:
    # A decision was just made, transition to session viewer
    session_id = st.session_state.get('decision_session_id')
    if session_id:
        st.session_state['selected_session_id'] = session_id
    # Clean up all processing state
    for key in ['process_pdf_path', 'processing_started', 'agent_thread', 'start_time', 'processing_complete', 'agent_session_id', 'decision_just_made', 'decision_session_id']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
    st.stop()

# Check if we need to start processing
if 'process_pdf_path' in st.session_state:
    pdf_path = st.session_state['process_pdf_path']
    submission_id = st.session_state.get('current_submission_id')
    
    # CRITICAL: Check if we have a session ID and if that session already has a decision
    # This catches the case where approve/reject was just clicked
    session_id_to_check = st.session_state.get('agent_session_id') or st.session_state.get('decision_session_id')
    if session_id_to_check:
        try:
            existing_state = state_manager.load_state(session_id_to_check)
            if existing_state and existing_state.human_decision:
                # Decision already made, transition to session viewer immediately
                st.session_state['selected_session_id'] = existing_state.session_id
                for key in ['process_pdf_path', 'processing_started', 'agent_thread', 'start_time', 'processing_complete', 'agent_session_id', 'decision_session_id']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
                st.stop()
        except:
            pass  # If state doesn't exist yet, continue
    
    # Early exit: Check ALL state files to see if this PDF already has a decision
    # This prevents restarting agent if user clicked approve/reject
    state_dir = Path("state")
    if state_dir.exists():
        for session_file in state_dir.glob("*.json"):
            try:
                existing_state = state_manager.load_state(session_file.stem)
                # Check if this is the same PDF and already has a decision
                if (existing_state and 
                    existing_state.pdf_path == pdf_path and 
                    existing_state.human_decision):
                    # Decision already made for this PDF, skip processing block
                    st.session_state['selected_session_id'] = existing_state.session_id
                    for key in ['process_pdf_path', 'processing_started', 'agent_thread', 'start_time', 'processing_complete', 'agent_session_id']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
                    st.stop()
            except:
                continue  # Skip invalid state files
    
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
        # Guard: Check if a decision was already made for this PDF
        # Look for existing sessions with this PDF path that have a decision
        state_dir = Path("state")
        if state_dir.exists():
            for session_file in state_dir.glob("*.json"):
                try:
                    existing_state = state_manager.load_state(session_file.stem)
                    if (existing_state and 
                        existing_state.pdf_path == pdf_path and 
                        existing_state.human_decision):
                        # Decision already exists, don't start new processing
                        st.session_state['selected_session_id'] = existing_state.session_id
                        for key in ['process_pdf_path', 'processing_started', 'agent_thread', 'start_time', 'processing_complete']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
                        st.stop()
                except:
                    continue
        
        st.session_state['processing_started'] = True
        st.session_state['agent_session_id'] = None
        st.session_state['thread_error'] = None
        st.session_state['start_time'] = time.time()
        
        # Start processing in background thread
        def run_agent():
            try:
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
                
                # Don't access st.session_state from thread - causes ScriptRunContext warnings
                # Main thread will detect session via file system polling
                
            except Exception as e:
                import traceback
                # Store error in a file instead of session_state
                error_file = Path("state") / "error.txt"
                with open(error_file, 'w') as f:
                    f.write(f"ERROR: {str(e)}\n\nTRACEBACK:\n{traceback.format_exc()}")
        
        thread = threading.Thread(target=run_agent, daemon=True)
        thread.start()
        st.session_state['agent_thread'] = thread
    
    # Check for errors (now stored in file)
    error_file = Path("state") / "error.txt"
    if error_file.exists():
        with open(error_file, 'r') as f:
            error_content = f.read()
        
        error_lines = error_content.split('\n')
        error_msg = error_lines[0].replace('ERROR: ', '') if error_lines else 'Unknown error'
        traceback_text = '\n'.join(error_lines[2:]) if len(error_lines) > 2 else 'No traceback available'
        
        status_box.error(f"❌ Error: {error_msg}")
        with st.expander("Show Details"):
            st.code(traceback_text)
        if st.button("⬅️ Back to Approvals"):
            # Clean up error file
            error_file.unlink()
            for key in ['process_pdf_path', 'processing_started', 'thread_error', 'agent_thread', 'start_time']:
                if key in st.session_state:
                    del st.session_state[key]
            st.switch_page("pages/approvals.py")
        st.stop()
    
    # Poll for state file updates
    state_dir = Path("state")
    elapsed = time.time() - st.session_state.get('start_time', time.time())
    
    if state_dir.exists():
        sessions = sorted(
            state_dir.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if sessions:
            # If agent has finished and set session ID, use that
            if st.session_state.get('agent_session_id'):
                latest_session = st.session_state['agent_session_id']
                status_box.success(f"✅ Session: {latest_session[:12]}...")
            else:
                # Look for newest session created after we started
                start_time = st.session_state.get('start_time', time.time())
                recent_session = None
                
                for session_file in sessions:
                    file_mtime = session_file.stat().st_mtime
                    if file_mtime >= start_time - 2:  # Created around when we started (2s buffer)
                        recent_session = session_file.stem
                        break
                
                if recent_session:
                    latest_session = recent_session
                    # Once we find the session, track it in session_state
                    st.session_state['agent_session_id'] = recent_session
                    status_box.info(f"🔄 Processing session: {latest_session[:12]}...")
                else:
                    # IMPORTANT: Don't show old session data when starting fresh processing
                    # Just wait for the new session to be created
                    if elapsed > 30:
                        status_box.error(f"⚠️ Session creation taking longer than expected ({int(elapsed)}s)")
                    else:
                        status_box.info(f"⏳ Initializing AI agents... ({int(elapsed)}s)")
                    time.sleep(2)
                    st.rerun()
                    latest_session = None
            
            if latest_session:
                try:
                    state = state_manager.load_state(latest_session)
                    # Critical check: If decision already made, exit processing block immediately
                    if state and state.human_decision:
                        # Decision exists, transition to session viewer
                        st.session_state['selected_session_id'] = latest_session
                        for key in ['process_pdf_path', 'processing_started', 'agent_thread', 'start_time', 'processing_complete', 'agent_session_id']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
                        st.stop()
                except Exception as e:
                    status_box.warning(f"⏳ Loading session data... ({int(elapsed)}s)")
                    time.sleep(2)
                    st.rerun()
                    state = None
            else:
                state = None
            
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
                    completed = len([s for s in state.completed_steps if s])
                    total_actions = len(state.agent_decisions) if state.agent_decisions else 0
                    st.metric("Actions", total_actions, delta=f"{completed} tools used")
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
                
                # PROMINENT ALERT when human review is needed - BEFORE tabs
                if state.requires_human_review and not state.human_decision:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); padding: 20px; border-radius: 10px; margin: 15px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.2); animation: pulse 2s infinite;">
                        <h3 style="color: white; margin: 0 0 8px 0; font-size: 18px;">⚠️ ACTION REQUIRED: Human Review Needed</h3>
                        <p style="color: rgba(255,255,255,0.95); margin: 0; font-size: 14px;">✅ AI analysis finished! Scroll down to review findings and approve/reject.</p>
                    </div>
                    <style>
                    @keyframes pulse {
                        0%, 100% { opacity: 1; }
                        50% { opacity: 0.9; }
                    }
                    </style>
                    """, unsafe_allow_html=True)
                
                # Main content in tabs for compactness
                tab1, tab2, tab3, tab4 = st.tabs(["📋 Activity", "✅ Results", "💬 Messages", "📊 Details"])
                
                with tab1:
                    # Clear activity timeline showing what's happening
                    st.markdown("### 🔄 Current Workflow Progress")
                    
                    # IMPORTANT: Show human review request prominently at the top
                    if state.requires_human_review and not state.human_decision:
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                            <h3 style="color: white; margin: 0 0 8px 0; font-size: 18px;">⏸️ WORKFLOW PAUSED - Human Review Required</h3>
                            <p style="color: rgba(255,255,255,0.95); margin: 0; font-size: 14px;">✅ AI processing finished! Check the <strong>Results</strong> tab to review findings and make your decision.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Show completed steps first
                    if state.completed_steps:
                        st.markdown("**✅ Completed:**")
                        step_icons = {
                            'extract_from_pdf': '📄 Extracted company data from PDF',
                            'search_registry': '🔍 Verified company in business registry',
                            'check_sanctions': '🚨 Checked sanctions lists',
                            'compute_risk': '📊 Calculated risk score',
                            'explain_risk': '🧠 Generated AI risk explanation'
                        }
                        for step in state.completed_steps:
                            st.markdown(f"- {step_icons.get(step, step.replace('_', ' ').title())}")
                        
                        # Show when workflow handed over to human
                        if state.requires_human_review:
                            st.markdown("- ⏸️ **Workflow paused → Awaiting human review**")
                        
                        st.markdown("---")
                    
                    # Show what's currently happening
                    if state.requires_human_review and not state.human_decision:
                        # Show which agent completed before pausing
                        if state.current_agent:
                            agent_names = {
                                'extractor': 'Extractor',
                                'verifier': 'Verifier', 
                                'risk_analyst': 'Risk Analyst'
                            }
                            agent_name = agent_names.get(state.current_agent, state.current_agent)
                            st.warning(f"**Last Active:** {agent_name} → ⏸️ **Paused for Human Review**")
                        else:
                            st.warning(f"**Currently Active:** 👤 Human reviewer (awaiting decision)")
                    elif state.current_agent:
                        agent_status = {
                            'extractor': '📄 Extracting company information from PDF...',
                            'verifier': '🔍 Verifying company details and checking sanctions...',
                            'risk_analyst': '📊 Analyzing risk factors and computing scores...'
                        }
                        st.info(f"**Currently Active:** {agent_status.get(state.current_agent, f'{state.current_agent} is working...')}")
                    
                    # Show recent agent reasoning (last 3 decisions)
                    if state.agent_decisions:
                        st.markdown("**📋 Recent Agent Actions:**")
                        recent_decisions = list(reversed(state.agent_decisions[-3:]))  # Show newest first
                        
                        for i, decision in enumerate(recent_decisions):
                            agent_colors = {
                                'coordinator': '#2563eb',
                                'extractor': '#10b981', 
                                'verifier': '#f59e0b',
                                'risk_analyst': '#ef4444'
                            }
                            agent_color = agent_colors.get(decision.agent_id, '#6366f1')
                            
                            # Create agent emoji mapping
                            agent_emoji = {
                                'coordinator': '🎯',
                                'extractor': '📄',
                                'verifier': '🔍',
                                'risk_analyst': '📊'
                            }
                            emoji = agent_emoji.get(decision.agent_id, '🤖')
                            
                            # Show what tools were used
                            tools_used = ""
                            if decision.tool_calls:
                                tool_names = []
                                for tool in decision.tool_calls:
                                    if isinstance(tool, dict):
                                        fn = tool.get('function', '')
                                        if fn == 'extract_from_pdf':
                                            tool_names.append('PDF Extraction')
                                        elif fn == 'search_registry':
                                            tool_names.append('Registry Search')
                                        elif fn == 'check_sanctions':
                                            tool_names.append('Sanctions Check')
                                        elif fn == 'compute_risk':
                                            tool_names.append('Risk Calculation')
                                        elif fn == 'explain_risk':
                                            tool_names.append('Risk Explanation')
                                        else:
                                            tool_names.append(fn.replace('_', ' ').title())
                                if tool_names:
                                    tools_used = f" → Used: {', '.join(tool_names)}"
                            
                            agent_name = decision.agent_id.replace('_', ' ').title()
                            
                            with st.expander(f"{emoji} {agent_name}{tools_used}", expanded=(i==0)):
                                reasoning_text = decision.reasoning[:300] + "..." if len(decision.reasoning) > 300 else decision.reasoning
                                st.markdown(f"""
                                <div style="background: #f9fafb; padding: 12px; border-left: 3px solid {agent_color}; border-radius: 4px; font-size: 13px; line-height: 1.6;">
                                    {reasoning_text.replace(chr(10), '<br>')}
                                </div>
                                """, unsafe_allow_html=True)
                    
                    if not state.agent_decisions and not state.completed_steps:
                        st.info("⏳ Workflow is starting...")
                
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
                            # Display summary (main explanation)
                            summary_text = state.risk_explanation.summary[:300] + "..." if len(state.risk_explanation.summary) > 300 else state.risk_explanation.summary
                            st.text(summary_text)
                            
                            # Show key factors if available
                            if state.risk_explanation.key_factors:
                                st.markdown("**Key Factors:**")
                                for factor in state.risk_explanation.key_factors[:3]:  # Show first 3
                                    st.text(f"• {factor}")
                            
                            # Show recommendation if available
                            if state.risk_explanation.recommendation:
                                st.markdown("**Recommendation:**")
                                rec_text = state.risk_explanation.recommendation[:200] + "..." if len(state.risk_explanation.recommendation) > 200 else state.risk_explanation.recommendation
                                st.text(rec_text)
                
                # Human Review Section - OUTSIDE tabs, always visible at bottom
                if state.requires_human_review and not state.human_decision:
                    st.markdown("---")
                    # Make human review section very prominent
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); padding: 25px; border-radius: 10px; margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                        <h2 style="color: white; margin: 0 0 10px 0;">⚠️ Human Review Required</h2>
                        <p style="color: rgba(255,255,255,0.95); margin: 0; font-size: 16px;">Your decision is required to proceed.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if state.review_reason:
                        # Clean up review reason text to remove redundant "complete" phrase
                        review_text = state.review_reason
                        # Remove "complete - " pattern (e.g., "Risk assessment complete - human approval required" -> "human approval required")
                        if "complete - " in review_text.lower():
                            parts = review_text.split("complete - ", 1)
                            review_text = parts[1].strip() if len(parts) > 1 else review_text
                        elif " - " in review_text and "complete" in review_text.lower():
                            # Handle other patterns like "something complete - something"
                            parts = review_text.split(" - ", 1)
                            if "complete" in parts[0].lower():
                                review_text = parts[1].strip() if len(parts) > 1 else review_text
                        if review_text:
                            st.markdown(f"""
                            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                                <strong>Review Reason:</strong> {review_text}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Review decision buttons
                    review_col1, review_col2, review_col3, review_col4 = st.columns([1, 1, 1, 3])
                    
                    with review_col1:
                        if st.button("✅ Approve", type="primary", use_container_width=True, key="human_approve"):
                            # Update state with human decision
                            state.human_decision = "approved"
                            state_manager.save_state(state)
                            
                            # Generate access recommendation directly (no need for agent instance)
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
                            
                            # Set flag to prevent restart on rerun
                            st.session_state['decision_just_made'] = True
                            st.session_state['decision_session_id'] = state.session_id
                            st.session_state['agent_session_id'] = state.session_id  # Also set this for early exit check
                            
                            # Clean up processing state before rerun (but keep agent_session_id for now)
                            st.session_state['selected_session_id'] = state.session_id
                            for key in ['process_pdf_path', 'processing_started', 'agent_thread', 'start_time', 'processing_complete']:
                                if key in st.session_state:
                                    del st.session_state[key]
                            
                            st.success("✅ Approved! Generating access recommendation...")
                            st.rerun()
                    
                    with review_col2:
                        if st.button("❌ Reject", use_container_width=True, key="human_reject"):
                            state.human_decision = "rejected"
                            state.workflow_complete = True
                            state_manager.save_state(state)
                            
                            # Update database
                            if 'current_submission_id' in st.session_state:
                                db.mark_submission_status(st.session_state['current_submission_id'], 'rejected')
                            
                            # Set flag to prevent restart on rerun
                            st.session_state['decision_just_made'] = True
                            st.session_state['decision_session_id'] = state.session_id
                            st.session_state['agent_session_id'] = state.session_id  # Also set this for early exit check
                            
                            # Clean up processing state before rerun (but keep agent_session_id for now)
                            st.session_state['selected_session_id'] = state.session_id
                            for key in ['process_pdf_path', 'processing_started', 'agent_thread', 'start_time', 'processing_complete']:
                                if key in st.session_state:
                                    del st.session_state[key]
                            
                            st.warning("❌ Rejected")
                            st.rerun()
                    
                    with review_col3:
                        if st.button("📋 Request Info", use_container_width=True, key="human_request_info"):
                            state.human_decision = "request_more_info"
                            state.workflow_complete = True
                            state_manager.save_state(state)
                            
                            # Set flag to prevent restart on rerun
                            st.session_state['decision_just_made'] = True
                            st.session_state['decision_session_id'] = state.session_id
                            st.session_state['agent_session_id'] = state.session_id  # Also set this for early exit check
                            
                            # Clean up processing state before rerun (but keep agent_session_id for now)
                            st.session_state['selected_session_id'] = state.session_id
                            for key in ['process_pdf_path', 'processing_started', 'agent_thread', 'start_time', 'processing_complete']:
                                if key in st.session_state:
                                    del st.session_state[key]
                            
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
                        status_box.success("✅ AI Processing Complete - Review Required Below ⬇️")
                        # Clean up processing state but keep session selected
                        st.session_state['selected_session_id'] = latest_session
                        if 'processing_started' in st.session_state:
                            del st.session_state['processing_started']
                        if 'agent_thread' in st.session_state:
                            del st.session_state['agent_thread']
                        if 'processing_complete' in st.session_state:
                            del st.session_state['processing_complete']
                        # IMPORTANT: Don't delete 'process_pdf_path' yet - we need to stay in this block
                        # to show the human review UI. Only delete it after human makes a decision.
                        
                        # Reload state to ensure we have the latest (with human review flag)
                        try:
                            state = state_manager.load_state(latest_session)
                        except:
                            pass  # Use existing state if reload fails
                        
                        # Stop auto-refresh - human review UI is now visible
                        st.stop()
                else:
                    # Still processing
                    status_box.info("🔄 Processing... Auto-refreshing every 2 seconds")
                    time.sleep(2)
                    st.rerun()
    
    # Fallback status
    elapsed = time.time() - st.session_state.get('start_time', time.time())
    if not state_dir.exists() or not sessions:
        if elapsed > 30:
            status_box.error(f"⚠️ Still waiting after {int(elapsed)}s. There may be an issue.")
            if st.button("⬅️ Cancel and Return"):
                for key in ['process_pdf_path', 'processing_started', 'agent_thread', 'start_time']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.switch_page("pages/approvals.py")
        else:
            status_box.info(f"⏳ Starting AI agents... ({int(elapsed)}s)")
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
        
        # Human Review Section - Only show if NOT in live processing mode
        # (Live processing block has its own human review section)
        if state.requires_human_review and not state.human_decision and 'process_pdf_path' not in st.session_state:
            st.markdown("---")
            # Make human review section very prominent
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); padding: 25px; border-radius: 10px; margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                <h2 style="color: white; margin: 0 0 10px 0;">⚠️ Human Review Required</h2>
                <p style="color: rgba(255,255,255,0.95); margin: 0; font-size: 16px;">Your decision is required to proceed.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if state.review_reason:
                # Clean up review reason text to remove redundant "complete" phrase
                review_text = state.review_reason
                # Remove "complete - " pattern (e.g., "Risk assessment complete - human approval required" -> "human approval required")
                if "complete - " in review_text.lower():
                    parts = review_text.split("complete - ", 1)
                    review_text = parts[1].strip() if len(parts) > 1 else review_text
                elif " - " in review_text and "complete" in review_text.lower():
                    # Handle other patterns like "something complete - something"
                    parts = review_text.split(" - ", 1)
                    if "complete" in parts[0].lower():
                        review_text = parts[1].strip() if len(parts) > 1 else review_text
                if review_text:
                    st.markdown(f"""
                    <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                        <strong>Review Reason:</strong> {review_text}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Review decision buttons
            review_col1, review_col2, review_col3, review_col4 = st.columns([1, 1, 1, 3])
            
            with review_col1:
                if st.button("✅ Approve", type="primary", use_container_width=True, key="human_approve_main"):
                    # Update state with human decision
                    state.human_decision = "approved"
                    state_manager.save_state(state)
                    
                    # Generate access recommendation directly (no need for agent instance)
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
                    
                    # Set flag to prevent restart on rerun
                    st.session_state['decision_just_made'] = True
                    st.session_state['decision_session_id'] = state.session_id
                    
                    st.success("✅ Approved! Generating access recommendation...")
                    st.rerun()
            
            with review_col2:
                if st.button("❌ Reject", use_container_width=True, key="human_reject_main"):
                    state.human_decision = "rejected"
                    state.workflow_complete = True
                    state_manager.save_state(state)
                    
                    # Update database
                    if 'current_submission_id' in st.session_state:
                        db.mark_submission_status(st.session_state['current_submission_id'], 'rejected')
                    
                    # Set flag to prevent restart on rerun
                    st.session_state['decision_just_made'] = True
                    st.session_state['decision_session_id'] = state.session_id
                    
                    st.warning("❌ Rejected")
                    st.rerun()
            
            with review_col3:
                if st.button("📋 Request Info", use_container_width=True, key="human_request_info_main"):
                    state.human_decision = "request_more_info"
                    state.workflow_complete = True
                    state_manager.save_state(state)
                    
                    # Set flag to prevent restart on rerun
                    st.session_state['decision_just_made'] = True
                    st.session_state['decision_session_id'] = state.session_id
                    
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
