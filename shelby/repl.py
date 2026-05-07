import asyncio
from typing import List, Dict

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.panel import Panel

from .config import HISTORY_FILE
from .core import generate_shell_command, run_command
from .safety import get_risk_info, RiskLevel
from .history import save_to_history

console = Console()

async def start_repl():
    """Start the interactive Shelby REPL."""
    session = PromptSession(history=FileHistory(str(HISTORY_FILE.parent / "repl_history")))
    history: List[Dict[str, str]] = []
    
    console.print(Panel("[bold cyan]Shelby REPL[/bold cyan] - AI Shell Assistant\nType 'exit' or 'quit' to stop.", title="Welcome"))
    
    while True:
        try:
            user_input = await session.prompt_async("shelby > ")
            
            if user_input.lower() in ("exit", "quit"):
                break
            
            if not user_input.strip():
                continue
                
            with console.status("[bold blue]Generating command..."):
                command, explanation = await generate_shell_command(user_input, history)
            
            if not command:
                console.print("[bold red]Failed to generate command.[/bold red]")
                continue
                
            level, risk_desc = get_risk_info(command)
            
            # Show output
            console.print(Panel(
                f"[bold green]{command}[/bold green]\n\n[dim]{explanation}[/dim]\n\n[bold]{risk_desc}[/bold]",
                title="Suggested Command",
                border_style="yellow" if level == RiskLevel.CAUTION else "red" if level == RiskLevel.DANGER else "green"
            ))
            
            # Confirmation
            run = False
            if level == RiskLevel.SAFE:
                confirm = console.input("[bold]Press Enter to run, or 'n' to cancel: [/bold]")
                if confirm.lower() != 'n':
                    run = True
            elif level == RiskLevel.CAUTION:
                confirm = console.input("[bold yellow]Type 'y' to confirm: [/bold]")
                if confirm.lower() == 'y':
                    run = True
            elif level == RiskLevel.DANGER:
                base_cmd = command.split()[0]
                confirm = console.input(f"[bold red]Type '{base_cmd}' to confirm: [/bold]")
                if confirm == base_cmd:
                    run = True
            
            if run:
                result = run_command(command)
                if result.stdout:
                    console.print(result.stdout)
                if result.stderr:
                    console.print(f"[bold red]{result.stderr}[/bold red]")
                
                # Save to history
                save_to_history(user_input, command, result.returncode, result.stdout, result.stderr)
                
                # Add to multi-turn conversation context
                history.append({"role": "user", "content": user_input})
                # Cap context output to avoid token bloat
                history.append({"role": "assistant", "content": f"COMMAND: {command}\nOUTPUT: {result.stdout[:2000]}"})
                
                # Limit history size to last 5 turns
                if len(history) > 10:
                    history = history[-10:]
            else:
                console.print("[yellow]Aborted.[/yellow]")
                
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")

    console.print("[bold cyan]Goodbye![/bold cyan]")
