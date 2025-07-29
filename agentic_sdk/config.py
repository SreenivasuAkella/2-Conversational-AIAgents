import yaml
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class ConversationMode(str, Enum):
    SCRIPTED = "scripted"
    UNSCRIPTED = "unscripted"

class ConversationConfig(BaseModel):
    turns: int
    topic: str
    tone: str
    voices: List[str]  # e.g., ["male", "female"]
    tts_provider: str
    mode: ConversationMode = ConversationMode.UNSCRIPTED  # Default to unscripted
    
    # For scripted conversations
    scripted_messages: Optional[List[str]] = None
    
    # For unscripted conversations (AI-generated)
    agent_a_persona: Optional[str] = None
    agent_b_persona: Optional[str] = None
    conversation_context: Optional[str] = None
    
    class Config:
        extra = "ignore"  # Ignore unused YAML fields

def load_config(path: str) -> ConversationConfig:
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    return ConversationConfig(**data)