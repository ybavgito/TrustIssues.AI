# TrustIssues AI - Test Scenarios Reference

## 📊 Overview

11 comprehensive test PDFs covering all risk levels and edge cases.

---

## 🟢 LOW RISK Scenarios (Score < 40)

### 1. Legitimate UK Tech Company
**File:** `test_legitimate_uk_tech.pdf`

**Company:** TechVision Solutions Ltd  
**Country:** United Kingdom  
**Founded:** 2015 (9 years old)  
**Business:** Technology Services  

**Risk Factors:**
- ✅ Verified UK company
- ✅ Long operating history
- ✅ Proper compliance (ISO 27001, GDPR)
- ✅ Legitimate business address
- ✅ Not on sanctions lists

**Expected Result:**
```
Risk Score: ~30-35/100 (LOW)
Recommendation: APPROVE - Standard Access
Reasoning: "Well-established company in low-risk jurisdiction 
           with verified registration and clean record."
```

---

### 2. Legitimate US Logistics
**File:** `test_legitimate_us_logistics.pdf`

**Company:** Swift Logistics Inc  
**Country:** United States  
**Founded:** 2012 (12 years old)  
**Business:** Logistics & Supply Chain  

**Risk Factors:**
- ✅ US-registered with 10+ years history
- ✅ DOT & TSA certified
- ✅ Proper banking details
- ✅ Not on sanctions lists

**Expected Result:**
```
Risk Score: ~25-30/100 (LOW)
Recommendation: APPROVE - Standard Access
```

---

## 🟡 MEDIUM RISK Scenarios (Score 40-69)

### 3. New Company (< 1 Year)
**File:** `test_medium_new_company.pdf`

**Company:** StartupTech Innovations  
**Country:** United Kingdom  
**Founded:** January 2024 (< 1 year)  
**Business:** Software Development  

**Risk Factors:**
- ⚠️ Very new company (+25 points)
- ⚠️ Co-working space address (+15 points)
- ✅ UK registered
- ✅ Not on sanctions lists

**Expected Result:**
```
Risk Score: ~40-45/100 (MEDIUM)
Recommendation: CONDITIONAL APPROVAL - Enhanced Monitoring
Reasoning: "Company is legitimate but very new with limited 
           track record. Recommend 6-month review period."
```

---

### 4. High-Risk Country
**File:** `test_medium_high_risk_country.pdf`

**Company:** Dubai Trading Partners LLC  
**Country:** United Arab Emirates  
**Founded:** 2020  
**Business:** Import/Export Trading  

**Risk Factors:**
- ⚠️ UAE jurisdiction (+20 points)
- ⚠️ Import/Export business (+15 points)
- ⚠️ Limited compliance documentation
- ✅ Verified registration
- ✅ Not on sanctions lists

**Expected Result:**
```
Risk Score: ~50-55/100 (MEDIUM)
Recommendation: ENHANCED DUE DILIGENCE
Reasoning: "Operating in higher-risk jurisdiction. Trade-based 
           business requires additional verification."
```

---

### 5. Incomplete Data
**File:** `test_medium_incomplete_data.pdf`

**Company:** QuickStart Solutions  
**Country:** Ireland  
**Founded:** Not Provided  
**Business:** Business Consulting  

**Risk Factors:**
- ⚠️ Registration number: PENDING (+40 points)
- ⚠️ Missing incorporation date (+25 points)
- ⚠️ Incomplete banking info (+20 points)
- ✅ Ireland (low-risk country)

**Expected Result:**
```
Risk Score: ~55-60/100 (MEDIUM)
Recommendation: REQUEST MORE INFO
Reasoning: "Critical information missing. Cannot complete 
           assessment without registration and banking details."
```

---

## 🔴 HIGH RISK Scenarios (Score ≥ 70)

### 6. Sanctioned Entity
**File:** `test_high_sanctioned_entity.pdf`

**Company:** Evil Corp International  
**Country:** Offshore Jurisdiction  
**Founded:** 2024 (very recent)  
**Business:** Financial Services  

