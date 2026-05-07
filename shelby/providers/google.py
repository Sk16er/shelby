import httpx
from typing import Any, Dict, List, Optional
from .base import LLMProvider

class GoogleProvider(LLMProvider):
    """Google Gemini provider implementation."""
    
    async def generate_command(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        contents = []
        if history:
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        
        data = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.0,
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data, timeout=30.0)
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]

    async def explain_command(self, command: str) -> str:
        prompt = f"Explain this shell command in detail, breaking down each flag: {command}"
        return await self.generate_command(prompt)
