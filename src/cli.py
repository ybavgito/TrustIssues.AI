"""Command-line interface for RiskLens AI"""
import sys
from pathlib import Path

# Ensure project root is in path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from colorama import Fore, Style, init
from tabulate import tabulate

from src.models import AgentState
from src.state_manager import StateManager
from src.agent import RiskLensAgent
from src.industry_config import detect_industry, get_industry_profile

# Initialize colorama
init(autoreset=True)


class RiskLensCLI:
    """Interactive CLI for human-in-the-loop approval"""
    
    def __init__(self):
        self.state_manager = StateManager()
        self.agent = RiskLensAgent(self.state_manager)
    
    def run(self, pdf_path: str = None):
        """Main CLI entry point"""
        self._print_banner()
        
        if pdf_path:
            # Process new submission
            self._process_new_submission(pdf_path)
        else:
            # Interactive mode
            self._interactive_mode()
    
    def _print_banner(self):
        """Print application banner"""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║           RiskLens AI - Vendor Onboarding               ║
║        Automated Risk Assessment & Verification         ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(banner)
    
    def _interactive_mode(self):
        """Interactive menu"""
        while True:
            print(f"\n{Fore.YELLOW}Main Menu:{Style.RESET_ALL}")
            print("1. Process new vendor PDF")
            print("2. Review pending cases")
            print("3. View completed cases")
            print("4. Exit")
            
            choice = input(f"\n{Fore.GREEN}Select option: {Style.RESET_ALL}").strip()
            
            if choice == "1":
                pdf_path = input(f"{Fore.GREEN}Enter PDF path: {Style.RESET_ALL}").strip()
                if pdf_path:
                    self._process_new_submission(pdf_path)
            
            elif choice == "2":
                self._review_pending_cases()
            
            elif choice == "3":
                self._view_completed_cases()
            
            elif choice == "4":
                print(f"{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
                sys.exit(0)
            
            else:
                print(f"{Fore.RED}Invalid option{Style.RESET_ALL}")
    
    def _process_new_submission(self, pdf_path: str):
        """Process a new vendor submission"""
        pdf_file = Path(pdf_path)
        
        if not pdf_file.exists():
            print(f"{Fore.RED}Error: PDF file not found: {pdf_path}{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"Processing: {pdf_file.name}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        # Run agent workflow
        state = self.agent.run(str(pdf_file.absolute()))
        
        # Display results and request human review if needed
        if state.requires_human_review:
            self._human_review_interface(state)
        else:
            self._display_final_results(state)
    
    def _review_pending_cases(self):
        """Review cases waiting for human approval"""
        sessions = self.state_manager.list_sessions()
        pending = []
        
        for session_id in sessions:
            try:
                state = self.state_manager.load_state(session_id)
                if state.requires_human_review and state.human_decision is None:
                    pending.append(state)
            except:
                continue
        
        if not pending:
            print(f"\n{Fore.YELLOW}No pending cases for review{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}Pending Cases: {len(pending)}{Style.RESET_ALL}\n")
        
        for i, state in enumerate(pending, 1):
            print(f"{i}. {state.company_info.company_name if state.company_info else 'Unknown'} "
                  f"(Session: {state.session_id}) - Risk: {state.risk_score.risk_level if state.risk_score else 'N/A'}")
        
        choice = input(f"\n{Fore.GREEN}Select case to review (or 0 to cancel): {Style.RESET_ALL}").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(pending):
                self._human_review_interface(pending[idx])
        except:
            pass
    
    def _view_completed_cases(self):
        """View completed cases"""
        sessions = self.state_manager.list_sessions()
        completed = []
        
        for session_id in sessions:
            try:
                state = self.state_manager.load_state(session_id)
                if state.workflow_complete:
                    completed.append(state)
            except:
                continue
        
        if not completed:
            print(f"\n{Fore.YELLOW}No completed cases{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}Completed Cases: {len(completed)}{Style.RESET_ALL}\n")
        
        for state in completed:
            company = state.company_info.company_name if state.company_info else 'Unknown'
            decision = state.human_decision or 'Pending'
            risk = state.risk_score.risk_level if state.risk_score else 'N/A'
            
            print(f"• {company}")
            print(f"  Session: {state.session_id}")
            print(f"  Risk Level: {risk}")
            print(f"  Decision: {decision}")
            if state.access_recommendation:
                print(f"  Access Level: {state.access_recommendation.access_level}")
            print()
    
    def _human_review_interface(self, state: AgentState):
        """Interactive human review interface"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"HUMAN REVIEW REQUIRED")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        # Display agent collaboration (NEW: Show how agents worked together)
        self._display_agent_collaboration(state)
        
        # Display company information
        self._display_company_info(state)
        
        # Display verification results
        self._display_verification_results(state)
        
        # Display risk assessment
        self._display_risk_assessment(state)
        
        # Display risk explanation
        self._display_risk_explanation(state)
        
        # Review reason
        print(f"\n{Fore.YELLOW}Review Reason:{Style.RESET_ALL}")
        print(f"  {state.review_reason}")
        
        # Get human decision
        print(f"\n{Fore.GREEN}{'='*60}")
        print("DECISION REQUIRED")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        print("1. APPROVE - Grant access to vendor")
        print("2. REJECT - Deny vendor onboarding")
        print("3. REQUEST MORE INFO - Ask for additional documentation")
        
        decision = input(f"\n{Fore.GREEN}Your decision (1-3): {Style.RESET_ALL}").strip()
        
        decision_map = {
            "1": "approved",
            "2": "rejected",
            "3": "request_more_info"
        }
        
        if decision in decision_map:
            state.human_decision = decision_map[decision]
            state.human_notes = input(f"{Fore.GREEN}Notes (optional): {Style.RESET_ALL}").strip()
            
            # Save decision
            self.state_manager.save_state(state)
            
            print(f"\n{Fore.CYAN}Decision recorded: {state.human_decision.upper()}{Style.RESET_ALL}")
            
            # If approved, continue workflow to generate access recommendation
            if state.human_decision == "approved":
                print(f"\n{Fore.CYAN}Generating access recommendations...{Style.RESET_ALL}\n")
                state = self.agent.run(state.pdf_path, state.session_id)
                self._display_final_results(state)
        else:
            print(f"{Fore.RED}Invalid decision{Style.RESET_ALL}")
    
    def _display_company_info(self, state: AgentState):
        """Display company information"""
        if not state.company_info:
            return
        
        print(f"{Fore.CYAN}Company Information:{Style.RESET_ALL}")
        info = [
            ["Name", state.company_info.company_name or "N/A"],
            ["Registration #", state.company_info.registration_number or "N/A"],
            ["Incorporation Date", state.company_info.incorporation_date or "N/A"],
            ["Address", state.company_info.address or "N/A"],
            ["Business Type", state.company_info.business_type or "N/A"],
            ["Email", state.company_info.contact_email or "N/A"],
            ["Phone", state.company_info.contact_phone or "N/A"],
        ]
        print(tabulate(info, tablefmt="simple"))
        print()
    
    def _display_verification_results(self, state: AgentState):
        """Display verification results"""
        print(f"{Fore.CYAN}Verification Results:{Style.RESET_ALL}")
        
        results = []
        
        # Registry
        if state.registry_result:
            status = "✓ MATCH" if state.registry_result.match else "✗ NOT FOUND"
            color = Fore.GREEN if state.registry_result.match else Fore.RED
            results.append([
                "Registry Check",
                f"{color}{status}{Style.RESET_ALL}",
                state.registry_result.status or "N/A",
                f"{state.registry_result.confidence:.0%}"
            ])
        
        # Sanctions
        if state.sanctions_result:
            status = "⚠ MATCH" if state.sanctions_result.match else "✓ CLEAR"
            color = Fore.RED if state.sanctions_result.match else Fore.GREEN
            results.append([
                "Sanctions Check",
                f"{color}{status}{Style.RESET_ALL}",
                state.sanctions_result.list_name or "N/A",
                f"{state.sanctions_result.match_score:.0%}"
            ])
        
        print(tabulate(results, headers=["Check", "Result", "Details", "Confidence"], tablefmt="simple"))
        print()
    
    def _display_risk_assessment(self, state: AgentState):
        """Display risk assessment with industry context"""
        if not state.risk_score:
            return
        
        print(f"{Fore.CYAN}Risk Assessment:{Style.RESET_ALL}")
        
        # Display industry context
        if state.company_info:
            industry = detect_industry(state.company_info.business_type, state.company_info.address)
            industry_profile = get_industry_profile(industry)
            print(f"\n{Fore.MAGENTA}  Industry: {industry_profile.name}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}  Regulatory: {industry_profile.regulatory_strictness.upper()}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}  Typical Risk: {industry_profile.typical_risk_level.upper()}{Style.RESET_ALL}\n")
        
        # Risk level with color
        level = state.risk_score.risk_level.upper()
        color = {
            'LOW': Fore.GREEN,
            'MEDIUM': Fore.YELLOW,
            'HIGH': Fore.RED
        }.get(level, Fore.WHITE)
        
        print(f"  Risk Level: {color}{level}{Style.RESET_ALL}")
        print(f"  Risk Score: {state.risk_score.total_score}")
        print(f"\n  Score Breakdown:")
        for factor, points in state.risk_score.breakdown.items():
            sign = "+" if points >= 0 else ""
            print(f"    {factor}: {sign}{points}")
        
        print(f"\n  Risk Flags:")
        for flag in state.risk_score.flags:
            print(f"    • {flag}")
        print()
    
    def _display_risk_explanation(self, state: AgentState):
        """Display risk explanation"""
        if not state.risk_explanation:
            return
        
        print(f"{Fore.CYAN}Risk Analysis:{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Summary:{Style.RESET_ALL}")
        print(f"  {state.risk_explanation.summary}")
        
        print(f"\n{Fore.YELLOW}Key Factors:{Style.RESET_ALL}")
        for factor in state.risk_explanation.key_factors:
            print(f"  • {factor}")
        
        print(f"\n{Fore.YELLOW}Assumptions:{Style.RESET_ALL}")
        for assumption in state.risk_explanation.assumptions:
            print(f"  • {assumption}")
        
        print(f"\n{Fore.YELLOW}Unknowns/Uncertainties:{Style.RESET_ALL}")
        for unknown in state.risk_explanation.unknowns:
            print(f"  • {unknown}")
        
        print(f"\n{Fore.YELLOW}Recommendation:{Style.RESET_ALL}")
        print(f"  {state.risk_explanation.recommendation}")
        print()
    
    def _display_agent_collaboration(self, state: AgentState):
        """Display how agents collaborated (NEW: Agentic transparency)"""
        if not state.agent_decisions:
            return
        
        print(f"{Fore.CYAN}Agent Collaboration:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}\n")
        
        # Show key decisions from each agent
        agents_shown = set()
        for decision in state.agent_decisions:
            if decision.agent_id not in agents_shown:
                agents_shown.add(decision.agent_id)
                
                # Agent emoji
                emoji = {
                    "coordinator": "🎯",
                    "extractor": "📄",
                    "verifier": "🔍",
                    "risk_analyst": "📊"
                }.get(decision.agent_id, "🤖")
                
                agent_name = decision.agent_id.replace("_", " ").title()
                
                print(f"{emoji} {Fore.YELLOW}{agent_name}:{Style.RESET_ALL}")
                print(f"   {decision.reasoning[:150]}...")
                
                if decision.tool_calls:
                    tools = [tc["function"] for tc in decision.tool_calls]
                    print(f"   Tools used: {', '.join(tools)}")
                
                if decision.confidence:
                    conf_color = Fore.GREEN if decision.confidence > 0.7 else Fore.YELLOW
                    print(f"   Confidence: {conf_color}{decision.confidence:.0%}{Style.RESET_ALL}")
                
                print()
        
        # Show agent messages if any
        if state.agent_messages:
            recent_messages = state.agent_messages[-3:]
            if recent_messages:
                print(f"{Fore.CYAN}Agent Messages:{Style.RESET_ALL}")
                for msg in recent_messages:
                    print(f"  {msg.sender} → {msg.receiver}: {msg.content[:80]}...")
                print()
    
    def _display_final_results(self, state: AgentState):
        """Display final results with access recommendations"""
        print(f"\n{Fore.GREEN}{'='*60}")
        print("WORKFLOW COMPLETE")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        # Show agent collaboration summary
        if state.agent_decisions:
            print(f"{Fore.CYAN}Agents involved: {Style.RESET_ALL}", end="")
            agents = list(set(d.agent_id for d in state.agent_decisions))
            print(", ".join(agents))
            print()
        
        if state.access_recommendation:
            print(f"{Fore.CYAN}Access Recommendation:{Style.RESET_ALL}")
            print(f"  Level: {state.access_recommendation.access_level.upper()}")
            
            print(f"\n  Permissions Granted:")
            for perm in state.access_recommendation.permissions:
                print(f"    ✓ {perm}")
            
            print(f"\n  Restrictions:")
            for restriction in state.access_recommendation.restrictions:
                print(f"    ⚠ {restriction}")
            
            print(f"\n  Justification:")
            print(f"    {state.access_recommendation.justification}")
        else:
            print(f"{Fore.YELLOW}No access granted{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Session ID: {state.session_id}{Style.RESET_ALL}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RiskLens AI - Automated Vendor Onboarding')
    parser.add_argument('--pdf', type=str, help='Path to vendor PDF document')
    
    args = parser.parse_args()
    
    cli = RiskLensCLI()
    cli.run(args.pdf)


if __name__ == '__main__':
    main()

