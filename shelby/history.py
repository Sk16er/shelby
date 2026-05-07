import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import HISTORY_FILE

def save_to_history(query: str, command: str, exit_code: int, stdout: str = "", stderr: str = "") -> None:
    """Save a command execution to history."""
    entry = {
        "timestamp": time.time(),
        "query": query,
        "command": command,
        "exit_code": exit_code,
        "stdout": stdout[:1000],  # Limit size
        "stderr": stderr[:1000]
    }
    
    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except Exception:
            history = []
            
    history.append(entry)
    
    # Keep last 1000 entries
    history = history[-1000:]
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def get_last_failed_command() -> Optional[Dict[str, Any]]:
    """Get the last command that had a non-zero exit code."""
    if not HISTORY_FILE.exists():
        return None
        
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
            for entry in reversed(history):
                if entry.get("exit_code", 0) != 0:
                    return entry
    except Exception:
        pass
    return None

async def semantic_search_history(query: str, provider: Any) -> List[Dict[str, Any]]:
    """Use the LLM to find relevant past commands from history."""
    if not HISTORY_FILE.exists():
        return []
        
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    except Exception:
        return []
        
    if not history:
        return []
        
    # Prepare history for LLM
    history_summary = "\n".join([
        f"- Query: {h['query']}\n  Command: {h['command']}"
        for h in history[-50:]  # Last 50 for context
    ])
    
    prompt = (
        f"Search through the following command history and find the most relevant commands for the user's search query: \"{query}\"\n\n"
        f"History:\n{history_summary}\n\n"
        f"Return the relevant commands as a simple list. If nothing is relevant, say 'No relevant commands found'."
    )
    
    response = await provider.generate_command(prompt)
    return response
