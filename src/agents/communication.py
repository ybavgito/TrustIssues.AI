"""Agent communication and message passing system"""
from typing import Optional
from src.models import AgentState, AgentMessage


class AgentCommunication:
    """
    Handles message passing and communication between agents.
    
    Enables agents to:
    - Send messages to other agents
    - Retrieve messages sent to them
    - Coordinate actions
    - Share findings
    """
    
    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        content: str,
        state: AgentState,
        priority: str = "normal"
    ) -> None:
        """
        Send a message from one agent to another
        
        Args:
            from_agent: ID of sending agent
            to_agent: ID of receiving agent
            content: Message content
            state: Current agent state
            priority: Message priority ('normal' or 'high')
        """
        message = AgentMessage(
            sender=from_agent,
            receiver=to_agent,
            content=content,
            priority=priority
        )
        state.agent_messages.append(message)
    
    def get_messages(
        self,
        agent_id: str,
        state: AgentState,
        unread_only: bool = False,
        from_agent: Optional[str] = None
    ) -> list[AgentMessage]:
        """
        Get messages for a specific agent
        
        Args:
            agent_id: ID of agent to get messages for
            state: Current agent state
            unread_only: If True, only return unread messages
            from_agent: If provided, only return messages from this agent
            
        Returns:
            List of messages for the agent
        """
        messages = [msg for msg in state.agent_messages if msg.receiver == agent_id]
        
        if from_agent:
            messages = [msg for msg in messages if msg.sender == from_agent]
        
        return messages
    
    def get_latest_message(
        self,
        agent_id: str,
        state: AgentState,
        from_agent: Optional[str] = None
    ) -> Optional[AgentMessage]:
        """Get the most recent message for an agent"""
        messages = self.get_messages(agent_id, state, from_agent=from_agent)
        return messages[-1] if messages else None
    
    def get_conversation(
        self,
        agent1: str,
        agent2: str,
        state: AgentState
    ) -> list[AgentMessage]:
        """Get all messages between two agents"""
        return [
            msg for msg in state.agent_messages
            if (msg.sender == agent1 and msg.receiver == agent2) or
               (msg.sender == agent2 and msg.receiver == agent1)
        ]
    
    def broadcast(
        self,
        from_agent: str,
        content: str,
        state: AgentState,
        recipients: list[str] = None
    ) -> None:
        """
        Broadcast a message to multiple agents
        
        Args:
            from_agent: ID of sending agent
            content: Message content
            state: Current agent state
            recipients: List of recipient agent IDs. If None, sends to all agents except sender
        """
        if recipients is None:
            # Send to all agents except sender
            all_agents = ["coordinator", "extractor", "verifier", "risk_analyst"]
            recipients = [a for a in all_agents if a != from_agent]
        
        for recipient in recipients:
            self.send_message(from_agent, recipient, content, state)

