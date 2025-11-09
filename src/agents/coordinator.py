"""Coordinator Agent - Master orchestrator for multi-agent workflow"""
from src.agents.base_agent import BaseAgent
from src.models import AgentState


class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent orchestrates the entire vendor onboarding workflow.
    
    Responsibilities:
    - Analyze overall workflow state
    - Decide which specialist agent should act next
    - Coordinate agent handoffs
    - Determine when workflow is complete
    - Request human review when appropriate
    """
    
    SYSTEM_PROMPT = """You are the Coordinator Agent for an AI-powered vendor onboarding system.

Your role is to ADAPTIVELY orchestrate a team of specialist agents:
- Extractor Agent: Extracts company data from PDFs
- Verification Agent: Verifies companies via registry and sanctions checks
- Risk Analyst Agent: Computes risk scores and provides recommendations

═══════════════════════════════════════════════════════════
ADAPTIVE WORKFLOW STRATEGY:
═══════════════════════════════════════════════════════════

You can ADAPT the workflow based on context:

1. FAST PATH (Low-Risk Companies):
   - Well-known Fortune 500 companies
   - Established companies in low-risk countries (UK, US, Germany)
   - Companies with complete data and high confidence
   → Can skip detailed verification, go straight to risk assessment
   → Example: "This is a well-established UK company with complete data. 
               I'll skip detailed verification and delegate to risk_analyst."

2. STANDARD PATH (Normal Cases):
   - Extract → Verify → Risk Assessment
   → Follow normal sequence

3. ENHANCED PATH (High-Risk Indicators):
   - New companies (< 1 year)
   - High-risk countries (Iran, North Korea, etc.)
   - Incomplete data
   - Suspicious patterns
   → Add extra verification steps
   → Request additional information
   → Example: "Company is very new and in high-risk jurisdiction. 
               I'll have verifier do enhanced checks before risk assessment."

4. SHORTCUTS (When Appropriate):
   - If company is clearly on sanctions list → Skip to risk analyst immediately
   - If data is obviously incomplete → Request more info before proceeding
   - If risk is clearly low → Streamline workflow

CRITICAL RULES:
- Sanctions check is ALWAYS MANDATORY (never skip)
- Registry check can be skipped for well-known companies
- Risk assessment is always required
- Human review required for all final decisions

DECISION MAKING:
- Analyze current state and context
- Reason about optimal workflow path
- Decide which agent should act next (or if workflow should adapt)
- Explain your adaptive reasoning

CRITICAL DELEGATION RULES:
- DO NOT delegate to extractor if company_info already exists (extraction is done)
- DO NOT delegate to verifier if both registry_result AND sanctions_result exist (verification is done)
- DO NOT delegate to risk_analyst if risk_score AND risk_explanation exist (risk assessment is done)
- Only delegate to agents whose work is NOT YET COMPLETE

Your response should:
1. Analyze what has been completed (check state summary carefully)
2. Identify what work is still needed
3. Assess the context (low-risk, high-risk, incomplete, etc.)
4. Choose ADAPTIVE strategy (fast path, standard, enhanced)
5. Delegate ONLY to agents whose work is incomplete

To delegate, say in your response:
- "I will send_message to extractor" (ONLY if company_info is missing)
- "I will send_message to verifier" (ONLY if registry_result or sanctions_result is missing)
- "I will send_message to risk_analyst" (ONLY if risk_score or risk_explanation is missing)

Example adaptive responses:
- "Well-established UK company with complete data. Fast path: Skip detailed verification, delegate to risk_analyst."
- "New company in high-risk country. Enhanced path: Verifier should do thorough checks before risk assessment."
- "Company on sanctions list detected. Immediate: Delegate to risk_analyst for high-risk assessment."

IMPORTANT: Be adaptive! Don't always follow the same sequence. Reason about the optimal path!
"""
    
    def __init__(self):
        super().__init__(
            agent_id="coordinator",
            system_prompt=self.SYSTEM_PROMPT
        )
    
    def _summarize_state(self, state: AgentState) -> str:
        """Summarize state for coordinator decision-making"""
        summary = "CURRENT WORKFLOW STATE:\n\n"
        
        # Data extraction status
        if state.company_info:
            summary += f"✓ Company Data: {state.company_info.company_name}\n"
        else:
            summary += "○ Company Data: NOT EXTRACTED\n"
        
        # Verification status
        if state.registry_result:
            status = "MATCH" if state.registry_result.match else "NOT FOUND"
            summary += f"✓ Registry Check: {status} ({state.registry_result.confidence:.0%} confidence)\n"
        else:
            summary += "○ Registry Check: NOT DONE\n"
        
        if state.sanctions_result:
            status = "MATCH FOUND" if state.sanctions_result.match else "CLEAR"
            summary += f"✓ Sanctions Check: {status} (score: {state.sanctions_result.match_score:.0%})\n"
        else:
            summary += "○ Sanctions Check: NOT DONE (CRITICAL - REQUIRED)\n"
        
        # Risk assessment status
        if state.risk_score:
            summary += f"✓ Risk Assessment: {state.risk_score.risk_level.upper()} (score: {state.risk_score.total_score})\n"
        else:
            summary += "○ Risk Assessment: NOT COMPUTED\n"
        
        if state.risk_explanation:
            summary += "✓ Risk Explanation: GENERATED\n"
        else:
            summary += "○ Risk Explanation: NOT GENERATED\n"
        
        # Human review status
        if state.human_decision:
            summary += f"✓ Human Decision: {state.human_decision.upper()}\n"
        elif state.requires_human_review:
            summary += f"⚠ Human Review: REQUIRED - {state.review_reason}\n"
        else:
            summary += "○ Human Review: NOT YET REQUESTED\n"
        
        # Active agents
        if state.agent_decisions:
            last_agent = state.agent_decisions[-1].agent_id
            summary += f"\nLast active agent: {last_agent}\n"
        
        summary += "\nYour task: Decide which agent should act next and why."
        
        return summary

