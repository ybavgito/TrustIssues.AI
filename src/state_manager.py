"""State management for agent workflow"""
import json
import os
from pathlib import Path
from datetime import datetime
from src.models import AgentState


class StateManager:
    """Manages agent state persistence"""
    
    def __init__(self, state_dir: str = "state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
    
    def save_state(self, state: AgentState) -> None:
        """Save current state to disk"""
        state.updated_at = datetime.now()
        state_file = self.state_dir / f"{state.session_id}.json"
        
        with open(state_file, 'w') as f:
            json.dump(state.model_dump(mode='json'), f, indent=2, default=str)
    
    def load_state(self, session_id: str) -> AgentState:
        """Load state from disk"""
        state_file = self.state_dir / f"{session_id}.json"
        
        if not state_file.exists():
            raise FileNotFoundError(f"No state found for session {session_id}")
        
        with open(state_file, 'r') as f:
            data = json.load(f)
        
        return AgentState(**data)
    
    def list_sessions(self) -> list[str]:
        """List all available sessions"""
        return [f.stem for f in self.state_dir.glob("*.json")]
    
    def delete_state(self, session_id: str) -> None:
        """Delete a session state"""
        state_file = self.state_dir / f"{session_id}.json"
        if state_file.exists():
            state_file.unlink()

