from pydantic import BaseModel
from typing import List, Optional

class ConversationState(BaseModel):
    messages: List[str] = []
    turn: int = 0
    max_turns: int = 10
    speaker: str = "agent_a"  # agent_a or agent_b
    config: Optional[dict] = None