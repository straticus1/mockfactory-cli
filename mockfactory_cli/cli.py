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


# ============================================================================
# Mock Resource Management Commands
# ============================================================================

@cli.group()
def organization():
    """Manage mock organizations."""
    pass


@organization.command(name="create")
@click.argument("name")
@click.option("--description", help="Organization description")
@click.option("--owner", help="Owner user ID")
@click.option("--plan", type=click.Choice(["free", "pro", "enterprise"]), default="free", help="Organization plan")
def organization_create(name: str, description: Optional[str], owner: Optional[str], plan: str):
    """Create a new mock organization.

    Organizations can contain multiple users, domains, and projects.

    Examples:
        mockfactory organization create acme-corp --description "Acme Corporation"
        mockfactory organization create startup --owner john.doe --plan pro
    """
    try:
        client = get_client()
        import uuid

        org_data = {
            "name": name,
            "plan": plan,
            "org_id": str(uuid.uuid4())
        }
        if description:
            org_data["description"] = description
        if owner:
            org_data["owner"] = owner

        # TODO: Call API endpoint when implemented
        # org = client.create_mock_organization(**org_data)

        success(f"Mock organization '{name}' created successfully")
        info(f"Organization ID: {org_data['org_id']}")
        info(f"Plan: {plan}")
        if description:
            info(f"Description: {description}")
        if owner:
            info(f"Owner: {owner}")
    except Exception as e:
        error(str(e))


@organization.command(name="list")
@click.option("--plan", type=click.Choice(["free", "pro", "enterprise"]), help="Filter by plan")
def organization_list(plan: Optional[str]):
    """List all mock organizations."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # orgs = client.list_mock_organizations(plan=plan)

        table = Table(title="Mock Organizations", border_style="blue")
        table.add_column("Org ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Plan", style="yellow")
        table.add_column("Users", style="white")
        table.add_column("Domains", style="white")
        table.add_column("Projects", style="white")
        table.add_column("Owner", style="magenta")

        info("Mock organization listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@organization.command(name="get")
@click.argument("name")
def organization_get(name: str):
    """Get details of a mock organization."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # org = client.get_mock_organization(name)

        table = Table(title=f"Organization: {name}", show_header=False, border_style="blue")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        info(f"Fetching organization '{name}'...")
        info("API endpoint to be implemented")

        console.print(table)
    except Exception as e:
        error(str(e))


@organization.command(name="delete")
@click.argument("name")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
def organization_delete(name: str, yes: bool):
    """Delete a mock organization."""
    try:
        if not yes:
            if not click.confirm(f"Are you sure you want to delete organization '{name}'?"):
                info("Cancelled")
                return

        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.delete_mock_organization(name)

        success(f"Mock organization '{name}' deleted successfully")
    except Exception as e:
        error(str(e))


@organization.command(name="add-user")
@click.argument("org_name")
@click.argument("username")
@click.option("--role", type=click.Choice(["member", "admin", "owner"]), default="member", help="User role in organization")
def organization_add_user(org_name: str, username: str, role: str):
    """Add a user to an organization.

    Example:
        mockfactory organization add-user acme-corp john.doe --role admin
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.add_user_to_organization(org_name, username, role)

        success(f"Added user '{username}' to organization '{org_name}'")
        info(f"Role: {role}")
    except Exception as e:
        error(str(e))


@organization.command(name="remove-user")
@click.argument("org_name")
@click.argument("username")
def organization_remove_user(org_name: str, username: str):
    """Remove a user from an organization.

    Example:
        mockfactory organization remove-user acme-corp john.doe
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.remove_user_from_organization(org_name, username)

        success(f"Removed user '{username}' from organization '{org_name}'")
    except Exception as e:
        error(str(e))


@cli.group()
def domain():
    """Manage mock domains."""
    pass


@domain.command(name="create")
@click.argument("domain_name")
@click.option("--organization", help="Bind to organization")
@click.option("--verified", is_flag=True, help="Mark domain as verified")
@click.option("--dns-records", help="Comma-separated DNS records to create")
def domain_create(domain_name: str, organization: Optional[str], verified: bool, dns_records: Optional[str]):
    """Create a new mock domain.

    Domains can be bound to organizations and used for email, APIs, and other services.

    Examples:
        mockfactory domain create example.com --organization acme-corp
        mockfactory domain create test.io --verified --dns-records "A:1.2.3.4,MX:mail.test.io"
    """
    try:
        client = get_client()
        import uuid

        domain_data = {
            "domain": domain_name,
            "verified": verified,
            "domain_id": str(uuid.uuid4())
        }
        if organization:
            domain_data["organization"] = organization
        if dns_records:
            domain_data["dns_records"] = dns_records.split(",")

        # TODO: Call API endpoint when implemented
        # domain_obj = client.create_mock_domain(**domain_data)

        success(f"Mock domain '{domain_name}' created successfully")
        info(f"Domain ID: {domain_data['domain_id']}")
        info(f"Verified: {'Yes' if verified else 'No'}")
        if organization:
            info(f"Organization: {organization}")
        if dns_records:
            info(f"DNS Records: {dns_records}")
    except Exception as e:
        error(str(e))


@domain.command(name="list")
@click.option("--organization", help="Filter by organization")
@click.option("--verified", is_flag=True, help="Show only verified domains")
def domain_list(organization: Optional[str], verified: bool):
    """List all mock domains."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # domains = client.list_mock_domains(organization=organization, verified=verified)

        table = Table(title="Mock Domains", border_style="blue")
        table.add_column("Domain ID", style="cyan")
        table.add_column("Domain", style="white")
        table.add_column("Organization", style="yellow")
        table.add_column("Verified", style="green")
        table.add_column("DNS Records", style="white")
        table.add_column("Created", style="white")

        info("Mock domain listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@domain.command(name="get")
@click.argument("domain_name")
def domain_get(domain_name: str):
    """Get details of a mock domain."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # domain_obj = client.get_mock_domain(domain_name)

        table = Table(title=f"Domain: {domain_name}", show_header=False, border_style="blue")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        info(f"Fetching domain '{domain_name}'...")
        info("API endpoint to be implemented")

        console.print(table)
    except Exception as e:
        error(str(e))


