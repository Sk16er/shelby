from enum import Enum
from typing import List, Tuple

class RiskLevel(Enum):
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    DANGER = "DANGER"

DANGER_COMMANDS = [
    "rm -rf", "rm -r", "dd", "mkfs", "truncate", "kill -9", 
    "DROP TABLE", "DELETE FROM", "shred", "format", "wipe"
]

CAUTION_COMMANDS = [
    "rm", "mv", "cp", "chmod", "chown", "pip install", "pip uninstall",
    "git push", "git reset", "git clean", "systemctl", "sudo", "apt install",
    "apt remove", "yum install", "dnf install", "pacman -S", "npm install",
    "npm uninstall", "yarn add", "yarn remove"
]

SAFE_COMMANDS = [
    "ls", "find", "ps", "df", "du", "git log", "git status", "git diff",
    "curl", "wget", "cat", "echo", "pwd", "whoami", "grep", "sed", "awk",
    "top", "htop", "history", "man", "type", "which"
]

def classify_command(command: str) -> RiskLevel:
    """Classify a command based on its risk level."""
    cmd_lower = command.lower().strip()
    
    for danger in DANGER_COMMANDS:
        if cmd_lower.startswith(danger.lower()) or f" {danger.lower()}" in cmd_lower:
            return RiskLevel.DANGER
            
    for caution in CAUTION_COMMANDS:
        if cmd_lower.startswith(caution.lower()) or f" {caution.lower()}" in cmd_lower:
            return RiskLevel.CAUTION
            
    return RiskLevel.SAFE

def get_risk_info(command: str) -> Tuple[RiskLevel, str]:
    """Get risk level and a brief description."""
    level = classify_command(command)
    if level == RiskLevel.DANGER:
        return level, "⚠ DANGER — irreversible or highly destructive operation"
    elif level == RiskLevel.CAUTION:
        return level, "⚠ CAUTION — modifies files or system state"
    return level, "✓ SAFE — read-only or low-impact operation"
