import httpx
from typing import Any, Dict, List, Optional
from .base import LLMProvider

class OllamaProvider(LLMProvider):
    """Ollama provider implementation."""
    
    async def generate_command(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        url = "http://localhost:11434/api/chat"
        
        messages = history or []
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.0
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, timeout=60.0)
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", "Unknown Ollama error")
                    raise Exception(f"Ollama Error: {error_msg}")
                except Exception as e:
                    if "Ollama Error" in str(e): raise
                    response.raise_for_status()
            return response.json()["message"]["content"]

    async def explain_command(self, command: str) -> str:
        prompt = f"Explain this shell command in detail, breaking down each flag: {command}"
        return await self.generate_command(prompt)