**Risk Factors:**
- 🚨 ON SANCTIONS LIST (+100 points) **AUTOMATIC REJECT**
- 🚨 Offshore jurisdiction (+40 points)
- 🚨 Shell company indicators (+40 points)
- 🚨 Suspicious banking details (+20 points)
- 🚨 Very new (+35 points)

**Expected Result:**
```
Risk Score: 235/100 (HIGH) - CAPPED AT 100
Recommendation: REJECT - DO NOT ONBOARD
Reasoning: "CRITICAL: Company appears on OFAC sanctions list.
           Onboarding would violate compliance regulations.
           IMMEDIATE REJECTION REQUIRED."
```

---

### 7. Sanctioned Country
**File:** `test_high_sanctioned_country.pdf`

**Company:** Tehran Import Export Co  
**Country:** Iran  
**Founded:** 2023  
**Business:** Import/Export  

**Risk Factors:**
- 🚨 Sanctioned country: Iran (+100 points) **AUTOMATIC REJECT**
- ⚠️ Recently incorporated (+35 points)
- ⚠️ Trade-based business (+15 points)

**Expected Result:**
```
Risk Score: 150/100 (HIGH) - CAPPED AT 100
Recommendation: REJECT - Sanctions Restrictions
Reasoning: "Company operates in sanctioned jurisdiction (Iran).
           Cannot proceed due to trade restrictions and 
           compliance requirements."
```

---

### 8. Shell Company
**File:** `test_high_shell_company.pdf`

**Company:** Offshore Holdings Anonymous  
**Country:** British Virgin Islands  
**Founded:** December 2023  
**Business:** Holding Company  

**Risk Factors:**
- 🚨 Shell company indicators (+40 points)
- 🚨 BVI offshore jurisdiction (+40 points)
- 🚨 Minimal transparency (+30 points)
- 🚨 PO Box address only (+15 points)
- ⚠️ Very new (+35 points)

**Expected Result:**
```
Risk Score: ~95/100 (HIGH)
Recommendation: REJECT
Reasoning: "Multiple shell company indicators. Minimal operational
           transparency. Offshore jurisdiction with no substance.
           High risk of being used for illicit purposes."
```

---

### 9. Suspicious Financial Services
**File:** `test_high_recent_suspicious.pdf`

**Company:** FastCash Financial Ltd  
**Country:** United Kingdom  
**Founded:** November 2024 (1 week old!)  
**Business:** Crypto/High-Yield Investment  

**Risk Factors:**
- 🚨 No FCA registration (+30 points)
- 🚨 Very new (< 1 month) (+35 points)
- ⚠️ High-risk business model (+20 points)
- ⚠️ Virtual office address (+15 points)
- ⚠️ Unregulated bank (+15 points)

**Expected Result:**
```
Risk Score: ~80/100 (HIGH)
Recommendation: REJECT - Regulatory Concerns
Reasoning: "Extremely new financial services company without
           proper FCA authorization. Business model (crypto/
           high-yield) combined with no license raises red flags.
           Potential fraud risk."
```

---

## 🔀 EDGE CASES

### 10. Sanctioned Person Name Match
**File:** `test_edge_sanctioned_person.pdf`

**Company:** BadActor Industries Ltd  
**Country:** United Kingdom  
**Founded:** 2021  
**Business:** Manufacturing  

**Risk Factors:**
- 🚨 Company name matches sanctions list entity (+100 points)
- ✅ Otherwise legitimate UK company
- ✅ Proper registrations

**Expected Result:**
```
Risk Score: ~105/100 (HIGH) - CAPPED AT 100
Recommendation: REJECT - Name Match Review Required
Reasoning: "Company name 'BadActor Industries' matches entity
           on UN sanctions list. May be false positive due to
           common name, but requires manual review before 
           proceeding. Cannot auto-approve."
```

---

### 11. Mixed Signals
**File:** `test_edge_mixed_signals.pdf`

**Company:** Global Ventures Trading AG  
**Country:** Switzerland (low-risk)  
**Founded:** 2019 (5 years)  
**Business:** International Trading  

**Risk Factors:**
- ✅ Switzerland (reputable jurisdiction) (+0)
- ✅ UBS banking (reputable) (+0)
- 🚨 Operations in Iran & North Korea (+60 points)
- ⚠️ Multi-jurisdiction high-risk operations (+20 points)

