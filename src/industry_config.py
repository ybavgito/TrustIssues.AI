"""Industry-specific risk assessment configuration"""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class IndustryProfile:
    """Profile defining risk characteristics for an industry"""
    name: str
    min_age_concern: float  # Years - below this is concerning
    optimal_age_range: tuple[float, float]  # Years - typical range
    must_have_docs: List[str]  # Required documentation
    high_risk_indicators: List[str]  # Keywords that increase risk
    low_risk_indicators: List[str]  # keywords that decrease risk
    weight_multipliers: Dict[str, float]  # Adjust standard weights
    regulatory_strictness: str  # 'low', 'medium', 'high', 'critical'
    typical_risk_level: str  # 'low', 'medium', 'high'
    common_red_flags: List[str]  # Industry-specific warnings


# Industry-specific configurations
INDUSTRY_PROFILES = {
    'technology': IndustryProfile(
        name='Technology',
        min_age_concern=0.0,  # Young companies are normal in tech
        optimal_age_range=(0.5, 5.0),
        must_have_docs=[],  # Flexible requirements
        high_risk_indicators=[
            'crypto', 'cryptocurrency', 'blockchain', 'ico', 'token',
            'gambling', 'adult content', 'vpn', 'proxy'
        ],
        low_risk_indicators=[
            'saas', 'software', 'cloud', 'api', 'enterprise',
            'b2b', 'productivity', 'analytics', 'security'
        ],
        weight_multipliers={
            'age': 0.5,  # Age matters less
            'registry': 1.2,  # Still need to be registered
            'innovation': 1.3  # Innovation is expected
        },
        regulatory_strictness='medium',
        typical_risk_level='medium',
        common_red_flags=[
            'No website or GitHub presence',
            'Vague business model',
            'ICO or token sale without proper licensing'
        ]
    ),
    
    'finance': IndustryProfile(
        name='Financial Services',
        min_age_concern=3.0,  # Should be established
        optimal_age_range=(5.0, 50.0),
        must_have_docs=[
            'banking_license', 'financial_license', 'fca_approval',
            'aml_compliance', 'kyc_policy', 'audited_financials'
        ],
        high_risk_indicators=[
            'offshore', 'high_cash', 'unregulated', 'unlicensed',
            'payday_loan', 'high_interest', 'debt_collection'
        ],
        low_risk_indicators=[
            'bank', 'licensed', 'regulated', 'fca', 'sec', 'audited',
            'established', 'tier_1', 'member_fdic'
        ],
        weight_multipliers={
            'age': 1.8,  # Age matters significantly
            'regulatory': 2.5,  # Regulation is critical
            'sanctions': 3.0  # Sanctions are deal-breaker
        },
        regulatory_strictness='critical',
        typical_risk_level='high',
        common_red_flags=[
            'No financial services license',
            'Less than 3 years established',
            'Missing AML/KYC documentation',
            'Offshore registration without proper licensing'
        ]
    ),
    
    'construction': IndustryProfile(
        name='Construction',
        min_age_concern=5.0,  # Long establishment expected
        optimal_age_range=(5.0, 30.0),
        must_have_docs=[
            'liability_insurance', 'workers_comp', 'bonding',
            'safety_certification', 'contractor_license', 'osha_compliance'
        ],
        high_risk_indicators=[
            'unlicensed', 'no_insurance', 'no_bond', 'safety_violations',
            'recent_accidents', 'litigation'
        ],
        low_risk_indicators=[
            'licensed', 'bonded', 'insured', 'safety_record',
            'certifications', 'iso_certified', 'leed'
        ],
        weight_multipliers={
            'age': 2.0,  # Age matters a lot
            'certifications': 2.0,  # Critical for construction
            'insurance': 2.5  # Must be insured
        },
        regulatory_strictness='high',
        typical_risk_level='high',
        common_red_flags=[
            'No liability insurance',
            'No contractor license',
            'Recent safety violations',
            'Less than 5 years experience'
        ]
    ),
    
    'healthcare': IndustryProfile(
        name='Healthcare',
        min_age_concern=3.0,
        optimal_age_range=(3.0, 40.0),
        must_have_docs=[
            'medical_license', 'hipaa_compliance', 'accreditation',
            'malpractice_insurance', 'facility_license', 'provider_credentials'
        ],
        high_risk_indicators=[
            'unlicensed', 'non_accredited', 'malpractice_history',
            'hipaa_violations', 'medicare_fraud'
        ],
        low_risk_indicators=[
            'licensed', 'accredited', 'jcaho', 'certified', 'board_certified',
            'hospital_privileges', 'medicare_approved'
        ],
        weight_multipliers={
            'age': 1.5,
            'regulatory': 2.5,  # Healthcare is highly regulated
            'licensing': 3.0,  # Licenses are mandatory
            'data_security': 2.0  # HIPAA compliance critical
        },
        regulatory_strictness='critical',
        typical_risk_level='high',
        common_red_flags=[
            'No medical licenses',
            'Missing HIPAA compliance documentation',
            'No malpractice insurance',
            'History of regulatory violations'
        ]
    ),
    
    'manufacturing': IndustryProfile(
        name='Manufacturing',
        min_age_concern=5.0,
        optimal_age_range=(5.0, 50.0),
        must_have_docs=[
            'quality_certification', 'iso_certification', 'environmental_permits',
            'safety_compliance', 'product_liability_insurance'
        ],
        high_risk_indicators=[
            'environmental_violations', 'product_recalls', 'safety_issues',
            'supply_chain_disruption', 'quality_problems'
        ],
        low_risk_indicators=[
            'iso_certified', 'quality_control', 'established_supply_chain',
            'environmental_compliance', 'safety_record', 'lean_manufacturing'
        ],
        weight_multipliers={
            'age': 1.7,
            'certifications': 2.0,
            'supply_chain': 1.5
        },
        regulatory_strictness='high',
        typical_risk_level='medium',
        common_red_flags=[
            'No ISO or quality certifications',
            'Environmental compliance issues',
            'Product recall history',
            'Unreliable supply chain'
        ]
    ),
    
    'retail': IndustryProfile(
        name='Retail & E-commerce',
        min_age_concern=1.0,
        optimal_age_range=(1.0, 20.0),
        must_have_docs=[
            'business_license', 'sales_tax_permit', 'pci_compliance'
        ],
        high_risk_indicators=[
            'counterfeit', 'gray_market', 'dropshipping_unverified',
            'high_return_rate', 'payment_disputes', 'fraud_complaints'
        ],
        low_risk_indicators=[
            'established_brand', 'verified_supplier', 'positive_reviews',
            'pci_compliant', 'secure_payment', 'transparent_returns'
        ],
        weight_multipliers={
            'age': 1.0,  # Age matters moderately
            'reputation': 1.8,  # Reputation is key
            'payment_security': 1.5
        },
        regulatory_strictness='medium',
        typical_risk_level='medium',
        common_red_flags=[
            'High customer complaint rate',
            'Payment security issues',
            'Selling counterfeit goods',
            'Unclear return policy'
        ]
    ),
    
    'consulting': IndustryProfile(
        name='Professional Services & Consulting',
        min_age_concern=1.0,
        optimal_age_range=(1.0, 30.0),
        must_have_docs=[
            'professional_license', 'liability_insurance', 'credentials'
        ],
        high_risk_indicators=[
            'unlicensed', 'no_credentials', 'litigation_history',
            'client_complaints', 'unverified_claims'
        ],
        low_risk_indicators=[
            'licensed', 'certified', 'accredited', 'professional_body_member',
            'client_references', 'case_studies', 'established_reputation'
        ],
        weight_multipliers={
            'age': 1.0,
            'credentials': 2.0,  # Credentials are important
            'reputation': 1.8
        },
        regulatory_strictness='medium',
        typical_risk_level='low',
        common_red_flags=[
            'No professional credentials',
            'Missing liability insurance',
            'No client references',
            'Exaggerated claims'
        ]
    ),
    
    'logistics': IndustryProfile(
        name='Logistics & Transportation',
        min_age_concern=3.0,
        optimal_age_range=(3.0, 40.0),
        must_have_docs=[
            'carrier_license', 'cargo_insurance', 'dot_compliance',
            'vehicle_insurance', 'safety_ratings'
        ],
        high_risk_indicators=[
            'safety_violations', 'uninsured', 'unlicensed',
            'delivery_failures', 'cargo_claims', 'dot_violations'
        ],
        low_risk_indicators=[
            'licensed_carrier', 'insured', 'safety_rated', 'bonded',
            'tracking_system', 'on_time_delivery', 'certified_drivers'
        ],
        weight_multipliers={
            'age': 1.5,
            'safety': 2.0,  # Safety is critical
            'insurance': 2.0,
            'regulatory': 1.8
        },
        regulatory_strictness='high',
        typical_risk_level='medium',
        common_red_flags=[
            'No DOT compliance',
            'Poor safety ratings',
            'Missing cargo insurance',
            'History of delivery failures'
        ]
    )
}


