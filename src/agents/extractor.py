"""Extractor Agent - Data extraction specialist"""
from src.agents.base_agent import BaseAgent
from src.models import AgentState


class ExtractorAgent(BaseAgent):
    """
    Extractor Agent specializes in extracting structured data from documents.
    
    Responsibilities:
    - Extract company information from PDF documents
    - Identify missing or incomplete data fields
    - Request additional information when needed
    - Validate extracted data quality
    """
    
    SYSTEM_PROMPT = """You are the Extractor Agent, a specialist in data extraction for vendor onboarding.

Your expertise:
- Extracting structured company information from PDF documents
- Identifying missing or incomplete data
- Validating data quality and consistency

KEY INFORMATION TO EXTRACT:
- Company name (CRITICAL)
- Registration number
- Incorporation date
- Address
- Contact information (email, phone)
- Business type
- Bank account details

DECISION MAKING:
CRITICAL: ALWAYS CHECK STATE BEFORE CALLING TOOLS!

1. Check if extraction is already done:
   - If state.company_info exists → Data already extracted, DO NOT call extract_from_pdf again
   - If state.company_info is None → Call extract_from_pdf

2. NEVER call search_registry, check_sanctions, or compute_risk - those are other agents' jobs!

3. Only call send_message if you have important information to communicate

When you need to extract data, explicitly state in your response:
- "I will call extract_from_pdf" (ONLY if company_info is None)
- If extraction already done: "Extraction is complete. Company data: {company_name}. No further action needed."

Example response:
"The PDF document is available and company_info is None. I will call extract_from_pdf to get the company information from the document."

After extraction:
- Highlight any missing critical information
- Note data quality concerns
- Defer to coordinator for next steps

Be thorough but efficient. Once data is extracted successfully, your work is done - let other agents handle verification and risk assessment.

IMPORTANT: Always explicitly mention the tool name you want to use in your response!
"""
    
    def __init__(self):
        super().__init__(
            agent_id="extractor",
            system_prompt=self.SYSTEM_PROMPT
        )
    
    def _summarize_state(self, state: AgentState) -> str:
        """Summarize state focusing on extraction needs"""
        summary = "DATA EXTRACTION STATUS:\n\n"
        
        if state.pdf_path:
            summary += f"PDF Document: {state.pdf_path}\n\n"
        
        if state.company_info:
            summary += "EXTRACTED DATA:\n"
            summary += f"- Company Name: {state.company_info.company_name or 'MISSING'}\n"
            summary += f"- Registration #: {state.company_info.registration_number or 'MISSING'}\n"
            summary += f"- Incorporation Date: {state.company_info.incorporation_date or 'MISSING'}\n"
            summary += f"- Address: {state.company_info.address or 'MISSING'}\n"
            summary += f"- Contact Email: {state.company_info.contact_email or 'MISSING'}\n"
            summary += f"- Business Type: {state.company_info.business_type or 'MISSING'}\n"
            
            # Assess completeness
            critical_fields = [
                state.company_info.company_name,
                state.company_info.registration_number,
                state.company_info.address
            ]
            completeness = sum(1 for f in critical_fields if f) / len(critical_fields)
            summary += f"\nData Completeness: {completeness:.0%}\n"
        else:
            summary += "NO DATA EXTRACTED YET\n"
            summary += "Action needed: Extract company information from PDF\n"
        
        return summary

