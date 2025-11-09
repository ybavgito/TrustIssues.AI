"""PDF extraction tool"""
import re
from pathlib import Path
from datetime import datetime
from PyPDF2 import PdfReader
from src.models import CompanyInfo, ToolResult


class PDFExtractor:
    """Extracts company information from PDF documents"""
    
    def __init__(self):
        self.patterns = {
            'company_name': [
                r'company\s*name[:\s]+([^\n]+)',
                r'business\s*name[:\s]+([^\n]+)',
                r'legal\s*name[:\s]+([^\n]+)',
            ],
            'registration_number': [
                r'registration\s*(?:number|no\.?)[:\s]+([A-Z0-9\-]+)',
                r'company\s*(?:number|no\.?)[:\s]+([A-Z0-9\-]+)',
                r'reg\.?\s*(?:number|no\.?)[:\s]+([A-Z0-9\-]+)',
            ],
            'incorporation_date': [
                r'incorporation\s*date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'incorporated\s*on[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'date\s*of\s*incorporation[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            ],
            'address': [
                r'(?:registered\s*)?address[:\s]+([^\n]+(?:\n[^\n]+)?)',
                r'business\s*address[:\s]+([^\n]+(?:\n[^\n]+)?)',
            ],
            'contact_email': [
                r'email[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'e-mail[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            ],
            'contact_phone': [
                r'phone[:\s]+([+\d\s\-()]{10,})',
                r'tel[:\s]+([+\d\s\-()]{10,})',
                r'telephone[:\s]+([+\d\s\-()]{10,})',
            ],
            'bank_account': [
                r'bank\s*account[:\s]+([A-Z0-9\-\s]{10,})',
                r'account\s*(?:number|no\.?)[:\s]+([A-Z0-9\-\s]{10,})',
            ],
            'business_type': [
                r'business\s*type[:\s]+([^\n]+)',
                r'industry[:\s]+([^\n]+)',
                r'sector[:\s]+([^\n]+)',
            ],
        }
    
    def extract_from_pdf(self, pdf_path: str) -> ToolResult:
        """Extract company information from a PDF"""
        try:
            path = Path(pdf_path)
            if not path.exists():
                return ToolResult(
                    tool_name="extract_from_pdf",
                    success=False,
                    error=f"PDF file not found: {pdf_path}"
                )
            
            # Read PDF
            reader = PdfReader(str(path))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Extract fields
            company_info = CompanyInfo()
            for field, patterns in self.patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                    if match:
                        value = match.group(1).strip()
                        setattr(company_info, field, value)
                        break
            
            # Check if we extracted anything meaningful
            if not company_info.company_name:
                return ToolResult(
                    tool_name="extract_from_pdf",
                    success=False,
                    error="Could not extract company name from PDF"
                )
            
            return ToolResult(
                tool_name="extract_from_pdf",
                success=True,
                data=company_info.model_dump(),
                next_action="search_registry"
            )
        
        except Exception as e:
            return ToolResult(
                tool_name="extract_from_pdf",
                success=False,
                error=f"Error extracting PDF: {str(e)}"
            )

