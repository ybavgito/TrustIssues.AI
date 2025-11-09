# RiskLens AI - Quick Start Guide

Get up and running with RiskLens AI in 5 minutes.

## Prerequisites

- Python 3.9+
- NVIDIA API Key from https://build.nvidia.com/

## Installation (3 steps)

### 1. Set up environment

```bash
cd /Users/vaibhav/Downloads/risklens-ai

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Create .env file
cat > .env << 'EOF'
NVIDIA_API_KEY=your_actual_api_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
EOF
```

**Get your NVIDIA API Key:**
1. Visit https://build.nvidia.com/
2. Sign in (free account)
3. Go to API Keys section
4. Create new key (starts with `nvapi-`)
5. Copy and paste into `.env` file above

### 3. Generate Sample PDFs

```bash
# Create sample vendor PDFs for testing
python scripts/create_sample_pdfs.py
```

## First Run (Test the System)

### Test System Setup

```bash
python scripts/test_system.py
```

This will verify all components are working.

### Process a Legitimate Vendor

```bash
python main.py --pdf data/sample_vendor_acme.pdf
```

You'll see:
1. Agent extracts company data from PDF
2. Verifies against registry (mock)
3. Checks sanctions list
4. Computes risk score
5. Generates LLM explanation
6. **Requests your approval** ⬅️ This is where you interact

**When prompted:**
- Option 1: APPROVE → System generates access recommendation
- Option 2: REJECT → Denies onboarding
- Option 3: REQUEST MORE INFO → Pauses for additional docs

### Process a High-Risk Vendor

```bash
python main.py --pdf data/sample_vendor_suspicious.pdf
```

This vendor will trigger sanctions match → automatic HIGH risk.

## Understanding the Output

### Agent Workflow (You'll see this)

```
👁 OBSERVE: Iteration 1: Observing state...
  Company: Not extracted
  Registry: ○ | Sanctions: ○ | Risk: ○ | Explanation: ○

🧠 DECIDE: Next action: extract_from_pdf

⚡ ACT: Executing extract_from_pdf...

✓ SUCCESS: ✓ extract_from_pdf completed

👁 OBSERVE: Iteration 2: Observing state...
  Company: ACME Corporation
  Registry: ○ | Sanctions: ○ | Risk: ○ | Explanation: ○

🧠 DECIDE: Next action: search_registry
...
```

### Human Review Screen

```
╔══════════════════════════════════════════════════════════╗
║           RiskLens AI - Vendor Onboarding               ║
║        Automated Risk Assessment & Verification         ║
╚══════════════════════════════════════════════════════════╝

HUMAN REVIEW REQUIRED
============================================================

Company Information:
Name                 ACME Corporation
Registration #       UK-12345678
Incorporation Date   15-03-2018
...

Verification Results:
Registry Check      ✓ MATCH    active    95%
Sanctions Check     ✓ CLEAR    N/A       0%

Risk Assessment:
  Risk Level: LOW
  Risk Score: 65
  
  Score Breakdown:
    registry_match: +30
    registry_active: +20
    incorporation_age_3y: +15

Risk Analysis:
  Summary: ACME Corporation is a verified, low-risk entity...
  
  Key Factors:
    • Company verified in registry
    • Active status for 5+ years
    • No sanctions matches
  
  Recommendation: Approve with standard access controls

DECISION REQUIRED
============================================================
1. APPROVE - Grant access to vendor
2. REJECT - Deny vendor onboarding  
3. REQUEST MORE INFO - Ask for additional documentation

Your decision (1-3): 
```

### Access Recommendation (After Approval)

```
WORKFLOW COMPLETE
============================================================

Access Recommendation:
  Level: STANDARD

  Permissions Granted:
    ✓ view_dashboard
    ✓ submit_orders
    ✓ view_invoices
    ✓ manage_profile
    ✓ create_tickets
    ✓ upload_documents
    ✓ view_reports

  Restrictions:
    ⚠ No financial transaction approval
    ⚠ No user management
    ⚠ Rate limited API access

  Justification:
    Standard access granted due to low risk profile.
    Company has been verified and poses minimal security concerns.

Session ID: 20251108_143022
```

## Interactive Mode

Run without arguments for menu:

```bash
python main.py
```

Menu options:
1. **Process new vendor PDF** - Upload and analyze new vendor
2. **Review pending cases** - See cases waiting for your approval
3. **View completed cases** - Audit trail of all decisions
4. Exit

## Testing with Your Own PDFs

Create a vendor PDF with this structure:

```
Company Name: YourCompany Inc
Registration Number: REG-12345
Incorporation Date: 01-01-2020
Address: 123 Main St, City, Country
Contact Email: contact@yourcompany.com
Business Type: Software Services
```

Then process it:

```bash
python main.py --pdf /path/to/your/vendor.pdf
```

## Key Concepts

### ReAct Agent Loop

The system follows **Observe → Decide → Act → Update** cycle:

1. **OBSERVE**: Check current state (what's done, what's missing)
2. **DECIDE**: Choose next action based on planner logic
3. **ACT**: Execute the tool (extract PDF, check sanctions, etc.)
4. **UPDATE**: Save results to state, continue loop

### Deterministic Risk Scoring

Risk is **NOT** computed by AI. It uses fixed rules:

```
Score = 0
+ 30 if found in registry
+ 20 if status is "active"
+ 15 if company age >= 3 years
= 90+ if sanctions match (overrides)
- 10 if address mismatch
- 10 if first-time banking

Risk Level:
  >= 70 = HIGH
  40-69 = MEDIUM
  < 40  = LOW
```

### Human-in-the-Loop

**Critical**: Access is NEVER granted without human approval.

The agent:
1. Gathers all data
2. Computes risk
3. Explains reasoning
4. **STOPS and waits for human**
5. Only after approval → recommends access

## Troubleshooting

### "NVIDIA_API_KEY not found"

```bash
# Check if .env exists
ls -la .env

# Verify contents
cat .env

# Should show: NVIDIA_API_KEY=nvapi-...
```

### PDF extraction fails

The system uses regex to extract data. Your PDF must be:
- Text-based (not scanned image)
- Contains keywords like "Company Name:", "Registration Number:", etc.

### Mock vs Real APIs

By default, the system uses **mock data** for:
- Company registry lookups
- Some sanctions checks (uses local list in `data/sanctions_list.txt`)

To use real APIs, add to `.env`:
```
REGISTRY_API_KEY=your_key
REGISTRY_API_URL=https://api.companieshouse.gov.uk
```

## Next Steps

1. ✅ Process sample vendors (see above)
2. 📄 Read full [README.md](README.md) for architecture details
3. 🔧 Customize risk rules in `src/tools/risk_calculator.py`
4. 📋 Modify access policies in `src/tools/access_recommender.py`
5. 🔌 Integrate real APIs (registry, sanctions)
6. 🚀 Deploy to production environment

## Architecture Summary

```
PDF → Agent → [Extract → Registry → Sanctions → Risk → Explain] 
              ↓
         Human Review
              ↓
         [Approve/Reject]
              ↓
         Access Recommendation
```

**Key Files:**
- `src/agent.py` - ReAct agent core (Observe-Decide-Act loop)
- `src/tools/risk_calculator.py` - Deterministic scoring
- `src/tools/risk_explainer.py` - NVIDIA Nemotron integration
- `src/cli.py` - Human review interface

## Support

- NVIDIA API: https://build.nvidia.com/
- Documentation: See [README.md](README.md)
- Test system: `python scripts/test_system.py`

---

**Ready? Run your first vendor assessment:**

```bash
python main.py --pdf data/sample_vendor_acme.pdf
```

