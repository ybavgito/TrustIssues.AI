"""Data models for RiskLens AI"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class CompanyInfo(BaseModel):
    """Extracted company information from PDF"""
    company_name: Optional[str] = None
    registration_number: Optional[str] = None
    incorporation_date: Optional[str] = None
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    bank_account: Optional[str] = None
    business_type: Optional[str] = None


class RegistryResult(BaseModel):
    """Company registry lookup result"""
    match: bool
    status: Optional[Literal["active", "dissolved", "inactive"]] = None
    registered_name: Optional[str] = None
    registered_address: Optional[str] = None
    incorporation_date: Optional[str] = None
    confidence: float = 0.0


class SanctionsResult(BaseModel):
    """Sanctions check result"""
    match: bool
    matched_name: Optional[str] = None
    list_name: Optional[str] = None
    match_score: float = 0.0
    details: Optional[str] = None


class RiskScore(BaseModel):
    """Computed risk score"""
    total_score: int
    risk_level: Literal["low", "medium", "high"]
    breakdown: dict[str, int] = Field(default_factory=dict)
    flags: list[str] = Field(default_factory=list)


class RiskExplanation(BaseModel):
    """LLM-generated risk explanation"""
    summary: str
    key_factors: list[str]
    assumptions: list[str]
    unknowns: list[str]
    recommendation: str


class AccessRecommendation(BaseModel):
    """Least-privilege access recommendation"""
    access_level: Literal["read_only", "standard", "elevated"]
    permissions: list[str]
    restrictions: list[str]
    justification: str


class AgentMessage(BaseModel):
    """Message passed between agents"""
    sender: str
    receiver: str
    content: str
    priority: Literal["normal", "high"] = "normal"
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentDecision(BaseModel):
    """Record of an agent's reasoning and decision"""
    agent_id: str
    reasoning: str
    action: Optional[str] = None
    tool_calls: list[dict] = Field(default_factory=list)
    confidence: Optional[float] = None
    requests_human_review: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentState(BaseModel):
    """Current state of the agent workflow"""
    # Input
    pdf_path: Optional[str] = None
    
    # Extracted data
    company_info: Optional[CompanyInfo] = None
    
    # Verification results
    registry_result: Optional[RegistryResult] = None
    sanctions_result: Optional[SanctionsResult] = None
    
    # Risk assessment
    risk_score: Optional[RiskScore] = None
    risk_explanation: Optional[RiskExplanation] = None
    
    # Human review
    requires_human_review: bool = False
    review_reason: Optional[str] = None
    human_decision: Optional[Literal["approved", "rejected", "request_more_info"]] = None
    human_notes: Optional[str] = None
    
    # Final recommendation
    access_recommendation: Optional[AccessRecommendation] = None
    
    # Workflow tracking
    completed_steps: list[str] = Field(default_factory=list)
    current_step: Optional[str] = None
    workflow_complete: bool = False
    
    # Multi-agent support
    agent_messages: list[AgentMessage] = Field(default_factory=list)
    agent_decisions: list[AgentDecision] = Field(default_factory=list)
    current_agent: Optional[str] = None
    
    # Metadata
    session_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ToolResult(BaseModel):
    """Result from a tool execution"""
    tool_name: str
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    next_action: Optional[str] = None

