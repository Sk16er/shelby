import asyncio
import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from .config import load_config, save_config, get_config_value
from .core import generate_shell_command, run_command, get_provider
from .safety import get_risk_info, RiskLevel
from .repl import start_repl
from .history import save_to_history, get_last_failed_command, semantic_search_history

console = Console()

@click.group(invoke_without_command=True)
@click.argument("query", required=False, nargs=-1)
@click.option("--setup", is_flag=True, help="Run setup wizard")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation (auto-run)")
@click.option("--dry-run", is_flag=True, help="Show command but don't run")
@click.option("--safe", is_flag=True, help="Block all DANGER commands")
@click.pass_context
def cli(ctx, query, setup, yes, dry_run, safe):
    """Shelby: AI-powered terminal assistant."""
    if setup:
        run_setup_wizard()
        return

    # Join multi-word queries
    query_str = " ".join(query) if query else ""

    if ctx.invoked_subcommand is None:
        if not sys.stdin.isatty():
            # Pipe mode
            pipe_input = sys.stdin.read().strip()
            full_query = f"{query_str} {pipe_input}".strip()
            if full_query:
                asyncio.run(handle_inline_query(full_query, True, dry_run, safe))
        elif query_str:
            asyncio.run(handle_inline_query(query_str, yes, dry_run, safe))
        else:
            # REPL mode
            asyncio.run(start_repl())

@cli.command()
@click.argument("command_str", required=False)
def explain(command_str):
    """Explain a shell command in plain English."""
    if not command_str and not sys.stdin.isatty():
        command_str = sys.stdin.read().strip()
    
    if not command_str:
        console.print("[bold red]Error: No command provided to explain.[/bold red]")
        return
        
    asyncio.run(handle_explain(command_str))

@cli.command()
def fix():
    """Suggest a fix for the last failed command."""
    last_failed = get_last_failed_command()
    if last_failed:
        error_context = (
            f"Last failed command: {last_failed['command']}\n"
            f"Exit code: {last_failed['exit_code']}\n"
            f"Error output: {last_failed['stderr']}"
        )
        console.print(Panel(error_context, title="Analyzing Last Failure"))
        asyncio.run(handle_inline_query(f"Fix this failed command: {error_context}", False, False, False))
    else:
        # Fallback: ask for input
        error_msg = console.input("[bold red]No tracked failure found. Enter the error message: [/bold red]")
        asyncio.run(handle_inline_query(f"Fix this error: {error_msg}", False, False, False))

@cli.command()
@click.argument("query", required=True)
def history(query):
    """Search through past commands using semantic search."""
    asyncio.run(handle_history_search(query))

async def handle_inline_query(query, yes, dry_run, safe):
    try:
        with console.status("[bold blue]Thinking..."):
            command, explanation = await generate_shell_command(query)
        
        if not command:
            console.print("[bold red]Failed to generate command.[/bold red]")
            return

        level, risk_desc = get_risk_info(command)
        
        # Session-level safe mode block
        if safe and level == RiskLevel.DANGER:
            console.print(Panel(f"[bold red]BLOCKED:[/bold red] {command}\n\nThis command is blocked due to --safe flag.", title="Safety Block"))
            return

        console.print(Panel(
            f"[bold green]{command}[/bold green]\n\n[dim]{explanation}[/dim]\n\n[bold]{risk_desc}[/bold]",
            title="Suggested Command",
            border_style="yellow" if level == RiskLevel.CAUTION else "red" if level == RiskLevel.DANGER else "green"
        ))

        if dry_run:
            console.print("[yellow]Dry run: Command not executed.[/yellow]")
            return

        run = False
        if yes:
            run = True
        elif level == RiskLevel.SAFE:
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
            save_to_history(query, command, result.returncode, result.stdout, result.stderr)
        else:
            console.print("[yellow]Aborted.[/yellow]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

async def handle_explain(command_str):
    try:
        provider = get_provider()
        with console.status("[bold blue]Analyzing command..."):
            explanation = await provider.explain_command(command_str)
        console.print(Panel(explanation, title=f"Explanation: {command_str}"))
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

async def handle_history_search(query):
    try:
        provider = get_provider()
        with console.status("[bold blue]Searching history..."):
            results = await semantic_search_history(query, provider)
        console.print(Panel(results, title=f"History Search: {query}"))
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

def run_setup_wizard():
    console.print(Panel("[bold cyan]Shelby Setup Wizard[/bold cyan]", title="Setup"))
    
    provider = Prompt.ask("Choose provider", choices=["openai", "anthropic", "google", "ollama"], default="openai")
    
    default_model = "gpt-4o-mini"
    if provider == "anthropic": default_model = "claude-3-5-sonnet-20240620"
    elif provider == "google": default_model = "gemini-1.5-flash"
    elif provider == "ollama": default_model = "llama3"
    
    model = Prompt.ask(f"Enter model name", default=default_model)
    api_key = ""
    if provider != "ollama":
        api_key = Prompt.ask("Enter API key", password=True)
    
    config = {
        "provider": provider,
        "model": model,
        "api_key": api_key,
        "safe_mode": False
    }
    
    save_config(config)
    console.print("[bold green]Configuration saved to ~/.shelby/config.toml[/bold green]")

if __name__ == "__main__":
    cli()