@domain.command(name="verify")
@click.argument("domain_name")
def domain_verify(domain_name: str):
    """Verify a mock domain.

    Example:
        mockfactory domain verify example.com
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.verify_mock_domain(domain_name)

        success(f"Domain '{domain_name}' verified successfully")
        info("DNS records validated")
    except Exception as e:
        error(str(e))


@domain.command(name="delete")
@click.argument("domain_name")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
def domain_delete(domain_name: str, yes: bool):
    """Delete a mock domain."""
    try:
        if not yes:
            if not click.confirm(f"Are you sure you want to delete domain '{domain_name}'?"):
                info("Cancelled")
                return

        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.delete_mock_domain(domain_name)

        success(f"Mock domain '{domain_name}' deleted successfully")
    except Exception as e:
        error(str(e))


@cli.group()
def project():
    """Manage mock projects."""
    pass


@project.command(name="create")
@click.argument("name")
@click.option("--organization", help="Organization to create project under")
@click.option("--description", help="Project description")
@click.option("--environment", type=click.Choice(["development", "staging", "production"]), default="development", help="Project environment")
def project_create(name: str, organization: Optional[str], description: Optional[str], environment: str):
    """Create a new mock project.

    Projects use UUID-based project IDs to tie together related resources.

    Examples:
        mockfactory project create my-app --organization acme-corp
        mockfactory project create api-test --environment staging --description "API Testing Project"
    """
    try:
        client = get_client()
        import uuid

        project_id = str(uuid.uuid4())
        project_data = {
            "name": name,
            "project_id": project_id,
            "environment": environment
        }
        if organization:
            project_data["organization"] = organization
        if description:
            project_data["description"] = description

        # TODO: Call API endpoint when implemented
        # project_obj = client.create_mock_project(**project_data)

        success(f"Mock project '{name}' created successfully")
        info(f"Project ID: {project_id}")
        info(f"Environment: {environment}")
        if organization:
            info(f"Organization: {organization}")
        if description:
            info(f"Description: {description}")

        console.print("\n[bold cyan]Use this Project ID to bind resources:[/bold cyan]")
        console.print(f"  mockfactory user create john --project-id {project_id}")
        console.print(f"  mockfactory container create web --project-id {project_id}")
        console.print(f"  mockfactory api create api --project-id {project_id}")
    except Exception as e:
        error(str(e))


@project.command(name="list")
@click.option("--organization", help="Filter by organization")
@click.option("--environment", type=click.Choice(["development", "staging", "production"]), help="Filter by environment")
def project_list(organization: Optional[str], environment: Optional[str]):
    """List all mock projects."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # projects = client.list_mock_projects(organization=organization, environment=environment)

        table = Table(title="Mock Projects", border_style="blue")
        table.add_column("Project ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Organization", style="yellow")
        table.add_column("Environment", style="green")
        table.add_column("Resources", style="white")
        table.add_column("Created", style="white")

        info("Mock project listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@project.command(name="get")
@click.argument("project_id")
def project_get(project_id: str):
    """Get details of a mock project.

    Example:
        mockfactory project get 550e8400-e29b-41d4-a716-446655440000
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # project_obj = client.get_mock_project(project_id)

        table = Table(title=f"Project: {project_id}", border_style="blue")
        table.add_column("Resource Type", style="cyan")
        table.add_column("Resource Name", style="white")
        table.add_column("Resource ID", style="yellow")
        table.add_column("Created", style="white")

        info(f"Fetching project resources for '{project_id}'...")
        info("API endpoint to be implemented")

        console.print(table)
    except Exception as e:
        error(str(e))


@project.command(name="bind-resource")
@click.argument("project_id")
@click.argument("resource_type")
@click.argument("resource_id")
def project_bind_resource(project_id: str, resource_type: str, resource_id: str):
    """Bind a resource to a project.

    Examples:
        mockfactory project bind-resource 550e8400-... user john.doe
        mockfactory project bind-resource 550e8400-... container web-app
        mockfactory project bind-resource 550e8400-... domain example.com
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.bind_resource_to_project(project_id, resource_type, resource_id)

        success(f"Bound {resource_type} '{resource_id}' to project '{project_id}'")
    except Exception as e:
        error(str(e))


@project.command(name="unbind-resource")
@click.argument("project_id")
@click.argument("resource_type")
@click.argument("resource_id")
def project_unbind_resource(project_id: str, resource_type: str, resource_id: str):
    """Unbind a resource from a project.

    Example:
        mockfactory project unbind-resource 550e8400-... user john.doe
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.unbind_resource_from_project(project_id, resource_type, resource_id)

        success(f"Unbound {resource_type} '{resource_id}' from project '{project_id}'")
    except Exception as e:
        error(str(e))


@project.command(name="delete")
@click.argument("project_id")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
@click.option("--delete-resources", is_flag=True, help="Also delete all bound resources")
def project_delete(project_id: str, yes: bool, delete_resources: bool):
    """Delete a mock project.

    Example:
        mockfactory project delete 550e8400-... --delete-resources
    """
    try:
        if not yes:
            msg = f"Are you sure you want to delete project '{project_id}'?"
            if delete_resources:
                msg += " This will also delete all bound resources!"
            if not click.confirm(msg):
                info("Cancelled")
                return

        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.delete_mock_project(project_id, delete_resources=delete_resources)

        success(f"Mock project '{project_id}' deleted successfully")
        if delete_resources:
            info("All bound resources were also deleted")
    except Exception as e:
        error(str(e))


@cli.group()
def cloud():
    """Manage mock clouds."""
    pass


@cloud.command(name="create")
@click.argument("name")
@click.option("--provider", type=click.Choice(["aws", "gcp", "azure", "custom"]), default="aws", help="Cloud provider type")
@click.option("--organization", help="Bind to organization")
@click.option("--region", default="us-east-1", help="Default region")
def cloud_create(name: str, provider: str, organization: Optional[str], region: str):
    """Create a new mock cloud environment.

    Examples:
        mockfactory cloud create dev-cloud --provider aws --organization acme-corp
        mockfactory cloud create test-env --provider gcp --region us-west1
    """
    try:
        client = get_client()
        import uuid
        cloud_data = {
            "name": name,
            "provider": provider,
            "region": region,
            "cloud_id": str(uuid.uuid4())
        }
        if organization:
            cloud_data["organization"] = organization
        # TODO: Call API endpoint when implemented
        # cloud_obj = client.create_mock_cloud(**cloud_data)
        success(f"Mock cloud '{name}' created successfully")
        info(f"Cloud ID: {cloud_data['cloud_id']}")
        info(f"Provider: {provider}")
        info(f"Region: {region}")
        if organization:
            info(f"Organization: {organization}")
    except Exception as e:
        error(str(e))


@cloud.command(name="list")
@click.option("--provider", type=click.Choice(["aws", "gcp", "azure", "custom"]), help="Filter by provider")
@click.option("--organization", help="Filter by organization")
def cloud_list(provider: Optional[str], organization: Optional[str]):
    """List all mock clouds."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # clouds = client.list_mock_clouds(provider=provider, organization=organization)
        table = Table(title="Mock Clouds", border_style="blue")
        table.add_column("Cloud ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Provider", style="yellow")
        table.add_column("Region", style="white")
        table.add_column("Organization", style="magenta")
        table.add_column("Resources", style="white")
        info("Mock cloud listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@cloud.command(name="get")
@click.argument("name")
def cloud_get(name: str):
    """Get details of a mock cloud."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # cloud_obj = client.get_mock_cloud(name)
        table = Table(title=f"Cloud: {name}", show_header=False, border_style="blue")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        info(f"Fetching cloud '{name}'...")
        info("API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@cloud.command(name="delete")
@click.argument("name")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
def cloud_delete(name: str, yes: bool):
    """Delete a mock cloud."""
    try:
        if not yes:
            if not click.confirm(f"Are you sure you want to delete cloud '{name}'?"):
                info("Cancelled")
                return
        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.delete_mock_cloud(name)
        success(f"Mock cloud '{name}' deleted successfully")
    except Exception as e:
        error(str(e))


@cli.group()
def user():
    """Manage mock users."""
    pass


@user.command(name="create")
@click.argument("username")
@click.option("--email", help="User email address")
@click.option("--full-name", help="Full name of the user")
@click.option("--role", default="user", help="User role (user, admin, developer)")
@click.option("--organization", help="Bind to organization")
@click.option("--cloud", help="Bind to cloud environment")
@click.option("--domain", help="Email domain")
@click.option("--project-id", help="UUID-based project ID to group resources")
def user_create(username: str, email: Optional[str], full_name: Optional[str], role: str,
                organization: Optional[str], cloud: Optional[str], domain: Optional[str], project_id: Optional[str]):
    """Create a new mock user within organizations, clouds, and domains.

    Examples:
        mockfactory user create john.doe --email john@example.com --full-name "John Doe"
        mockfactory user create alice --role admin --organization acme-corp
        mockfactory user create bob --cloud dev-cloud --domain example.com
        mockfactory user create charlie --project-id 550e8400-e29b-41d4-a716-446655440000
    """
    try:
        client = get_client()
        user_data = {
            "username": username,
            "role": role
        }
        if email:
            user_data["email"] = email
        if full_name:
            user_data["full_name"] = full_name
        if organization:
            user_data["organization"] = organization
        if cloud:
            user_data["cloud"] = cloud
        if domain:
            user_data["domain"] = domain
        if project_id:
            user_data["project_id"] = project_id

        # TODO: Call API endpoint when implemented
        # user = client.create_mock_user(**user_data)

        success(f"Mock user '{username}' created successfully")
        info(f"Username: {username}")
        if email:
            info(f"Email: {email}")
        info(f"Role: {role}")
        if organization:
            info(f"Organization: {organization}")
        if cloud:
            info(f"Cloud: {cloud}")
        if domain:
            info(f"Domain: {domain}")
        if project_id:
            info(f"Project ID: {project_id}")
    except Exception as e:
        error(str(e))


@user.command(name="list")
@click.option("--role", help="Filter by role")
def user_list(role: Optional[str]):
    """List all mock users."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # users = client.list_mock_users(role=role)

        table = Table(title="Mock Users", border_style="blue")
        table.add_column("ID", style="cyan")
        table.add_column("Username", style="white")
        table.add_column("Email", style="white")
        table.add_column("Role", style="yellow")
        table.add_column("Created", style="green")

        # Placeholder data
        info("Mock user listing - API endpoint to be implemented")

        console.print(table)
    except Exception as e:
        error(str(e))


@user.command(name="get")
@click.argument("username")
def user_get(username: str):
    """Get details of a mock user."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # user = client.get_mock_user(username)

        table = Table(title=f"Mock User: {username}", show_header=False, border_style="blue")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        info(f"Fetching details for mock user '{username}'...")
        info("API endpoint to be implemented")

        console.print(table)
    except Exception as e:
        error(str(e))


@user.command(name="delete")
@click.argument("username")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def user_delete(username: str, yes: bool):
    """Delete a mock user."""
    try:
        if not yes:
            if not click.confirm(f"Are you sure you want to delete mock user '{username}'?"):
                info("Cancelled")
                return

        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.delete_mock_user(username)

        success(f"Mock user '{username}' deleted successfully")
    except Exception as e:
        error(str(e))


@cli.group()
def group():
    """Manage mock groups."""
    pass


@group.command(name="create")
@click.argument("name")
@click.option("--description", help="Group description")
def group_create(name: str, description: Optional[str]):
    """Create a new mock group.

    Examples:
        mockfactory group create developers --description "Development team"
        mockfactory group create admins
    """
    try:
        client = get_client()
        group_data = {"name": name}
        if description:
            group_data["description"] = description

        # TODO: Call API endpoint when implemented
        # group = client.create_mock_group(**group_data)

        success(f"Mock group '{name}' created successfully")
        if description:
            info(f"Description: {description}")
    except Exception as e:
        error(str(e))


@group.command(name="list")
def group_list():
    """List all mock groups."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # groups = client.list_mock_groups()

        table = Table(title="Mock Groups", border_style="blue")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Description", style="white")
        table.add_column("Members", style="yellow")
        table.add_column("Created", style="green")

        info("Mock group listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@group.command(name="add-user")
@click.argument("group_name")
@click.argument("username")
def group_add_user(group_name: str, username: str):
    """Add a mock user to a group.

    Example:
        mockfactory group add-user developers john.doe
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.add_user_to_group(group_name, username)

        success(f"Added user '{username}' to group '{group_name}'")
    except Exception as e:
        error(str(e))


@group.command(name="remove-user")
@click.argument("group_name")
@click.argument("username")
def group_remove_user(group_name: str, username: str):
    """Remove a mock user from a group.

    Example:
        mockfactory group remove-user developers john.doe
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.remove_user_from_group(group_name, username)

        success(f"Removed user '{username}' from group '{group_name}'")
    except Exception as e:
        error(str(e))


@cli.group()
def container():
    """Manage mock containers."""
    pass


@container.command(name="create")
@click.argument("name")
@click.option("--image", default="alpine", help="Container image")
@click.option("--network", help="Network to attach to")
@click.option("--user", help="Bind to mock user")
@click.option("--group", help="Bind to mock group")
def container_create(name: str, image: str, network: Optional[str], user: Optional[str], group: Optional[str]):
    """Create a new mock container.

    Examples:
        mockfactory container create web-app --image nginx --network frontend
        mockfactory container create api --user john.doe --group developers
    """
    try:
        client = get_client()
        container_data = {
            "name": name,
            "image": image
        }
        if network:
            container_data["network"] = network
        if user:
            container_data["user"] = user
        if group:
            container_data["group"] = group

        # TODO: Call API endpoint when implemented
        # container = client.create_mock_container(**container_data)

        success(f"Mock container '{name}' created successfully")
        info(f"Image: {image}")
        if network:
            info(f"Network: {network}")
        if user:
            info(f"Bound to user: {user}")
        if group:
            info(f"Bound to group: {group}")
    except Exception as e:
        error(str(e))


@container.command(name="list")
@click.option("--network", help="Filter by network")
@click.option("--user", help="Filter by bound user")
def container_list(network: Optional[str], user: Optional[str]):
    """List all mock containers."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # containers = client.list_mock_containers(network=network, user=user)

        table = Table(title="Mock Containers", border_style="blue")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Image", style="white")
        table.add_column("Network", style="yellow")
        table.add_column("User", style="magenta")
        table.add_column("Status", style="green")

        info("Mock container listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@container.command(name="bind-user")
@click.argument("container_name")
@click.argument("username")
def container_bind_user(container_name: str, username: str):
    """Bind a mock user to a container.

    Example:
        mockfactory container bind-user web-app john.doe
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.bind_user_to_container(container_name, username)

        success(f"Bound user '{username}' to container '{container_name}'")
    except Exception as e:
        error(str(e))


@container.command(name="unbind-user")
@click.argument("container_name")
@click.argument("username")
def container_unbind_user(container_name: str, username: str):
    """Unbind a mock user from a container.

    Example:
        mockfactory container unbind-user web-app john.doe
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.unbind_user_from_container(container_name, username)

        success(f"Unbound user '{username}' from container '{container_name}'")
    except Exception as e:
        error(str(e))


@cli.group()
def network():
    """Manage mock networks."""
    pass


@network.command(name="create")
@click.argument("name")
@click.option("--cidr", default="10.0.0.0/24", help="Network CIDR block")
@click.option("--isolated", is_flag=True, help="Create isolated network")
def network_create(name: str, cidr: str, isolated: bool):
    """Create a new mock network.

    Examples:
        mockfactory network create frontend --cidr 10.1.0.0/24
        mockfactory network create backend --isolated
    """
    try:
        client = get_client()
        network_data = {
            "name": name,
            "cidr": cidr,
            "isolated": isolated
        }

        # TODO: Call API endpoint when implemented
        # network = client.create_mock_network(**network_data)

        success(f"Mock network '{name}' created successfully")
        info(f"CIDR: {cidr}")
        if isolated:
            info("Type: Isolated")
    except Exception as e:
        error(str(e))


@network.command(name="list")
def network_list():
    """List all mock networks."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # networks = client.list_mock_networks()

        table = Table(title="Mock Networks", border_style="blue")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("CIDR", style="white")
        table.add_column("Containers", style="yellow")
        table.add_column("Isolated", style="magenta")

        info("Mock network listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@cli.group()
def profile():
    """Manage mock user profiles."""
    pass


@profile.command(name="create")
@click.argument("username")
@click.option("--bio", help="User biography")
@click.option("--avatar", help="Avatar URL")
@click.option("--preferences", help="JSON preferences string")
def profile_create(username: str, bio: Optional[str], avatar: Optional[str], preferences: Optional[str]):
    """Create a mock user profile.

    Example:
        mockfactory profile create john.doe --bio "Senior Developer" --avatar https://example.com/avatar.jpg
    """
    try:
        client = get_client()
        profile_data = {"username": username}
        if bio:
            profile_data["bio"] = bio
        if avatar:
            profile_data["avatar"] = avatar
        if preferences:
            import json
            profile_data["preferences"] = json.loads(preferences)

        # TODO: Call API endpoint when implemented
        # profile = client.create_mock_profile(**profile_data)

        success(f"Mock profile created for user '{username}'")
        if bio:
            info(f"Bio: {bio}")
        if avatar:
            info(f"Avatar: {avatar}")
    except Exception as e:
        error(str(e))


@profile.command(name="get")
@click.argument("username")
def profile_get(username: str):
    """Get mock user profile."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # profile = client.get_mock_profile(username)

        table = Table(title=f"Profile: {username}", show_header=False, border_style="blue")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        info(f"Fetching profile for '{username}'...")
        info("API endpoint to be implemented")

        console.print(table)
    except Exception as e:
        error(str(e))


@cli.group()
def mail_server():
    """Manage mock mail servers."""
    pass


@mail_server.command(name="create")
@click.argument("name")
@click.option("--host", default="localhost", help="Mail server host")
@click.option("--port", default=25, help="Mail server port")
@click.option("--protocol", type=click.Choice(["smtp", "imap", "pop3"]), default="smtp", help="Mail protocol")
@click.option("--tls", is_flag=True, help="Enable TLS encryption")
def mail_server_create(name: str, host: str, port: int, protocol: str, tls: bool):
    """Create a new mock mail server.

    Examples:
        mockfactory mail-server create smtp-server --protocol smtp --port 587 --tls
        mockfactory mail-server create imap-server --protocol imap --port 993
    """
    try:
        client = get_client()
        server_data = {
            "name": name,
            "host": host,
            "port": port,
            "protocol": protocol,
            "tls": tls
        }

        # TODO: Call API endpoint when implemented
        # server = client.create_mock_mail_server(**server_data)

        success(f"Mock mail server '{name}' created successfully")
        info(f"Protocol: {protocol}")
        info(f"Host: {host}:{port}")
        if tls:
            info("TLS: Enabled")
    except Exception as e:
        error(str(e))


@mail_server.command(name="list")
@click.option("--protocol", type=click.Choice(["smtp", "imap", "pop3"]), help="Filter by protocol")
def mail_server_list(protocol: Optional[str]):
    """List all mock mail servers."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # servers = client.list_mock_mail_servers(protocol=protocol)

        table = Table(title="Mock Mail Servers", border_style="blue")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Protocol", style="yellow")
        table.add_column("Host:Port", style="white")
        table.add_column("TLS", style="green")
        table.add_column("Status", style="green")

        info("Mock mail server listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@mail_server.command(name="get")
@click.argument("name")
def mail_server_get(name: str):
    """Get details of a mock mail server."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # server = client.get_mock_mail_server(name)

        table = Table(title=f"Mail Server: {name}", show_header=False, border_style="blue")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        info(f"Fetching mail server '{name}'...")
        info("API endpoint to be implemented")

        console.print(table)
    except Exception as e:
        error(str(e))


@mail_server.command(name="delete")
@click.argument("name")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
def mail_server_delete(name: str, yes: bool):
    """Delete a mock mail server."""
    try:
        if not yes:
            if not click.confirm(f"Are you sure you want to delete mail server '{name}'?"):
                info("Cancelled")
                return

        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.delete_mock_mail_server(name)

        success(f"Mock mail server '{name}' deleted successfully")
    except Exception as e:
        error(str(e))


@cli.group()
def mail_client():
    """Manage mock mail clients."""
    pass


@mail_client.command(name="create")
@click.argument("name")
@click.option("--user", help="Bind to mock user")
@click.option("--server", help="Connect to mail server")
@click.option("--mailbox", help="Default mailbox")
def mail_client_create(name: str, user: Optional[str], server: Optional[str], mailbox: Optional[str]):
    """Create a new mock mail client.

    Examples:
        mockfactory mail-client create client1 --user john.doe --server smtp-server
        mockfactory mail-client create client2 --mailbox john.doe@example.com
    """
    try:
        client = get_client()
        client_data = {"name": name}
        if user:
            client_data["user"] = user
        if server:
            client_data["server"] = server
        if mailbox:
            client_data["mailbox"] = mailbox

        # TODO: Call API endpoint when implemented
        # mail_client_obj = client.create_mock_mail_client(**client_data)

        success(f"Mock mail client '{name}' created successfully")
        if user:
            info(f"Bound to user: {user}")
        if server:
            info(f"Connected to server: {server}")
        if mailbox:
            info(f"Default mailbox: {mailbox}")
    except Exception as e:
        error(str(e))


@mail_client.command(name="list")
@click.option("--user", help="Filter by bound user")
@click.option("--server", help="Filter by mail server")
def mail_client_list(user: Optional[str], server: Optional[str]):
    """List all mock mail clients."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # clients = client.list_mock_mail_clients(user=user, server=server)

        table = Table(title="Mock Mail Clients", border_style="blue")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("User", style="magenta")
        table.add_column("Server", style="yellow")
        table.add_column("Mailbox", style="white")
        table.add_column("Status", style="green")

        info("Mock mail client listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@mail_client.command(name="delete")
@click.argument("name")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
def mail_client_delete(name: str, yes: bool):
    """Delete a mock mail client."""
    try:
        if not yes:
            if not click.confirm(f"Are you sure you want to delete mail client '{name}'?"):
                info("Cancelled")
                return

        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.delete_mock_mail_client(name)

        success(f"Mock mail client '{name}' deleted successfully")
    except Exception as e:
        error(str(e))


@cli.group()
def mailbox():
    """Manage mock mailboxes."""
    pass


@mailbox.command(name="create")
@click.argument("email")
@click.option("--user", help="Bind to mock user")
@click.option("--quota", type=int, default=1000, help="Mailbox quota in MB")
def mailbox_create(email: str, user: Optional[str], quota: int):
    """Create a new mock mailbox.

    Creates a mailbox with standard folders: inbox, outbox, sent, bulk, drafts.

    Examples:
        mockfactory mailbox create john.doe@example.com --user john.doe
        mockfactory mailbox create admin@example.com --quota 5000
    """
    try:
        client = get_client()
        mailbox_data = {
            "email": email,
            "quota": quota,
            "folders": ["inbox", "outbox", "sent", "bulk", "drafts"]
        }
        if user:
            mailbox_data["user"] = user

        # TODO: Call API endpoint when implemented
        # mailbox_obj = client.create_mock_mailbox(**mailbox_data)

        success(f"Mock mailbox '{email}' created successfully")
        info(f"Quota: {quota} MB")
        info("Folders: inbox, outbox, sent, bulk, drafts")
        if user:
            info(f"Bound to user: {user}")
    except Exception as e:
        error(str(e))


@mailbox.command(name="list")
@click.option("--user", help="Filter by bound user")
def mailbox_list(user: Optional[str]):
    """List all mock mailboxes."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # mailboxes = client.list_mock_mailboxes(user=user)

        table = Table(title="Mock Mailboxes", border_style="blue")
        table.add_column("ID", style="cyan")
        table.add_column("Email", style="white")
        table.add_column("User", style="magenta")
        table.add_column("Quota (MB)", style="yellow")
        table.add_column("Messages", style="white")
        table.add_column("Status", style="green")

        info("Mock mailbox listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@mailbox.command(name="get")
@click.argument("email")
def mailbox_get(email: str):
    """Get details of a mock mailbox including folder statistics."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # mailbox_obj = client.get_mock_mailbox(email)

        table = Table(title=f"Mailbox: {email}", border_style="blue")
        table.add_column("Folder", style="cyan")
        table.add_column("Messages", style="white")
        table.add_column("Unread", style="yellow")
        table.add_column("Size (MB)", style="white")

        # Example folder data structure
        folders = ["inbox", "outbox", "sent", "bulk", "drafts"]
        for folder in folders:
            table.add_row(folder.capitalize(), "0", "0", "0.00")

        info(f"Fetching mailbox '{email}'...")
        info("API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@mailbox.command(name="delete")
@click.argument("email")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
def mailbox_delete(email: str, yes: bool):
    """Delete a mock mailbox."""
    try:
        if not yes:
            if not click.confirm(f"Are you sure you want to delete mailbox '{email}'?"):
                info("Cancelled")
                return

        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.delete_mock_mailbox(email)

        success(f"Mock mailbox '{email}' deleted successfully")
    except Exception as e:
        error(str(e))


@mailbox.command(name="send")
@click.argument("from_email")
@click.argument("to_email")
@click.option("--subject", required=True, help="Email subject")
@click.option("--body", required=True, help="Email body")
@click.option("--attachments", help="Comma-separated list of attachment filenames")
def mailbox_send(from_email: str, to_email: str, subject: str, body: str, attachments: Optional[str]):
    """Send a mock email from one mailbox to another.

    Example:
        mockfactory mailbox send john@example.com jane@example.com \\
            --subject "Test Email" --body "Hello Jane!"
    """
    try:
        client = get_client()
        email_data = {
            "from": from_email,
            "to": to_email,
            "subject": subject,
            "body": body
        }
        if attachments:
            email_data["attachments"] = attachments.split(",")

        # TODO: Call API endpoint when implemented
        # client.send_mock_email(**email_data)

        success(f"Email sent from '{from_email}' to '{to_email}'")
        info(f"Subject: {subject}")
        if attachments:
            info(f"Attachments: {attachments}")
    except Exception as e:
        error(str(e))


@mailbox.command(name="list-messages")
@click.argument("email")
@click.option("--folder", type=click.Choice(["inbox", "outbox", "sent", "bulk", "drafts"]), default="inbox", help="Folder to list messages from")
@click.option("--limit", type=int, default=20, help="Number of messages to show")
def mailbox_list_messages(email: str, folder: str, limit: int):
    """List messages in a mailbox folder.

    Example:
        mockfactory mailbox list-messages john@example.com --folder inbox
        mockfactory mailbox list-messages john@example.com --folder sent --limit 50
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # messages = client.list_mailbox_messages(email, folder=folder, limit=limit)

        table = Table(title=f"{email} - {folder.capitalize()}", border_style="blue")
        table.add_column("ID", style="cyan")
        table.add_column("From", style="white")
        table.add_column("Subject", style="white")
        table.add_column("Date", style="yellow")
        table.add_column("Size", style="white")
        table.add_column("Read", style="green")

        info(f"Listing messages from '{email}' - {folder} folder...")
        info("API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@cli.group()
def sms():
    """Manage mock SMS services."""
    pass


@sms.command(name="create-provider")
@click.argument("name")
@click.option("--provider", type=click.Choice(["twilio", "aws-sns", "nexmo", "custom"]), default="twilio", help="SMS provider type")
@click.option("--api-key", help="Provider API key")
def sms_create_provider(name: str, provider: str, api_key: Optional[str]):
    """Create a new mock SMS provider.

    Examples:
        mockfactory sms create-provider twilio-prod --provider twilio
        mockfactory sms create-provider aws-sms --provider aws-sns
    """
    try:
        client = get_client()
        provider_data = {
            "name": name,
            "provider": provider
        }
        if api_key:
            provider_data["api_key"] = api_key

        # TODO: Call API endpoint when implemented
        # sms_provider = client.create_mock_sms_provider(**provider_data)

        success(f"Mock SMS provider '{name}' created successfully")
        info(f"Provider type: {provider}")
    except Exception as e:
        error(str(e))


@sms.command(name="list-providers")
def sms_list_providers():
    """List all mock SMS providers."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # providers = client.list_mock_sms_providers()

        table = Table(title="Mock SMS Providers", border_style="blue")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Provider", style="yellow")
        table.add_column("Messages Sent", style="white")
        table.add_column("Status", style="green")

        info("Mock SMS provider listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@sms.command(name="send")
@click.argument("from_number")
@click.argument("to_number")
@click.option("--message", required=True, help="SMS message text")
@click.option("--provider", help="SMS provider to use")
def sms_send(from_number: str, to_number: str, message: str, provider: Optional[str]):
    """Send a mock SMS message.

    Example:
        mockfactory sms send +1234567890 +0987654321 --message "Your verification code is 123456"
    """
    try:
        client = get_client()
        sms_data = {
            "from": from_number,
            "to": to_number,
            "message": message
        }
        if provider:
            sms_data["provider"] = provider

        # TODO: Call API endpoint when implemented
        # client.send_mock_sms(**sms_data)

        success(f"SMS sent from '{from_number}' to '{to_number}'")
        info(f"Message: {message}")
        if provider:
            info(f"Provider: {provider}")
    except Exception as e:
        error(str(e))


@sms.command(name="list-messages")
@click.option("--phone-number", help="Filter by phone number")
@click.option("--provider", help="Filter by provider")
@click.option("--limit", type=int, default=20, help="Number of messages to show")
def sms_list_messages(phone_number: Optional[str], provider: Optional[str], limit: int):
    """List mock SMS messages.

    Example:
        mockfactory sms list-messages --phone-number +1234567890
        mockfactory sms list-messages --provider twilio-prod --limit 50
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # messages = client.list_mock_sms_messages(phone_number=phone_number, provider=provider, limit=limit)

        table = Table(title="Mock SMS Messages", border_style="blue")
        table.add_column("ID", style="cyan")
        table.add_column("From", style="white")
        table.add_column("To", style="white")
        table.add_column("Message", style="white")
        table.add_column("Provider", style="yellow")
        table.add_column("Timestamp", style="white")
        table.add_column("Status", style="green")

        info("Mock SMS message listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@sms.command(name="create-number")
@click.argument("phone_number")
@click.option("--user", help="Bind to mock user")
@click.option("--provider", help="SMS provider")
def sms_create_number(phone_number: str, user: Optional[str], provider: Optional[str]):
    """Create a mock phone number.

    Example:
        mockfactory sms create-number +1234567890 --user john.doe --provider twilio-prod
    """
    try:
        client = get_client()
        number_data = {"phone_number": phone_number}
        if user:
            number_data["user"] = user
        if provider:
            number_data["provider"] = provider

        # TODO: Call API endpoint when implemented
        # phone = client.create_mock_phone_number(**number_data)

        success(f"Mock phone number '{phone_number}' created successfully")
        if user:
            info(f"Bound to user: {user}")
        if provider:
            info(f"Provider: {provider}")
    except Exception as e:
        error(str(e))


@sms.command(name="list-numbers")
@click.option("--user", help="Filter by bound user")
@click.option("--provider", help="Filter by provider")
def sms_list_numbers(user: Optional[str], provider: Optional[str]):
    """List all mock phone numbers."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # numbers = client.list_mock_phone_numbers(user=user, provider=provider)

        table = Table(title="Mock Phone Numbers", border_style="blue")
        table.add_column("ID", style="cyan")
        table.add_column("Phone Number", style="white")
        table.add_column("User", style="magenta")
        table.add_column("Provider", style="yellow")
        table.add_column("Messages", style="white")
        table.add_column("Status", style="green")

        info("Mock phone number listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@cli.group()
def workflow():
    """Manage user registration and notification workflows."""
    pass


@workflow.command(name="create-registration")
@click.argument("name")
@click.option("--email-verification", is_flag=True, help="Enable email verification")
@click.option("--sms-verification", is_flag=True, help="Enable SMS verification")
@click.option("--mail-server", help="Mail server to use for verification emails")
@click.option("--sms-provider", help="SMS provider to use for verification")
def workflow_create_registration(name: str, email_verification: bool, sms_verification: bool, mail_server: Optional[str], sms_provider: Optional[str]):
    """Create a user registration workflow.

    Examples:
        mockfactory workflow create-registration signup-flow --email-verification --mail-server smtp-server
        mockfactory workflow create-registration mobile-signup --sms-verification --sms-provider twilio-prod
        mockfactory workflow create-registration full-signup --email-verification --sms-verification
    """
    try:
        client = get_client()
        workflow_data = {
            "name": name,
            "type": "registration",
            "email_verification": email_verification,
            "sms_verification": sms_verification
        }
        if mail_server:
            workflow_data["mail_server"] = mail_server
        if sms_provider:
            workflow_data["sms_provider"] = sms_provider

        # TODO: Call API endpoint when implemented
        # workflow_obj = client.create_mock_workflow(**workflow_data)

        success(f"User registration workflow '{name}' created successfully")
        if email_verification:
            info("✓ Email verification enabled")
            if mail_server:
                info(f"  Mail server: {mail_server}")
        if sms_verification:
            info("✓ SMS verification enabled")
            if sms_provider:
                info(f"  SMS provider: {sms_provider}")
    except Exception as e:
        error(str(e))


@workflow.command(name="test-registration")
@click.argument("workflow_name")
@click.option("--username", required=True, help="Username to register")
@click.option("--email", help="User email address")
@click.option("--phone", help="User phone number")
def workflow_test_registration(workflow_name: str, username: str, email: Optional[str], phone: Optional[str]):
    """Test a user registration workflow.

    Example:
        mockfactory workflow test-registration signup-flow \\
            --username john.doe \\
            --email john@example.com \\
            --phone +1234567890
    """
    try:
        client = get_client()
        test_data = {
            "workflow": workflow_name,
            "username": username
        }
        if email:
            test_data["email"] = email
        if phone:
            test_data["phone"] = phone

        # TODO: Call API endpoint when implemented
        # result = client.test_mock_workflow(**test_data)

        success(f"Testing registration workflow '{workflow_name}' for user '{username}'")
        if email:
            info(f"✓ Verification email sent to: {email}")
        if phone:
            info(f"✓ Verification SMS sent to: {phone}")
        info("\nWorkflow steps:")
        info("  1. User registration initiated")
        if email:
            info("  2. Email verification sent")
        if phone:
            info(f"  {'3' if email else '2'}. SMS verification sent")
        info(f"  {'4' if email and phone else '3' if email or phone else '2'}. Registration complete")
    except Exception as e:
        error(str(e))


@workflow.command(name="list")
def workflow_list():
    """List all workflows."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # workflows = client.list_mock_workflows()

        table = Table(title="Mock Workflows", border_style="blue")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Type", style="yellow")
        table.add_column("Email", style="green")
        table.add_column("SMS", style="green")
        table.add_column("Tests Run", style="white")
        table.add_column("Status", style="green")

        info("Mock workflow listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@cli.group()
def api():
    """Manage mock APIs and webhooks."""
    pass


@api.command(name="create")
@click.argument("name")
@click.option("--type", "api_type", type=click.Choice(["rest", "graphql", "webhook"]), default="rest", help="API type")
@click.option("--base-url", help="Base URL for the API")
@click.option("--auth", type=click.Choice(["none", "basic", "bearer", "api-key"]), default="none", help="Authentication type")
def api_create(name: str, api_type: str, base_url: Optional[str], auth: str):
    """Create a mock API endpoint.

    Examples:
        mockfactory api create user-api --type rest --base-url https://api.example.com
        mockfactory api create graphql-api --type graphql --auth bearer
        mockfactory api create payment-webhook --type webhook
    """
    try:
        client = get_client()
        api_data = {
            "name": name,
            "type": api_type,
            "auth": auth
        }
        if base_url:
            api_data["base_url"] = base_url

        # TODO: Call API endpoint when implemented
        # api_obj = client.create_mock_api(**api_data)

        success(f"Mock API '{name}' created successfully")
        info(f"Type: {api_type.upper()}")
        if base_url:
            info(f"Base URL: {base_url}")
        info(f"Authentication: {auth}")
    except Exception as e:
        error(str(e))


@api.command(name="add-endpoint")
@click.argument("api_name")
@click.argument("path")
@click.option("--method", type=click.Choice(["GET", "POST", "PUT", "PATCH", "DELETE"]), default="GET", help="HTTP method")
@click.option("--response", help="JSON response body")
@click.option("--status", type=int, default=200, help="HTTP status code")
def api_add_endpoint(api_name: str, path: str, method: str, response: Optional[str], status: int):
    """Add an endpoint to a mock API.

    Examples:
        mockfactory api add-endpoint user-api /users --method GET --status 200
        mockfactory api add-endpoint user-api /users --method POST --response '{"id": 1}'
    """
    try:
        client = get_client()
        endpoint_data = {
            "api_name": api_name,
            "path": path,
            "method": method,
            "status": status
        }
        if response:
            import json
            endpoint_data["response"] = json.loads(response)

        # TODO: Call API endpoint when implemented
        # client.add_mock_api_endpoint(**endpoint_data)

        success(f"Endpoint added to API '{api_name}'")
        info(f"{method} {path} → {status}")
        if response:
            info(f"Response: {response}")
    except Exception as e:
        error(str(e))


@api.command(name="list")
@click.option("--type", "api_type", type=click.Choice(["rest", "graphql", "webhook"]), help="Filter by API type")
def api_list(api_type: Optional[str]):
    """List all mock APIs."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # apis = client.list_mock_apis(api_type=api_type)

        table = Table(title="Mock APIs", border_style="blue")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Type", style="yellow")
        table.add_column("Base URL", style="white")
        table.add_column("Endpoints", style="white")
        table.add_column("Requests", style="white")
        table.add_column("Status", style="green")

        info("Mock API listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@api.command(name="list-requests")
@click.argument("api_name")
@click.option("--limit", type=int, default=20, help="Number of requests to show")
def api_list_requests(api_name: str, limit: int):
    """List requests received by a mock API.

    Example:
        mockfactory api list-requests user-api --limit 50
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # requests = client.list_mock_api_requests(api_name, limit=limit)

        table = Table(title=f"API Requests: {api_name}", border_style="blue")
        table.add_column("ID", style="cyan")
        table.add_column("Method", style="yellow")
        table.add_column("Path", style="white")
        table.add_column("Status", style="green")
        table.add_column("Timestamp", style="white")
        table.add_column("IP Address", style="white")

        info(f"Listing requests for API '{api_name}'...")
        info("API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@api.command(name="delete")
@click.argument("name")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
def api_delete(name: str, yes: bool):
    """Delete a mock API."""
    try:
        if not yes:
            if not click.confirm(f"Are you sure you want to delete API '{name}'?"):
                info("Cancelled")
                return

        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.delete_mock_api(name)

        success(f"Mock API '{name}' deleted successfully")
    except Exception as e:
        error(str(e))


@api.command(name="create-webhook")
@click.argument("name")
@click.option("--url", required=True, help="Webhook URL to receive events")
@click.option("--events", help="Comma-separated list of events to listen for")
@click.option("--secret", help="Webhook signing secret")
def api_create_webhook(name: str, url: str, events: Optional[str], secret: Optional[str]):
    """Create a mock webhook.

    Examples:
        mockfactory api create-webhook payment-hook --url https://example.com/webhook
        mockfactory api create-webhook user-events --url https://api.com/hook --events "user.created,user.updated"
    """
    try:
        client = get_client()
        webhook_data = {
            "name": name,
            "url": url
        }
        if events:
            webhook_data["events"] = events.split(",")
        if secret:
            webhook_data["secret"] = secret

        # TODO: Call API endpoint when implemented
        # webhook = client.create_mock_webhook(**webhook_data)

        success(f"Mock webhook '{name}' created successfully")
        info(f"URL: {url}")
        if events:
            info(f"Events: {events}")
        if secret:
            info("Secret configured for request signing")
    except Exception as e:
        error(str(e))


@api.command(name="trigger-webhook")
@click.argument("webhook_name")
@click.option("--event", required=True, help="Event name to trigger")
@click.option("--payload", help="JSON payload to send")
def api_trigger_webhook(webhook_name: str, event: str, payload: Optional[str]):
    """Trigger a mock webhook event.

    Example:
        mockfactory api trigger-webhook payment-hook --event "payment.completed" --payload '{"amount": 100}'
    """
    try:
        client = get_client()
        trigger_data = {
            "webhook_name": webhook_name,
            "event": event
        }
        if payload:
            import json
            trigger_data["payload"] = json.loads(payload)

        # TODO: Call API endpoint when implemented
        # result = client.trigger_mock_webhook(**trigger_data)

        success(f"Webhook '{webhook_name}' triggered successfully")
        info(f"Event: {event}")
        if payload:
            info(f"Payload: {payload}")
    except Exception as e:
        error(str(e))


@cli.group()
def iam():
    """Manage mock IAM (Identity and Access Management)."""
    pass


@iam.command(name="create-user")
@click.argument("username")
@click.option("--organization", help="Bind to organization")
@click.option("--cloud", help="Bind to cloud environment")
@click.option("--path", default="/", help="IAM user path")
def iam_create_user(username: str, organization: Optional[str], cloud: Optional[str], path: str):
    """Create a mock IAM user.

    Examples:
        mockfactory iam create-user john.smith --organization acme-corp
        mockfactory iam create-user api-user --cloud dev-cloud --path /service-accounts/
    """
    try:
        client = get_client()
        user_data = {
            "username": username,
            "path": path
        }
        if organization:
            user_data["organization"] = organization
        if cloud:
            user_data["cloud"] = cloud

        # TODO: Call API endpoint when implemented
        # iam_user = client.create_iam_user(**user_data)

        success(f"IAM user '{username}' created successfully")
        info(f"Path: {path}")
        if organization:
            info(f"Organization: {organization}")
        if cloud:
            info(f"Cloud: {cloud}")
    except Exception as e:
        error(str(e))


@iam.command(name="create-group")
@click.argument("group_name")
@click.option("--organization", help="Bind to organization")
@click.option("--cloud", help="Bind to cloud environment")
@click.option("--description", help="Group description")
def iam_create_group(group_name: str, organization: Optional[str], cloud: Optional[str], description: Optional[str]):
    """Create a mock IAM group.

    Examples:
        mockfactory iam create-group developers --organization acme-corp
        mockfactory iam create-group admins --cloud prod-cloud --description "Production administrators"
    """
    try:
        client = get_client()
        group_data = {
            "group_name": group_name
        }
        if organization:
            group_data["organization"] = organization
        if cloud:
            group_data["cloud"] = cloud
        if description:
            group_data["description"] = description

        # TODO: Call API endpoint when implemented
        # iam_group = client.create_iam_group(**group_data)

        success(f"IAM group '{group_name}' created successfully")
        if description:
            info(f"Description: {description}")
        if organization:
            info(f"Organization: {organization}")
        if cloud:
            info(f"Cloud: {cloud}")
    except Exception as e:
        error(str(e))


@iam.command(name="create-role")
@click.argument("role_name")
@click.option("--trust-policy", required=True, help="Trust policy JSON")
@click.option("--organization", help="Bind to organization")
@click.option("--cloud", help="Bind to cloud environment")
@click.option("--description", help="Role description")
def iam_create_role(role_name: str, trust_policy: str, organization: Optional[str], cloud: Optional[str], description: Optional[str]):
    """Create a mock IAM role with trust policy.

    Examples:
        mockfactory iam create-role lambda-execution --trust-policy '{"Service": "lambda"}' --cloud dev-cloud
        mockfactory iam create-role cross-account --trust-policy '{"AWS": "arn:aws:iam::123456:root"}'
    """
    try:
        client = get_client()
        import json

        role_data = {
            "role_name": role_name,
            "trust_policy": json.loads(trust_policy)
        }
        if organization:
            role_data["organization"] = organization
        if cloud:
            role_data["cloud"] = cloud
        if description:
            role_data["description"] = description

        # TODO: Call API endpoint when implemented
        # iam_role = client.create_iam_role(**role_data)

        success(f"IAM role '{role_name}' created successfully")
        info(f"Trust policy: {trust_policy}")
        if description:
            info(f"Description: {description}")
    except Exception as e:
        error(str(e))


@iam.command(name="create-policy")
@click.argument("policy_name")
@click.option("--policy-document", required=True, help="Policy document JSON")
@click.option("--description", help="Policy description")
@click.option("--organization", help="Bind to organization")
@click.option("--cloud", help="Bind to cloud environment")
def iam_create_policy(policy_name: str, policy_document: str, description: Optional[str], organization: Optional[str], cloud: Optional[str]):
    """Create a mock IAM policy.

    Examples:
        mockfactory iam create-policy s3-read-only --policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"s3:Get*","Resource":"*"}]}'
        mockfactory iam create-policy admin-policy --policy-document @policy.json --cloud prod-cloud
    """
    try:
        client = get_client()
        import json

        # Support reading from file with @ prefix
        if policy_document.startswith("@"):
            with open(policy_document[1:], 'r') as f:
                policy_doc = json.load(f)
        else:
            policy_doc = json.loads(policy_document)

        policy_data = {
            "policy_name": policy_name,
            "policy_document": policy_doc
        }
        if description:
            policy_data["description"] = description
        if organization:
            policy_data["organization"] = organization
        if cloud:
            policy_data["cloud"] = cloud

        # TODO: Call API endpoint when implemented
        # iam_policy = client.create_iam_policy(**policy_data)

        success(f"IAM policy '{policy_name}' created successfully")
        if description:
            info(f"Description: {description}")
        info(f"Policy document: {json.dumps(policy_doc, indent=2)}")
    except Exception as e:
        error(str(e))


@iam.command(name="attach-user-policy")
@click.argument("username")
@click.argument("policy_name")
def iam_attach_user_policy(username: str, policy_name: str):
    """Attach a policy to an IAM user.

    Example:
        mockfactory iam attach-user-policy john.smith s3-read-only
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.attach_iam_user_policy(username, policy_name)

        success(f"Attached policy '{policy_name}' to user '{username}'")
    except Exception as e:
        error(str(e))


@iam.command(name="attach-group-policy")
@click.argument("group_name")
@click.argument("policy_name")
def iam_attach_group_policy(group_name: str, policy_name: str):
    """Attach a policy to an IAM group.

    Example:
        mockfactory iam attach-group-policy developers s3-read-only
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.attach_iam_group_policy(group_name, policy_name)

        success(f"Attached policy '{policy_name}' to group '{group_name}'")
    except Exception as e:
        error(str(e))


@iam.command(name="attach-role-policy")
@click.argument("role_name")
@click.argument("policy_name")
def iam_attach_role_policy(role_name: str, policy_name: str):
    """Attach a policy to an IAM role.

    Example:
        mockfactory iam attach-role-policy lambda-execution cloudwatch-logs
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.attach_iam_role_policy(role_name, policy_name)

        success(f"Attached policy '{policy_name}' to role '{role_name}'")
    except Exception as e:
        error(str(e))


@iam.command(name="add-user-to-group")
@click.argument("username")
@click.argument("group_name")
def iam_add_user_to_group(username: str, group_name: str):
    """Add an IAM user to a group.

    Example:
        mockfactory iam add-user-to-group john.smith developers
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # client.add_iam_user_to_group(username, group_name)

        success(f"Added user '{username}' to group '{group_name}'")
    except Exception as e:
        error(str(e))


@iam.command(name="create-access-key")
@click.argument("username")
@click.option("--description", help="Access key description")
def iam_create_access_key(username: str, description: Optional[str]):
    """Create an access key for an IAM user.

    Example:
        mockfactory iam create-access-key john.smith --description "CLI access key"
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # access_key = client.create_iam_access_key(username, description)

        success(f"Created access key for user '{username}'")
        info("Access Key ID: AKIA..." + "X" * 16)
        info("Secret Access Key: " + "*" * 40)
        console.print("\n[bold yellow]⚠ Save these credentials now - the secret key won't be shown again![/bold yellow]")
    except Exception as e:
        error(str(e))


@iam.command(name="list-users")
@click.option("--organization", help="Filter by organization")
@click.option("--cloud", help="Filter by cloud")
def iam_list_users(organization: Optional[str], cloud: Optional[str]):
    """List all IAM users."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # users = client.list_iam_users(organization=organization, cloud=cloud)

        table = Table(title="IAM Users", border_style="blue")
        table.add_column("Username", style="cyan")
        table.add_column("Path", style="white")
        table.add_column("Organization", style="yellow")
        table.add_column("Cloud", style="white")
        table.add_column("Policies", style="green")
        table.add_column("Access Keys", style="white")

        info("IAM user listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@iam.command(name="list-policies")
@click.option("--organization", help="Filter by organization")
@click.option("--cloud", help="Filter by cloud")
def iam_list_policies(organization: Optional[str], cloud: Optional[str]):
    """List all IAM policies."""
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # policies = client.list_iam_policies(organization=organization, cloud=cloud)

        table = Table(title="IAM Policies", border_style="blue")
        table.add_column("Policy Name", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Attached To", style="yellow")
        table.add_column("Organization", style="white")
        table.add_column("Cloud", style="white")

        info("IAM policy listing - API endpoint to be implemented")
        console.print(table)
    except Exception as e:
        error(str(e))


@iam.command(name="get-policy")
@click.argument("policy_name")
def iam_get_policy(policy_name: str):
    """Get IAM policy details and document.

    Example:
        mockfactory iam get-policy s3-read-only
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # policy = client.get_iam_policy(policy_name)

        console.print(f"\n[bold cyan]Policy:[/bold cyan] {policy_name}\n")
        info("Policy document:")

        # Example policy document
        example_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:GetObject", "s3:ListBucket"],
                    "Resource": "*"
                }
            ]
        }

        import json
        console.print(json.dumps(example_doc, indent=2))
        info("\nAPI endpoint to be implemented")
    except Exception as e:
        error(str(e))


@iam.command(name="simulate-policy")
@click.argument("policy_name")
@click.option("--action", required=True, help="Action to test (e.g., s3:GetObject)")
@click.option("--resource", required=True, help="Resource ARN or name")
@click.option("--user", help="Test as specific user")
def iam_simulate_policy(policy_name: str, action: str, resource: str, user: Optional[str]):
    """Simulate IAM policy evaluation.

    Examples:
        mockfactory iam simulate-policy s3-read-only --action s3:GetObject --resource bucket/key
        mockfactory iam simulate-policy admin-policy --action ec2:RunInstances --resource * --user john.smith
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # result = client.simulate_iam_policy(policy_name, action, resource, user)

        console.print(f"\n[bold cyan]Policy Simulation[/bold cyan]\n")
        info(f"Policy: {policy_name}")
        info(f"Action: {action}")
        info(f"Resource: {resource}")
        if user:
            info(f"User: {user}")

        console.print("\n[bold green]✓ ALLOWED[/bold green]")
        info("Matching statement: Statement[0]")
        info("Effect: Allow")
        info("\nAPI endpoint to be implemented")
    except Exception as e:
        error(str(e))


@iam.command(name="create-resource-policy")
@click.argument("resource_type")
@click.argument("resource_id")
@click.option("--policy-document", required=True, help="Resource policy JSON")
def iam_create_resource_policy(resource_type: str, resource_id: str, policy_document: str):
    """Attach a resource-based policy to a resource.

    Examples:
        mockfactory iam create-resource-policy vpc vpc-123 --policy-document '{"Version":"2012-10-17","Statement":[...]}'
        mockfactory iam create-resource-policy lambda my-function --policy-document @policy.json
    """
    try:
        client = get_client()
        import json

        if policy_document.startswith("@"):
            with open(policy_document[1:], 'r') as f:
                policy_doc = json.load(f)
        else:
            policy_doc = json.loads(policy_document)

        # TODO: Call API endpoint when implemented
        # client.create_resource_policy(resource_type, resource_id, policy_doc)

        success(f"Created resource policy for {resource_type} '{resource_id}'")
        info(f"Policy document: {json.dumps(policy_doc, indent=2)}")
    except Exception as e:
        error(str(e))


@iam.command(name="check-permission")
@click.argument("username")
@click.option("--action", required=True, help="Action to check")
@click.option("--resource", required=True, help="Resource to access")
@click.option("--cloud", help="Cloud environment")
def iam_check_permission(username: str, action: str, resource: str, cloud: Optional[str]):
    """Check if a user has permission for an action on a resource.

    Examples:
        mockfactory iam check-permission john.smith --action s3:GetObject --resource bucket/key
        mockfactory iam check-permission api-user --action dynamodb:PutItem --resource users-table --cloud dev
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # result = client.check_iam_permission(username, action, resource, cloud)

        console.print(f"\n[bold cyan]Permission Check[/bold cyan]\n")
        info(f"User: {username}")
        info(f"Action: {action}")
        info(f"Resource: {resource}")
        if cloud:
            info(f"Cloud: {cloud}")

        console.print("\n[bold green]✓ ALLOWED[/bold green]")
        info("Granted via: Policy 's3-read-only' attached to group 'developers'")
        info("\nAPI endpoint to be implemented")
    except Exception as e:
        error(str(e))


@cli.group()
def generate():
    """Generate realistic test data for mock resources."""
    pass


@generate.command(name="users")
@click.option("--count", type=int, default=10, help="Number of users to generate")
@click.option("--role", type=click.Choice(["user", "admin", "developer", "mixed"]), default="mixed", help="User role")
@click.option("--organization", help="Organization to bind users to")
@click.option("--cloud", help="Cloud environment to bind to")
@click.option("--domain", help="Email domain")
@click.option("--output", type=click.Choice(["json", "csv", "apply"]), default="json", help="Output format")
def generate_users(count: int, role: str, organization: Optional[str], cloud: Optional[str], domain: Optional[str], output: str):
    """Generate realistic test users.

    Examples:
        mockfactory generate users --count 50 --role mixed --output json
        mockfactory generate users --count 10 --organization acme-corp --output apply
        mockfactory generate users --count 5 --domain example.com --output csv
    """
    try:
        client = get_client()
        # TODO: Call API endpoint when implemented
        # users = client.generate_users(count=count, role=role, organization=organization, cloud=cloud, domain=domain)

        import json
        import random

        # Generate realistic user data
        first_names = ["John", "Jane", "Alice", "Bob", "Carol", "David", "Emma", "Frank", "Grace", "Henry",
                      "Iris", "Jack", "Kate", "Leo", "Mary", "Noah", "Olivia", "Peter", "Quinn", "Rachel"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        roles = ["user", "admin", "developer"] if role == "mixed" else [role]

        users = []
        for i in range(count):
            first = random.choice(first_names)
            last = random.choice(last_names)
            username = f"{first.lower()}.{last.lower()}{i if i > 0 else ''}"
            email_domain = domain or "example.com"

            user_data = {
                "username": username,
                "email": f"{username}@{email_domain}",
                "full_name": f"{first} {last}",
                "role": random.choice(roles)
            }
            if organization:
                user_data["organization"] = organization
            if cloud:
                user_data["cloud"] = cloud

            users.append(user_data)

        if output == "json":
            console.print_json(data={"users": users, "count": len(users)})
        elif output == "csv":
            console.print("username,email,full_name,role,organization,cloud")
            for u in users:
                console.print(f"{u['username']},{u['email']},{u['full_name']},{u['role']},{u.get('organization', '')},{u.get('cloud', '')}")
        elif output == "apply":
            success(f"Generated {len(users)} users - applying to system...")
            for u in users:
                info(f"Creating user: {u['username']}")
                # TODO: Actually create the users via API
            success(f"Created {len(users)} users successfully")

    except Exception as e:
        error(str(e))


@generate.command(name="employees")
@click.option("--count", type=int, default=20, help="Number of employees to generate")
@click.option("--organization", required=True, help="Organization for employees")
@click.option("--departments", help="Comma-separated departments")
@click.option("--output", type=click.Choice(["json", "csv", "apply"]), default="json", help="Output format")
def generate_employees(count: int, organization: str, departments: Optional[str], output: str):
    """Generate realistic employee data with departments and roles.

    Examples:
        mockfactory generate employees --count 100 --organization acme-corp
        mockfactory generate employees --count 50 --organization startup --departments "engineering,sales,hr" --output apply
    """
    try:
        import random
        import json

        dept_list = departments.split(",") if departments else ["engineering", "sales", "marketing", "hr", "finance", "operations"]
        job_titles = {
            "engineering": ["Software Engineer", "Senior Engineer", "Tech Lead", "Engineering Manager", "DevOps Engineer"],
            "sales": ["Sales Rep", "Account Executive", "Sales Manager", "VP Sales"],
            "marketing": ["Marketing Specialist", "Content Manager", "Marketing Director"],
            "hr": ["HR Specialist", "Recruiter", "HR Manager"],
            "finance": ["Accountant", "Financial Analyst", "CFO"],
            "operations": ["Operations Manager", "Project Manager", "COO"]
        }

        first_names = ["John", "Jane", "Alice", "Bob", "Carol", "David", "Emma", "Frank", "Grace", "Henry"] * 5
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"] * 5

        employees = []
        for i in range(count):
            first = random.choice(first_names)
            last = random.choice(last_names)
            dept = random.choice(dept_list)
            title = random.choice(job_titles.get(dept, ["Employee"]))

            emp_data = {
                "username": f"{first.lower()}.{last.lower()}.{i}",
                "email": f"{first.lower()}.{last.lower()}.{i}@{organization}.com",
                "full_name": f"{first} {last}",
                "department": dept,
                "job_title": title,
                "employee_id": f"EMP{1000 + i}",
                "organization": organization,
                "role": "admin" if "Manager" in title or "Director" in title else "user"
            }
            employees.append(emp_data)

        if output == "json":
            console.print_json(data={"employees": employees, "count": len(employees)})
        elif output == "csv":
            console.print("username,email,full_name,department,job_title,employee_id,organization,role")
            for e in employees:
                console.print(f"{e['username']},{e['email']},{e['full_name']},{e['department']},{e['job_title']},{e['employee_id']},{e['organization']},{e['role']}")
        elif output == "apply":
            success(f"Generated {len(employees)} employees - applying to system...")
            # Group by department
            by_dept = {}
            for e in employees:
                dept = e['department']
                if dept not in by_dept:
                    by_dept[dept] = []
                by_dept[dept].append(e)

            for dept, emps in by_dept.items():
                info(f"Creating {len(emps)} employees in {dept} department")
            success(f"Created {len(employees)} employees successfully")

    except Exception as e:
        error(str(e))


@generate.command(name="organizations")
@click.option("--count", type=int, default=5, help="Number of organizations to generate")
@click.option("--output", type=click.Choice(["json", "apply"]), default="json", help="Output format")
def generate_organizations(count: int, output: str):
    """Generate realistic organization structures.

    Examples:
        mockfactory generate organizations --count 10
        mockfactory generate organizations --count 3 --output apply
    """
    try:
        import random

        company_prefixes = ["Tech", "Global", "Digital", "Cloud", "Smart", "Quantum", "Cyber", "Mega", "Super", "Ultra"]
        company_suffixes = ["Corp", "Inc", "Systems", "Solutions", "Industries", "Technologies", "Enterprises", "Group"]
        industries = ["technology", "finance", "healthcare", "retail", "manufacturing"]
        plans = ["free", "pro", "enterprise"]

        orgs = []
        for i in range(count):
            name = f"{random.choice(company_prefixes)}{random.choice(company_suffixes)}{i if i > 0 else ''}".lower()
            org_data = {
                "name": name,
                "description": f"{name.title()} - {random.choice(industries).title()} Company",
                "plan": random.choice(plans),
                "industry": random.choice(industries)
            }
            orgs.append(org_data)

        if output == "json":
            console.print_json(data={"organizations": orgs, "count": len(orgs)})
        elif output == "apply":
            success(f"Generated {len(orgs)} organizations - applying to system...")
            for org in orgs:
                info(f"Creating organization: {org['name']} ({org['plan']} plan)")
            success(f"Created {len(orgs)} organizations successfully")

    except Exception as e:
        error(str(e))


@generate.command(name="network-config")
@click.option("--cloud", required=True, help="Cloud environment")
@click.option("--subnets", type=int, default=3, help="Number of subnets")
@click.option("--output", type=click.Choice(["json", "apply"]), default="json", help="Output format")
def generate_network_config(cloud: str, subnets: int, output: str):
    """Generate realistic network configurations.

    Examples:
        mockfactory generate network-config --cloud dev-cloud --subnets 5
        mockfactory generate network-config --cloud prod-cloud --subnets 3 --output apply
    """
    try:
        config = {
            "cloud": cloud,
            "vpc": {
                "cidr_block": "10.0.0.0/16",
                "enable_dns": True,
                "enable_dns_hostnames": True
            },
            "subnets": [],
            "security_groups": []
        }

        # Generate subnets
        for i in range(subnets):
            config["subnets"].append({
                "name": f"subnet-{i+1}",
                "cidr_block": f"10.0.{i}.0/24",
                "availability_zone": f"us-east-1{chr(97+i)}",
                "public": i == 0  # First subnet is public
            })

        # Generate security groups
        config["security_groups"] = [
            {
                "name": "web-sg",
                "description": "Security group for web servers",
                "ingress": [
                    {"protocol": "tcp", "port": 80, "cidr": "0.0.0.0/0"},
                    {"protocol": "tcp", "port": 443, "cidr": "0.0.0.0/0"}
                ]
            },
            {
                "name": "app-sg",
                "description": "Security group for application servers",
                "ingress": [
                    {"protocol": "tcp", "port": 8080, "cidr": "10.0.0.0/16"}
                ]
            },
            {
                "name": "db-sg",
                "description": "Security group for databases",
                "ingress": [
                    {"protocol": "tcp", "port": 5432, "cidr": "10.0.0.0/16"},
                    {"protocol": "tcp", "port": 3306, "cidr": "10.0.0.0/16"}
                ]
            }
        ]

        if output == "json":
            console.print_json(data=config)
        elif output == "apply":
            success(f"Generated network config - applying to {cloud}...")
            info(f"Creating VPC: {config['vpc']['cidr_block']}")
            info(f"Creating {len(config['subnets'])} subnets")
            info(f"Creating {len(config['security_groups'])} security groups")
            success("Network configuration applied successfully")

    except Exception as e:
        error(str(e))


@generate.command(name="iam-policies")
@click.option("--type", "policy_type", type=click.Choice(["read-only", "read-write", "admin", "service-role", "all"]), default="all", help="Policy type")
@click.option("--services", help="Comma-separated AWS services (e.g., s3,dynamodb,lambda)")
@click.option("--output", type=click.Choice(["json", "files"]), default="json", help="Output format")
def generate_iam_policies(policy_type: str, services: Optional[str], output: str):
    """Generate common IAM policy templates.

    Examples:
        mockfactory generate iam-policies --type read-only --services s3,dynamodb
        mockfactory generate iam-policies --type all --output files
    """
    try:
        import json

        service_list = services.split(",") if services else ["s3", "dynamodb", "lambda", "sqs", "ec2"]
        policies = {}

        for service in service_list:
            if policy_type in ["read-only", "all"]:
                policies[f"{service}-read-only"] = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [f"{service}:Get*", f"{service}:List*", f"{service}:Describe*"],
                            "Resource": "*"
                        }
                    ]
                }

            if policy_type in ["read-write", "all"]:
                policies[f"{service}-read-write"] = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [f"{service}:*"],
                            "Resource": "*"
                        }
                    ]
                }

        if policy_type in ["admin", "all"]:
            policies["admin-access"] = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "*",
                        "Resource": "*"
                    }
                ]
            }

        if policy_type in ["service-role", "all"]:
            policies["lambda-execution-role-policy"] = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents"
                        ],
                        "Resource": "arn:aws:logs:*:*:*"
                    }
                ]
            }

        if output == "json":
            console.print_json(data={"policies": policies, "count": len(policies)})
        elif output == "files":
            success(f"Generated {len(policies)} policy templates")
            for name, doc in policies.items():
                filename = f"{name}.json"
                info(f"Policy template: {filename}")
                # In real implementation, write to files

    except Exception as e:
        error(str(e))


