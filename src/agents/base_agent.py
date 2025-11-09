"""Base agent class with Nemotron reasoning capabilities"""
import os
import json
from abc import ABC, abstractmethod
from typing import Optional, Any
from openai import OpenAI

from src.models import AgentState, AgentDecision, AgentMessage


class BaseAgent(ABC):
    """
    Abstract base class for all agentic agents.
    
    Uses NVIDIA Nemotron via OpenAI-compatible API for:
    - Reasoning about current state
    - Deciding which tools to call
    - Function calling to execute tools
    - Communication with other agents
    """
    
    def __init__(self, agent_id: str, system_prompt: str):
        """
        Initialize base agent
        
        Args:
            agent_id: Unique identifier for this agent
            system_prompt: System prompt defining agent's role and capabilities
        """
        self.agent_id = agent_id
        self.system_prompt = system_prompt
        
        # Initialize Nemotron client
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        
        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY not found in environment")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        self.model = "nvidia/llama-3.3-nemotron-super-49b-v1.5"
        
        # Conversation history for this agent
        self.conversation_history = []
    
    def reason(
        self,
        state: AgentState,
        coordinator_guidance: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> AgentDecision:
        """
        Use Nemotron to reason about current state and decide next action
        
        Args:
            state: Current agent state
            coordinator_guidance: Optional guidance from coordinator agent
            additional_context: Optional additional context
            
        Returns:
            AgentDecision with reasoning, tool calls, and recommendations
        """
        # Build context for Nemotron
        context = self._build_context(state, coordinator_guidance, additional_context)
        
        # Get messages from other agents
        incoming_messages = [msg for msg in state.agent_messages if msg.receiver == self.agent_id]
        if incoming_messages:
            latest_messages = incoming_messages[-3:]  # Last 3 messages
            messages_text = "\n".join([
                f"Message from {msg.sender}: {msg.content}" 
                for msg in latest_messages
            ])
            context += f"\n\nRECENT MESSAGES:\n{messages_text}"
        
        # Prepare messages for Nemotron
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context}
        ]
        
        # Add conversation history
        messages.extend(self.conversation_history[-4:])  # Last 2 exchanges
        
        try:
            # Call Nemotron (without function calling - parse from response instead)
            # NVIDIA NIM doesn't fully support OpenAI function calling protocol yet
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower for more deterministic reasoning
                max_tokens=1500
            )
            
            # Extract response
            message = response.choices[0].message
            reasoning = message.content or "No explicit reasoning provided"
            
            # Save to conversation history
            self.conversation_history.append({"role": "user", "content": context})
            self.conversation_history.append({
                "role": "assistant",
                "content": reasoning
            })
            
            # Parse tool calls from reasoning text
            # Agents will specify tools in their response like:
            # "TOOL: extract_from_pdf" or "TOOLS: search_registry, check_sanctions"
            tool_calls = self._parse_tool_calls_from_text(reasoning)
            
            # Check if agent requests human review
            requests_review = any(
                tc["function"] == "request_human_review" 
                for tc in tool_calls
            )
            
            # Create decision object
            decision = AgentDecision(
                agent_id=self.agent_id,
                reasoning=reasoning,
                tool_calls=tool_calls,
                confidence=self._estimate_confidence(reasoning, tool_calls),
                requests_human_review=requests_review
            )
            
            return decision
        
        except Exception as e:
            # Fallback decision if Nemotron fails
            return AgentDecision(
                agent_id=self.agent_id,
                reasoning=f"Error during reasoning: {str(e)}. Falling back to default behavior.",
                tool_calls=[],
                confidence=0.0,
                requests_human_review=True  # Request human review on errors
            )
    
    def _build_context(
        self,
        state: AgentState,
        coordinator_guidance: Optional[str],
        additional_context: Optional[str]
    ) -> str:
        """Build context string for Nemotron"""
        context_parts = []
        
        # Coordinator guidance
        if coordinator_guidance:
            context_parts.append(f"COORDINATOR GUIDANCE:\n{coordinator_guidance}\n")
        
        # Current state summary
        context_parts.append(self._summarize_state(state))
        
        # Additional context
        if additional_context:
            context_parts.append(f"\nADDITIONAL CONTEXT:\n{additional_context}")
        
        # What's been completed
        if state.completed_steps:
            context_parts.append(f"\nCOMPLETED STEPS:\n{', '.join(state.completed_steps)}")
        
        # Recent agent decisions
        if state.agent_decisions:
            recent = state.agent_decisions[-2:]  # Last 2 decisions
            decisions_text = "\n".join([
                f"- {d.agent_id}: {d.reasoning[:100]}..." 
                for d in recent
            ])
            context_parts.append(f"\nRECENT DECISIONS:\n{decisions_text}")
        
        return "\n".join(context_parts)
    
    @abstractmethod
    def _summarize_state(self, state: AgentState) -> str:
        """
        Create agent-specific state summary
        
        Each agent implements this to focus on relevant state information
        """
        pass
    
    def _estimate_confidence(self, reasoning: str, tool_calls: list[dict]) -> float:
        """Estimate confidence based on reasoning quality and tool calls"""
        confidence = 0.5  # Base confidence
        
        # Higher confidence if specific tools are being called
        if tool_calls:
            confidence += 0.2
        
        # Check reasoning quality indicators
        if reasoning and len(reasoning) > 50:
            confidence += 0.1
        
        if any(word in reasoning.lower() for word in ['confident', 'clear', 'verified', 'confirmed']):
            confidence += 0.1
        
        if any(word in reasoning.lower() for word in ['uncertain', 'unclear', 'maybe', 'possibly']):
            confidence -= 0.2
        
        return min(max(confidence, 0.0), 1.0)
    
    def send_message(
        self,
        to_agent: str,
        message: str,
        state: AgentState,
        priority: str = "normal"
    ):
        """Send message to another agent"""
        msg = AgentMessage(
            sender=self.agent_id,
            receiver=to_agent,
            content=message,
            priority=priority
        )
        state.agent_messages.append(msg)
    
    def get_messages(self, state: AgentState) -> list[AgentMessage]:
        """Get messages for this agent"""
        return [msg for msg in state.agent_messages if msg.receiver == self.agent_id]
    
    def _parse_tool_calls_from_text(self, reasoning: str) -> list[dict]:
        """
        Parse tool calls from agent's reasoning text
        
        Agents specify tools like:
        - "I will call extract_from_pdf"
        - "TOOL: search_registry"
        - "I'll use check_sanctions"
        """
        tool_calls = []
        reasoning_lower = reasoning.lower()
        
        # Map of tool keywords to actual function names
        tool_map = {
            'extract_from_pdf': 'extract_from_pdf',
            'search_registry': 'search_registry',
            'check_sanctions': 'check_sanctions',
            'compute_risk': 'compute_risk',
            'get_additional_info': 'get_additional_info',
            'request_human_review': 'request_human_review',
            'send_message': 'send_message',  # For agent collaboration
        }
        
        # Check for each tool mention
        for keyword, tool_name in tool_map.items():
            if keyword in reasoning_lower and tool_name not in [tc['function'] for tc in tool_calls]:
                tool_calls.append({
                    'id': f"call_{len(tool_calls)}",
                    'function': tool_name,
                    'arguments': {}  # Default empty, can be enhanced
                })
        
        return tool_calls
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []

