import os
import tomllib
from pathlib import Path
from typing import Any, Dict, Optional

import tomli_w
import keyring

CONFIG_DIR = Path.home() / ".shelby"
CONFIG_FILE = CONFIG_DIR / "config.toml"
HISTORY_FILE = CONFIG_DIR / "history.json"

DEFAULT_CONFIG = {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "safe_mode": False,
}

def ensure_config_dir() -> None:
    """Ensure the config directory exists with restricted permissions."""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        # Set permissions to 700 (rwx------)
        os.chmod(CONFIG_DIR, 0o700)

def load_config() -> Dict[str, Any]:
    """Load config from disk or return default."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, "rb") as f:
            config = {**DEFAULT_CONFIG, **tomllib.load(f)}
            
            # Load API key from keyring if it exists
            provider = config.get("provider")
            if provider:
                api_key = keyring.get_password("shelby", provider)
                if api_key:
                    config["api_key"] = api_key
            
            return config
    except Exception:
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]) -> None:
    """Save config to disk and sensitive keys to keyring."""
    ensure_config_dir()
    
    # Extract API key to save in keyring
    api_key = config.pop("api_key", None)
    provider = config.get("provider")
    
    if api_key and provider:
        keyring.set_password("shelby", provider, api_key)
    
    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(config, f)
    
    # Set permissions to 600 (rw-------)
    os.chmod(CONFIG_FILE, 0o600)

def get_config_value(key: str, default: Any = None) -> Any:
    """Get a specific config value."""
    config = load_config()
    return config.get(key, default)