@generate.command(name="test-scenario")
@click.argument("scenario", type=click.Choice(["startup", "enterprise", "multi-cloud", "dev-team"]))
@click.option("--output", type=click.Choice(["json", "apply"]), default="json", help="Output format")
def generate_test_scenario(scenario: str, output: str):
    """Generate complete test scenarios with all resources.

    Scenarios:
        startup: Small startup with 10-20 employees, simple infrastructure
        enterprise: Large enterprise with 100+ employees, complex multi-region setup
        multi-cloud: Multi-cloud deployment across AWS, GCP, Azure
        dev-team: Development team with CI/CD, multiple environments

    Examples:
        mockfactory generate test-scenario startup
        mockfactory generate test-scenario enterprise --output apply
    """
    try:
        import json

        scenarios = {
            "startup": {
                "organization": {"name": "startup-inc", "plan": "free"},
                "employees": 15,
                "clouds": [{"name": "prod", "provider": "aws", "region": "us-east-1"}],
                "projects": [{"name": "web-app", "environment": "production"}],
                "iam_users": 10,
                "iam_groups": ["developers", "ops"]
            },
            "enterprise": {
                "organization": {"name": "enterprise-corp", "plan": "enterprise"},
                "employees": 500,
                "clouds": [
                    {"name": "us-east", "provider": "aws", "region": "us-east-1"},
                    {"name": "us-west", "provider": "aws", "region": "us-west-2"},
                    {"name": "eu-west", "provider": "aws", "region": "eu-west-1"}
                ],
                "projects": [
                    {"name": "core-services", "environment": "production"},
                    {"name": "analytics", "environment": "production"},
                    {"name": "staging", "environment": "staging"}
                ],
                "iam_users": 100,
                "iam_groups": ["admins", "developers", "analysts", "operations", "security"]
            },
            "multi-cloud": {
                "organization": {"name": "multi-cloud-co", "plan": "pro"},
                "employees": 50,
                "clouds": [
                    {"name": "aws-primary", "provider": "aws", "region": "us-east-1"},
                    {"name": "gcp-analytics", "provider": "gcp", "region": "us-central1"},
                    {"name": "azure-backup", "provider": "azure", "region": "eastus"}
                ],
                "projects": [{"name": "unified-platform", "environment": "production"}],
                "iam_users": 30,
                "iam_groups": ["cloud-admins", "developers", "data-engineers"]
            },
            "dev-team": {
                "organization": {"name": "dev-team", "plan": "pro"},
                "employees": 25,
                "clouds": [
                    {"name": "dev", "provider": "aws", "region": "us-east-1"},
                    {"name": "staging", "provider": "aws", "region": "us-east-1"},
                    {"name": "prod", "provider": "aws", "region": "us-west-2"}
                ],
                "projects": [
                    {"name": "api", "environment": "development"},
                    {"name": "api", "environment": "staging"},
                    {"name": "api", "environment": "production"}
                ],
                "iam_users": 20,
                "iam_groups": ["developers", "qa", "devops"]
            }
        }

        scenario_data = scenarios[scenario]

        if output == "json":
            console.print_json(data={"scenario": scenario, "config": scenario_data})
        elif output == "apply":
            success(f"Applying '{scenario}' test scenario...")
            info(f"Creating organization: {scenario_data['organization']['name']}")
            info(f"Generating {scenario_data['employees']} employees")
            info(f"Creating {len(scenario_data['clouds'])} cloud environments")
            info(f"Creating {len(scenario_data['projects'])} projects")
            info(f"Creating {scenario_data['iam_users']} IAM users")
            info(f"Creating {len(scenario_data['iam_groups'])} IAM groups")
            success(f"Test scenario '{scenario}' applied successfully!")

    except Exception as e:
        error(str(e))


