"""LLM-powered risk explanation tool"""
import os
from openai import OpenAI
from src.models import (
    RiskExplanation, ToolResult, CompanyInfo, 
    RegistryResult, SanctionsResult, RiskScore
)


class RiskExplainer:
    """Generates human-readable risk explanations using LLM"""
    
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        
        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY not found in environment")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        self.model = "nvidia/llama-3.3-nemotron-super-49b-v1.5"
    
    def explain_risk(
        self,
        company_info: CompanyInfo,
        registry_result: RegistryResult,
        sanctions_result: SanctionsResult,
        risk_score: RiskScore
    ) -> ToolResult:
        """Generate detailed risk explanation using LLM"""
        try:
            # Build context for LLM
            context = self._build_context(
                company_info, registry_result, sanctions_result, risk_score
            )
            
            # Create prompt
            prompt = f"""You are a risk analyst for an AI-powered vendor onboarding system. 
Analyze the following company assessment and provide a clear, structured risk explanation.

{context}

Provide a structured analysis with:
1. SUMMARY: A 2-3 sentence executive summary of the risk assessment
2. KEY_FACTORS: List 3-5 key factors that influenced the risk score
3. ASSUMPTIONS: List any assumptions made in the assessment
4. UNKNOWNS: List any missing information or uncertainties
5. RECOMMENDATION: A clear recommendation for the approval decision

Be objective, factual, and concise. Format your response as JSON with keys: summary, key_factors (array), assumptions (array), unknowns (array), recommendation."""

            # Call NVIDIA NIM API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional risk analyst. Provide structured, objective assessments in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more deterministic output
                max_tokens=1000
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text parsing
            try:
                import json
                data = json.loads(content)
                explanation = RiskExplanation(
                    summary=data.get('summary', ''),
                    key_factors=data.get('key_factors', []),
                    assumptions=data.get('assumptions', []),
                    unknowns=data.get('unknowns', []),
                    recommendation=data.get('recommendation', '')
                )
            except:
                # Fallback: parse structured text
                explanation = self._parse_text_response(content, risk_score)
            
            return ToolResult(
                tool_name="explain_risk",
                success=True,
                data=explanation.model_dump(),
                next_action="request_human_review"
            )
        
        except Exception as e:
            # Fallback to rule-based explanation if LLM fails
            explanation = self._fallback_explanation(risk_score)
            return ToolResult(
                tool_name="explain_risk",
                success=True,
                data=explanation.model_dump(),
                next_action="request_human_review"
            )
    
    def _build_context(
        self,
        company_info: CompanyInfo,
        registry_result: RegistryResult,
        sanctions_result: SanctionsResult,
        risk_score: RiskScore
    ) -> str:
        """Build context string for LLM"""
        context = f"""COMPANY INFORMATION:
- Name: {company_info.company_name}
- Registration Number: {company_info.registration_number or 'N/A'}
- Incorporation Date: {company_info.incorporation_date or 'N/A'}
- Address: {company_info.address or 'N/A'}
- Business Type: {company_info.business_type or 'N/A'}

REGISTRY VERIFICATION:
- Match Found: {'YES' if registry_result.match else 'NO'}
- Status: {registry_result.status or 'N/A'}
- Confidence: {registry_result.confidence:.0%}

SANCTIONS CHECK:
- Sanctions Match: {'YES - CRITICAL' if sanctions_result.match else 'NO'}
{f"- Matched Entity: {sanctions_result.matched_name}" if sanctions_result.match else ""}
{f"- List: {sanctions_result.list_name}" if sanctions_result.match else ""}

RISK SCORE:
- Total Score: {risk_score.total_score}
- Risk Level: {risk_score.risk_level.upper()}
- Score Breakdown: {risk_score.breakdown}

FLAGS:
{chr(10).join(f"- {flag}" for flag in risk_score.flags)}
"""
        return context
    
    def _parse_text_response(self, content: str, risk_score: RiskScore) -> RiskExplanation:
        """Parse text response into structured format"""
        lines = content.split('\n')
        
        summary = ""
        key_factors = []
        assumptions = []
        unknowns = []
        recommendation = ""
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if 'SUMMARY' in line.upper():
                current_section = 'summary'
            elif 'KEY' in line.upper() and 'FACTOR' in line.upper():
                current_section = 'key_factors'
            elif 'ASSUMPTION' in line.upper():
                current_section = 'assumptions'
            elif 'UNKNOWN' in line.upper():
                current_section = 'unknowns'
            elif 'RECOMMENDATION' in line.upper():
                current_section = 'recommendation'
            elif current_section == 'summary':
                summary += line + " "
            elif current_section == 'key_factors' and line.startswith(('-', '*', '•')):
                key_factors.append(line.lstrip('-*•').strip())
            elif current_section == 'assumptions' and line.startswith(('-', '*', '•')):
                assumptions.append(line.lstrip('-*•').strip())
            elif current_section == 'unknowns' and line.startswith(('-', '*', '•')):
                unknowns.append(line.lstrip('-*•').strip())
            elif current_section == 'recommendation':
                recommendation += line + " "
        
        return RiskExplanation(
            summary=summary.strip() or f"Risk assessment completed with {risk_score.risk_level} risk level.",
            key_factors=key_factors or risk_score.flags,
            assumptions=assumptions or ["Assessment based on available data"],
            unknowns=unknowns or ["Complete business history not available"],
            recommendation=recommendation.strip() or f"{'Recommend rejection' if risk_score.risk_level == 'high' else 'Recommend approval with monitoring'}"
        )
    
    def _fallback_explanation(self, risk_score: RiskScore) -> RiskExplanation:
        """Generate fallback explanation without LLM"""
        if risk_score.risk_level == 'high':
            summary = f"High risk assessment (score: {risk_score.total_score}). This company presents significant concerns that require careful review."
            recommendation = "Recommend rejection or request additional documentation for further verification."
        elif risk_score.risk_level == 'medium':
            summary = f"Medium risk assessment (score: {risk_score.total_score}). This company has some risk factors but may be acceptable with proper monitoring."
            recommendation = "Recommend approval with enhanced monitoring and periodic reviews."
        else:
            summary = f"Low risk assessment (score: {risk_score.total_score}). This company appears to be a legitimate, low-risk entity."
            recommendation = "Recommend approval with standard monitoring procedures."
        
        return RiskExplanation(
            summary=summary,
            key_factors=risk_score.flags,
            assumptions=["Risk score computed using deterministic rules", "Data accuracy depends on source quality"],
            unknowns=["Complete financial history", "Beneficial ownership details", "Ongoing legal proceedings"],
            recommendation=recommendation
        )

