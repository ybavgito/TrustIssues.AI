# TrustIssues AI - Complete Code Explanation

## 📁 Project Structure

```
trustissues-ai/
├── main.py                 # Entry point
├── src/
│   ├── agent.py           # Main orchestrator (RiskLensAgent)
│   ├── cli.py             # Command-line interface
│   ├── models.py          # Data structures (Pydantic models)
│   ├── state_manager.py   # Save/load workflow state
│   │
│   ├── agents/            # AI Agents (Nemotron-powered)
│   │   ├── base_agent.py      # Base class for all agents
│   │   ├── coordinator.py     # Orchestrates workflow
│   │   ├── extractor.py       # Extracts PDF data
│   │   ├── verifier.py        # Verifies company legitimacy
│   │   ├── risk_analyst.py    # Calculates and explains risk
│   │   └── communication.py   # Agent-to-agent messaging
│   │
│   └── tools/             # Tools agents can call
│       ├── pdf_extractor.py      # Reads PDFs
│       ├── registry_checker.py    # Checks company registries
│       ├── sanctions_checker.py   # Screens sanctions lists
│       ├── risk_calculator.py     # Computes risk scores
│       ├── risk_explainer.py      # AI explanations
│       └── access_recommender.py  # Generates access permissions
```

---

## 🚀 1. Entry Point: `main.py`

**What it does:** Starts the application

```python
# main.py
from dotenv import load_dotenv
load_dotenv()  # Loads NVIDIA_API_KEY from .env

from src.cli import main
main()  # Starts CLI interface
```

**Flow:**
1. Loads environment variables (API keys)
2. Adds project to Python path
3. Calls CLI to start interactive interface

---

## 🎯 2. CLI Interface: `src/cli.py`

**What it does:** Handles user interaction and displays results

### Key Functions:

#### `main()` - Entry point
```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf', help='PDF file to process')
    args = parser.parse_args()
    
    cli = CLI()
    cli.run(args.pdf)  # Process the PDF
```

#### `run()` - Processes a vendor PDF
```python
def run(self, pdf_path: str):
    # Initialize agent system
    agent = RiskLensAgent(state_manager)
    
    # Run agentic workflow
    state = agent.run(pdf_path)
    
    # Show human review if needed
    if state.requires_human_review:
        self._human_review_interface(state)
```

#### `_human_review_interface()` - Shows review screen
```python
def _human_review_interface(self, state: AgentState):
    # Display all agent reasoning
    # Show company info, verification results, risk assessment
    # Ask human: Approve (1), Reject (2), or Request More Info (3)
    
    decision = input("Your decision (1-3): ")
    state.human_decision = decision_map[decision]
    
    if decision == "1":  # Approved
        # Resume workflow to generate access
        state = agent.run(pdf_path, session_id)
        self._display_final_results(state)
```

---

## 🧠 3. Core Orchestrator: `src/agent.py`

**What it does:** The main brain that coordinates all agents

### `RiskLensAgent` Class

#### Initialization
```python
def __init__(self, state_manager: StateManager):
    # Create 4 specialist agents
    self.coordinator = CoordinatorAgent()
    self.extractor = ExtractorAgent()
    self.verifier = VerificationAgent()
    self.risk_analyst = RiskAnalystAgent()
    
    # Create tools (agents call these)
    self.pdf_extractor = PDFExtractor()
    self.registry_checker = RegistryChecker()
    self.sanctions_checker = SanctionsChecker()
    self.risk_calculator = RiskCalculator()
    self.risk_explainer = RiskExplainer()
    self.access_recommender = AccessRecommender()
```

