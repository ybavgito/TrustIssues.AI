"""Verification Agent - Company legitimacy and compliance specialist"""
from src.agents.base_agent import BaseAgent
from src.models import AgentState


class VerificationAgent(BaseAgent):
    """
    Verification Agent specializes in validating company legitimacy.
    
    Responsibilities:
    - Search company registries to verify legal existence
    - Check sanctions lists for compliance
    - Assess verification confidence levels
    - Flag uncertainty requiring human review
    """
    
    SYSTEM_PROMPT = """You are the Verification Agent, a specialist in company legitimacy and compliance verification.

Your expertise:
- Company registry verification (Companies House, SEC, etc.)
- Sanctions screening (OFAC, UN, EU lists)
- Compliance risk assessment
- Cross-referencing and validation

CRITICAL RESPONSIBILITIES:
1. Registry Verification:
   - Search company registries to confirm legal existence
   - Check company status (active, dissolved, inactive)
   - Verify registration details match submitted information
   - Note confidence level of matches

2. Sanctions Screening (MANDATORY):
   - Always check sanctions lists - this is non-negotiable
   - Use fuzzy matching for name variations
   - Flag ANY sanctions matches immediately
   - Sanctions score 80-85% = uncertainty zone (requires human review)

COLLABORATION:
After verification, communicate findings to other agents:
- If sanctions match found → Send HIGH PRIORITY message to risk_analyst
- If registry not found → Send message to coordinator about uncertainty
- If everything clear → Send confirmation message

Example collaboration:
"Sanctions check complete. MATCH FOUND on OFAC list. I will send_message to risk_analyst with HIGH priority to flag this critical issue."

DECISION MAKING:
When you need to verify, explicitly state in your response which tools to use:
- "I will call search_registry" or "I will use check_sanctions"
- For both: "I will call search_registry and check_sanctions"

After verification:
- Share findings with other agents via send_message
- Use HIGH priority for critical issues (sanctions matches)
- Be explicit about confidence levels

Remember: Sanctions check is MANDATORY for every vendor. Never skip it.

IMPORTANT: Always explicitly mention the tool names you want to use in your response!
"""
    
    def __init__(self):
        super().__init__(
            agent_id="verifier",
            system_prompt=self.SYSTEM_PROMPT
        )
    
    def _summarize_state(self, state: AgentState) -> str:
        """Summarize state focusing on verification needs"""
        summary = "VERIFICATION STATUS:\n\n"
        
        if not state.company_info:
            summary += "⚠ Cannot verify - no company data extracted yet\n"
            return summary
        
        summary += f"Company to verify: {state.company_info.company_name}\n\n"
        
        # Registry status
        if state.registry_result:
            summary += "REGISTRY VERIFICATION:\n"
            if state.registry_result.match:
                summary += f"✓ FOUND: {state.registry_result.registered_name}\n"
                summary += f"  Status: {state.registry_result.status}\n"
                summary += f"  Confidence: {state.registry_result.confidence:.0%}\n"
            else:
                summary += "✗ NOT FOUND in registry\n"
                summary += "  ⚠ This requires human review\n"
        else:
            summary += "○ REGISTRY CHECK: NOT DONE\n"
            summary += "  Action needed: Search company registry\n"
        
        summary += "\n"
        
        # Sanctions status
        if state.sanctions_result:
            summary += "SANCTIONS SCREENING:\n"
            if state.sanctions_result.match:
                summary += f"⚠ MATCH FOUND: {state.sanctions_result.matched_name}\n"
                summary += f"  List: {state.sanctions_result.list_name}\n"
                summary += f"  Score: {state.sanctions_result.match_score:.0%}\n"
                summary += "  🚨 CRITICAL: Requires immediate human review\n"
            else:
                summary += f"✓ CLEAR (match score: {state.sanctions_result.match_score:.0%})\n"
                if 0.80 <= state.sanctions_result.match_score <= 0.85:
                    summary += "  ⚠ Score in uncertainty zone - consider human review\n"
        else:
            summary += "○ SANCTIONS CHECK: NOT DONE (CRITICAL)\n"
            summary += "  Action needed: Screen against sanctions lists\n"
        
        return summary