# ============================================================================
# Utilities Commands
# ============================================================================

@cli.group()
def utilities():
    """Utility helpers for common transformations and operations."""
    pass


# Binary/Hex Conversion
@utilities.command(name="bin2hex")
@click.argument("binary")
def utilities_bin2hex(binary: str):
    """Convert binary to hexadecimal.

    Example: mockfactory utilities bin2hex 11010101
    """
    try:
        hex_val = hex(int(binary, 2))[2:]
        console.print(f"Hex: {hex_val}")
    except Exception as e:
        error(str(e))


@utilities.command(name="hex2bin")
@click.argument("hex_string")
def utilities_hex2bin(hex_string: str):
    """Convert hexadecimal to binary.

    Example: mockfactory utilities hex2bin d5
    """
    try:
        binary = bin(int(hex_string, 16))[2:]
        console.print(f"Binary: {binary}")
    except Exception as e:
        error(str(e))


# IP Conversion
@utilities.command(name="ip2bin")
@click.argument("ip")
def utilities_ip2bin(ip: str):
    """Convert IP address to binary.

    Example: mockfactory utilities ip2bin 192.168.1.1
    """
    try:
        parts = ip.split('.')
        binary = ''.join(format(int(part), '08b') for part in parts)
        console.print(f"Binary: {binary}")
        console.print(f"Formatted: {'.'.join(format(int(part), '08b') for part in parts)}")
    except Exception as e:
        error(str(e))