#### Main Loop: `run()`
```python
def run(self, pdf_path: str, session_id: Optional[str] = None):
    # 1. Initialize or load state
    state = AgentState(session_id=session_id, pdf_path=pdf_path)
    
    # 2. Agentic Loop (ReAct pattern)
    while not state.workflow_complete:
        # OBSERVE: Print current state
        self._print_state_summary(state)
        
        # REASON: Coordinator decides who acts next
        next_agent_id, reasoning = self._agentic_planning(state)
        
        # ACT: Specialist agent reasons and calls tools
        agent = self._get_agent(next_agent_id)
        decision = agent.reason(state)
        
        # EXECUTE: Run tools agent chose
        for tool_call in decision.tool_calls:
            self._execute_tool_call(tool_call, state, next_agent_id)
        
        # Check if human review needed
        if state.requires_human_review:
            break
    
    return state
```

#### `_agentic_planning()` - Coordinator decides next agent
```python
def _agentic_planning(self, state: AgentState):
    # Coordinator agent reasons about current state
    decision = self.coordinator.reason(state)
    
    # Parse which agent to delegate to
    next_agent = self._infer_next_agent(state, decision.reasoning)
    
    return next_agent, decision.reasoning
```

#### `_infer_next_agent()` - Determines workflow progression
```python
def _infer_next_agent(self, state: AgentState, reasoning: str):
    # Priority based on STATE (not keywords)
    
    if not state.company_info:
        return "extractor"  # Need data first
    
    if state.company_info and not state.registry_result:
        return "verifier"  # Need verification
    
    if state.registry_result and not state.risk_score:
        return "risk_analyst"  # Need risk assessment
    
    return None  # Done
```

#### `_execute_tool_call()` - Runs tools agents request
```python
def _execute_tool_call(self, tool_call: dict, state: AgentState, agent_id: str):
    function_name = tool_call['function']
    arguments = tool_call.get('arguments', {})
    
    if function_name == "extract_from_pdf":
        result = self.pdf_extractor.extract_from_pdf(state.pdf_path)
        state.company_info = CompanyInfo(**result.data)
    
    elif function_name == "search_registry":
        result = self.registry_checker.search_registry(state.company_info)
        state.registry_result = RegistryResult(**result.data)
    
    elif function_name == "check_sanctions":
        result = self.sanctions_checker.check_sanctions(state.company_info)
        state.sanctions_result = SanctionsResult(**result.data)
    
    elif function_name == "compute_risk":
        result = self.risk_calculator.compute_risk(
            state.company_info,
            state.registry_result,
            state.sanctions_result
        )
        state.risk_score = RiskScore(**result.data)
    
    # ... more tools
```

---

## 📊 4. Data Models: `src/models.py`

**What it does:** Defines all data structures using Pydantic

### Key Models:

#### `CompanyInfo` - Extracted company data
```python
class CompanyInfo(BaseModel):
    company_name: Optional[str] = None
    registration_number: Optional[str] = None
    incorporation_date: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    bank_account: Optional[str] = None
    business_type: Optional[str] = None
```

#### `AgentState` - Complete workflow state
```python
class AgentState(BaseModel):
    session_id: str
    pdf_path: str
    
    # Workflow data
    company_info: Optional[CompanyInfo] = None
    registry_result: Optional[RegistryResult] = None
    sanctions_result: Optional[SanctionsResult] = None
    risk_score: Optional[RiskScore] = None
    risk_explanation: Optional[RiskExplanation] = None
    access_recommendation: Optional[AccessRecommendation] = None
    
    # Agent tracking
    agent_decisions: list[AgentDecision] = []
    agent_messages: list[AgentMessage] = []
    current_agent: Optional[str] = None
    
    # Human review
    requires_human_review: bool = False
    human_decision: Optional[str] = None
    human_notes: Optional[str] = None
    
    # Status
    workflow_complete: bool = False
    completed_steps: list[str] = []
```

#### `AgentDecision` - What an agent decided to do
```python
class AgentDecision(BaseModel):
    agent_id: str
    reasoning: str  # Why agent made this decision
    tool_calls: list[dict]  # Tools agent wants to call
    confidence: float  # How confident (0.0-1.0)
    requests_human_review: bool
```

---

## 🤖 5. Base Agent: `src/agents/base_agent.py`

**What it does:** Base class that all agents inherit from

### Key Methods:

#### `__init__()` - Sets up Nemotron client
```python
def __init__(self, agent_id: str, system_prompt: str):
    self.agent_id = agent_id
    self.system_prompt = system_prompt
    
    # Initialize NVIDIA Nemotron API
    self.api_key = os.getenv("NVIDIA_API_KEY")
    self.client = OpenAI(
        api_key=self.api_key,
        base_url="https://integrate.api.nvidia.com/v1"
    )
    self.model = "nvidia/llama-3.3-nemotron-super-49b-v1.5"
```

#### `reason()` - Agent thinks and decides
```python
def reason(self, state: AgentState) -> AgentDecision:
    # 1. Build context for AI
    context = self._build_context(state)
    
    # 2. Call Nemotron API
    response = self.client.chat.completions.create(
        model=self.model,
        messages=[
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context}
        ],
        temperature=0.3,
        max_tokens=1500
    )
    
    # 3. Get AI reasoning
    reasoning = response.choices[0].message.content
    
    # 4. Parse tool calls from reasoning text
    tool_calls = self._parse_tool_calls_from_text(reasoning)
    
    # 5. Return decision
    return AgentDecision(
        agent_id=self.agent_id,
        reasoning=reasoning,
        tool_calls=tool_calls,
        confidence=self._estimate_confidence(reasoning, tool_calls)
    )
```

#### `_parse_tool_calls_from_text()` - Extracts tool names
```python
def _parse_tool_calls_from_text(self, reasoning: str) -> list[dict]:
    tool_calls = []
    reasoning_lower = reasoning.lower()
    
    # Map keywords to tool names
    tool_map = {
        'extract_from_pdf': 'extract_from_pdf',
        'search_registry': 'search_registry',
        'check_sanctions': 'check_sanctions',
        'compute_risk': 'compute_risk',
    }
    
    # Check if agent mentioned any tools
    for keyword, tool_name in tool_map.items():
        if keyword in reasoning_lower:
            tool_calls.append({
                'id': f"call_{len(tool_calls)}",
                'function': tool_name,
                'arguments': {}
            })
    
    return tool_calls
```

---

## 🎯 6. Specialist Agents

### Coordinator Agent: `src/agents/coordinator.py`

**Role:** Decides which specialist should work next

```python
class CoordinatorAgent(BaseAgent):
    SYSTEM_PROMPT = """You are the Coordinator Agent.
    
    Your job: Decide which specialist agent should act next.
    
    Available agents:
    - extractor: Extracts data from PDFs
    - verifier: Verifies company legitimacy
    - risk_analyst: Calculates and explains risk
    
    Look at current state and delegate appropriately.
    """
    
    def _summarize_state(self, state: AgentState) -> str:
        # Summarize what's been done and what's missing
        return f"""
        Current State:
        - Company data: {'Extracted' if state.company_info else 'Not extracted'}
        - Registry check: {'Done' if state.registry_result else 'Pending'}
        - Sanctions check: {'Done' if state.sanctions_result else 'Pending'}
        - Risk assessment: {'Done' if state.risk_score else 'Pending'}
        """
```

### Extractor Agent: `src/agents/extractor.py`

**Role:** Extracts company data from PDFs

```python
class ExtractorAgent(BaseAgent):
    SYSTEM_PROMPT = """You are the Extractor Agent.
    
    Your job: Extract company information from PDF documents.
    
    When you see a PDF, explicitly state:
    "I will call extract_from_pdf"
    
    After extraction, check if data is complete.
    """
    
    def _summarize_state(self, state: AgentState) -> str:
        if state.company_info:
            return f"Company already extracted: {state.company_info.company_name}"
        return "No company data extracted yet. PDF available for extraction."
```

### Verification Agent: `src/agents/verifier.py`

**Role:** Verifies company legitimacy

