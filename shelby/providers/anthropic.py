import httpx
from typing import Any, Dict, List, Optional
from .base import LLMProvider

class AnthropicProvider(LLMProvider):
    """Anthropic provider implementation."""
    
    async def generate_command(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        messages = history or []
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.0
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data, timeout=30.0)
            response.raise_for_status()
            return response.json()["content"][0]["text"]

    async def explain_command(self, command: str) -> str:
        prompt = f"Explain this shell command in detail, breaking down each flag: {command}"
        return await self.generate_command(prompt)
