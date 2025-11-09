"""Company registry verification tool"""
import os
import random
from datetime import datetime, timedelta
from src.models import RegistryResult, ToolResult, CompanyInfo


class RegistryChecker:
    """Verifies company registration via registry API or mock data"""
    
    def __init__(self):
        self.api_key = os.getenv("REGISTRY_API_KEY")
        self.api_url = os.getenv("REGISTRY_API_URL")
        self.use_mock = not self.api_key  # Use mock if no API key
        
        # Mock registry data
        self.mock_registry = {
            "ACME Corporation": {
                "match": True,
                "status": "active",
                "registered_name": "ACME Corporation Ltd.",
                "registered_address": "123 Business St, London, UK",
                "incorporation_date": "2018-03-15",
                "confidence": 0.95
            },
            "TechStart Inc": {
                "match": True,
                "status": "active",
                "registered_name": "TechStart Incorporated",
                "registered_address": "456 Innovation Ave, San Francisco, CA",
                "incorporation_date": "2020-07-22",
                "confidence": 0.90
            },
            "GlobalTrade LLC": {
                "match": True,
                "status": "dissolved",
                "registered_name": "GlobalTrade Limited Liability Company",
                "registered_address": "789 Commerce Blvd, New York, NY",
                "incorporation_date": "2015-11-10",
                "confidence": 0.88
            },
        }
    
    def search_registry(self, company_info: CompanyInfo) -> ToolResult:
        """Search company registry for verification"""
        try:
            if self.use_mock:
                result = self._mock_search(company_info)
            else:
                result = self._api_search(company_info)
            
            return ToolResult(
                tool_name="search_registry",
                success=True,
                data=result.model_dump(),
                next_action="check_sanctions"
            )
        
        except Exception as e:
            return ToolResult(
                tool_name="search_registry",
                success=False,
                error=f"Registry search failed: {str(e)}"
            )
    
    def _mock_search(self, company_info: CompanyInfo) -> RegistryResult:
        """Mock registry search"""
        company_name = company_info.company_name
        
        # Check if company exists in mock data
        for mock_name, mock_data in self.mock_registry.items():
            if self._fuzzy_match(company_name, mock_name):
                return RegistryResult(**mock_data)
        
        # Generate random result for unknown companies
        # 70% chance of match
        if random.random() < 0.7:
            return RegistryResult(
                match=True,
                status=random.choice(["active", "active", "active", "inactive"]),
                registered_name=company_name,
                registered_address=company_info.address or "Unknown",
                incorporation_date=company_info.incorporation_date or self._random_date(),
                confidence=random.uniform(0.75, 0.95)
            )
        else:
            return RegistryResult(
                match=False,
                confidence=random.uniform(0.3, 0.6)
            )
    
    def _api_search(self, company_info: CompanyInfo) -> RegistryResult:
        """Real API search (placeholder - implement with actual API)"""
        # TODO: Implement real API call
        # For now, fall back to mock
        return self._mock_search(company_info)
    
    def _fuzzy_match(self, name1: str, name2: str) -> bool:
        """Simple fuzzy matching"""
        n1 = name1.lower().replace(" ", "").replace(".", "")
        n2 = name2.lower().replace(" ", "").replace(".", "")
        return n1 in n2 or n2 in n1
    
    def _random_date(self) -> str:
        """Generate random incorporation date"""
        days_ago = random.randint(365, 3650)  # 1-10 years ago
        date = datetime.now() - timedelta(days=days_ago)
        return date.strftime("%Y-%m-%d")