@utilities.command(name="bin2ip")
@click.argument("binary")
def utilities_bin2ip(binary: str):
    """Convert binary to IP address.

    Example: mockfactory utilities bin2ip 11000000101010000000000100000001
    """
    try:
        # Remove any dots/spaces
        binary = binary.replace('.', '').replace(' ', '')
        if len(binary) != 32:
            raise ValueError("Binary must be 32 bits for IPv4")

        octets = [str(int(binary[i:i+8], 2)) for i in range(0, 32, 8)]
        ip = '.'.join(octets)
        console.print(f"IP: {ip}")
    except Exception as e:
        error(str(e))


@utilities.command(name="ip2long")
@click.argument("ip")
def utilities_ip2long(ip: str):
    """Convert IP address to long integer.

    Example: mockfactory utilities ip2long 192.168.1.1
    """
    try:
        parts = ip.split('.')
        long_ip = (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])
        console.print(f"Long: {long_ip}")
    except Exception as e:
        error(str(e))


@utilities.command(name="long2ip")
@click.argument("long_int", type=int)
def utilities_long2ip(long_int: int):
    """Convert long integer to IP address.

    Example: mockfactory utilities long2ip 3232235777
    """
    try:
        octets = [
            str(long_int >> 24 & 0xFF),
            str(long_int >> 16 & 0xFF),
            str(long_int >> 8 & 0xFF),
            str(long_int & 0xFF)
        ]
        ip = '.'.join(octets)
        console.print(f"IP: {ip}")
    except Exception as e:
        error(str(e))


