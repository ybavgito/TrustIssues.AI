# RiskLens AI

**Automated Vendor/Client Onboarding with Agentic Multi-Agent System**

RiskLens AI is an intelligent, **Nemotron-powered multi-agent system** that automates vendor onboarding using specialized AI agents that reason, collaborate, and dynamically decide actions. The system extracts company data from PDFs, verifies identity through registry and sanctions checks, computes deterministic risk scores, explains reasoning with AI, and requires human approval before granting least-privilege system access.

## 🚀 NEW: Agentic Multi-Agent Architecture

**This is NOT a simple workflow - it's a true agentic AI system!**

- **4 Specialist Agents**: Coordinator, Extractor, Verifier, Risk Analyst (all Nemotron-powered)
- **Autonomous Reasoning**: Agents reason about what to do next using NVIDIA Nemotron
- **Function Calling**: Agents dynamically choose tools via OpenAI function calling API
- **Agent Collaboration**: Agents communicate findings and coordinate actions
- **Simple RAG**: Agents request additional information when needed
- **Transparent Decisions**: All agent reasoning and tool calls are logged

## 🎯 Key Features

- **ReAct-Style Agents**: Each agent follows Observe → Reason → Act → Communicate
- **Multi-Agent System**: Specialized agents collaborate like a real team
- **Nemotron-Powered**: All decisions driven by NVIDIA Nemotron-70B-Instruct
- **Function Calling**: Agents use OpenAI function calling to invoke tools
- **Human-in-the-Loop**: Mandatory approval before access is granted
- **Deterministic Risk Scoring**: Rule-based scoring (not AI) for compliance
- **LLM Explanations**: Nemotron generates human-readable risk analysis
- **Agent Communication**: Agents send messages and share findings
- **Least-Privilege Access**: Risk-based access recommendations
- **Complete Audit Trail**: All agent decisions and reasoning logged

## 🏗️ Agentic Multi-Agent Architecture

```
┌─────────────┐
│   PDF Input │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│         🎯 COORDINATOR AGENT (Nemotron)                  │
│  Reasons about workflow state, delegates to specialists  │
└──────────────┬───────────────────────────────────────────┘
               │
       ┌───────┼───────┐
       │       │       │
       ▼       ▼       ▼
┌─────────┐ ┌─────────┐ ┌──────────────┐
│📄 EXTRACTOR│ │🔍 VERIFIER│ │📊 RISK ANALYST│
│  Agent   │ │  Agent   │ │   Agent      │
│          │ │          │ │              │
│ Reasons: │ │ Reasons: │ │  Reasons:    │
│ Extract  │ │ Verify   │ │  Assess risk │
│ data     │ │ company  │ │  Explain     │
│          │ │          │ │              │
│ Calls:   │ │ Calls:   │ │  Calls:      │
│ extract_ │ │ search_  │ │  compute_    │
│ from_pdf │ │ registry │ │  risk        │
│          │ │ check_   │ │  request_    │
│          │ │ sanctions│ │  human_review│
└─────┬────┘ └────┬────┘ └──────┬───────┘
      │           │              │
      └───────────┼──────────────┘
                  │ Agent Messages
                  ▼
       ┌──────────────────┐
       │  Agent Messages  │
       │  "Found match"   │
       │  "Risk assessed" │
       └────────┬─────────┘
                │
                ▼
         ┌─────────────┐
         │    State    │
         │  Manager    │
         └──────┬──────┘
                │
                ▼
         ┌─────────────────┐
         │ Human Review    │
         │ (See agent      │
         │  collaboration) │
         └─────────────────┘
```

### Agent Workflow

1. **Coordinator** reasons: "No data extracted → delegate to Extractor"
2. **Extractor** reasons: "PDF available → call extract_from_pdf tool"
3. **Extractor** sends message: "Extraction complete: ACME Corp"
4. **Coordinator** reasons: "Data ready → delegate to Verifier"
5. **Verifier** reasons: "Need registry + sanctions → call both tools"
6. **Verifier** sends message: "Verification done: Match found, no sanctions"
7. **Coordinator** reasons: "Verified → delegate to Risk Analyst"
8. **Risk Analyst** reasons: "Compute risk → explain → request human review"
9. **Human** reviews agent decisions and approves/rejects

## 🔄 Workflow

### Agent Planner Logic (DO NOT CHANGE)

The agent follows this exact decision tree:

1. **If company name not extracted** → `extract_from_pdf`
2. **If registry check not done** → `search_registry`
3. **If sanctions check not done** → `check_sanctions`
4. **If risk not computed** → `compute_risk`
5. **If uncertainty detected** (missing registration OR sanctions score 80-85%) → `request_human_review`
6. **Else** → `explain_risk` → `request_human_review`