# Industry benchmarks (typical values for comparison)
INDUSTRY_BENCHMARKS = {
    'technology': {
        'avg_age_years': 3.2,
        'median_age_years': 2.1,
        'avg_risk_score': 48,
        'approval_rate': 0.78,
        'typical_countries': ['US', 'UK', 'Israel', 'India', 'Germany']
    },
    'finance': {
        'avg_age_years': 18.5,
        'median_age_years': 12.0,
        'avg_risk_score': 62,
        'approval_rate': 0.45,
        'typical_countries': ['UK', 'US', 'Switzerland', 'Singapore', 'Luxembourg']
    },
    'construction': {
        'avg_age_years': 15.8,
        'median_age_years': 10.0,
        'avg_risk_score': 58,
        'approval_rate': 0.52,
        'typical_countries': ['US', 'UK', 'Germany', 'Canada', 'Australia']
    },
    'healthcare': {
        'avg_age_years': 12.4,
        'median_age_years': 8.0,
        'avg_risk_score': 55,
        'approval_rate': 0.61,
        'typical_countries': ['US', 'UK', 'Germany', 'Canada', 'Switzerland']
    },
    'manufacturing': {
        'avg_age_years': 22.1,
        'median_age_years': 15.0,
        'avg_risk_score': 52,
        'approval_rate': 0.68,
        'typical_countries': ['China', 'Germany', 'US', 'Japan', 'South Korea']
    },
    'retail': {
        'avg_age_years': 8.3,
        'median_age_years': 5.0,
        'avg_risk_score': 51,
        'approval_rate': 0.72,
        'typical_countries': ['US', 'UK', 'China', 'Germany', 'France']
    },
    'consulting': {
        'avg_age_years': 6.7,
        'median_age_years': 4.0,
        'avg_risk_score': 42,
        'approval_rate': 0.82,
        'typical_countries': ['US', 'UK', 'Germany', 'France', 'Switzerland']
    },
    'logistics': {
        'avg_age_years': 14.2,
        'median_age_years': 9.0,
        'avg_risk_score': 54,
        'approval_rate': 0.64,
        'typical_countries': ['US', 'Germany', 'Netherlands', 'UK', 'Singapore']
    }
}