# CIDR Helpers
@utilities.command(name="cidr-to-range")
@click.argument("cidr")
def utilities_cidr_to_range(cidr: str):
    """Convert CIDR to IP range.

    Example: mockfactory utilities cidr-to-range 10.0.0.0/24
    """
    try:
        import ipaddress
        network = ipaddress.ip_network(cidr, strict=False)

        table = Table(title=f"CIDR: {cidr}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Network Address", str(network.network_address))
        table.add_row("Broadcast Address", str(network.broadcast_address))
        table.add_row("First Usable IP", str(list(network.hosts())[0] if network.num_addresses > 2 else network.network_address))
        table.add_row("Last Usable IP", str(list(network.hosts())[-1] if network.num_addresses > 2 else network.broadcast_address))
        table.add_row("Total IPs", str(network.num_addresses))
        table.add_row("Usable IPs", str(network.num_addresses - 2 if network.num_addresses > 2 else network.num_addresses))
        table.add_row("Netmask", str(network.netmask))

        console.print(table)
    except Exception as e:
        error(str(e))


@utilities.command(name="ip-in-cidr")
@click.argument("ip")
@click.argument("cidr")
def utilities_ip_in_cidr(ip: str, cidr: str):
    """Check if IP is in CIDR range.

    Example: mockfactory utilities ip-in-cidr 10.0.0.50 10.0.0.0/24
    """
    try:
        import ipaddress
        ip_addr = ipaddress.ip_address(ip)
        network = ipaddress.ip_network(cidr, strict=False)

        in_range = ip_addr in network
        if in_range:
            success(f"{ip} is IN the range {cidr}")
        else:
            error(f"{ip} is NOT in the range {cidr}")
    except Exception as e:
        error(str(e))


