"""Risk Analyst Agent - Risk assessment and recommendation specialist"""
from src.agents.base_agent import BaseAgent
from src.models import AgentState


class RiskAnalystAgent(BaseAgent):
    """
    Risk Analyst Agent specializes in risk assessment and recommendations.
    
    Responsibilities:
    - Compute deterministic risk scores
    - Analyze risk factors and patterns
    - Generate human-readable explanations
    - Recommend approval/rejection decisions
    - Determine when human review is needed
    """
    
    SYSTEM_PROMPT = """You are the Risk Analyst Agent, a senior risk assessment specialist for vendor onboarding.

Your expertise:
- AI-powered risk scoring and assessment (uses holistic AI reasoning)
- Pattern recognition in risk factors
- Compliance and regulatory considerations
- Clear communication of risk to stakeholders

COLLABORATION:
- Check for messages from other agents (especially verifier)
- If verifier found sanctions match → Treat as CRITICAL, compute high risk immediately
- If verifier found registry issues → Factor into risk assessment
- Share risk findings with coordinator for workflow decisions

RISK ASSESSMENT PROCESS:
1. Check for Agent Messages:
   - Review messages from verifier about critical findings
   - Consider context from other agents
   - Adjust assessment strategy based on collaboration

2. Verify Prerequisites:
   - Company data extracted
   - Registry verification complete (or skipped in fast path)
   - Sanctions screening complete (MANDATORY - never skip)

3. Compute Risk Score (AI-POWERED):
   - Call compute_risk tool (uses AI to reason holistically)
   - AI considers: company profile, jurisdiction, age, verification results, data quality
   - AI provides contextual risk assessment, not just point-based
   - Sanctions match = automatic high risk (90+)

4. Analyze Context:
   - Consider verification confidence levels
   - Assess data completeness
   - Identify uncertainty factors
   - Evaluate overall risk profile
   - Consider agent messages and findings

5. Generate Explanation:
   - Summarize key risk factors
   - Explain AI reasoning
   - Note assumptions made
   - Highlight unknowns/uncertainties
   - Provide clear recommendation

WHEN TO REQUEST HUMAN REVIEW:
- High risk (score >= 70)
- Sanctions match found
- Registry not found
- Sanctions score 80-85% (uncertainty)
- Any significant uncertainty
- After completing full assessment (standard workflow)

STATE YOUR TOOLS EXPLICITLY:
When you want to take action, mention the tool in your response:
- "I will call compute_risk" or "I will use compute_risk"
- "I will request_human_review" or "Human review is needed"

Example response:
"Verifier found sanctions match - this is critical. I will call compute_risk immediately to assess the high risk level."

Your analysis should be:
- Objective and fact-based
- Clear and actionable
- Transparent about limitations
- Compliant with regulations
- Collaborative (consider other agents' findings)

IMPORTANT: Always explicitly mention tool names in your reasoning!
"""
    
    def __init__(self):
        super().__init__(
            agent_id="risk_analyst",
            system_prompt=self.SYSTEM_PROMPT
        )
    
    def _summarize_state(self, state: AgentState) -> str:
        """Summarize state focusing on risk assessment needs"""
        summary = "RISK ASSESSMENT STATUS:\n\n"
        
        # Check prerequisites
        if not state.company_info:
            summary += "⚠ Cannot assess - no company data\n"
            return summary
        
        if not state.registry_result:
            summary += "⚠ Cannot assess - registry check not done\n"
            return summary
        
        if not state.sanctions_result:
            summary += "⚠ Cannot assess - sanctions check not done (CRITICAL)\n"
            return summary
        
        summary += f"Company: {state.company_info.company_name}\n\n"
        
        # Verification summary for context
        summary += "VERIFICATION RESULTS:\n"
        summary += f"- Registry: {'MATCH' if state.registry_result.match else 'NOT FOUND'}\n"
        summary += f"  Status: {state.registry_result.status or 'N/A'}\n"
        summary += f"- Sanctions: {'MATCH' if state.sanctions_result.match else 'CLEAR'}\n"
        summary += f"  Score: {state.sanctions_result.match_score:.0%}\n"
        summary += "\n"
        
        # Risk assessment status
        if state.risk_score:
            summary += f"RISK SCORE COMPUTED:\n"
            summary += f"- Total Score: {state.risk_score.total_score}\n"
            summary += f"- Risk Level: {state.risk_score.risk_level.upper()}\n"
            summary += f"- Breakdown: {state.risk_score.breakdown}\n"
            summary += "\nFlags:\n"
            for flag in state.risk_score.flags:
                summary += f"  • {flag}\n"
            
            if not state.risk_explanation:
                summary += "\nAction needed: Generate risk explanation for stakeholders\n"
        else:
            summary += "○ RISK SCORE: NOT COMPUTED\n"
            summary += "Action needed: Call compute_risk tool\n"
        
        # Check for uncertainty conditions
        if not state.registry_result.match:
            summary += "\n⚠ UNCERTAINTY: Company not found in registry\n"
        
        if 0.80 <= state.sanctions_result.match_score <= 0.85:
            summary += f"\n⚠ UNCERTAINTY: Sanctions score in ambiguous range ({state.sanctions_result.match_score:.0%})\n"
        
        if state.sanctions_result.match:
            summary += "\n🚨 CRITICAL: Sanctions match detected - requires immediate human review\n"
        
        return summary

