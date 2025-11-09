"""Agentic Multi-Agent System for RiskLens AI

This is the new agentic version that uses Nemotron-powered specialist agents
that reason, collaborate, and dynamically decide actions using function calling.
"""
import json
from datetime import datetime
from typing import Optional
from colorama import Fore, Style, init

from src.models import (
    AgentState, CompanyInfo, RegistryResult, SanctionsResult,
    RiskScore, RiskExplanation, AgentDecision, AccessRecommendation
)
from src.state_manager import StateManager
from src.agents import (
    CoordinatorAgent, ExtractorAgent, VerificationAgent,
    RiskAnalystAgent, AgentCommunication
)
from src.tools import (
    PDFExtractor, RegistryChecker, SanctionsChecker,
    RiskCalculator, RiskExplainer, AccessRecommender
)

# Initialize colorama
init(autoreset=True)


class RiskLensAgent:
    """
    Agentic multi-agent system for automated vendor onboarding.
    
    Instead of deterministic if/else logic, this system uses:
    - Coordinator Agent: Decides which specialist acts next (Nemotron-powered)
    - Specialist Agents: Reason about actions and call tools (Nemotron-powered)
    - Agent Communication: Agents collaborate and share findings
    - Function Calling: Agents dynamically choose tools via OpenAI function calling
    
    Workflow: Coordinator reasons → Specialist reasons → Tool execution → Repeat
    """
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        
        # Initialize specialist agents (Nemotron-powered)
        self.coordinator = CoordinatorAgent()
        self.extractor = ExtractorAgent()
        self.verifier = VerificationAgent()
        self.risk_analyst = RiskAnalystAgent()
        
        # Communication system
        self.communication = AgentCommunication()
        
        # Initialize tools (agents call these via function calling)
        self.pdf_extractor = PDFExtractor()
        self.registry_checker = RegistryChecker()
        self.sanctions_checker = SanctionsChecker()
        self.risk_calculator = RiskCalculator()
        self.risk_explainer = RiskExplainer()
        self.access_recommender = AccessRecommender()
    
    def run(self, pdf_path: str, session_id: Optional[str] = None) -> AgentState:
        """
        Run the agentic workflow
        
        Flow:
        1. Coordinator reasons about which agent should act
        2. Specialist agent reasons about what to do
        3. Specialist agent calls tools via function calling
        4. Tools execute and update state
        5. Repeat until workflow complete or human review needed
        """
        # Initialize or load state
        if session_id:
            state = self.state_manager.load_state(session_id)
            self._log("info", f"Resuming session {session_id}")
            
            # If resuming after human approval, generate access recommendation
            if state.human_decision == "approved" and not state.access_recommendation:
                result = self.access_recommender.recommend_access(
                    state.risk_score,
                    state.human_decision,
                    state.human_notes
                )
                if result.success:
                    state.access_recommendation = AccessRecommendation(**result.data)
                    state.workflow_complete = True
                    self.state_manager.save_state(state)
                return state
        else:
            # Generate unique session ID with microseconds to prevent collisions
            import uuid
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]  # Short UUID suffix
            session_id = f"{timestamp}_{unique_id}"
            state = AgentState(session_id=session_id, pdf_path=pdf_path)
            self._log("info", f"Starting new agentic session {session_id}")
        
        # Agentic Loop
        max_iterations = 20
        iteration = 0
        last_3_agents = []  # Track last 3 agents to prevent looping
        
        while not state.workflow_complete and iteration < max_iterations:
            iteration += 1
            
            self._log("observe", f"Iteration {iteration}")
            self._print_state_summary(state)
            
            # AGENTIC PLANNING: Coordinator decides which agent acts
            next_agent_id, coordinator_reasoning = self._agentic_planning(state)
            
            if next_agent_id is None:
                self._log("info", "Coordinator: Workflow complete or awaiting human review")
                break
            
            # LOOP PREVENTION: Check if same agent called 3 times in a row
            last_3_agents.append(next_agent_id)
            if len(last_3_agents) > 3:
                last_3_agents.pop(0)
            
            if len(last_3_agents) == 3 and len(set(last_3_agents)) == 1:
                self._log("warning", f"⚠️ Agent {next_agent_id} called 3 times in a row - forcing workflow to continue")
                # Force extraction as complete if extractor is looping
                if next_agent_id == "extractor" and not state.company_info:
                    self._log("warning", "Extractor stuck - moving forward with partial data")
                    # Move to next phase anyway
                    next_agent_id = "verifier"
                    last_3_agents = [next_agent_id]  # Reset counter
                elif next_agent_id == "verifier":
                    # Move to risk analyst
                    next_agent_id = "risk_analyst"
                    last_3_agents = [next_agent_id]
            
            self._log("decide", f"Coordinator delegates to: {next_agent_id}")
            self._log("decide", f"Reasoning: {coordinator_reasoning[:150]}...")
            
            state.current_agent = next_agent_id
            
            # Get the specialist agent
            agent = self._get_agent(next_agent_id)
            
            # AGENT REASONING: Specialist reasons about what to do
            self._log("act", f"{next_agent_id.upper()}: Reasoning about action...")
            decision = agent.reason(state=state, coordinator_guidance=coordinator_reasoning)
            
            # Log agent's reasoning
            self._log("act", f"{next_agent_id.upper()}: {decision.reasoning[:200]}...")
            state.agent_decisions.append(decision)
            
            # TOOL EXECUTION: Execute agent's tool calls
            if decision.tool_calls:
                for tool_call in decision.tool_calls:
                    self._execute_tool_call(tool_call, state, next_agent_id)
            
            # Save state after each agent action (before checking for human review)
            self.state_manager.save_state(state)
            
            # Check if agent requests human review
            if decision.requests_human_review:
                state.requires_human_review = True
                if not state.review_reason:
                    state.review_reason = decision.reasoning
                self._log("info", "Agent requests human review")
                # Save state with human review flag before breaking
                self.state_manager.save_state(state)
                break
            
            # Automatically require human review after risk assessment is complete
            if state.risk_score and state.risk_explanation and not state.requires_human_review:
                state.requires_human_review = True
                state.review_reason = "Risk assessment complete - human approval required"
                # Keep current_agent set so frontend can show which agent completed
                # Don't clear it - helps with visibility
                self._log("info", "Risk assessment complete → requesting human review")
                # Save state with human review flag before breaking
                self.state_manager.save_state(state)
                break
            
            # Check if human review needed based on state
            if state.requires_human_review:
                break
        
        if iteration >= max_iterations:
            self._log("error", "Max iterations reached - workflow stopped")
        
        return state
    
    def _agentic_planning(self, state: AgentState) -> tuple[Optional[str], str]:
        """
        Use Coordinator Agent to decide which specialist should act next
        
        This replaces the deterministic if/else planner with Nemotron reasoning
        """
        # Coordinator reasons about next step
        decision = self.coordinator.reason(state=state)
        
        # Parse coordinator's decision
        reasoning = decision.reasoning
        
        # Check for messages to other agents (coordinator delegates via messages)
        coordinator_messages = [
            msg for msg in state.agent_messages 
            if msg.sender == "coordinator" 
            and msg.timestamp > state.updated_at
        ]
        
        # Determine next agent from coordinator's tool calls or reasoning
        next_agent = None
        
        if decision.tool_calls:
            for tool_call in decision.tool_calls:
                if tool_call["function"] == "send_message":
                    to_agent = tool_call["arguments"].get("to_agent")
                    if to_agent in ["extractor", "verifier", "risk_analyst"]:
                        next_agent = to_agent
                        # Actually send the message
                        self.communication.send_message(
                            "coordinator",
                            to_agent,
                            tool_call["arguments"].get("message", reasoning),
                            state
                        )
                        break
        
        # Fallback: Infer from reasoning if no explicit delegation
        if not next_agent:
            next_agent = self._infer_next_agent(state, reasoning)
        
        # Check if workflow should end
        if self._should_end_workflow(state, reasoning):
            return None, reasoning
        
        return next_agent, reasoning
    
    def _infer_next_agent(self, state: AgentState, reasoning: str) -> Optional[str]:
        """Infer which agent should act based on state and coordinator's ADAPTIVE reasoning"""
        reasoning_lower = reasoning.lower()
        
        # ADAPTIVE: Check coordinator's reasoning for adaptive strategies
        # Fast path: Skip verification for low-risk companies
        if any(phrase in reasoning_lower for phrase in ["fast path", "skip verification", "skip detailed", "well-established", "fortune 500"]):
            if state.company_info and not state.risk_score:
                # Sanctions check still mandatory, but can skip registry
                if not state.sanctions_result:
                    return "verifier"  # Still need sanctions check
                else:
                    return "risk_analyst"  # Skip to risk assessment
        
        # Enhanced path: Extra verification for high-risk
        if any(phrase in reasoning_lower for phrase in ["enhanced path", "thorough checks", "high-risk", "extra verification"]):
            if state.company_info and (not state.registry_result or not state.sanctions_result):
                return "verifier"  # Do enhanced verification
        
        # Immediate: Sanctions match detected
        if any(phrase in reasoning_lower for phrase in ["sanctions list", "sanctions match", "immediate"]):
            if state.sanctions_result and state.sanctions_result.match:
                return "risk_analyst"  # Skip to risk assessment immediately
        
        # Standard workflow (fallback to state-based)
        # 1. If no company data, need extraction
        if not state.company_info:
            return "extractor"
        
        # 2. If have company data but no verification, need verifier
        # BUT: Check if coordinator wants to skip (fast path)
        if state.company_info and (not state.registry_result or not state.sanctions_result):
            # Sanctions is always mandatory
            if not state.sanctions_result:
                return "verifier"
            # Registry can be skipped in fast path
            if not state.registry_result and "skip" not in reasoning_lower:
                return "verifier"
        
        # 3. If verified (or skipped) but no risk assessment, need risk analyst
        if state.company_info and (state.sanctions_result or "skip" in reasoning_lower) and not state.risk_score:
            return "risk_analyst"
        
        # 4. If risk score done but no explanation, need risk analyst
        if state.risk_score and not state.risk_explanation:
            return "risk_analyst"
        
        # 5. All done, request human review
        if state.risk_score and state.risk_explanation:
            return "risk_analyst"  # For final human review request
        
        return None
    
    def _should_end_workflow(self, state: AgentState, reasoning: str) -> bool:
        """Determine if workflow should end"""
        # End if human review is required
        if state.requires_human_review and not state.human_decision:
            return True
        
        # End if human decision is final
        if state.human_decision in ["rejected", "request_more_info"]:
            state.workflow_complete = True
            return True
        
        # End if access recommendation generated
        if state.access_recommendation:
            state.workflow_complete = True
            return True
        
        # Check reasoning for completion indicators
        reasoning_lower = reasoning.lower()
        if any(word in reasoning_lower for word in ["complete", "done", "finished", "human review"]):
            if state.risk_score and state.risk_explanation:
                return True
        
        return False
    
    def _get_agent(self, agent_id: str):
        """Get agent by ID"""
        agents = {
            "extractor": self.extractor,
            "verifier": self.verifier,
            "risk_analyst": self.risk_analyst,
        }
        return agents.get(agent_id)
    
    def _execute_tool_call(self, tool_call: dict, state: AgentState, agent_id: str):
        """Execute a tool call made by an agent"""
        function_name = tool_call["function"]
        arguments = tool_call["arguments"]
        
        # Safety check: Skip redundant tool calls
        if function_name == "extract_from_pdf" and state.company_info:
            self._log("warning", f"  ⚠️ Skipping {function_name} - already extracted: {state.company_info.company_name}")
            return
        
        if function_name == "search_registry" and state.registry_result:
            self._log("warning", f"  ⚠️ Skipping {function_name} - registry already checked")
            return
        
        if function_name == "check_sanctions" and state.sanctions_result:
            self._log("warning", f"  ⚠️ Skipping {function_name} - sanctions already checked")
            return
        
        if function_name == "compute_risk" and state.risk_score:
            self._log("warning", f"  ⚠️ Skipping {function_name} - risk already computed: {state.risk_score.total_score}")
            return
        
        if function_name == "explain_risk" and state.risk_explanation:
            self._log("warning", f"  ⚠️ Skipping {function_name} - explanation already generated")
            return
        
        self._log("act", f"  Calling tool: {function_name}")
        
        try:
            if function_name == "extract_from_pdf":
                result = self.pdf_extractor.extract_from_pdf(state.pdf_path)
                if result.success and result.data:
                    state.company_info = CompanyInfo(**result.data)
                    state.completed_steps.append("extract_from_pdf")
                    self._log("success", f"  ✓ Extracted: {state.company_info.company_name}")
            
            elif function_name == "search_registry":
                result = self.registry_checker.search_registry(state.company_info)
                if result.success and result.data:
                    state.registry_result = RegistryResult(**result.data)
                    state.completed_steps.append("search_registry")
                    status = "MATCH" if state.registry_result.match else "NOT FOUND"
                    self._log("success", f"  ✓ Registry: {status}")
            
            elif function_name == "check_sanctions":
                result = self.sanctions_checker.check_sanctions(state.company_info)
                if result.success and result.data:
                    state.sanctions_result = SanctionsResult(**result.data)
                    state.completed_steps.append("check_sanctions")
                    status = "MATCH" if state.sanctions_result.match else "CLEAR"
                    self._log("success", f"  ✓ Sanctions: {status}")
            
            elif function_name == "compute_risk":
                flags = arguments.get("flags", {})
                result = self.risk_calculator.compute_risk(
                    state.company_info,
                    state.registry_result,
                    state.sanctions_result,
                    flags
                )
                if result.success and result.data:
                    state.risk_score = RiskScore(**result.data)
                    state.completed_steps.append("compute_risk")
                    self._log("success", f"  ✓ Risk Score: {state.risk_score.total_score} ({state.risk_score.risk_level})")
                    
                    # Generate explanation using LLM
                    explain_result = self.risk_explainer.explain_risk(
                        state.company_info,
                        state.registry_result,
                        state.sanctions_result,
                        state.risk_score
                    )
                    if explain_result.success and explain_result.data:
                        state.risk_explanation = RiskExplanation(**explain_result.data)
                        state.completed_steps.append("explain_risk")
            
            elif function_name == "get_additional_info":
                query = arguments.get("query", "")
                info = self._get_additional_info(query, state)
                self._log("success", f"  ✓ Retrieved info: {info[:100]}...")
                # Send info back to agent via message
                self.communication.send_message(
                    "system",
                    agent_id,
                    f"Additional info for '{query}': {info}",
                    state
                )
            
            elif function_name == "request_human_review":
                reason = arguments.get("reason", "Agent requested review")
                urgency = arguments.get("urgency", "medium")
                state.requires_human_review = True
                state.review_reason = f"[{urgency.upper()}] {reason}"
                self._log("info", f"  Human review requested: {reason}")
            
            elif function_name == "send_message":
                # Parse message from reasoning if not in arguments
                to_agent = arguments.get("to_agent")
                message = arguments.get("message")
                priority = arguments.get("priority", "normal")
                
                # If not provided, try to infer from reasoning context
                if not to_agent or not message:
                    # Look for agent mentions in recent decisions
                    if state.agent_decisions:
                        last_reasoning = state.agent_decisions[-1].reasoning.lower()
                        # Try to find target agent
                        if "risk_analyst" in last_reasoning or "risk analyst" in last_reasoning:
                            to_agent = "risk_analyst"
                        elif "verifier" in last_reasoning or "verification" in last_reasoning:
                            to_agent = "verifier"
                        elif "extractor" in last_reasoning:
                            to_agent = "extractor"
                        elif "coordinator" in last_reasoning:
                            to_agent = "coordinator"
                    
                    # Use a default message if none provided
                    if not message:
                        message = f"Message from {agent_id}: {state.agent_decisions[-1].reasoning[:200] if state.agent_decisions else 'Important finding'}"
                
                if to_agent:
                    # Check for high priority keywords
                    if any(word in message.lower() for word in ["critical", "urgent", "sanctions match", "high risk"]):
                        priority = "high"
                    
                    self.communication.send_message(agent_id, to_agent, message, state, priority)
                    self._log("success", f"  ✓ Message sent to {to_agent} ({priority} priority)")
                else:
                    self._log("warning", f"  ⚠ send_message called but target agent unclear")
        
        except Exception as e:
            self._log("error", f"  ✗ Tool execution failed: {str(e)}")
    
    def _get_additional_info(self, query: str, state: AgentState) -> str:
        """Simple RAG: Return context-specific information"""
        query_lower = query.lower()
        
        if "registry" in query_lower and state.registry_result:
            return f"Registry verification: Match={state.registry_result.match}, Status={state.registry_result.status}, Confidence={state.registry_result.confidence:.0%}"
        
        if "sanction" in query_lower and state.sanctions_result:
            return f"Sanctions screening: Match={state.sanctions_result.match}, Score={state.sanctions_result.match_score:.0%}"
        
        if "risk" in query_lower and state.risk_score:
            return f"Risk assessment: Score={state.risk_score.total_score}, Level={state.risk_score.risk_level}, Breakdown={state.risk_score.breakdown}"
        
        if "company" in query_lower and state.company_info:
            return f"Company: {state.company_info.company_name}, Reg#={state.company_info.registration_number}"
        
        return "No additional information available for this query."
    
    def _print_state_summary(self, state: AgentState):
        """Print current state summary"""
        company = state.company_info.company_name if state.company_info else "Not extracted"
        print(f"  Company: {company}")
        print(f"  Registry: {'✓' if state.registry_result else '○'} | "
              f"Sanctions: {'✓' if state.sanctions_result else '○'} | "
              f"Risk: {'✓' if state.risk_score else '○'} | "
              f"Explanation: {'✓' if state.risk_explanation else '○'}")
        
        # Show active agent
        if state.current_agent:
            print(f"  Active Agent: {state.current_agent}")
    
    def _log(self, level: str, message: str):
        """Colored logging"""
        colors = {
            'info': Fore.CYAN,
            'observe': Fore.BLUE,
            'decide': Fore.YELLOW,
            'act': Fore.MAGENTA,
            'success': Fore.GREEN,
            'error': Fore.RED,
        }
        color = colors.get(level, Fore.WHITE)
        prefix = {
            'observe': '👁  OBSERVE',
            'decide': '🧠 DECIDE',
            'act': '🤖 ACT',
            'success': '✓ SUCCESS',
            'error': '✗ ERROR',
            'info': 'ℹ INFO'
        }.get(level, level.upper())
        
        print(f"{color}{prefix}: {message}{Style.RESET_ALL}")

