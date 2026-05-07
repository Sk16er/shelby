from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    async def generate_command(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """Generate a shell command and explanation from a prompt."""
        pass

    @abstractmethod
    async def explain_command(self, command: str) -> str:
        """Explain a shell command in plain English."""
        pass
