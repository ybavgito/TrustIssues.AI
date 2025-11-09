"""Sanctions list checking tool"""
import os
from pathlib import Path
from fuzzywuzzy import fuzz
from src.models import SanctionsResult, ToolResult, CompanyInfo


class SanctionsChecker:
    """Checks company names against sanctions lists"""
    
    def __init__(self, sanctions_file: str = "data/sanctions_list.txt"):
        self.sanctions_file = Path(sanctions_file)
        self.sanctions_list = self._load_sanctions()
        self.match_threshold = 85  # Fuzzy match threshold
    
    def _load_sanctions(self) -> list[dict]:
        """Load sanctions list from file"""
        sanctions = []
        
        # Default sanctions list if file doesn't exist
        default_sanctions = [
            {"name": "Evil Corp International", "list": "OFAC SDN", "details": "Sanctions for money laundering"},
            {"name": "BadActor Industries", "list": "UN Sanctions", "details": "Human rights violations"},
            {"name": "Sanctioned Trading Co", "list": "EU Sanctions", "details": "Arms trafficking"},
            {"name": "Blocked Enterprises LLC", "list": "OFAC SDN", "details": "Terrorism financing"},
            {"name": "Prohibited Partners", "list": "UN Sanctions", "details": "Nuclear proliferation"},
        ]
        
        if self.sanctions_file.exists():
            # Load from file
            with open(self.sanctions_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('|')
                        if len(parts) >= 2:
                            sanctions.append({
                                "name": parts[0].strip(),
                                "list": parts[1].strip(),
                                "details": parts[2].strip() if len(parts) > 2 else ""
                            })
        else:
            sanctions = default_sanctions
        
        return sanctions
    
    def check_sanctions(self, company_info: CompanyInfo) -> ToolResult:
        """Check company against sanctions lists"""
        try:
            company_name = company_info.company_name
            
            # Fuzzy match against all sanctioned entities
            best_match = None
            best_score = 0
            
            for sanctioned in self.sanctions_list:
                # Try multiple matching algorithms
                ratio = fuzz.ratio(company_name.lower(), sanctioned["name"].lower())
                partial = fuzz.partial_ratio(company_name.lower(), sanctioned["name"].lower())
                token_sort = fuzz.token_sort_ratio(company_name.lower(), sanctioned["name"].lower())
                
                # Take the best score
                score = max(ratio, partial, token_sort)
                
                if score > best_score:
                    best_score = score
                    best_match = sanctioned
            
            # Determine if it's a match
            if best_score >= self.match_threshold:
                result = SanctionsResult(
                    match=True,
                    matched_name=best_match["name"],
                    list_name=best_match["list"],
                    match_score=best_score / 100.0,
                    details=best_match["details"]
                )
            else:
                result = SanctionsResult(
                    match=False,
                    match_score=best_score / 100.0
                )
            
            return ToolResult(
                tool_name="check_sanctions",
                success=True,
                data=result.model_dump(),
                next_action="compute_risk"
            )
        
        except Exception as e:
            return ToolResult(
                tool_name="check_sanctions",
                success=False,
                error=f"Sanctions check failed: {str(e)}"
            )