```python
class VerificationAgent(BaseAgent):
    SYSTEM_PROMPT = """You are the Verification Agent.
    
    Your job: Verify company legitimacy.
    
    Always check BOTH:
    1. "I will call search_registry" - Check company registration
    2. "I will call check_sanctions" - Screen against sanctions lists
    
    NEVER call extract_from_pdf - that's the Extractor's job!
    """
```

### Risk Analyst Agent: `src/agents/risk_analyst.py`

**Role:** Calculates risk and explains it

```python
class RiskAnalystAgent(BaseAgent):
    SYSTEM_PROMPT = """You are the Risk Analyst Agent.
    
    Your job: Calculate risk score and explain it.
    
    Steps:
    1. "I will call compute_risk" - Calculate deterministic score
    2. Review the score and explain why it's high/medium/low
    3. "I will call request_human_review" - Request human approval
    """
```

---

## 🛠️ 7. Tools

### PDF Extractor: `src/tools/pdf_extractor.py`

**What it does:** Reads PDF and extracts structured data

```python
class PDFExtractor:
    def extract_from_pdf(self, pdf_path: str) -> ToolResult:
        # 1. Read PDF file
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        
        # 2. Parse text to extract fields
        company_info = CompanyInfo(
            company_name=self._extract_field(text, "Company Name"),
            registration_number=self._extract_field(text, "Registration"),
            # ... more fields
        )
        
        # 3. Return result
        return ToolResult(
            tool_name="extract_from_pdf",
            success=True,
            data=company_info.model_dump()
        )
```

### Registry Checker: `src/tools/registry_checker.py`

**What it does:** Checks if company exists in registries

```python
class RegistryChecker:
    def __init__(self):
        # Mock registry data (or real API key)
        self.mock_registry = {
            "ACME Corporation": {
                "match": True,
                "status": "active",
                "confidence": 0.95
            }
        }
    
    def search_registry(self, company_info: CompanyInfo) -> ToolResult:
        # Check mock data or call real API
        if company_info.company_name in self.mock_registry:
            result = RegistryResult(**self.mock_registry[company_info.company_name])
        else:
            # 70% random match for unknown companies
            result = RegistryResult(match=random.random() < 0.7)
        
        return ToolResult(
            tool_name="search_registry",
            success=True,
            data=result.model_dump()
        )
```

### Sanctions Checker: `src/tools/sanctions_checker.py`

**What it does:** Screens company against sanctions lists

```python
class SanctionsChecker:
    def __init__(self):
        # Load sanctions list from file
        self.sanctions_list = self._load_sanctions()
        self.match_threshold = 85  # 85% similarity = match
    
    def check_sanctions(self, company_info: CompanyInfo) -> ToolResult:
        company_name = company_info.company_name
        
        # Fuzzy match against all sanctioned entities
        best_score = 0
        best_match = None
        
        for sanctioned in self.sanctions_list:
            score = fuzz.ratio(company_name.lower(), sanctioned["name"].lower())
            if score > best_score:
                best_score = score
                best_match = sanctioned
        
        # Determine if match
        if best_score >= self.match_threshold:
            result = SanctionsResult(
                match=True,
                matched_name=best_match["name"],
                list_name=best_match["list"],
                match_score=best_score / 100.0
            )
        else:
            result = SanctionsResult(match=False)
        
        return ToolResult(
            tool_name="check_sanctions",
            success=True,
            data=result.model_dump()
        )
```

### Risk Calculator: `src/tools/risk_calculator.py`

**What it does:** Computes deterministic risk score

