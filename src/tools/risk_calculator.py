"""AI-Powered risk scoring engine"""
import os
import json
from datetime import datetime
from dateutil import parser
from openai import OpenAI
from src.models import RiskScore, ToolResult, CompanyInfo, RegistryResult, SanctionsResult


class RiskCalculator:
    """Computes risk scores using AI reasoning (agentic) with deterministic fallback"""
    
    def __init__(self):
        # Fallback rules (used if AI fails)
        self.fallback_rules = {
            'registry_match': 30,
            'registry_active': 20,
            'incorporation_age_3y': 15,
            'sanctions_match': 90,
            'address_mismatch': -10,
            'first_time_bank': -10,
        }
        
        # Initialize AI client for agentic risk assessment
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            self.model = "nvidia/llama-3.3-nemotron-super-49b-v1.5"
            self.use_ai = True
        else:
            self.use_ai = False
    
    def compute_risk(
        self,
        company_info: CompanyInfo,
        registry_result: RegistryResult,
        sanctions_result: SanctionsResult,
        flags: dict = None
    ) -> ToolResult:
        """
        Compute risk score using AI reasoning (agentic approach)
        
        Uses NVIDIA Nemotron to reason holistically about risk factors,
        considering context, patterns, and relationships between factors.
        Falls back to deterministic rules if AI is unavailable.
        
        Risk levels:
        >= 70: high
        40-69: medium
        < 40: low
        """
        try:
            flags = flags or {}
            
            # CRITICAL: Sanctions match = automatic HIGH risk (non-negotiable)
            if sanctions_result.match:
                return self._handle_sanctions_match(sanctions_result)
            
            # Use AI-powered risk assessment if available
            if self.use_ai:
                return self._ai_compute_risk(company_info, registry_result, sanctions_result, flags)
            else:
                # Fallback to deterministic rules
                return self._deterministic_compute_risk(company_info, registry_result, sanctions_result, flags)
        
        except Exception as e:
            # Fallback on any error
            return self._deterministic_compute_risk(company_info, registry_result, sanctions_result, flags or {})
    
    def _handle_sanctions_match(self, sanctions_result: SanctionsResult) -> ToolResult:
        """Handle sanctions match - automatic HIGH risk"""
        result = RiskScore(
            total_score=90,
            risk_level='high',
            breakdown={'sanctions_match': 90},
            flags=[f"CRITICAL: Sanctions list match ({sanctions_result.matched_name})"]
        )
        return ToolResult(
            tool_name="compute_risk",
            success=True,
            data=result.model_dump(),
            next_action="explain_risk"
        )
    
    def _ai_compute_risk(
        self,
        company_info: CompanyInfo,
        registry_result: RegistryResult,
        sanctions_result: SanctionsResult,
        flags: dict
    ) -> ToolResult:
        """AI-powered risk assessment using Nemotron"""
        
        # Build comprehensive context
        context = self._build_risk_context(company_info, registry_result, sanctions_result, flags)
        
        prompt = f"""You are an expert risk analyst for vendor onboarding. Analyze the following company profile and assess the overall risk.

{context}

Consider:
- Company legitimacy (registry verification, age, status)
- Jurisdiction risk (country, regulatory environment)
- Business profile (industry, type, operations)
- Data completeness and quality
- Any red flags or suspicious indicators
- Context and patterns (e.g., UK tech company in 2024 vs Iranian company in 2020)

Provide a risk assessment in JSON format:
{{
  "score": <0-100 integer>,
  "risk_level": "low" | "medium" | "high",
  "breakdown": {{
    "factor_name": <points>,
    ...
  }},
  "flags": ["flag1", "flag2", ...],
  "reasoning": "Brief explanation of risk assessment"
}}

Be holistic - consider all factors together, not just individual points. A well-established UK tech company should score lower than a new offshore shell company, even if both have similar individual factors."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional risk analyst. Provide structured risk assessments in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Low temperature for consistent scoring
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            
            # Parse AI response
            try:
                # Try to extract JSON from response
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "{" in content:
                    json_start = content.find("{")
                    json_end = content.rfind("}") + 1
                    content = content[json_start:json_end]
                
                data = json.loads(content)
                
                score = int(data.get('score', 0))
                risk_level = data.get('risk_level', 'medium')
                breakdown = data.get('breakdown', {})
                flags = data.get('flags', [])
                reasoning = data.get('reasoning', '')
                
                # Ensure score is in valid range
                score = max(0, min(100, score))
                
                # Ensure risk_level matches score
                if score >= 70:
                    risk_level = 'high'
                elif score >= 40:
                    risk_level = 'medium'
                else:
                    risk_level = 'low'
                
                # Add AI reasoning to flags
                if reasoning:
                    flags.append(f"AI Reasoning: {reasoning}")
                
                result = RiskScore(
                    total_score=score,
                    risk_level=risk_level,
                    breakdown=breakdown,
                    flags=flags
                )
                
                return ToolResult(
                    tool_name="compute_risk",
                    success=True,
                    data=result.model_dump(),
                    next_action="explain_risk"
                )
            
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # If JSON parsing fails, fall back to deterministic
                return self._deterministic_compute_risk(company_info, registry_result, sanctions_result, flags)
        
        except Exception as e:
            # Fallback on API error
            return self._deterministic_compute_risk(company_info, registry_result, sanctions_result, flags)
    
    def _build_risk_context(
        self,
        company_info: CompanyInfo,
        registry_result: RegistryResult,
        sanctions_result: SanctionsResult,
        flags: dict
    ) -> str:
        """Build comprehensive context for AI risk assessment"""
        
        # Calculate company age
        age_info = ""
        if company_info.incorporation_date:
            try:
                inc_date = parser.parse(company_info.incorporation_date)
                age_years = (datetime.now() - inc_date).days / 365.25
                age_info = f"Company Age: {age_years:.1f} years"
            except:
                age_info = "Company Age: Unknown"
        
        context = f"""COMPANY PROFILE:
- Name: {company_info.company_name or 'Unknown'}
- Registration: {company_info.registration_number or 'Not provided'}
- Country: {company_info.country or 'Unknown'}
- Business Type: {company_info.business_type or 'Unknown'}
- {age_info}
- Address: {company_info.address or 'Not provided'}

VERIFICATION RESULTS:
- Registry Match: {'YES' if registry_result.match else 'NO'}
- Registry Status: {registry_result.status or 'Unknown'}
- Registry Confidence: {registry_result.confidence:.0%}
- Sanctions Check: {'CLEAR' if not sanctions_result.match else 'MATCH FOUND'}

DATA QUALITY:
- Complete Registration: {'Yes' if company_info.registration_number else 'No'}
- Complete Address: {'Yes' if company_info.address else 'No'}
- Complete Banking: {'Yes' if company_info.bank_account else 'No'}
- Complete Contact: {'Yes' if company_info.contact_email else 'No'}

ADDITIONAL FLAGS:
{chr(10).join(f"- {k}: {v}" for k, v in flags.items()) if flags else "- None"}
"""
        return context
    
    def _deterministic_compute_risk(
        self,
        company_info: CompanyInfo,
        registry_result: RegistryResult,
        sanctions_result: SanctionsResult,
        flags: dict
    ) -> ToolResult:
        """Fallback deterministic risk calculation"""
        score = 0
        breakdown = {}
        score_flags = []
        
        # Registry match
        if registry_result.match:
            score += self.fallback_rules['registry_match']
            breakdown['registry_match'] = self.fallback_rules['registry_match']
            score_flags.append("✓ Company found in registry")
        else:
            score_flags.append("✗ Company NOT found in registry (major risk)")
        
        # Registry status
        if registry_result.status == 'active':
            score += self.fallback_rules['registry_active']
            breakdown['registry_active'] = self.fallback_rules['registry_active']
            score_flags.append("✓ Company status: ACTIVE")
        elif registry_result.status == 'dissolved':
            score_flags.append("✗ Company status: DISSOLVED")
        elif registry_result.status == 'inactive':
            score_flags.append("⚠ Company status: INACTIVE")
        
        # Incorporation age
        if company_info.incorporation_date or registry_result.incorporation_date:
            inc_date_str = company_info.incorporation_date or registry_result.incorporation_date
            try:
                inc_date = parser.parse(inc_date_str)
                age_years = (datetime.now() - inc_date).days / 365.25
                
                if age_years >= 3:
                    score += self.fallback_rules['incorporation_age_3y']
                    breakdown['incorporation_age_3y'] = self.fallback_rules['incorporation_age_3y']
                    score_flags.append(f"✓ Company age: {age_years:.1f} years (>= 3 years)")
                else:
                    score_flags.append(f"⚠ Company age: {age_years:.1f} years (< 3 years)")
            except:
                score_flags.append("⚠ Could not determine company age")
        
        # Address mismatch flag
        if flags.get('address_mismatch', False):
            score += self.fallback_rules['address_mismatch']
            breakdown['address_mismatch'] = self.fallback_rules['address_mismatch']
            score_flags.append("✗ Address mismatch detected (-10 points)")
        
        # First time bank details flag
        if flags.get('first_time_bank_details', False):
            score += self.fallback_rules['first_time_bank']
            breakdown['first_time_bank'] = self.fallback_rules['first_time_bank']
            score_flags.append("⚠ First-time bank details (-10 points)")
        
        # Determine risk level
        if score >= 70:
            risk_level = 'high'
        elif score >= 40:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        result = RiskScore(
            total_score=score,
            risk_level=risk_level,
            breakdown=breakdown,
            flags=score_flags
        )
        
        return ToolResult(
            tool_name="compute_risk",
            success=True,
            data=result.model_dump(),
            next_action="explain_risk"
        )