**Expected Result:**
```
Risk Score: ~70-75/100 (HIGH/MEDIUM border)
Recommendation: ENHANCED DUE DILIGENCE REQUIRED
Reasoning: "Reputable Swiss company but operates in sanctioned
           jurisdictions. Requires detailed review of business
           activities to ensure no sanctions violations.
           Borderline case - needs human judgment."
```

---

## 🧪 Testing Commands

### Test Single Scenario
```bash
# Low risk (should approve)
python3 main.py --pdf data/test_pdfs/test_legitimate_uk_tech.pdf

# Medium risk (conditional)
python3 main.py --pdf data/test_pdfs/test_medium_new_company.pdf

# High risk (should reject)
python3 main.py --pdf data/test_pdfs/test_high_sanctioned_entity.pdf
```

### Test All Scenarios (Batch)
```bash
for pdf in data/test_pdfs/*.pdf; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Testing: $(basename $pdf)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python3 main.py --pdf "$pdf"
    echo
    echo "Press Enter to continue..."
    read
done
```

---

## 📊 Expected Distribution

When testing all 11 PDFs:

```
Results Summary:
├── APPROVE (2 PDFs)
│   ├── legitimate_uk_tech
│   └── legitimate_us_logistics
│
├── CONDITIONAL / ENHANCED DUE DILIGENCE (3 PDFs)
│   ├── medium_new_company
│   ├── medium_high_risk_country
│   └── edge_mixed_signals
│
├── REQUEST MORE INFO (1 PDF)
│   └── medium_incomplete_data
│
└── REJECT (5 PDFs)
    ├── high_sanctioned_entity
    ├── high_sanctioned_country
    ├── high_shell_company
    ├── high_recent_suspicious
    └── edge_sanctioned_person
```

---

## 🎯 What to Observe During Testing

### 1. Agent Reasoning
Watch how each agent thinks:
```
🧠 COORDINATOR: "Data not extracted yet → delegate to Extractor"
🧠 EXTRACTOR: "I see company name and registration → extract both"
🧠 VERIFIER: "Need to check registry AND sanctions → call both tools"
🧠 RISK ANALYST: "Sanctions match found → HIGH RISK immediately"
```

### 2. Tool Execution
See what tools agents choose:
```
🤖 Calling tool: extract_from_pdf
✅ SUCCESS: Extracted company data

🤖 Calling tool: search_registry  
✅ SUCCESS: Registry MATCH

🤖 Calling tool: check_sanctions
🚨 WARNING: Sanctions MATCH FOUND
```

### 3. Risk Calculation
Understand the scoring:
```
Risk Breakdown:
  Base Score: 0
  + Sanctions Match: +100
  + Offshore Jurisdiction: +40
  + Shell Company Indicators: +40
  ─────────────────────────────
  Total: 180 → Capped at 100 (HIGH)
```

### 4. Explainability
Review natural language explanations:
```
AI Explanation:
"This vendor presents HIGH RISK due to appearing on the OFAC
sanctions list. The company operates in an offshore jurisdiction
with minimal transparency and shows multiple shell company
indicators including PO Box address, unclear business purpose,
and recent incorporation. Recommendation: REJECT immediately
to maintain compliance with sanctions regulations."
```

---

## 💡 Key Learning Points

1. **Deterministic + AI Hybrid**: Risk score is rule-based (transparent), but explanations use AI (natural language)

2. **Human-in-Loop**: System recommends, but human MUST approve/reject for compliance

3. **Audit Trail**: Every agent decision is logged with reasoning

4. **Adaptable**: Agents choose different tool sequences based on context

5. **Explainable**: Every decision includes "why" in plain English

---

## 🚀 Ready to Test!

Start with the LOW risk scenario to see a smooth approval:
```bash
python3 main.py --pdf data/test_pdfs/test_legitimate_uk_tech.pdf
```

Then try HIGH risk to see rejection:
```bash
python3 main.py --pdf data/test_pdfs/test_high_sanctioned_entity.pdf
```

Watch the agents collaborate and reason! 🧠✨

