"""MockFactory CLI - Command-line interface."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from . import __version__
from .client import MockFactoryClient
from .config import Config

console = Console()


def get_client() -> MockFactoryClient:
    """Get configured API client."""
    config = Config.load()
    return MockFactoryClient(config)


def error(message: str) -> None:
    """Display error message and exit."""
    console.print(f"[bold red]Error:[/bold red] {message}")
    sys.exit(1)


def success(message: str) -> None:
    """Display success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def info(message: str) -> None:
    """Display info message."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


@click.group()
@click.version_option(version=__version__, prog_name="mockfactory")
@click.pass_context
def cli(ctx):
    """MockFactory CLI - Secure code execution sandbox.

    Execute code in isolated containers with comprehensive security controls.
    """
    ctx.ensure_object(dict)


@cli.command()
@click.option("--email", prompt=True, help="Your email address")
@click.option("--password", prompt=True, hide_input=True, help="Your password")
def login(email: str, password: str):
    """Sign in to your MockFactory account."""
    try:
        config = Config.load()
        client = MockFactoryClient(config)

        with console.status("[bold blue]Signing in..."):
            token = client.signin(email, password)

        config.save_token(token)
        success("Successfully logged in!")

        # Show user info
        client = get_client()
        profile = client.get_profile()
        info(f"Welcome back, {profile.get('email', 'user')}!")

    except Exception as e:
        error(str(e))


@cli.command()
@click.option("--email", prompt=True, help="Your email address")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Your password")
def signup(email: str, password: str):
    """Create a new MockFactory account."""
    try:
        config = Config.load()
        client = MockFactoryClient(config)

        with console.status("[bold blue]Creating account..."):
            token = client.signup(email, password)

        config.save_token(token)
        success("Account created successfully!")
        info("You now have 10 free code executions per day.")

    except Exception as e:
        error(str(e))


@cli.command()
def logout():
    """Sign out of your MockFactory account."""
    try:
        config = Config.load()
        config.delete_token()
        success("Successfully logged out!")
    except Exception as e:
        error(str(e))


@cli.command()
def status():
    """Show authentication status and usage information."""
    try:
        client = get_client()
        config = Config.load()

        # Create status table
        table = Table(title="MockFactory Status", show_header=False, border_style="blue")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        # API URL
        table.add_row("API URL", config.api_url)

        # Authentication status
        token = config.get_token()
        if token:
            try:
                profile = client.get_profile()
                table.add_row("Status", "[green]Authenticated[/green]")
                table.add_row("Email", profile.get("email", "N/A"))
                table.add_row("Plan", profile.get("subscription_tier", "free").title())
            except Exception:
                table.add_row("Status", "[yellow]Token expired[/yellow]")
        else:
            table.add_row("Status", "[red]Not authenticated[/red]")

        # Usage info
        try:
            usage = client.get_usage()
            table.add_row("Usage", f"{usage.runs_used}/{usage.runs_limit} runs")
            table.add_row("Tier", usage.tier.title())
        except Exception:
            pass

        console.print(table)

    except Exception as e:
        error(str(e))


@cli.command()
@click.argument("language")
@click.option("--code", "-c", help="Code to execute (inline)")
@click.option("--file", "-f", type=click.Path(exists=True), help="File containing code to execute")
@click.option("--timeout", "-t", type=int, help="Execution timeout in seconds")
@click.option("--raw", is_flag=True, help="Output raw result without formatting")
def run(language: str, code: Optional[str], file: Optional[str], timeout: Optional[int], raw: bool):
    """Execute code in the sandbox.

    LANGUAGE: Programming language (python, javascript, php, perl, go, shell, html)

    Examples:

      mockfactory run python -c "print('Hello World')"

      mockfactory run javascript -f script.js

      mockfactory run python --timeout 60 -c "import time; time.sleep(2); print('done')"
    """
    try:
        # Get code from file or inline
        if code and file:
            error("Cannot specify both --code and --file")
        elif file:
            code = Path(file).read_text()
        elif not code:
            error("Must specify either --code or --file")

        client = get_client()

        with console.status(f"[bold blue]Executing {language} code..."):
            result = client.execute_code(code=code, language=language, timeout=timeout)

        if raw:
            # Raw output mode
            print(result.output, end="")
            if result.error:
                print(result.error, file=sys.stderr, end="")
        else:
            # Formatted output mode
            if result.success:
                console.print(Panel(
                    result.output,
                    title=f"[green]Output ({language})[/green]",
                    border_style="green",
                ))
                if result.execution_time:
                    info(f"Completed in {result.execution_time:.2f}s")
            else:
                console.print(Panel(
                    result.error or "Unknown error",
                    title=f"[red]Error ({language})[/red]",
                    border_style="red",
                ))
                sys.exit(1)

    except Exception as e:
        error(str(e))


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--timeout", "-t", type=int, help="Execution timeout in seconds")
@click.option("--raw", is_flag=True, help="Output raw result without formatting")
def execute(file: str, timeout: Optional[int], raw: bool):
    """Execute a code file (auto-detect language from extension).

    FILE: Path to the code file

    Supported extensions: .py, .js, .php, .pl, .go, .sh, .html

    Examples:

      mockfactory execute script.py

      mockfactory execute app.js --timeout 60
    """
    try:
        file_path = Path(file)

        # Auto-detect language from extension
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".php": "php",
            ".pl": "perl",
            ".go": "go",
            ".sh": "shell",
            ".html": "html",
        }

        language = extension_map.get(file_path.suffix.lower())
        if not language:
            error(f"Unsupported file extension: {file_path.suffix}")

        code = file_path.read_text()
        client = get_client()

        with console.status(f"[bold blue]Executing {file_path.name}..."):
            result = client.execute_code(code=code, language=language, timeout=timeout)

        if raw:
            # Raw output mode
            print(result.output, end="")
            if result.error:
                print(result.error, file=sys.stderr, end="")
        else:
            # Formatted output mode
            if result.success:
                console.print(Panel(
                    result.output,
                    title=f"[green]Output ({file_path.name})[/green]",
                    border_style="green",
                ))
                if result.execution_time:
                    info(f"Completed in {result.execution_time:.2f}s")
            else:
                console.print(Panel(
                    result.error or "Unknown error",
                    title=f"[red]Error ({file_path.name})[/red]",
                    border_style="red",
                ))
                sys.exit(1)

    except Exception as e:
        error(str(e))


@cli.command()
def usage():
    """Show current usage statistics."""
    try:
        client = get_client()
        usage_info = client.get_usage()

        # Create usage table
        table = Table(title="Usage Statistics", border_style="blue")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Tier", usage_info.tier.title())
        table.add_row("Runs Used", str(usage_info.runs_used))
        table.add_row("Runs Limit", str(usage_info.runs_limit))

        remaining = usage_info.runs_limit - usage_info.runs_used
        if remaining > 0:
            table.add_row("Remaining", f"[green]{remaining}[/green]")
        else:
            table.add_row("Remaining", "[red]0[/red]")

        console.print(table)

        # Show upgrade message if needed
        if usage_info.tier == "anonymous" or usage_info.tier == "free":
            info("Upgrade to Pro for unlimited executions: mockfactory.io/pricing")

    except Exception as e:
        error(str(e))


@cli.group()
def config():
    """Manage CLI configuration."""
    pass


@config.command(name="show")
def config_show():
    """Show current configuration."""
    try:
        cfg = Config.load()
        table = Table(title="Configuration", show_header=False, border_style="blue")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("API URL", cfg.api_url)
        table.add_row("Timeout", f"{cfg.timeout}s")
        if cfg.session_id:
            table.add_row("Session ID", cfg.session_id)

        console.print(table)
    except Exception as e:
        error(str(e))


@config.command(name="set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set a configuration value.

    Available keys: api_url, timeout, session_id
    """
    try:
        cfg = Config.load()

        if key == "api_url":
            cfg.api_url = value
        elif key == "timeout":
            cfg.timeout = int(value)
        elif key == "session_id":
            cfg.session_id = value
        else:
            error(f"Unknown configuration key: {key}")

        cfg.save()
        success(f"Set {key} = {value}")
    except Exception as e:
        error(str(e))


@config.command(name="reset")
def config_reset():
    """Reset configuration to defaults."""
    try:
        cfg = Config()
        cfg.save()
        success("Configuration reset to defaults")
    except Exception as e:
        error(str(e))


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
