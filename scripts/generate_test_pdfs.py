#!/usr/bin/env python3
"""
Generate comprehensive test PDFs for all RiskLens AI scenarios
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime

# Test scenarios covering all risk levels and edge cases
TEST_SCENARIOS = {
    # LOW RISK SCENARIOS (Score < 40)
    "legitimate_uk_tech": {
        "company_name": "TechVision Solutions Ltd",
        "registration_number": "UK-87654321",
        "incorporation_date": "12-06-2015",
        "country": "United Kingdom",
        "business_type": "Technology Services",
        "address": "45 Innovation Park, Manchester, M1 2HQ, United Kingdom",
        "email": "contact@techvision.co.uk",
        "phone": "+44 161 234 5678",
        "bank_account": "GB82WEST12345698765432",
        "bank_name": "Barclays Bank PLC",
        "swift": "BARCGB22",
        "description": "Established IT consulting firm providing cloud solutions and software development services to enterprise clients across the UK and EU.",
        "services": ["Cloud Migration", "DevOps Consulting", "Software Development", "IT Support"],
        "compliance": ["GDPR Compliant", "ISO 27001 Certified", "UK Companies House Registered", "Cyber Essentials Plus"],
        "risk_indicators": "LOW - Established company, verified registration, good compliance record"
    },
    
    "legitimate_us_logistics": {
        "company_name": "Swift Logistics Inc",
        "registration_number": "US-DE-123456",
        "incorporation_date": "20-08-2012",
        "country": "United States",
        "business_type": "Logistics and Supply Chain",
        "address": "1200 Commerce Drive, Dover, Delaware 19901, USA",
        "email": "operations@swiftlogistics.com",
        "phone": "+1 302 555 0123",
        "bank_account": "US0123456789012345678",
        "bank_name": "Wells Fargo Bank",
        "swift": "WFBIUS6S",
        "description": "Full-service logistics provider with 10+ years experience in freight forwarding, warehousing, and supply chain management.",
        "services": ["Freight Forwarding", "Warehousing", "Last-Mile Delivery", "Customs Clearance"],
        "compliance": ["DOT Registered", "TSA Certified", "C-TPAT Member", "ISO 9001"],
        "risk_indicators": "LOW - Long operating history, US-based, strong regulatory compliance"
    },
    
    # MEDIUM RISK SCENARIOS (Score 40-69)
    "medium_new_company": {
        "company_name": "StartupTech Innovations",
        "registration_number": "UK-11223344",
        "incorporation_date": "15-01-2024",
        "country": "United Kingdom",
        "business_type": "Software Development",
        "address": "Suite 5, Co-Working Space, London, E1 6AN, United Kingdom",
        "email": "hello@startuptech.io",
        "phone": "+44 20 8888 9999",
        "bank_account": "GB12HSBC40123456789012",
        "bank_name": "HSBC UK",
        "swift": "HBUKGB4B",
        "description": "Newly formed startup developing mobile applications for the healthcare sector.",
        "services": ["Mobile App Development", "Healthcare Solutions", "Cloud Services"],
        "compliance": ["UK Companies House Registered", "GDPR Policy in Development"],
        "risk_indicators": "MEDIUM - New company (< 1 year), limited track record, co-working address"
    },
    
    "medium_high_risk_country": {
        "company_name": "Dubai Trading Partners LLC",
        "registration_number": "AE-DXB-556677",
        "incorporation_date": "10-03-2020",
        "country": "United Arab Emirates",
        "business_type": "Import/Export Trading",
        "address": "Office 404, Business Tower, Dubai, UAE",
        "email": "info@dubaitrading.ae",
        "phone": "+971 4 123 4567",
        "bank_account": "AE070331234567890123456",
        "bank_name": "Emirates NBD",
        "swift": "EBILAEAD",
        "description": "International trading company specializing in electronics and consumer goods import/export between Asia and Middle East.",
        "services": ["Import/Export", "Trade Financing", "Logistics Coordination"],
        "compliance": ["UAE Trade License", "Customs Registration"],
        "risk_indicators": "MEDIUM - High-risk jurisdiction, trade-based business, recent incorporation"
    },
    
    "medium_incomplete_data": {
        "company_name": "QuickStart Solutions",
        "registration_number": "PENDING",
        "incorporation_date": "Not Provided",
        "country": "Ireland",
        "business_type": "Business Consulting",
        "address": "Dublin, Ireland",
        "email": "contact@quickstart.ie",
        "phone": "Not Available",
        "bank_account": "Information Pending",
        "bank_name": "To Be Confirmed",
        "swift": "N/A",
        "description": "Business consulting services for small and medium enterprises.",
        "services": ["Business Strategy", "Process Optimization"],
        "compliance": ["Application in Progress"],
        "risk_indicators": "MEDIUM - Incomplete information, missing critical data points"
    },
    
    # HIGH RISK SCENARIOS (Score ≥ 70)
    "high_sanctioned_entity": {
        "company_name": "Evil Corp International",
        "registration_number": "OFF-99999999",
        "incorporation_date": "01-01-2024",
        "country": "Offshore Jurisdiction",
        "business_type": "Financial Services",
        "address": "Unknown Building, Offshore Location, Tax Haven, 00000",
        "email": "contact@evilcorp-intl.xyz",
        "phone": "+000 0000000000",
        "bank_account": "XX00000000000000000000",
        "bank_name": "Suspicious Offshore Bank",
        "swift": "XXXXXX00",
        "description": "Financial services and consulting. Recently established to expand operations internationally.",
        "services": ["Money Transfer", "Investment Consulting", "Asset Management"],
        "compliance": ["Status Pending"],
        "risk_indicators": "HIGH - On sanctions list, offshore jurisdiction, suspicious details"
    },
    
    "high_sanctioned_country": {
        "company_name": "Tehran Import Export Co",
        "registration_number": "IR-123456",
        "incorporation_date": "05-05-2023",
        "country": "Iran",
        "business_type": "Import/Export",
        "address": "Tehran, Iran",
        "email": "info@tehran-trade.ir",
        "phone": "+98 21 1234 5678",
        "bank_account": "IR123456789012345678",
        "bank_name": "Bank Melli Iran",
        "swift": "BKMLIRITXXX",
        "description": "International trade company dealing in industrial equipment and machinery.",
        "services": ["Industrial Equipment Import", "Machinery Trading"],
        "compliance": ["Local Registration"],
        "risk_indicators": "HIGH - Sanctioned country (Iran), trade restrictions apply"
    },
    
    "high_shell_company": {
        "company_name": "Offshore Holdings Anonymous",
        "registration_number": "BVI-000000",
        "incorporation_date": "31-12-2023",
        "country": "British Virgin Islands",
        "business_type": "Holding Company",
        "address": "PO Box 9999, Road Town, Tortola, BVI",
        "email": "admin@offshore-holdings.vg",
        "phone": "Not Listed",
        "bank_account": "SHELL-ACCOUNT",
        "bank_name": "Offshore International Bank",
        "swift": "UNKNOWN",
        "description": "Investment holding company. Minimal operational details available.",
        "services": ["Asset Holding", "Investment Management"],
        "compliance": ["BVI Registration Only"],
        "risk_indicators": "HIGH - Shell company indicators, minimal transparency, offshore"
    },
    
    "high_recent_suspicious": {
        "company_name": "FastCash Financial Ltd",
        "registration_number": "UK-99887766",
        "incorporation_date": "01-11-2024",
        "country": "United Kingdom",
        "business_type": "Financial Services",
        "address": "Virtual Office, London, UK",
        "email": "urgent@fastcash-fin.xyz",
        "phone": "+44 7000 000000",
        "bank_account": "GB99UNKN12345678901234",
        "bank_name": "Small Unregulated Bank",
        "swift": "UNKNGB2L",
        "description": "High-yield investment services. Cryptocurrency trading and lending.",
        "services": ["Crypto Trading", "High-Yield Investments", "Quick Loans"],
        "compliance": ["Not FCA Registered", "No Financial License"],
        "risk_indicators": "HIGH - Very new, suspicious business model, no proper licenses"
    },
    
    # EDGE CASES
    "edge_sanctioned_person": {
        "company_name": "BadActor Industries Ltd",
        "registration_number": "UK-77889900",
        "incorporation_date": "15-08-2021",
        "country": "United Kingdom",
        "business_type": "Manufacturing",
        "address": "Industrial Estate, Birmingham, B1 1AA, UK",
        "email": "info@badactor-industries.com",
        "phone": "+44 121 555 0000",
        "bank_account": "GB44BARC20001234567890",
        "bank_name": "Barclays",
        "swift": "BARCGB22",
        "description": "Manufacturing and industrial equipment supplier.",
        "services": ["Industrial Equipment", "Manufacturing"],
        "compliance": ["UK Registered"],
        "risk_indicators": "HIGH - Company name matches sanctions list"
    },
    
    "edge_mixed_signals": {
        "company_name": "Global Ventures Trading AG",
        "registration_number": "CH-123456",
        "incorporation_date": "10-10-2019",
        "country": "Switzerland",
        "business_type": "Trading",
        "address": "Zurich, Switzerland",
        "email": "contact@globalventures.ch",
        "phone": "+41 44 123 4567",
        "bank_account": "CH9300762011623852957",
        "bank_name": "UBS Switzerland",
        "swift": "UBSWCHZH80A",
        "description": "International trading company with operations in multiple high-risk jurisdictions including Iran and North Korea.",
        "services": ["International Trade", "Business Development"],
        "compliance": ["Swiss Registration", "Multiple Jurisdiction Operations"],
        "risk_indicators": "MIXED - Reputable country but high-risk operations"
    }
}


def create_vendor_pdf(scenario_name, data, output_dir="data/test_pdfs"):
    """Create a professional-looking vendor application PDF"""
    
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"test_{scenario_name}.pdf")
    
    doc = SimpleDocTemplate(filename, pagesize=letter,
                           topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    story.append(Paragraph("═" * 60, styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("VENDOR ONBOARDING APPLICATION", title_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("═" * 60, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Section style
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    # Company Information
    story.append(Paragraph("COMPANY INFORMATION", section_style))
    company_data = [
        ["Company Name:", data['company_name']],
        ["Registration Number:", data['registration_number']],
        ["Incorporation Date:", data['incorporation_date']],
        ["Business Type:", data['business_type']],
        ["Country:", data['country']]
    ]
    t = Table(company_data, colWidths=[2*inch, 4.5*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    # Contact Details
    story.append(Paragraph("CONTACT DETAILS", section_style))
    story.append(Paragraph(f"<b>Registered Address:</b><br/>{data['address']}", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    contact_data = [
        ["Email:", data['email']],
        ["Phone:", data['phone']]
    ]
    t = Table(contact_data, colWidths=[2*inch, 4.5*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    # Banking Information
    story.append(Paragraph("BANKING INFORMATION", section_style))
    banking_data = [
        ["Bank Account:", data['bank_account']],
        ["Bank Name:", data['bank_name']],
        ["SWIFT Code:", data['swift']]
    ]
    t = Table(banking_data, colWidths=[2*inch, 4.5*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    # Business Description
    story.append(Paragraph("BUSINESS DESCRIPTION", section_style))
    story.append(Paragraph(data['description'], styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    if data['services']:
        story.append(Paragraph("<b>Services Offered:</b>", styles['Normal']))
        for service in data['services']:
            story.append(Paragraph(f"• {service}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Compliance
    story.append(Paragraph("COMPLIANCE & CERTIFICATIONS", section_style))
    for comp in data['compliance']:
        story.append(Paragraph(f"• {comp}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Risk Indicators (for testing - normally wouldn't be on vendor form)
    story.append(Paragraph("INTERNAL RISK ASSESSMENT NOTES", section_style))
    risk_style = ParagraphStyle(
        'Risk',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        leftIndent=10
    )
    story.append(Paragraph(f"<i>{data['risk_indicators']}</i>", risk_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Declaration
    story.append(Paragraph("DECLARATION", section_style))
    story.append(Paragraph(
        "I declare that all information provided is accurate and complete to the best of my knowledge.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    decl_data = [
        ["Authorized Signatory:", "_____________________"],
        ["Position:", "Director / Authorized Representative"],
        ["Date:", datetime.now().strftime("%d-%m-%Y")]
    ]
    t = Table(decl_data, colWidths=[2*inch, 4.5*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t)
    
    # Build PDF
    doc.build(story)
    return filename


def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     RiskLens AI - Test PDF Generator                    ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    output_dir = "data/test_pdfs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate PDFs for all scenarios
    print(f"Generating {len(TEST_SCENARIOS)} test PDFs...\n")
    
    generated = []
    for scenario_name, data in TEST_SCENARIOS.items():
        filename = create_vendor_pdf(scenario_name, data, output_dir)
        risk_level = "LOW" if "low" in scenario_name or "legitimate" in scenario_name else \
                    "MEDIUM" if "medium" in scenario_name else \
                    "HIGH" if "high" in scenario_name else "EDGE"
        
        print(f"  ✓ {scenario_name:40s} [{risk_level:6s}] → {os.path.basename(filename)}")
        generated.append((scenario_name, risk_level, filename))
    
    print()
    print("═" * 60)
    print("SUMMARY")
    print("═" * 60)
    print()
    
    # Group by risk level
    low = [s for s in generated if s[1] == "LOW"]
    medium = [s for s in generated if s[1] == "MEDIUM"]
    high = [s for s in generated if s[1] == "HIGH"]
    edge = [s for s in generated if s[1] == "EDGE"]
    
    print(f"📊 Total PDFs Generated: {len(generated)}")
    print(f"   • LOW Risk:    {len(low)}")
    print(f"   • MEDIUM Risk: {len(medium)}")
    print(f"   • HIGH Risk:   {len(high)}")
    print(f"   • EDGE Cases:  {len(edge)}")
    print()
    print(f"📁 Location: {output_dir}/")
    print()
    
    # Show test commands
    print("═" * 60)
    print("TEST COMMANDS")
    print("═" * 60)
    print()
    print("# Test LOW risk vendor:")
    if low:
        print(f"python3 main.py --pdf {low[0][2]}")
    print()
    print("# Test MEDIUM risk vendor:")
    if medium:
        print(f"python3 main.py --pdf {medium[0][2]}")
    print()
    print("# Test HIGH risk vendor:")
    if high:
        print(f"python3 main.py --pdf {high[0][2]}")
    print()
    print("# Test all vendors (batch):")
    print(f"for pdf in {output_dir}/*.pdf; do")
    print('    echo "Testing: $pdf"')
    print('    python3 main.py --pdf "$pdf"')
    print('done')
    print()


if __name__ == "__main__":
    main()

