import os
import platform
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

from .config import get_config_value
from .providers.openai import OpenAIProvider
from .providers.anthropic import AnthropicProvider
from .providers.google import GoogleProvider
from .providers.ollama import OllamaProvider
from .safety import RiskLevel, classify_command

def get_system_context() -> str:
    """Gather system context for the LLM."""
    os_name = platform.system()
    os_version = platform.release()
    shell = os.environ.get("SHELL", "unknown")
    cwd = os.getcwd()
    
    return (
        f"Context:\n"
        f"- Operating System: {os_name} ({os_version})\n"
        f"- Current Shell: {shell}\n"
        f"- Working Directory: {cwd}\n"
    )

def get_provider():
    """Initialize the configured LLM provider."""
    provider_name = get_config_value("provider")
    model = get_config_value("model")
    api_key = get_config_value("api_key")
    
    if provider_name == "openai":
        return OpenAIProvider(api_key, model)
    elif provider_name == "anthropic":
        return AnthropicProvider(api_key, model)
    elif provider_name == "google":
        return GoogleProvider(api_key, model)
    elif provider_name == "ollama":
        return OllamaProvider(api_key, model)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")

async def generate_shell_command(query: str, history: Optional[List[Dict[str, str]]] = None) -> Tuple[str, str]:
    """
    Generate a shell command and explanation.
    Returns: (command, explanation)
    """
    provider = get_provider()
    context = get_system_context()
    
    prompt = (
        f"{context}\n"
        f"User request: {query}\n\n"
        f"Generate the single best shell command to fulfill this request. "
        f"Provide your response in the following format:\n"
        f"COMMAND: <the_command>\n"
        f"EXPLANATION: <plain_english_explanation_of_flags>\n\n"
        f"Only provide the command and explanation. No other text."
    )
    
    response = await provider.generate_command(prompt, history)
    
    command = ""
    explanation = ""
    
    for line in response.splitlines():
        if line.startswith("COMMAND:"):
            command = line.replace("COMMAND:", "").strip()
        elif line.startswith("EXPLANATION:"):
            explanation = line.replace("EXPLANATION:", "").strip()
            
    # Fallback if parsing fails
    if not command:
        command = response.strip()
        
    return command, explanation

def run_command(command: str) -> subprocess.CompletedProcess:
    """Run a command in the user's current shell."""
    is_windows = platform.system() == "Windows"
    
    if is_windows:
        # Use cmd or powershell on Windows
        return subprocess.run(command, shell=True, text=True, capture_output=True)
    else:
        shell = os.environ.get("SHELL", "/bin/sh")
        return subprocess.run(command, shell=True, executable=shell, text=True, capture_output=True)