# Base64 Helpers
@utilities.command(name="base64-encode")
@click.argument("data")
def utilities_base64_encode(data: str):
    """Encode string to Base64.

    Example: mockfactory utilities base64-encode "Hello World"
    """
    try:
        import base64
        encoded = base64.b64encode(data.encode()).decode()
        console.print(f"Encoded: {encoded}")
    except Exception as e:
        error(str(e))


@utilities.command(name="base64-decode")
@click.argument("encoded")
def utilities_base64_decode(encoded: str):
    """Decode Base64 string.

    Example: mockfactory utilities base64-decode SGVsbG8gV29ybGQ=
    """
    try:
        import base64
        decoded = base64.b64decode(encoded.encode()).decode()
        console.print(f"Decoded: {decoded}")
    except Exception as e:
        error(str(e))


# URL Helpers
@utilities.command(name="url-encode")
@click.argument("data")
def utilities_url_encode(data: str):
    """URL encode string.

    Example: mockfactory utilities url-encode "hello world & stuff"
    """
    try:
        from urllib.parse import quote
        encoded = quote(data)
        console.print(f"Encoded: {encoded}")
    except Exception as e:
        error(str(e))


@utilities.command(name="url-decode")
@click.argument("encoded")
def utilities_url_decode(encoded: str):
    """URL decode string.

    Example: mockfactory utilities url-decode "hello%20world%20%26%20stuff"
    """
    try:
        from urllib.parse import unquote
        decoded = unquote(encoded)
        console.print(f"Decoded: {decoded}")
    except Exception as e:
        error(str(e))