### Risk Scoring Rules (Deterministic)

```
+30 points  → Registry match found
+20 points  → Company status is ACTIVE
+15 points  → Incorporation age >= 3 years
>=90 points → Sanctions match (overrides all)
-10 points  → Address mismatch (optional flag)
-10 points  → First-time bank details (optional flag)
```

**Risk Levels:**
- **High Risk**: Score >= 70
- **Medium Risk**: Score 40-69
- **Low Risk**: Score < 40

## 🛠️ Tools

| Tool | Purpose | Technology |
|------|---------|------------|
| `extract_from_pdf()` | Extract structured company data from PDF | PyPDF2 + Regex |
| `search_registry()` | Verify company registration | Mock/API |
| `check_sanctions()` | Fuzzy match against sanctions lists | FuzzyWuzzy |
| `compute_risk()` | Calculate deterministic risk score | Rules Engine |
| `explain_risk()` | Generate human-readable explanation | NVIDIA Nemotron |
| `recommend_access()` | Least-privilege access recommendation | Policy Engine |

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- NVIDIA API key (for Nemotron LLM)

### Setup

1. **Clone the repository**
```bash
cd /Users/vaibhav/Downloads/risklens-ai
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Create .env file
cat > .env << 'EOF'
# NVIDIA NIM API Configuration
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1

# Optional: Real API keys for registry/sanctions
REGISTRY_API_KEY=
SANCTIONS_API_KEY=
EOF
```

5. **Get your NVIDIA API Key**
   - Visit: https://build.nvidia.com/
   - Sign in and navigate to API Keys
   - Create a new API key
   - Copy and paste into `.env` file

6. **Create sample PDFs (optional)**
```bash
python scripts/create_sample_pdfs.py
```

## 🚀 Usage

### Quick Start

Process a vendor PDF document:

```bash
python main.py --pdf data/sample_vendor_acme.pdf
```

### Interactive Mode

Launch the interactive CLI:

```bash
python main.py
```

This will present a menu with options:
1. Process new vendor PDF
2. Review pending cases
3. View completed cases
4. Exit

### Example Workflow

```bash
# Process a legitimate vendor
python main.py --pdf data/sample_vendor_acme.pdf

# Process a suspicious vendor
python main.py --pdf data/sample_vendor_suspicious.pdf
```

## 📊 Human Review Interface

When human review is required, you'll see:

```
╔══════════════════════════════════════════════════════════╗
║           RiskLens AI - Vendor Onboarding               ║
║        Automated Risk Assessment & Verification         ║
╚══════════════════════════════════════════════════════════╝

HUMAN REVIEW REQUIRED

Company Information:
  Name: ACME Corporation
  Registration #: UK-12345678
  ...

Verification Results:
  Registry Check: ✓ MATCH | active | 95%
  Sanctions Check: ✓ CLEAR | N/A | 0%

Risk Assessment:
  Risk Level: LOW
  Risk Score: 65

Risk Analysis:
  Summary: ...
  Key Factors: ...
  Recommendation: ...

DECISION REQUIRED
1. APPROVE - Grant access to vendor
2. REJECT - Deny vendor onboarding
3. REQUEST MORE INFO - Ask for additional documentation

Your decision (1-3):
```

### Access Recommendations

After approval, the system generates least-privilege access:

**Low Risk** → Standard Access
- View dashboard, submit orders, view invoices
- Restrictions: No financial approvals, no user management

**Medium Risk** → Read-Only Access
- View dashboard, view invoices, view reports
- Restrictions: No transactions, enhanced monitoring

**High Risk** → Minimal Access
- View public info only
- Restrictions: Manual approval for each action, continuous monitoring

## 📁 Project Structure

```
risklens-ai/
├── data/
│   ├── sanctions_list.txt          # Sanctions database
│   ├── sample_vendor_acme.txt      # Sample legitimate vendor
│   ├── sample_vendor_suspicious.txt # Sample risky vendor
│   ├── sample_vendor_acme.pdf      # Generated PDF
│   └── sample_vendor_suspicious.pdf # Generated PDF
├── src/
│   ├── models.py                   # Pydantic data models
│   ├── state_manager.py            # State persistence
│   ├── agent.py                    # ReAct agent core
│   ├── cli.py                      # Human review CLI
│   └── tools/
│       ├── pdf_extractor.py        # PDF → JSON
│       ├── registry_checker.py     # Company verification
│       ├── sanctions_checker.py    # Sanctions matching
│       ├── risk_calculator.py      # Deterministic scoring
│       ├── risk_explainer.py       # LLM explanations
│       └── access_recommender.py   # Access policies
├── scripts/
│   └── create_sample_pdfs.py       # Generate sample PDFs
├── state/                          # Session states (auto-created)
├── requirements.txt                # Python dependencies
├── setup.py                        # Package setup
├── main.py                         # Entry point
└── README.md                       # This file
```