```python
class RiskCalculator:
    def compute_risk(
        self,
        company_info: CompanyInfo,
        registry_result: RegistryResult,
        sanctions_result: SanctionsResult
    ) -> ToolResult:
        score = 0
        breakdown = {}
        flags = []
        
        # CRITICAL: Sanctions match = automatic HIGH risk
        if sanctions_result.match:
            score = 90
            flags.append("CRITICAL: Sanctions list match")
            return RiskScore(
                total_score=score,
                risk_level='high',
                breakdown={'sanctions_match': 90},
                flags=flags
            )
        
        # Registry match: +30 points
        if registry_result.match:
            score += 30
            breakdown['registry_match'] = 30
            flags.append("✓ Company found in registry")
        
        # Active status: +20 points
        if registry_result.status == 'active':
            score += 20
            breakdown['active_status'] = 20
            flags.append("✓ Company status: ACTIVE")
        
        # Company age >= 3 years: +15 points
        if company_info.incorporation_date:
            age_years = (datetime.now() - parse_date(company_info.incorporation_date)).days / 365.25
            if age_years >= 3:
                score += 15
                breakdown['age_3y'] = 15
                flags.append(f"✓ Company age: {age_years:.1f} years")
        
        # Determine risk level
        if score >= 70:
            risk_level = 'high'
        elif score >= 40:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return RiskScore(
            total_score=score,
            risk_level=risk_level,
            breakdown=breakdown,
            flags=flags
        )
```

### Risk Explainer: `src/tools/risk_explainer.py`

**What it does:** Uses AI to explain risk in natural language

```python
class RiskExplainer:
    def explain_risk(self, risk_score: RiskScore, state: AgentState) -> ToolResult:
        # Build context for AI
        context = f"""
        Risk Score: {risk_score.total_score}/100
        Risk Level: {risk_score.risk_level}
        
        Breakdown:
        {json.dumps(risk_score.breakdown, indent=2)}
        
        Flags:
        {chr(10).join(risk_score.flags)}
        
        Company: {state.company_info.company_name}
        Registry: {'Verified' if state.registry_result.match else 'Not found'}
        Sanctions: {'CLEAR' if not state.sanctions_result.match else 'MATCH FOUND'}
        """
        
        # Call Nemotron to generate explanation
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Explain risk assessment in natural language"},
                {"role": "user", "content": context}
            ]
        )
        
        explanation_text = response.choices[0].message.content
        
        # Parse explanation into structured format
        explanation = RiskExplanation(
            summary=self._extract_summary(explanation_text),
            key_factors=self._extract_factors(explanation_text),
            recommendation=self._extract_recommendation(explanation_text)
        )
        
        return ToolResult(
            tool_name="explain_risk",
            success=True,
            data=explanation.model_dump()
        )
```

### Access Recommender: `src/tools/access_recommender.py`

**What it does:** Generates least-privilege access permissions

```python
class AccessRecommender:
    def recommend_access(
        self,
        risk_score: RiskScore,
        human_decision: str,
        human_notes: str = None
    ) -> ToolResult:
        # Only generate if approved
        if human_decision != 'approved':
            return ToolResult(
                success=True,
                data={
                    'access_level': 'none',
                    'permissions': [],
                    'restrictions': ['Access denied']
                }
            )
        
        # Get policy based on risk level
        policy = self.access_policies[risk_score.risk_level].copy()
        
        # Adjust for sanctions
        if 'sanctions' in str(risk_score.flags).lower():
            policy['level'] = 'read_only'
            policy['permissions'] = ['view_public_info']
        
        recommendation = AccessRecommendation(
            access_level=policy['level'],
            permissions=policy['permissions'],
            restrictions=policy['restrictions'],
            justification=policy['justification']
        )
        
        return ToolResult(
            tool_name="recommend_access",
            success=True,
            data=recommendation.model_dump()
        )
```

---

## 💾 8. State Manager: `src/state_manager.py`

**What it does:** Saves and loads workflow state

```python
class StateManager:
    def __init__(self, state_dir: str = "state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
    
    def save_state(self, state: AgentState):
        """Save state to JSON file"""
        file_path = self.state_dir / f"{state.session_id}.json"
        with open(file_path, 'w') as f:
            json.dump(state.model_dump(), f, indent=2)
    
    def load_state(self, session_id: str) -> AgentState:
        """Load state from JSON file"""
        file_path = self.state_dir / f"{session_id}.json"
        with open(file_path, 'r') as f:
            data = json.load(f)
        return AgentState(**data)
```

---

## 🔄 Complete Flow Example