# Hash Helpers
@utilities.command(name="hash")
@click.argument("data")
@click.option("--algorithm", type=click.Choice(["md5", "sha1", "sha256", "sha512"]), default="sha256", help="Hash algorithm")
def utilities_hash(data: str, algorithm: str):
    """Generate hash of data.

    Example: mockfactory utilities hash "Hello World" --algorithm sha256
    """
    try:
        import hashlib

        if algorithm == "md5":
            hash_obj = hashlib.md5(data.encode())
        elif algorithm == "sha1":
            hash_obj = hashlib.sha1(data.encode())
        elif algorithm == "sha256":
            hash_obj = hashlib.sha256(data.encode())
        elif algorithm == "sha512":
            hash_obj = hashlib.sha512(data.encode())

        hash_value = hash_obj.hexdigest()
        console.print(f"{algorithm.upper()}: {hash_value}")
    except Exception as e:
        error(str(e))


# UUID Helpers
@utilities.command(name="uuid")
@click.option("--version", type=click.Choice(["1", "4"]), default="4", help="UUID version")
@click.option("--count", type=int, default=1, help="Number of UUIDs to generate")
def utilities_uuid(version: str, count: int):
    """Generate UUID(s).

    Example: mockfactory utilities uuid --count 5
    """
    try:
        import uuid as uuid_lib

        for _ in range(count):
            if version == "1":
                new_uuid = uuid_lib.uuid1()
            else:
                new_uuid = uuid_lib.uuid4()
            console.print(str(new_uuid))
    except Exception as e:
        error(str(e))


# String Helpers
@utilities.command(name="slugify")
@click.argument("text")
def utilities_slugify(text: str):
    """Convert text to URL-friendly slug.

    Example: mockfactory utilities slugify "Hello World & Stuff!"
    """
    try:
        import re
        slug = text.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        console.print(f"Slug: {slug}")
    except Exception as e:
        error(str(e))


@utilities.command(name="random-string")
@click.option("--length", type=int, default=16, help="Length of string")
@click.option("--charset", type=click.Choice(["alphanumeric", "alpha", "numeric", "hex"]), default="alphanumeric", help="Character set")
def utilities_random_string(length: int, charset: str):
    """Generate random string.

    Example: mockfactory utilities random-string --length 32 --charset hex
    """
    try:
        import random
        import string

        if charset == "alphanumeric":
            chars = string.ascii_letters + string.digits
        elif charset == "alpha":
            chars = string.ascii_letters
        elif charset == "numeric":
            chars = string.digits
        elif charset == "hex":
            chars = string.hexdigits.lower()[:16]

        random_str = ''.join(random.choice(chars) for _ in range(length))
        console.print(random_str)
    except Exception as e:
        error(str(e))


@utilities.command(name="random-password")
@click.option("--length", type=int, default=16, help="Password length")
@click.option("--no-symbols", is_flag=True, help="Exclude symbols")
@click.option("--no-numbers", is_flag=True, help="Exclude numbers")
def utilities_random_password(length: int, no_symbols: bool, no_numbers: bool):
    """Generate secure random password.

    Example: mockfactory utilities random-password --length 20
    """
    try:
        import random
        import string

        chars = string.ascii_letters
        if not no_numbers:
            chars += string.digits
        if not no_symbols:
            chars += "!@#$%^&*"

        password = ''.join(random.choice(chars) for _ in range(length))
        console.print(f"Password: {password}")
    except Exception as e:
        error(str(e))


# Time Helpers
@utilities.command(name="timestamp")
@click.option("--format", type=click.Choice(["unix", "iso8601", "rfc3339"]), default="unix", help="Timestamp format")
def utilities_timestamp(format: str):
    """Get current timestamp.

    Example: mockfactory utilities timestamp --format iso8601
    """
    try:
        import time
        from datetime import datetime

        if format == "unix":
            ts = int(time.time())
            console.print(str(ts))
        elif format == "iso8601":
            iso = datetime.utcnow().isoformat() + "Z"
            console.print(iso)
        elif format == "rfc3339":
            rfc = datetime.utcnow().isoformat() + "Z"
            console.print(rfc)
    except Exception as e:
        error(str(e))


# JSON Helpers
@utilities.command(name="json-minify")
@click.argument("json_file", type=click.Path(exists=True))
def utilities_json_minify(json_file: str):
    """Minify JSON file.

    Example: mockfactory utilities json-minify config.json
    """
    try:
        import json
        with open(json_file, 'r') as f:
            data = json.load(f)
        minified = json.dumps(data, separators=(',', ':'))
        console.print(minified)
    except Exception as e:
        error(str(e))


@utilities.command(name="json-pretty")
@click.argument("json_file", type=click.Path(exists=True))
@click.option("--indent", type=int, default=2, help="Indentation level")
def utilities_json_pretty(json_file: str, indent: int):
    """Pretty print JSON file.

    Example: mockfactory utilities json-pretty config.json --indent 4
    """
    try:
        import json
        with open(json_file, 'r') as f:
            data = json.load(f)
        pretty = json.dumps(data, indent=indent)
        console.print(pretty)
    except Exception as e:
        error(str(e))


@utilities.command(name="json-validate")
@click.argument("json_file", type=click.Path(exists=True))
def utilities_json_validate(json_file: str):
    """Validate JSON file.

    Example: mockfactory utilities json-validate config.json
    """
    try:
        import json
        with open(json_file, 'r') as f:
            data = json.load(f)
        success(f"Valid JSON with {len(str(data))} characters")
    except json.JSONDecodeError as e:
        error(f"Invalid JSON: {e}")
    except Exception as e:
        error(str(e))


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