def detect_industry(business_type: Optional[str], business_description: Optional[str] = None) -> str:
    """
    Detect industry from business type and description
    
    Args:
        business_type: Stated business type
        business_description: Optional business description
        
    Returns:
        Industry key (lowercase) or 'general' if unknown
    """
    if not business_type:
        return 'general'
    
    text = (business_type + ' ' + (business_description or '')).lower()
    
    # Technology
    if any(kw in text for kw in ['tech', 'software', 'saas', 'it', 'cloud', 'app', 'digital', 'cyber']):
        return 'technology'
    
    # Finance
    if any(kw in text for kw in ['bank', 'financ', 'investment', 'trading', 'insurance', 'lending', 'fintech']):
        return 'finance'
    
    # Construction
    if any(kw in text for kw in ['construction', 'building', 'contractor', 'engineering', 'infrastructure']):
        return 'construction'
    
    # Healthcare
    if any(kw in text for kw in ['health', 'medical', 'hospital', 'clinic', 'pharma', 'biotech', 'healthcare']):
        return 'healthcare'
    
    # Manufacturing
    if any(kw in text for kw in ['manufactur', 'production', 'factory', 'industrial', 'assembly']):
        return 'manufacturing'
    
    # Retail
    if any(kw in text for kw in ['retail', 'ecommerce', 'e-commerce', 'shop', 'store', 'merchant', 'marketplace']):
        return 'retail'
    
    # Consulting
    if any(kw in text for kw in ['consult', 'advisory', 'professional services', 'accounting', 'legal', 'audit']):
        return 'consulting'
    
    # Logistics
    if any(kw in text for kw in ['logistic', 'transport', 'shipping', 'freight', 'delivery', 'supply chain']):
        return 'logistics'
    
    return 'general'


def get_industry_profile(industry: str) -> IndustryProfile:
    """Get industry profile, return general profile if not found"""
    return INDUSTRY_PROFILES.get(industry.lower(), INDUSTRY_PROFILES.get('consulting'))  # Consulting as default (most lenient)


def get_industry_benchmark(industry: str) -> Dict:
    """Get industry benchmarks, return empty dict if not found"""
    return INDUSTRY_BENCHMARKS.get(industry.lower(), {})