```
1. USER RUNS:
   python3 main.py --pdf vendor.pdf
   
   ↓
   
2. main.py → cli.py.run()
   
   ↓
   
3. cli.py creates RiskLensAgent → agent.run(pdf_path)
   
   ↓
   
4. agent.py LOOP:
   
   ITERATION 1:
   ├─ Coordinator.reason() → "Delegate to extractor"
   ├─ Extractor.reason() → "I'll call extract_from_pdf"
   ├─ agent._execute_tool_call("extract_from_pdf")
   │  └─ pdf_extractor.extract_from_pdf() → CompanyInfo
   └─ state.company_info = CompanyInfo(...)
   
   ITERATION 2:
   ├─ Coordinator.reason() → "Delegate to verifier"
   ├─ Verifier.reason() → "I'll call search_registry and check_sanctions"
   ├─ agent._execute_tool_call("search_registry")
   │  └─ registry_checker.search_registry() → RegistryResult
   ├─ agent._execute_tool_call("check_sanctions")
   │  └─ sanctions_checker.check_sanctions() → SanctionsResult
   └─ state.registry_result = RegistryResult(...)
       state.sanctions_result = SanctionsResult(...)
   
   ITERATION 3:
   ├─ Coordinator.reason() → "Delegate to risk_analyst"
   ├─ RiskAnalyst.reason() → "I'll call compute_risk"
   ├─ agent._execute_tool_call("compute_risk")
   │  └─ risk_calculator.compute_risk() → RiskScore
   └─ state.risk_score = RiskScore(...)
       state.requires_human_review = True
   
   ↓
   
5. agent.run() returns state → cli.py._human_review_interface()
   
   ↓
   
6. Human sees review screen, enters "1" (approve)
   
   ↓
   
7. cli.py → agent.run(pdf_path, session_id) [resume]
   
   ↓
   
8. agent.py detects approval → access_recommender.recommend_access()
   
   ↓
   
9. cli.py._display_final_results() → Shows access permissions
```

---

## 🎯 Key Design Patterns

### 1. **ReAct Pattern** (Reason → Act)
```
OBSERVE → REASON → ACT → OBSERVE → ...
```

### 2. **Multi-Agent Collaboration**
- Coordinator orchestrates
- Specialists do their jobs
- Agents communicate via messages

### 3. **Tool-Based Architecture**
- Agents decide which tools to use
- Tools are independent functions
- Easy to add new tools

### 4. **State-Driven Workflow**
- State object tracks everything
- Agents check state to decide actions
- State persists to disk

---

## 🔑 Key Files Summary

| File | Purpose | Key Classes/Functions |
|------|---------|---------------------|
| `main.py` | Entry point | Starts CLI |
| `cli.py` | User interface | `run()`, `_human_review_interface()` |
| `agent.py` | Orchestrator | `RiskLensAgent.run()`, `_execute_tool_call()` |
| `models.py` | Data structures | `AgentState`, `CompanyInfo`, `RiskScore` |
| `base_agent.py` | Agent base class | `reason()`, `_parse_tool_calls_from_text()` |
| `coordinator.py` | Workflow manager | `CoordinatorAgent` |
| `extractor.py` | PDF extraction | `ExtractorAgent` |
| `verifier.py` | Verification | `VerificationAgent` |
| `risk_analyst.py` | Risk assessment | `RiskAnalystAgent` |
| `pdf_extractor.py` | PDF tool | `PDFExtractor.extract_from_pdf()` |
| `registry_checker.py` | Registry tool | `RegistryChecker.search_registry()` |
| `sanctions_checker.py` | Sanctions tool | `SanctionsChecker.check_sanctions()` |
| `risk_calculator.py` | Risk tool | `RiskCalculator.compute_risk()` |
| `access_recommender.py` | Access tool | `AccessRecommender.recommend_access()` |
| `state_manager.py` | Persistence | `StateManager.save_state()`, `load_state()` |

---

**That's the complete codebase!** Every file, every function, every flow explained. 🚀