## 🔧 Configuration

### Risk Scoring Rules

Edit `src/tools/risk_calculator.py` to adjust scoring rules (use caution):

```python
self.rules = {
    'registry_match': 30,
    'registry_active': 20,
    'incorporation_age_3y': 15,
    'sanctions_match': 90,
    'address_mismatch': -10,
    'first_time_bank': -10,
}
```

### Access Policies

Edit `src/tools/access_recommender.py` to modify access levels:

```python
self.access_policies = {
    'low': {...},
    'medium': {...},
    'high': {...}
}
```

### Sanctions List

Add entries to `data/sanctions_list.txt`:

```
Entity Name | List Name | Details
```

## 🧪 Testing with Sample Data

### Legitimate Vendor (ACME Corporation)
```bash
python main.py --pdf data/sample_vendor_acme.pdf
```

Expected outcome:
- Registry: ✓ MATCH
- Sanctions: ✓ CLEAR
- Risk: LOW-MEDIUM
- Decision: Approve → Standard Access

### Suspicious Vendor (Evil Corp)
```bash
python main.py --pdf data/sample_vendor_suspicious.pdf
```

Expected outcome:
- Registry: May not match
- Sanctions: ⚠ MATCH (90+ points)
- Risk: HIGH
- Decision: Reject or severe restrictions

## 🔐 Security & Compliance

### Audit Trail
All agent decisions are logged in `state/*.json`:
- Session ID
- Timestamps
- All tool results
- Risk scores and explanations
- Human decisions and notes

### Human-in-the-Loop
**Access is NEVER granted without human approval.** This is mandatory for:
- Compliance requirements
- Risk mitigation
- Legal accountability

### Least-Privilege Principle
Access recommendations are:
- Risk-based
- Minimal by default
- Time-limited (implementation pending)
- Revocable

## 🤖 NVIDIA Nemotron Integration

The system uses **NVIDIA Nemotron-70B-Instruct** for risk explanations:

```python
model = "nvidia/llama-3.1-nemotron-70b-instruct"
```

Why Nemotron?
- Instruction-following capability
- Structured output generation
- Enterprise-grade quality
- Available via NVIDIA NIM API

## 📈 Extending the System

### Add New Risk Factors

1. Update `RiskScore` model in `src/models.py`
2. Add scoring logic in `src/tools/risk_calculator.py`
3. Update explanation prompts in `src/tools/risk_explainer.py`

### Integrate Real APIs

Replace mock implementations:

**Registry API** (`src/tools/registry_checker.py`):
```python
def _api_search(self, company_info):
    response = requests.get(
        f"{self.api_url}/search",
        headers={"Authorization": f"Bearer {self.api_key}"},
        params={"company": company_info.company_name}
    )
    # Process response...
```

**Sanctions API** (`src/tools/sanctions_checker.py`):
```python
def check_sanctions(self, company_info):
    # Call real sanctions screening API
    # (OFAC, UN, EU lists)
```

### Add New Tools

1. Create tool class in `src/tools/your_tool.py`
2. Import in `src/tools/__init__.py`
3. Initialize in `src/agent.py`
4. Add to planner logic in `_plan_next_action()`
5. Add execution in `_execute_action()`

## 🐛 Troubleshooting

### "NVIDIA_API_KEY not found"
- Ensure `.env` file exists and contains valid API key
- Check that `python-dotenv` is installed
- Load environment: `python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('NVIDIA_API_KEY'))"`

### PDF Extraction Fails
- Verify PDF is text-based (not scanned image)
- Check PDF format with: `python -c "from PyPDF2 import PdfReader; print(PdfReader('your.pdf').pages[0].extract_text())"`
- Use OCR for image-based PDFs (not included)

### LLM Explanation Fails
- System uses fallback rule-based explanation
- Check NVIDIA API status: https://build.nvidia.com/
- Verify API key permissions

## 📝 License

This is a demonstration project. Adapt for your use case.

## 🤝 Contributing

This is a reference implementation. Key principles:

1. **Never bypass human review** for access decisions
2. **Keep risk scoring deterministic** (no LLM in scoring)
3. **Maintain audit trail** for all decisions
4. **Follow least-privilege** for access grants

## 📧 Support

For NVIDIA API support: https://build.nvidia.com/

---

**Built with ❤️ using NVIDIA Nemotron**
