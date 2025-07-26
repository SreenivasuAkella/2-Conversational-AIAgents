import yaml
from pydantic import BaseModel
from typing import List

class ConversationConfig(BaseModel):
    turns: int
    topic: str
    tone: str
    voices: List[str]  # e.g., ["male", "female"]
    tts_provider: str

    class Config:
        extra = "ignore"  # Ignore unused YAML fields

def load_config(path: str) -> ConversationConfig:
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    return ConversationConfig(**data)