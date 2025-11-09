"""AI-Powered risk scoring engine with industry-aware assessment"""
import os
import json
from datetime import datetime
from dateutil import parser
from openai import OpenAI
from src.models import RiskScore, ToolResult, CompanyInfo, RegistryResult, SanctionsResult
from src.industry_config import (
    detect_industry, 
    get_industry_profile, 
    get_industry_benchmark,
    IndustryProfile
)


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
        """AI-powered risk assessment using Nemotron with industry awareness"""
        
        # Detect industry
        industry = detect_industry(company_info.business_type, company_info.address)
        industry_profile = get_industry_profile(industry)
        industry_benchmark = get_industry_benchmark(industry)
        
        # Build comprehensive context with industry awareness
        context = self._build_risk_context_with_industry(
            company_info, 
            registry_result, 
            sanctions_result, 
            flags,
            industry_profile,
            industry_benchmark
        )
        
        prompt = f"""You are an expert risk analyst for vendor onboarding with deep knowledge of industry-specific risk factors.

{context}

CRITICAL: Assess risk with INDUSTRY CONTEXT in mind:
- Different industries have different norms (tech startups vs banks vs construction)
- Age expectations vary by industry (1-year tech = OK, 1-year bank = RED FLAG)
- Regulatory requirements differ (finance = strict, consulting = lenient)
- Missing industry-specific documentation is a major red flag

Consider holistically:
1. Company legitimacy (registry, age relative to industry norm, status)
2. Industry-specific risk factors (highlighted above)
3. Jurisdiction risk (country + industry combination)
4. Business profile completeness for this industry
5. Red flags specific to this industry
6. How this company compares to industry benchmarks

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
    
    def _build_risk_context_with_industry(
        self,
        company_info: CompanyInfo,
        registry_result: RegistryResult,
        sanctions_result: SanctionsResult,
        flags: dict,
        industry_profile: IndustryProfile,
        industry_benchmark: dict
    ) -> str:
        """Build comprehensive context with industry-specific insights"""
        
        # Calculate company age
        age_years = None
        age_info = "Company Age: Unknown"
        if company_info.incorporation_date:
            try:
                inc_date = parser.parse(company_info.incorporation_date)
                age_years = (datetime.now() - inc_date).days / 365.25
                age_info = f"Company Age: {age_years:.1f} years"
            except:
                pass
        
        # Age comparison to industry
        age_comparison = ""
        if age_years and industry_benchmark:
            avg_age = industry_benchmark.get('avg_age_years', 0)
            median_age = industry_benchmark.get('median_age_years', 0)
            if age_years < industry_profile.min_age_concern:
                age_comparison = f" ⚠️ BELOW typical for {industry_profile.name} (avg: {avg_age:.1f}y, median: {median_age:.1f}y)"
            elif industry_profile.optimal_age_range[0] <= age_years <= industry_profile.optimal_age_range[1]:
                age_comparison = f" ✓ Within normal range for {industry_profile.name} (avg: {avg_age:.1f}y)"
            else:
                age_comparison = f" → Compared to industry avg: {avg_age:.1f}y, median: {median_age:.1f}y"
        
        context = f"""COMPANY PROFILE:
- Name: {company_info.company_name or 'Unknown'}
- Registration: {company_info.registration_number or 'Not provided'}
- Country: {company_info.country or 'Unknown'}
- Business Type: {company_info.business_type or 'Unknown'}
- {age_info}{age_comparison}
- Address: {company_info.address or 'Not provided'}

INDUSTRY ANALYSIS:
- Detected Industry: {industry_profile.name}
- Regulatory Strictness: {industry_profile.regulatory_strictness.upper()}
- Typical Risk Level: {industry_profile.typical_risk_level.upper()}
- Min Expected Age: {industry_profile.min_age_concern} years
- Optimal Age Range: {industry_profile.optimal_age_range[0]}-{industry_profile.optimal_age_range[1]} years

INDUSTRY-SPECIFIC RED FLAGS:
{chr(10).join(f"  • {flag}" for flag in industry_profile.common_red_flags)}

REQUIRED FOR THIS INDUSTRY:
{chr(10).join(f"  • {doc}" for doc in industry_profile.must_have_docs) if industry_profile.must_have_docs else "  • No specific documentation mandated"}

HIGH-RISK INDICATORS (for this industry):
{chr(10).join(f"  • {indicator}" for indicator in industry_profile.high_risk_indicators[:5])}

VERIFICATION RESULTS:
- Registry Match: {'YES' if registry_result.match else 'NO'}
- Registry Status: {registry_result.status or 'Unknown'}
- Registry Confidence: {registry_result.confidence:.0%}
- Sanctions Check: {'CLEAR' if not sanctions_result.match else 'MATCH FOUND'}

INDUSTRY BENCHMARK COMPARISON:
- Industry Avg Risk Score: {industry_benchmark.get('avg_risk_score', 'N/A')}
- Industry Approval Rate: {industry_benchmark.get('approval_rate', 0)*100:.0f}%
- Typical Countries: {', '.join(industry_benchmark.get('typical_countries', ['N/A'])[:3])}
- This Company's Country: {company_info.country or 'Unknown'} {'✓' if company_info.country in industry_benchmark.get('typical_countries', []) else '⚠️ Less common for this industry'}

DATA QUALITY:
- Complete Registration: {'Yes' if company_info.registration_number else 'No'}
- Complete Address: {'Yes' if company_info.address else 'No'}
- Complete Banking: {'Yes' if company_info.bank_account else 'No'}
- Complete Contact: {'Yes' if company_info.contact_email else 'No'}

ADDITIONAL FLAGS:
{chr(10).join(f"- {k}: {v}" for k, v in flags.items()) if flags else "- None"}
"""
        return context
    
    def _build_risk_context(
        self,
        company_info: CompanyInfo,
        registry_result: RegistryResult,
        sanctions_result: SanctionsResult,
        flags: dict
    ) -> str:
        """Build comprehensive context for AI risk assessment (fallback without industry)"""
        
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

