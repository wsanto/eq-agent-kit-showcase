"""
ANIMA AgentKit CLI - Setup and Configuration Tool

Easy command-line interface for setting up and managing ANIMA AgentKit.

Usage:
    anima setup              # Interactive setup wizard
    anima config             # View current configuration
    anima config set KEY VALUE  # Set configuration value
    anima validate           # Validate environment and connections
    anima quickstart         # Generate quickstart code
    anima doctor             # Diagnose common issues
"""

import os
import sys
import click
import json
from pathlib import Path
from typing import Optional, Dict, Any
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as rprint
from dotenv import load_dotenv, set_key, find_dotenv

console = Console()

# ASCII Art Branding
ANIMA_ASCII = r"""
[cyan]
   ▄████████ ███▄▄▄▄    ▄█    ▄▄▄▄███▄▄▄▄      ▄████████
  ███    ███ ███▀▀▀██▄ ███  ▄██▀▀▀███▀▀▀██▄   ███    ███
  ███    ███ ███   ███ ███▌ ███   ███   ███   ███    ███
  ███    ███ ███   ███ ███▌ ███   ███   ███   ███    ███
▀███████████ ███   ███ ███▌ ███   ███   ███ ▀███████████
  ███    ███ ███   ███ ███  ███   ███   ███   ███    ███
  ███    ███ ███   ███ ███  ███   ███   ███   ███    ███
  ███    █▀   ▀█   █▀  █▀    ▀█   ███   █▀    ███    █▀
[/cyan]
[dim]        Emotionally Intelligent AI AgentKit v1.0.0[/dim]
"""

SETUP_HEADER = r"""
[bold cyan]
╔════════════════════════════════════════════════════════╗
║                                                        ║
║        🧠  ANIMA AGENTKIT SETUP WIZARD  🧠            ║
║                                                        ║
║          Configure Your Intelligent Agent              ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
[/bold cyan]
"""

VALIDATE_HEADER = r"""
[bold cyan]
╔════════════════════════════════════════════════════════╗
║                                                        ║
║       🔍  ANIMA ENVIRONMENT VALIDATOR  🔍             ║
║                                                        ║
║          Testing Your Configuration                    ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
[/bold cyan]
"""

DOCTOR_HEADER = r"""
[bold cyan]
╔════════════════════════════════════════════════════════╗
║                                                        ║
║         🩺  ANIMA DIAGNOSTIC TOOL  🩺                 ║
║                                                        ║
║          Scanning for Issues                           ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
[/bold cyan]
"""

QUICKSTART_HEADER = r"""
[bold cyan]
╔════════════════════════════════════════════════════════╗
║                                                        ║
║       📝  ANIMA CODE GENERATOR  📝                    ║
║                                                        ║
║          Creating Your Agent                           ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
[/bold cyan]
"""


class CLIConfig:
    """Manages CLI configuration and .env file"""

    def __init__(self):
        self.env_file = self._find_or_create_env()
        load_dotenv(self.env_file)

    def _find_or_create_env(self) -> Path:
        """Find or create .env file"""
        env_path = find_dotenv()
        if env_path:
            return Path(env_path)

        # Create .env in current directory
        env_path = Path.cwd() / ".env"
        env_path.touch()
        return env_path

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value"""
        return os.getenv(key, default)

    def set(self, key: str, value: str) -> None:
        """Set configuration value"""
        set_key(str(self.env_file), key, value)
        os.environ[key] = value

    def get_all(self) -> Dict[str, str]:
        """Get all configuration values"""
        load_dotenv(self.env_file)
        return {
            # Core API Keys
            "SYNAPSE_API_KEY": os.getenv("SYNAPSE_API_KEY", ""),
            "SYNAPSE_BASE_URL": os.getenv("SYNAPSE_BASE_URL", "https://api.kaikostudios.xyz"),
            "MISTRAL_API_KEY": os.getenv("MISTRAL_API_KEY", ""),
            "NOUS_API_KEY": os.getenv("NOUS_API_KEY", ""),

            # LLM Configuration
            "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "mistral"),
            "MISTRAL_MODEL": os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
            "MISTRAL_TEMPERATURE": os.getenv("MISTRAL_TEMPERATURE", "0.7"),
            "NOUS_MODEL": os.getenv("NOUS_MODEL", "Hermes-4-70B"),
            "NOUS_TEMPERATURE": os.getenv("NOUS_TEMPERATURE", "0.7"),

            # Neo4j Configuration
            "NEO4J_URI": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            "NEO4J_USERNAME": os.getenv("NEO4J_USERNAME", "neo4j"),
            "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD", ""),

            # Intelligence Layer
            "ANIMA_ENABLE_INTELLIGENCE": os.getenv("ANIMA_ENABLE_INTELLIGENCE", "true"),
            "ANIMA_TOKEN_BUDGET_MAX": os.getenv("ANIMA_TOKEN_BUDGET_MAX", "15000"),

            # S.I. Mode (Synthetic Intelligence / IGA)
            "ANIMA_SI_MODE": os.getenv("ANIMA_SI_MODE", "false"),
            "ANIMA_IGA_EXPRESSION_PROBABILITY": os.getenv("ANIMA_IGA_EXPRESSION_PROBABILITY", "0.3"),
            "ANIMA_IGA_EXPLORATION_INTERVAL": os.getenv("ANIMA_IGA_EXPLORATION_INTERVAL", "6"),

            # Vector Embeddings
            "EMBEDDING_PROVIDER": os.getenv("EMBEDDING_PROVIDER", "local"),
            "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            "EMBEDDING_DIMENSION": os.getenv("EMBEDDING_DIMENSION", "1536"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "VOYAGE_API_KEY": os.getenv("VOYAGE_API_KEY", ""),

            # Web Search APIs (for IGA Deep-Xplore)
            "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY", ""),
            "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", ""),
            "SERPAPI_KEY": os.getenv("SERPAPI_KEY", ""),
        }


@click.group()
@click.version_option(version="1.0.0", prog_name="anima")
def cli():
    """ANIMA AgentKit - Emotionally Intelligent AI Framework"""
    pass


@cli.command()
@click.option('--quick', is_flag=True, help='Quick setup with defaults')
def setup(quick: bool):
    """Interactive setup wizard for ANIMA AgentKit"""

    console.print(ANIMA_ASCII)
    console.print(SETUP_HEADER)
    console.print("This wizard will help you configure ANIMA AgentKit.\n")

    config = CLIConfig()

    if not quick:
        console.print(Panel(
            "[yellow]You'll need the following:[/yellow]\n\n"
            "1. SYNAPSE API Key (required) - Get at https://kaiko.ai\n"
            "2. Mistral AI or Nous Research API Key (required)\n"
            "3. Neo4j Database (optional but recommended)\n\n"
            "[dim]Press Ctrl+C to cancel at any time[/dim]",
            title="Requirements",
            border_style="cyan"
        ))

    # Step 1: SYNAPSE API Configuration (Required)
    console.print("\n[bold]Step 1: SYNAPSE API Configuration[/bold]")
    console.print("[dim]SYNAPSE provides emotion analysis capabilities[/dim]\n")

    synapse_key = config.get("SYNAPSE_API_KEY")
    if synapse_key and not quick:
        use_existing = Confirm.ask(f"Use existing SYNAPSE API key ({synapse_key[:20]}...)?", default=True)
        if not use_existing:
            synapse_key = None

    if not synapse_key:
        synapse_key = Prompt.ask(
            "Enter your SYNAPSE API key",
            password=True
        )
        if not synapse_key.startswith("sk_"):
            console.print("[yellow]⚠️  Warning: SYNAPSE API keys usually start with 'sk_'[/yellow]")

        config.set("SYNAPSE_API_KEY", synapse_key)
        console.print("[green]✓[/green] SYNAPSE API key saved")

    # Set SYNAPSE Base URL
    synapse_base_url = config.get("SYNAPSE_BASE_URL")
    if not synapse_base_url:
        # Default to production URL
        synapse_base_url = "https://api.kaikostudios.xyz"

    if not quick:
        synapse_base_url = Prompt.ask(
            "SYNAPSE API base URL",
            default=synapse_base_url
        )

    config.set("SYNAPSE_BASE_URL", synapse_base_url)
    console.print(f"[green]✓[/green] SYNAPSE base URL set to {synapse_base_url}")

    # Step 2: LLM Provider Selection
    console.print("\n[bold]Step 2: LLM Provider Selection[/bold]")
    console.print("[dim]Choose your Large Language Model provider[/dim]\n")

    if quick:
        llm_provider = "mistral"
    else:
        llm_provider = Prompt.ask(
            "Select LLM provider",
            choices=["mistral", "nous"],
            default=config.get("LLM_PROVIDER", "mistral")
        )

    config.set("LLM_PROVIDER", llm_provider)

    # Step 3: LLM API Key
    if llm_provider == "mistral":
        console.print("\n[bold]Step 3: Mistral AI Configuration[/bold]")
        console.print("[dim]Get your API key at https://console.mistral.ai[/dim]\n")

        mistral_key = config.get("MISTRAL_API_KEY")
        if mistral_key and not quick:
            use_existing = Confirm.ask(f"Use existing Mistral API key ({mistral_key[:20]}...)?", default=True)
            if not use_existing:
                mistral_key = None

        if not mistral_key:
            mistral_key = Prompt.ask("Enter your Mistral API key", password=True)
            config.set("MISTRAL_API_KEY", mistral_key)
            console.print("[green]✓[/green] Mistral API key saved")

        if not quick:
            mistral_model = Prompt.ask(
                "Mistral model",
                default=config.get("MISTRAL_MODEL", "mistral-large-latest")
            )
            config.set("MISTRAL_MODEL", mistral_model)

            mistral_temp = Prompt.ask(
                "Temperature (0.0-1.0)",
                default=config.get("MISTRAL_TEMPERATURE", "0.7")
            )
            config.set("MISTRAL_TEMPERATURE", mistral_temp)

    elif llm_provider == "nous":
        console.print("\n[bold]Step 3: Nous Research Configuration[/bold]")
        console.print("[dim]Get your API key at https://api.nous.com[/dim]\n")

        nous_key = config.get("NOUS_API_KEY")
        if nous_key and not quick:
            use_existing = Confirm.ask(f"Use existing Nous API key ({nous_key[:20]}...)?", default=True)
            if not use_existing:
                nous_key = None

        if not nous_key:
            nous_key = Prompt.ask("Enter your Nous API key", password=True)
            config.set("NOUS_API_KEY", nous_key)
            console.print("[green]✓[/green] Nous API key saved")

        if not quick:
            nous_model = Prompt.ask(
                "Nous model",
                default=config.get("NOUS_MODEL", "Hermes-4-70B")
            )
            config.set("NOUS_MODEL", nous_model)

    # Step 4: Neo4j Configuration
    console.print("\n[bold]Step 4: Neo4j Database Configuration[/bold]")
    console.print("[dim]Neo4j is required for memory, beliefs, and intelligence features[/dim]\n")

    if quick:
        setup_neo4j = False
    else:
        setup_neo4j = Confirm.ask("Configure Neo4j?", default=True)

    if setup_neo4j:
        # Check if Docker is available
        import subprocess
        docker_available = False
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, timeout=5)
            docker_available = result.returncode == 0
        except:
            pass

        # Offer Docker setup if available
        if docker_available:
            console.print("\n[cyan]Neo4j Setup Options:[/cyan]")
            console.print("  1. [green]Auto-setup with Docker[/green] (recommended)")
            console.print("  2. Use existing Neo4j instance\n")

            use_docker = Confirm.ask("Set up Neo4j with Docker?", default=True)

            if use_docker:
                console.print("\n[yellow]→[/yellow] Setting up Neo4j with Docker...\n")

                try:
                    # Run neo4j-setup via subprocess
                    result = subprocess.run(
                        ['make', 'neo4j-setup'],
                        capture_output=False,
                        timeout=120
                    )

                    if result.returncode == 0:
                        # Auto-configure with Docker defaults
                        config.set("NEO4J_URI", "bolt://localhost:7687")
                        config.set("NEO4J_USERNAME", "neo4j")
                        config.set("NEO4J_PASSWORD", "anima123")
                        console.print("\n[green]✓[/green] Neo4j Docker setup complete!")
                        console.print("[green]✓[/green] Neo4j configuration saved")
                    else:
                        console.print("\n[red]✗[/red] Docker setup failed. Please configure manually.")
                        use_docker = False

                except subprocess.TimeoutExpired:
                    console.print("\n[red]✗ ERROR [E010]:[/red] Docker setup timed out")
                    use_docker = False
                except Exception as e:
                    console.print(f"\n[red]✗ ERROR [E011]:[/red] {str(e)}")
                    use_docker = False

                if not use_docker:
                    console.print("[yellow]Falling back to manual configuration...[/yellow]\n")

            if not use_docker:
                # Manual configuration
                neo4j_uri = Prompt.ask(
                    "Neo4j URI",
                    default=config.get("NEO4J_URI", "bolt://localhost:7687")
                )
                config.set("NEO4J_URI", neo4j_uri)

                neo4j_user = Prompt.ask(
                    "Neo4j username",
                    default=config.get("NEO4J_USERNAME", "neo4j")
                )
                config.set("NEO4J_USERNAME", neo4j_user)

                neo4j_password = Prompt.ask(
                    "Neo4j password",
                    password=True,
                    default=config.get("NEO4J_PASSWORD", "anima123")
                )
                config.set("NEO4J_PASSWORD", neo4j_password)

                console.print("[green]✓[/green] Neo4j configuration saved")
        else:
            # Docker not available, manual config only
            console.print("[yellow]ℹ[/yellow]  Docker not found. Manual configuration required.")
            console.print("[dim]Install Docker for auto-setup: https://docs.docker.com/get-docker/[/dim]\n")

            neo4j_uri = Prompt.ask(
                "Neo4j URI",
                default=config.get("NEO4J_URI", "bolt://localhost:7687")
            )
            config.set("NEO4J_URI", neo4j_uri)

            neo4j_user = Prompt.ask(
                "Neo4j username",
                default=config.get("NEO4J_USERNAME", "neo4j")
            )
            config.set("NEO4J_USERNAME", neo4j_user)

            neo4j_password = Prompt.ask(
                "Neo4j password",
                password=True,
                default=config.get("NEO4J_PASSWORD", "anima123")
            )
            config.set("NEO4J_PASSWORD", neo4j_password)

            console.print("[green]✓[/green] Neo4j configuration saved")

    # Step 5: Intelligence Layer Configuration
    if not quick:
        console.print("\n[bold]Step 5: Intelligence Layer Configuration[/bold]")
        console.print("[dim]Advanced features: arousal tracking, wonder index, beliefs[/dim]\n")

        enable_intelligence = Confirm.ask(
            "Enable Intelligence Layer?",
            default=config.get("ANIMA_ENABLE_INTELLIGENCE", "true") == "true"
        )
        config.set("ANIMA_ENABLE_INTELLIGENCE", "true" if enable_intelligence else "false")

        if enable_intelligence:
            token_budget = Prompt.ask(
                "Max token budget for context (2000-15000)",
                default=config.get("ANIMA_TOKEN_BUDGET_MAX", "15000")
            )
            config.set("ANIMA_TOKEN_BUDGET_MAX", token_budget)

    # Step 6: S.I. Mode (Synthetic Intelligence / IGA)
    if not quick:
        console.print("\n[bold]Step 6: Synthetic Intelligence Mode (S.I.)[/bold]")
        console.print("[dim]Enable ANIMA's own interests, goals, beliefs, and autonomous exploration[/dim]\n")

        enable_si = Confirm.ask(
            "Enable S.I. Mode (IGA)?",
            default=config.get("ANIMA_SI_MODE", "false") == "true"
        )
        config.set("ANIMA_SI_MODE", "true" if enable_si else "false")

        if enable_si:
            console.print("\n[cyan]S.I. Mode Features:[/cyan]")
            console.print("  • ANIMA develops its own interests from cross-user patterns")
            console.print("  • Autonomous Deep-Xplore research sessions")
            console.print("  • Formation of S.I. beliefs and goals")
            console.print("  • Natural expression of interests in conversations\n")

            expression_prob = Prompt.ask(
                "Interest expression probability (0.0-1.0)",
                default=config.get("ANIMA_IGA_EXPRESSION_PROBABILITY", "0.3")
            )
            config.set("ANIMA_IGA_EXPRESSION_PROBABILITY", expression_prob)

            exploration_interval = Prompt.ask(
                "Exploration interval in hours (1-24)",
                default=config.get("ANIMA_IGA_EXPLORATION_INTERVAL", "6")
            )
            config.set("ANIMA_IGA_EXPLORATION_INTERVAL", exploration_interval)

            # Web Search API for Deep-Xplore
            console.print("\n[cyan]Web Search for Deep-Xplore:[/cyan]")
            console.print("[dim]Enables ANIMA to research interests autonomously[/dim]\n")

            configure_web_search = Confirm.ask("Configure web search API?", default=False)

            if configure_web_search:
                console.print("\n[cyan]Web Search Providers:[/cyan]")
                console.print("  • [green]Tavily[/green] - Best for AI research (recommended)")
                console.print("  • [yellow]Brave[/yellow] - General purpose web search")
                console.print("  • [blue]SerpAPI[/blue] - Google search results\n")

                tavily_key = Prompt.ask(
                    "Enter Tavily API key (or press Enter to skip)",
                    default=config.get("TAVILY_API_KEY", ""),
                    password=True
                )
                if tavily_key:
                    config.set("TAVILY_API_KEY", tavily_key)

                brave_key = Prompt.ask(
                    "Enter Brave API key (or press Enter to skip)",
                    default=config.get("BRAVE_API_KEY", ""),
                    password=True
                )
                if brave_key:
                    config.set("BRAVE_API_KEY", brave_key)

                serpapi_key = Prompt.ask(
                    "Enter SerpAPI key (or press Enter to skip)",
                    default=config.get("SERPAPI_KEY", ""),
                    password=True
                )
                if serpapi_key:
                    config.set("SERPAPI_KEY", serpapi_key)

                console.print("[green]✓[/green] Web search configuration saved")

            console.print("[green]✓[/green] S.I. Mode configuration saved")

    # Step 7: Vector Embeddings Configuration
    if not quick:
        console.print("\n[bold]Step 7: Vector Embeddings Configuration[/bold]")
        console.print("[dim]Configure semantic similarity search for memories, beliefs, and emotions[/dim]\n")

        configure_embeddings = Confirm.ask("Configure vector embeddings?", default=False)

        if configure_embeddings:
            console.print("\n[cyan]Embedding Providers:[/cyan]")
            console.print("  • [green]local[/green] - Deterministic embeddings (no API key required)")
            console.print("  • [yellow]openai[/yellow] - OpenAI text-embedding-3 (requires API key)")
            console.print("  • [blue]voyage[/blue] - Voyage AI embeddings (requires API key)\n")

            embedding_provider = Prompt.ask(
                "Select embedding provider",
                choices=["local", "openai", "voyage"],
                default=config.get("EMBEDDING_PROVIDER", "local")
            )
            config.set("EMBEDDING_PROVIDER", embedding_provider)

            if embedding_provider == "openai":
                openai_key = config.get("OPENAI_API_KEY")
                if not openai_key:
                    openai_key = Prompt.ask("Enter your OpenAI API key", password=True)
                    config.set("OPENAI_API_KEY", openai_key)

                embedding_model = Prompt.ask(
                    "Embedding model",
                    default=config.get("EMBEDDING_MODEL", "text-embedding-3-small")
                )
                config.set("EMBEDDING_MODEL", embedding_model)

                embedding_dim = Prompt.ask(
                    "Embedding dimension",
                    default=config.get("EMBEDDING_DIMENSION", "1536")
                )
                config.set("EMBEDDING_DIMENSION", embedding_dim)

            elif embedding_provider == "voyage":
                voyage_key = config.get("VOYAGE_API_KEY")
                if not voyage_key:
                    voyage_key = Prompt.ask("Enter your Voyage API key", password=True)
                    config.set("VOYAGE_API_KEY", voyage_key)

                config.set("EMBEDDING_MODEL", "voyage-2")
                config.set("EMBEDDING_DIMENSION", "1024")

            else:  # local
                embedding_dim = Prompt.ask(
                    "Local embedding dimension",
                    default=config.get("EMBEDDING_DIMENSION", "768")
                )
                config.set("EMBEDDING_DIMENSION", embedding_dim)

            console.print("[green]✓[/green] Embedding configuration saved")

    # Summary
    console.print("\n[bold green]✅ Setup Complete![/bold green]\n")
    console.print(Panel(
        f"[green]Configuration saved to:[/green] {config.env_file}\n\n"
        "[yellow]Next steps:[/yellow]\n\n"
        "1. [cyan]anima validate[/cyan] - Test your configuration\n"
        "2. [cyan]anima quickstart[/cyan] - Generate example code\n"
        "3. [cyan]anima doctor[/cyan] - Diagnose any issues\n\n"
        "[dim]Run 'anima --help' for more commands[/dim]",
        title="Setup Complete",
        border_style="green"
    ))


@cli.command()
@click.argument('key', required=False)
@click.argument('value', required=False)
def config(key: Optional[str], value: Optional[str]):
    """View or modify configuration"""

    cfg = CLIConfig()

    if key and value:
        # Set configuration value
        cfg.set(key, value)
        console.print(f"[green]✓[/green] Set {key} = {value}")

    elif key:
        # Get single value
        val = cfg.get(key)
        if val:
            # Mask sensitive values
            if "KEY" in key.upper() or "PASSWORD" in key.upper():
                display_val = val[:20] + "..." if len(val) > 20 else val
            else:
                display_val = val
            console.print(f"{key} = {display_val}")
        else:
            console.print(f"[yellow]{key} not set[/yellow]")

    else:
        # Display all configuration
        all_config = cfg.get_all()

        table = Table(title="ANIMA AgentKit Configuration", show_header=True)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="yellow")

        for key, value in all_config.items():
            # Mask sensitive values
            if value and ("KEY" in key or "PASSWORD" in key):
                display_val = value[:20] + "..." if len(value) > 20 else value
            else:
                display_val = value or "[dim]not set[/dim]"

            # Status
            if value:
                status = "✓ Set"
            elif key in ["SYNAPSE_API_KEY", "MISTRAL_API_KEY", "NOUS_API_KEY"]:
                status = "⚠️  Required"
            else:
                status = "○ Optional"

            table.add_row(key, display_val, status)

        console.print(table)
        console.print(f"\n[dim]Configuration file: {cfg.env_file}[/dim]")
        console.print("[dim]Run 'anima config KEY VALUE' to update values[/dim]")


@cli.command()
@click.option('--fix', is_flag=True, help='Attempt to fix issues automatically')
def validate(fix: bool):
    """Validate environment and test connections"""

    console.print(ANIMA_ASCII)
    console.print(VALIDATE_HEADER)

    cfg = CLIConfig()
    issues = []
    warnings = []

    # Check API Keys
    console.print("[bold]1. Checking API Keys[/bold]")

    synapse_key = cfg.get("SYNAPSE_API_KEY")
    if synapse_key:
        console.print("  [green]✓[/green] SYNAPSE_API_KEY is set")
    else:
        issues.append("SYNAPSE_API_KEY is not set (required)")
        console.print("  [red]✗[/red] SYNAPSE_API_KEY is missing")

    llm_provider = cfg.get("LLM_PROVIDER", "mistral")
    console.print(f"  [cyan]→[/cyan] LLM Provider: {llm_provider}")

    if llm_provider == "mistral":
        mistral_key = cfg.get("MISTRAL_API_KEY")
        if mistral_key:
            console.print("  [green]✓[/green] MISTRAL_API_KEY is set")
        else:
            issues.append("MISTRAL_API_KEY is not set (required for Mistral provider)")
            console.print("  [red]✗[/red] MISTRAL_API_KEY is missing")
    elif llm_provider == "nous":
        nous_key = cfg.get("NOUS_API_KEY")
        if nous_key:
            console.print("  [green]✓[/green] NOUS_API_KEY is set")
        else:
            issues.append("NOUS_API_KEY is not set (required for Nous provider)")
            console.print("  [red]✗[/red] NOUS_API_KEY is missing")

    # Check Neo4j
    console.print("\n[bold]2. Checking Neo4j Configuration[/bold]")

    neo4j_uri = cfg.get("NEO4J_URI")
    neo4j_password = cfg.get("NEO4J_PASSWORD")

    if neo4j_uri and neo4j_password:
        console.print("  [green]✓[/green] Neo4j credentials are set")
        console.print(f"  [cyan]→[/cyan] URI: {neo4j_uri}")

        # Test connection
        console.print("  [yellow]→[/yellow] Testing Neo4j connection...")
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(
                neo4j_uri,
                auth=(cfg.get("NEO4J_USERNAME", "neo4j"), neo4j_password)
            )
            driver.verify_connectivity()
            driver.close()
            console.print("  [green]✓[/green] Neo4j connection successful")
        except Exception as e:
            warnings.append(f"Neo4j connection failed: {e}")
            console.print(f"  [yellow]⚠️[/yellow]  Neo4j connection failed: {e}")
    else:
        warnings.append("Neo4j not configured (intelligence features will be limited)")
        console.print("  [yellow]⚠️[/yellow]  Neo4j not configured")

    # Check Intelligence Layer
    console.print("\n[bold]3. Checking Intelligence Layer[/bold]")

    enable_intelligence = cfg.get("ANIMA_ENABLE_INTELLIGENCE", "true") == "true"
    if enable_intelligence:
        console.print("  [green]✓[/green] Intelligence Layer is enabled")

        if not (neo4j_uri and neo4j_password):
            warnings.append("Intelligence Layer requires Neo4j for full functionality")
            console.print("  [yellow]⚠️[/yellow]  Neo4j required for Intelligence Layer")

        token_budget = cfg.get("ANIMA_TOKEN_BUDGET_MAX", "15000")
        console.print(f"  [cyan]→[/cyan] Token Budget: {token_budget}")
    else:
        console.print("  [yellow]○[/yellow] Intelligence Layer is disabled")

    # Check Python dependencies
    console.print("\n[bold]4. Checking Python Dependencies[/bold]")

    required_packages = [
        "anima_agentkit",
        "click",
        "rich",
        "python-dotenv",
        "loguru",
        "neo4j"
    ]

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            console.print(f"  [green]✓[/green] {package} installed")
        except ImportError:
            issues.append(f"Python package '{package}' is not installed")
            console.print(f"  [red]✗[/red] {package} not found")

    # Summary
    console.print("\n[bold]Summary[/bold]")

    if not issues and not warnings:
        console.print(Panel(
            "[green]✅ All checks passed![/green]\n\n"
            "Your ANIMA AgentKit setup is ready to use.\n\n"
            "Try: [cyan]anima quickstart[/cyan] to generate example code",
            title="Validation Complete",
            border_style="green"
        ))
    else:
        if issues:
            console.print("\n[bold red]Issues Found:[/bold red]")
            for issue in issues:
                console.print(f"  [red]✗[/red] {issue}")

        if warnings:
            console.print("\n[bold yellow]Warnings:[/bold yellow]")
            for warning in warnings:
                console.print(f"  [yellow]⚠️[/yellow]  {warning}")

        console.print("\n[yellow]Run 'anima setup' to configure missing settings[/yellow]")

        if fix and issues:
            console.print("\n[cyan]Attempting to fix issues...[/cyan]")
            console.print("[yellow]Auto-fix not yet implemented. Please run 'anima setup'[/yellow]")


@cli.command()
@click.option('--output', '-o', default='quickstart.py', help='Output file name')
@click.option('--template', '-t', type=click.Choice(['basic', 'intelligent', 'full']), default='intelligent', help='Template type')
def quickstart(output: str, template: str):
    """Generate quickstart code examples"""

    console.print(ANIMA_ASCII)
    console.print(QUICKSTART_HEADER)
    console.print(f"[dim]Generating [cyan]{template}[/cyan] template...[/dim]\n")

    cfg = CLIConfig()

    if template == 'basic':
        code = _generate_basic_template(cfg)
    elif template == 'intelligent':
        code = _generate_intelligent_template(cfg)
    else:  # full
        code = _generate_full_template(cfg)

    # Write to file
    output_path = Path(output)
    output_path.write_text(code)

    console.print(f"[green]✓[/green] Generated {output_path}")
    console.print(f"\n[bold]Next steps:[/bold]")
    console.print(f"1. Review the generated code in {output_path}")
    console.print(f"2. Run: [cyan]python {output_path}[/cyan]")
    console.print(f"3. Customize for your use case\n")


@cli.command()
def doctor():
    """Diagnose common issues and provide solutions"""

    console.print(ANIMA_ASCII)
    console.print(DOCTOR_HEADER)
    console.print("[dim]Checking for common issues...[/dim]\n")

    cfg = CLIConfig()
    found_issues = False

    # Check 1: Missing API keys
    if not cfg.get("SYNAPSE_API_KEY"):
        found_issues = True
        console.print(Panel(
            "[red]Issue:[/red] SYNAPSE_API_KEY is not set\n\n"
            "[yellow]Solution:[/yellow]\n"
            "1. Get an API key from https://kaiko.ai\n"
            "2. Run: [cyan]anima config SYNAPSE_API_KEY your_key[/cyan]\n"
            "   OR\n"
            "   Run: [cyan]anima setup[/cyan]",
            title="Missing SYNAPSE API Key",
            border_style="red"
        ))

    # Check 2: No LLM configured
    llm_provider = cfg.get("LLM_PROVIDER", "mistral")
    llm_key = cfg.get(f"{llm_provider.upper()}_API_KEY")

    if not llm_key:
        found_issues = True
        console.print(Panel(
            f"[red]Issue:[/red] {llm_provider.upper()}_API_KEY is not set\n\n"
            "[yellow]Solution:[/yellow]\n"
            "1. Get an API key from the provider\n"
            f"2. Run: [cyan]anima config {llm_provider.upper()}_API_KEY your_key[/cyan]\n"
            "   OR\n"
            "   Switch provider: [cyan]anima config LLM_PROVIDER mistral[/cyan]",
            title=f"Missing {llm_provider.capitalize()} API Key",
            border_style="red"
        ))

    # Check 3: Neo4j connection issues
    neo4j_uri = cfg.get("NEO4J_URI")
    neo4j_password = cfg.get("NEO4J_PASSWORD")

    if neo4j_uri and neo4j_password:
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(
                neo4j_uri,
                auth=(cfg.get("NEO4J_USERNAME", "neo4j"), neo4j_password)
            )
            driver.verify_connectivity()
            driver.close()
        except Exception as e:
            found_issues = True
            console.print(Panel(
                f"[red]Issue:[/red] Cannot connect to Neo4j\n\n"
                f"[red]Error:[/red] {e}\n\n"
                "[yellow]Solutions:[/yellow]\n"
                "1. Ensure Neo4j is running: [cyan]docker-compose up -d neo4j[/cyan]\n"
                "2. Check URI: [cyan]anima config NEO4J_URI bolt://localhost:7687[/cyan]\n"
                "3. Verify credentials: [cyan]anima config NEO4J_PASSWORD your_password[/cyan]\n"
                "4. Install Neo4j: https://neo4j.com/download/",
                title="Neo4j Connection Failed",
                border_style="yellow"
            ))

    # Check 4: Import errors
    try:
        import anima_agentkit
    except ImportError:
        found_issues = True
        console.print(Panel(
            "[red]Issue:[/red] anima_agentkit package not found\n\n"
            "[yellow]Solution:[/yellow]\n"
            "Install the package:\n"
            "[cyan]pip install -e .[/cyan]",
            title="Package Not Installed",
            border_style="red"
        ))

    if not found_issues:
        console.print(Panel(
            "[green]✅ No issues found![/green]\n\n"
            "Your ANIMA AgentKit setup looks healthy.\n\n"
            "If you're experiencing problems:\n"
            "1. Check the logs for error messages\n"
            "2. Run: [cyan]anima validate[/cyan]\n"
            "3. Open an issue: https://github.com/animaai/anima-agentkit/issues",
            title="Health Check Complete",
            border_style="green"
        ))


def _generate_basic_template(cfg: CLIConfig) -> str:
    """Generate basic usage template"""
    return f'''"""
ANIMA AgentKit - Basic Usage Example

Auto-generated by: anima quickstart --template basic
"""

import asyncio
from anima_agentkit import NeuralAgent


async def main():
    """Basic ANIMA agent example"""

    # Initialize agent
    agent = NeuralAgent(
        synapse_api_key="{cfg.get("SYNAPSE_API_KEY", "your_synapse_key")}",
        mistral_api_key="{cfg.get("MISTRAL_API_KEY", "your_mistral_key")}",
        enable_neo4j=False  # Disable Neo4j for basic usage
    )

    # Chat with the agent
    response = await agent.chat(
        message="Hello! How are you?",
        user_id="user_123"
    )

    # Display response
    print("Agent:", response["content"])

    # Close agent
    await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
'''


def _generate_intelligent_template(cfg: CLIConfig) -> str:
    """Generate intelligent agent template"""
    return f'''"""
ANIMA AgentKit - Intelligent Agent Example

Auto-generated by: anima quickstart --template intelligent

This example demonstrates the intelligence layer:
- Clinical arousal tracking (10-stage model)
- Wonder index calculation (epistemic significance)
- Breakthrough detection (transformational moments)
- Intelligent context composition (2k-15k tokens)
- High-resistance belief formation
"""

import asyncio
from anima_agentkit import NeuralAgent


async def main():
    """Intelligent ANIMA agent with full intelligence layer"""

    # Initialize agent with intelligence enabled
    agent = NeuralAgent(
        synapse_api_key="{cfg.get("SYNAPSE_API_KEY", "your_synapse_key")}",
        mistral_api_key="{cfg.get("MISTRAL_API_KEY", "your_mistral_key")}",
        enable_neo4j=True,
        neo4j_uri="{cfg.get("NEO4J_URI", "bolt://localhost:7687")}",
        neo4j_auth=("{cfg.get("NEO4J_USERNAME", "neo4j")}", "{cfg.get("NEO4J_PASSWORD", "password")}"),
        enable_intelligence=True,  # Enable intelligence layer
        intelligence_token_budget_max={cfg.get("ANIMA_TOKEN_BUDGET_MAX", "15000")}
    )

    print("🧠 ANIMA AgentKit - Intelligent Agent")
    print("=" * 50)

    # Example 1: Simple conversation
    print("\\n📝 Example 1: Simple Conversation")
    response = await agent.chat(
        message="Hello! I'm learning about quantum physics.",
        user_id="user_123",
        context_id="session_1"
    )

    print(f"Agent: {{response['content'].get('text', 'No response')}}")

    # Example 2: High-wonder conversation (triggers intelligent context)
    print("\\n🔮 Example 2: High-Wonder Conversation")
    response = await agent.chat(
        message="Wait, so particles can be in two places at once? That completely changes my understanding of reality!",
        user_id="user_123",
        context_id="session_1"
    )

    print(f"Agent: {{response['content'].get('text', 'No response')}}")

    # Check intelligence metadata
    if "metadata" in response:
        metadata = response["metadata"]
        print(f"\\n📊 Intelligence Metadata:")
        print(f"  - Arousal: {{metadata.get('arousal', 'N/A')}}")
        print(f"  - Wonder Index: {{metadata.get('wonder_index', 'N/A')}}")
        print(f"  - Breakthrough: {{metadata.get('breakthrough', False)}}")

    # Example 3: Belief statement (high-resistance formation)
    print("\\n🌟 Example 3: Belief Formation")
    response = await agent.chat(
        message="I believe that continuous learning is the key to a fulfilling life.",
        user_id="user_123",
        context_id="session_1"
    )

    print(f"Agent: {{response['content'].get('text', 'No response')}}")

    # Check if belief was formed
    if "beliefs" in response.get("metadata", {{}}):
        beliefs = response["metadata"]["beliefs"]
        print(f"\\n✨ Beliefs Formed: {{len(beliefs)}}")
        for belief in beliefs:
            print(f"  - {{belief.get('statement', 'Unknown')}}")
            print(f"    Validation: {{belief.get('validation_score', 0):.2f}}")
            print(f"    Path: {{belief.get('formation_path', 'Unknown')}}")

    # Close agent
    await agent.close()
    print("\\n✅ Session complete")


if __name__ == "__main__":
    asyncio.run(main())
'''


def _generate_full_template(cfg: CLIConfig) -> str:
    """Generate full featured template"""
    return f'''"""
ANIMA AgentKit - Full Integration Example

Auto-generated by: anima quickstart --template full

This example demonstrates all ANIMA AgentKit features:
- Intelligence layer (arousal, wonder, breakthrough)
- Memory system (GraphRAG with wonder gating)
- Belief system (high-resistance formation)
- Goal system (psycho-aware planning)
- Intelligent context composition
"""

import asyncio
from anima_agentkit import NeuralAgent


async def main():
    """Full-featured ANIMA agent"""

    # Initialize agent with all features
    agent = NeuralAgent(
        synapse_api_key="{cfg.get("SYNAPSE_API_KEY", "your_synapse_key")}",
        mistral_api_key="{cfg.get("MISTRAL_API_KEY", "your_mistral_key")}",
        llm_provider="{cfg.get("LLM_PROVIDER", "mistral")}",
        enable_neo4j=True,
        neo4j_uri="{cfg.get("NEO4J_URI", "bolt://localhost:7687")}",
        neo4j_auth=("{cfg.get("NEO4J_USERNAME", "neo4j")}", "{cfg.get("NEO4J_PASSWORD", "password")}"),
        enable_intelligence=True,
        intelligence_token_budget_max={cfg.get("ANIMA_TOKEN_BUDGET_MAX", "15000")}
    )

    print("🧠 ANIMA AgentKit - Full Integration Demo")
    print("=" * 60)

    user_id = "demo_user"
    context_id = "demo_session"

    # Scenario 1: Learning conversation with high wonder
    print("\\n📚 Scenario 1: Learning Conversation")
    print("-" * 60)

    response1 = await agent.chat(
        message="I've been studying machine learning and I'm fascinated by how neural networks learn patterns!",
        user_id=user_id,
        context_id=context_id
    )

    print(f"User: I've been studying machine learning...")
    print(f"Agent: {{response1['content'].get('text', 'No response')[:200]}}...")

    # Scenario 2: Goal setting with emotional context
    print("\\n🎯 Scenario 2: Goal Setting")
    print("-" * 60)

    response2 = await agent.chat(
        message="I want to become proficient in AI development within the next 6 months. Can you help me create a learning plan?",
        user_id=user_id,
        context_id=context_id,
        goal_mode=True  # Enable goal detection
    )

    print(f"User: I want to become proficient in AI...")
    print(f"Agent: {{response2['content'].get('text', 'No response')[:200]}}...")

    # Check if goal was created
    if "goal_card" in response2:
        goal = response2["goal_card"]
        print(f"\\n🎯 Goal Detected:")
        print(f"  Title: {{goal.get('title', 'Unknown')}}")
        print(f"  Priority: {{goal.get('priority', 'Unknown')}}")

    # Scenario 3: Emotional support
    print("\\n💙 Scenario 3: Emotional Support")
    print("-" * 60)

    response3 = await agent.chat(
        message="I'm feeling a bit overwhelmed with all the concepts. Sometimes I wonder if I'm making progress.",
        user_id=user_id,
        context_id=context_id
    )

    print(f"User: I'm feeling a bit overwhelmed...")
    print(f"Agent: {{response3['content'].get('text', 'No response')[:200]}}...")

    # Display intelligence metrics
    if "metadata" in response3:
        meta = response3["metadata"]
        print(f"\\n📊 Intelligence Metrics:")
        print(f"  Arousal: {{meta.get('arousal', 'N/A')}}")
        print(f"  Wonder: {{meta.get('wonder_index', 'N/A')}}")
        print(f"  Context Quality: {{meta.get('context_quality', 'N/A')}}")

    # Scenario 4: Breakthrough moment
    print("\\n💫 Scenario 4: Breakthrough Moment")
    print("-" * 60)

    response4 = await agent.chat(
        message="Oh wow! I just realized that backpropagation is like teaching by showing what went wrong. That's genius!",
        user_id=user_id,
        context_id=context_id
    )

    print(f"User: Oh wow! I just realized...")
    print(f"Agent: {{response4['content'].get('text', 'No response')[:200]}}...")

    # Scenario 5: Belief statement
    print("\\n🌟 Scenario 5: Core Belief Formation")
    print("-" * 60)

    response5 = await agent.chat(
        message="I believe that understanding the fundamentals deeply is more important than memorizing frameworks.",
        user_id=user_id,
        context_id=context_id
    )

    print(f"User: I believe that understanding...")
    print(f"Agent: {{response5['content'].get('text', 'No response')[:200]}}...")

    # Check beliefs formed
    if "beliefs" in response5.get("metadata", {{}}):
        beliefs = response5["metadata"]["beliefs"]
        print(f"\\n✨ Beliefs Formed During Session: {{len(beliefs)}}")
        for belief in beliefs:
            print(f"  - {{belief.get('statement', 'Unknown')}}")
            print(f"    Formation Path: {{belief.get('formation_path', 'Unknown')}}")
            print(f"    Validation Score: {{belief.get('validation_score', 0):.2f}}")
            print(f"    Strength: {{belief.get('strength', 0):.2f}}")

    # Get session insights
    print("\\n📈 Session Summary")
    print("-" * 60)

    # Get user's goals
    goals = await agent.get_goals(user_id=user_id, context_id=context_id)
    print(f"Active Goals: {{len(goals)}}")

    # Close agent
    await agent.close()
    print("\\n✅ Demo complete!")
    print("\\nNext steps:")
    print("1. Review the generated responses")
    print("2. Check your Neo4j database for stored data")
    print("3. Customize this code for your use case")


if __name__ == "__main__":
    asyncio.run(main())
'''


@cli.command()
@click.option('--user-id', '-u', default='cli_user', help='User ID for chat session')
@click.option('--context-id', '-c', default=None, help='Context ID to resume conversation')
@click.option('--agent', '-a', default='default', help='Agent profile to use')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging to see full pipeline')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode with detailed logs')
def chat(user_id: str, context_id: Optional[str], agent: str, verbose: bool, debug: bool):
    """Interactive chat with your ANIMA agent"""

    # Set logging mode based on flags
    if verbose or debug:
        # Enable verbose/debug logging - show full pipeline
        os.environ["ANIMA_CHAT_MODE"] = "0"
        os.environ["ANIMA_DEBUG"] = "1"
        console.print("[yellow]🔧 Debug mode enabled - showing full pipeline logs[/yellow]\n")
    else:
        # CRITICAL: Set chat mode BEFORE any imports to suppress verbose logging
        os.environ["ANIMA_CHAT_MODE"] = "1"

    # Reconfigure logging to apply chat mode
    from anima_agentkit.logging_config import configure_logging
    configure_logging()

    console.print(ANIMA_ASCII)
    console.print("""
[bold cyan]
╔════════════════════════════════════════════════════════╗
║                                                        ║
║          💬  ANIMA INTERACTIVE CHAT  💬               ║
║                                                        ║
║          Talk with Your Intelligent Agent              ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
[/bold cyan]
""")

    cfg = CLIConfig()

    # Load agent profile - check agents/ directory first, then ~/.anima/profiles/
    from pathlib import Path
    agent_path = None
    agents_dir = Path.cwd() / "agents" / agent
    if agents_dir.exists() and (agents_dir / ".env").exists():
        agent_path = str(agents_dir)
        console.print(f"[green]✓[/green] Found agent directory: {agents_dir}")

    agent_profile = _load_agent_profile(agent)
    if not agent_profile and not agent_path:
        console.print(f"[red]✗[/red] Agent profile '{agent}' not found. Using default configuration.")
        agent_profile = {}

    console.print(f"[dim]Agent Profile: {agent}[/dim]")
    console.print(f"[dim]User ID: {user_id}[/dim]")
    if context_id:
        console.print(f"[dim]Resuming context: {context_id}[/dim]")
    console.print("\n[yellow]Commands:[/yellow]")
    console.print("  /exit or /quit - Exit chat")
    console.print("  /history - Show conversation history")
    console.print("  /save - Save current conversation")
    console.print("  /clear - Clear context (start fresh)")
    console.print("  /stats - Show session statistics")
    console.print("")

    # Run async chat loop
    asyncio.run(_chat_loop(cfg, user_id, context_id, agent_profile, agent_path))


async def _chat_loop(cfg: CLIConfig, user_id: str, context_id: Optional[str], agent_profile: Dict[str, Any], agent_path: Optional[str] = None):
    """Async chat loop with the agent"""

    try:
        # Initialize agent
        console.print("[dim]Initializing agent...[/dim]")

        from anima_agentkit import NeuralAgent

        # Build agent config from profile and environment
        agent_config = {
            "agent_path": agent_path,  # Load agent-specific configs from directory
            "synapse_api_key": agent_profile.get("synapse_api_key") or cfg.get("SYNAPSE_API_KEY"),
            "enable_neo4j": agent_profile.get("enable_neo4j", cfg.get("NEO4J_URI") is not None),
            "enable_intelligence": agent_profile.get("enable_intelligence", cfg.get("ANIMA_ENABLE_INTELLIGENCE", "true").lower() == "true"),
        }

        # Check S.I. mode status
        si_mode_enabled = cfg.get("ANIMA_SI_MODE", "false").lower() == "true"

        # Add LLM configuration
        llm_provider = agent_profile.get("llm_provider") or cfg.get("LLM_PROVIDER", "mistral")
        if llm_provider == "mistral":
            agent_config["mistral_api_key"] = agent_profile.get("mistral_api_key") or cfg.get("MISTRAL_API_KEY")
            agent_config["mistral_model"] = agent_profile.get("mistral_model") or cfg.get("MISTRAL_MODEL", "mistral-large-latest")
        else:
            agent_config["nous_api_key"] = agent_profile.get("nous_api_key") or cfg.get("NOUS_API_KEY")
            agent_config["nous_model"] = agent_profile.get("nous_model") or cfg.get("NOUS_MODEL", "Hermes-4-70B")

        # Add Neo4j config if enabled
        if agent_config["enable_neo4j"]:
            agent_config["neo4j_uri"] = agent_profile.get("neo4j_uri") or cfg.get("NEO4J_URI", "bolt://localhost:7687")
            neo4j_username = agent_profile.get("neo4j_username") or cfg.get("NEO4J_USERNAME", "neo4j")
            neo4j_password = agent_profile.get("neo4j_password") or cfg.get("NEO4J_PASSWORD")
            agent_config["neo4j_auth"] = (neo4j_username, neo4j_password)

        # Add S.I. mode config
        if si_mode_enabled:
            agent_config["enable_si_mode"] = True
            # Get expression probability (0.0-1.0)
            expr_prob = cfg.get("ANIMA_IGA_EXPRESSION_PROBABILITY", "0.3")
            try:
                agent_config["si_expression_probability"] = float(expr_prob)
            except ValueError:
                agent_config["si_expression_probability"] = 0.3

            # Get exploration interval (hours)
            explore_interval = cfg.get("ANIMA_IGA_EXPLORATION_INTERVAL", "6")
            try:
                agent_config["si_exploration_interval"] = int(explore_interval)
            except ValueError:
                agent_config["si_exploration_interval"] = 6

        agent = NeuralAgent(**agent_config)

        # Display initialization status
        init_status = "[green]✓[/green] Agent initialized"
        if si_mode_enabled:
            init_status += " [cyan](S.I. Mode Active)[/cyan]"
        console.print(init_status + "\n")

        # Display S.I. mode info if enabled
        if si_mode_enabled:
            console.print(Panel(
                "[cyan]Synthetic Intelligence Mode Active[/cyan]\n\n"
                "ANIMA will:\n"
                "  • Develop and express its own interests\n"
                "  • Form beliefs from cross-user patterns\n"
                "  • Pursue autonomous exploration goals\n\n"
                "[dim]Toggle with: ANIMA_SI_MODE=false[/dim]",
                title="🧠 S.I. Mode",
                border_style="cyan"
            ))

        # Track session stats
        message_count = 0
        total_arousal = 0
        total_wonder = 0
        breakthroughs = []
        si_expressions = 0  # Track S.I. interest expressions

        # Chat loop
        while True:
            try:
                # Get user input
                user_message = Prompt.ask("[bold cyan]You[/bold cyan]")

                if not user_message:
                    continue

                # Handle commands
                if user_message.startswith('/'):
                    command = user_message.lower().strip()

                    if command in ['/exit', '/quit']:
                        console.print("\n[yellow]Exiting chat...[/yellow]")
                        break

                    elif command == '/history':
                        console.print("\n[cyan]📜 Conversation History[/cyan]")
                        # TODO: Implement history retrieval from Neo4j
                        console.print("[dim]History feature coming soon...[/dim]\n")
                        continue

                    elif command == '/save':
                        console.print("\n[green]✓[/green] Conversation auto-saved to Neo4j\n")
                        continue

                    elif command == '/clear':
                        context_id = None
                        console.print("\n[yellow]Context cleared. Starting fresh conversation.[/yellow]\n")
                        continue

                    elif command == '/stats':
                        console.print("\n[cyan]📊 Session Statistics[/cyan]")
                        console.print(f"Messages: {message_count}")
                        if message_count > 0:
                            console.print(f"Avg Arousal: {total_arousal / message_count:.2f}")
                            console.print(f"Avg Wonder: {total_wonder / message_count:.2f}")
                            console.print(f"Breakthroughs: {len(breakthroughs)}")
                        if si_mode_enabled:
                            console.print(f"S.I. Interest Expressions: {si_expressions}")
                        console.print("")
                        continue

                    elif command == '/si':
                        if si_mode_enabled:
                            console.print("\n[cyan]🧠 S.I. Mode Status[/cyan]")
                            console.print(f"Mode: [green]Active[/green]")
                            console.print(f"Interest Expressions: {si_expressions}")
                            console.print(f"Expression Probability: {cfg.get('ANIMA_IGA_EXPRESSION_PROBABILITY', '0.3')}")
                            console.print(f"Exploration Interval: {cfg.get('ANIMA_IGA_EXPLORATION_INTERVAL', '6')}h")

                            # Get live S.I. state from agent
                            try:
                                si_state = await agent.get_si_state()
                                if si_state.get('enabled', True) and not si_state.get('error'):
                                    curiosity = si_state.get('curiosity', {})
                                    metrics = si_state.get('metrics', {})
                                    interests = si_state.get('top_interests', [])

                                    console.print(f"\n[bold]Curiosity Metrics:[/bold]")
                                    console.print(f"  Overall: {curiosity.get('overall', 0):.2f}")
                                    console.print(f"  Expression Readiness: {curiosity.get('expression_readiness', 0):.2f}")
                                    console.print(f"  Total Interests: {metrics.get('total_interests', 0)}")

                                    if interests:
                                        console.print(f"\n[bold]Top Interests:[/bold]")
                                        for i, interest in enumerate(interests[:5], 1):
                                            console.print(f"  {i}. {interest.get('topic', 'Unknown')} (strength: {interest.get('strength', 0):.2f})")
                            except Exception as e:
                                console.print(f"[dim]Could not fetch live state: {e}[/dim]")
                        else:
                            console.print("\n[yellow]S.I. Mode is disabled[/yellow]")
                            console.print("[dim]Enable with: anima setup (Step 6)[/dim]")
                        console.print("")
                        continue

                    else:
                        console.print(f"[red]Unknown command: {command}[/red]\n")
                        continue

                # Send message to agent
                response = await agent.chat(
                    message=user_message,
                    user_id=user_id,
                    context_id=context_id
                )

                # Update context_id if new
                if not context_id and response.get("context_id"):
                    context_id = response["context_id"]

                # Extract and display agent response text (clean format)
                content = response.get('content', {})

                # Handle both structured and plain text responses
                if isinstance(content, dict):
                    # Structured response with content_blocks
                    content_blocks = content.get('content_blocks', [])
                    if content_blocks:
                        agent_text = ""
                        for block in content_blocks:
                            if block.get('type') == 'paragraph':
                                segments = block.get('content', {}).get('segments', [])
                                for segment in segments:
                                    agent_text += segment.get('text', '')

                        if not agent_text:
                            agent_text = str(content)
                    else:
                        # Try to get text from other fields
                        agent_text = content.get('text', str(content))
                elif isinstance(content, str):
                    agent_text = content
                else:
                    agent_text = str(content)

                console.print(f"\n[bold green]Agent[/bold green]: {agent_text}\n")

                # Display reasoning chain if available
                reasoning = response.get('reasoning', '') or response.get('metadata', {}).get('reasoning', '')
                if reasoning and len(reasoning) > 50:
                    console.print(f"[dim]💭 Internal Reasoning:[/dim]")
                    console.print(f"[dim]{reasoning[:300]}{'...' if len(reasoning) > 300 else ''}[/dim]\n")

                # Display minimal intelligence metadata (clean format)
                metadata = response.get("metadata", {})

                # Build emotion and intelligence metrics summary
                sentiment_parts = []

                # Get emotions from response (check both top-level and metadata)
                emotions_data = response.get("emotions", {}) or metadata.get("emotions", {})

                if emotions_data:
                    # Get primary emotion category
                    category = emotions_data.get("category", "neutral")
                    intensity = emotions_data.get("intensity", 0.5)
                    sentiment_parts.append(f"Emotion: {category.capitalize()} ({intensity:.2f})")

                # Arousal level (from Intelligence Layer)
                if metadata.get("arousal"):
                    arousal_val = metadata["arousal"]
                    if isinstance(arousal_val, dict):
                        stage = arousal_val.get("stage", "baseline")
                        total_arousal += arousal_val.get("level", 0.5)
                    else:
                        stage = "baseline"
                        total_arousal += 0.5
                    sentiment_parts.append(f"Arousal: {stage.capitalize()}")

                # Wonder index (from Intelligence Layer)
                if metadata.get("wonder_index"):
                    wonder_val = metadata["wonder_index"]
                    if isinstance(wonder_val, dict):
                        score = wonder_val.get("score", 0.0)
                    else:
                        score = float(wonder_val) if wonder_val else 0.0

                    if score > 0.3:  # Only show if significant
                        sentiment_parts.append(f"Wonder: {score:.2f}")
                    total_wonder += score

                # Emotional trend (if tracked across messages)
                if metadata.get("emotional_trend"):
                    trend = metadata["emotional_trend"]
                    sentiment_parts.append(f"Trend: {trend}")

                # Show sentiment analysis in one compact line
                if sentiment_parts:
                    console.print(f"[dim]📊 Metrics: {' | '.join(sentiment_parts)}[/dim]")

                # Show tracked goals (if any)
                goal_card = response.get("goal_card")
                if goal_card:
                    goal_title = goal_card.get("data", {}).get("title", "Unnamed Goal")
                    goal_priority = goal_card.get("data", {}).get("priority", "medium")
                    console.print(f"[cyan]🎯 Goal Detected: {goal_title} (Priority: {goal_priority})[/cyan]")

                # Show active goals from metadata
                active_goals = metadata.get("active_goals", [])
                if active_goals and len(active_goals) > 0:
                    console.print(f"[cyan]📋 Active Goals ({len(active_goals)}):[/cyan]")
                    for goal in active_goals[:3]:  # Show max 3 goals
                        if isinstance(goal, dict):
                            goal_name = goal.get("title", goal.get("name", "Unknown goal"))
                            status = goal.get("status", "active")
                            console.print(f"   • {goal_name} ({status})")
                        else:
                            console.print(f"   • {goal}")

                # Show breakthrough (important event)
                breakthrough = metadata.get("breakthrough")
                if breakthrough:
                    if isinstance(breakthrough, dict) and breakthrough.get("is_breakthrough"):
                        bt_type = breakthrough.get("type", "Unknown")
                        console.print(f"[bold yellow]✨ Breakthrough: {bt_type}[/bold yellow]")
                        breakthroughs.append(bt_type)

                # Show newly formed beliefs
                beliefs = metadata.get("beliefs", metadata.get("new_beliefs", []))
                if beliefs and len(beliefs) > 0:
                    belief_statement = beliefs[0].get('statement', 'Unknown') if isinstance(beliefs[0], dict) else str(beliefs[0])
                    console.print(f"[bold cyan]💎 Belief Formed: {belief_statement}[/bold cyan]")

                # Show S.I. interests if in S.I. mode
                if si_mode_enabled:
                    si_interests = metadata.get("si_interests", metadata.get("anima_interests", []))
                    if si_interests and len(si_interests) > 0:
                        console.print(f"[cyan]🧠 S.I. Interests ({len(si_interests)}):[/cyan]")
                        for interest in si_interests[:3]:  # Show max 3 interests
                            if isinstance(interest, dict):
                                name = interest.get("name", interest.get("topic", "Unknown"))
                                strength = interest.get("strength", 0.5)
                                console.print(f"   • {name} (strength: {strength:.2f})")
                            else:
                                console.print(f"   • {interest}")

                    # Show S.I. interest expression if it occurred
                    si_expression = metadata.get("si_expression", metadata.get("interest_expression"))
                    if si_expression:
                        si_expressions += 1
                        if isinstance(si_expression, dict):
                            expression_text = si_expression.get("expression", si_expression.get("text", ""))
                            interest_name = si_expression.get("interest", {}).get("name", "")
                            if expression_text:
                                console.print(f"[bold magenta]✨ S.I. Expression[/bold magenta]")
                                if interest_name:
                                    console.print(f"   [dim]Interest: {interest_name}[/dim]")
                        elif isinstance(si_expression, str):
                            console.print(f"[bold magenta]✨ S.I. Expression: {si_expression[:100]}{'...' if len(si_expression) > 100 else ''}[/bold magenta]")

                console.print("")
                message_count += 1

            except KeyboardInterrupt:
                console.print("\n\n[yellow]Interrupted. Use /exit to quit properly.[/yellow]\n")
                continue
            except Exception as e:
                # Clean error display with error codes
                error_msg = str(e)
                error_code = "E999"  # Generic error

                # Map specific errors to error codes
                if "401" in error_msg or "Unauthorized" in error_msg:
                    error_code = "E012"  # Missing/Invalid API key
                    error_msg = "API authentication failed. Check your API key in .env"
                elif "Neo4j" in error_msg or "bolt://" in error_msg:
                    error_code = "E021"  # Neo4j connection error
                    error_msg = "Neo4j connection failed. Run 'make neo4j-status'"
                elif "authentication" in error_msg.lower() and "neo4j" in error_msg.lower():
                    error_code = "E022"  # Neo4j authentication
                    error_msg = "Neo4j authentication failed. Check credentials in .env"
                elif "synapse" in error_msg.lower() or "billing" in error_msg.lower():
                    error_code = "E023"  # SYNAPSE API error
                    error_msg = "SYNAPSE API error. Check API key or billing status."
                elif "timeout" in error_msg.lower():
                    error_code = "E024"  # Timeout error
                    error_msg = "Request timeout. Please try again."

                console.print(f"\n[red]✗ ERROR [{error_code}]:[/red] {error_msg}\n")
                console.print(f"[dim]Full error logged to .logs/errors_*.log[/dim]\n")

                # Log full error to file
                from loguru import logger
                logger.bind(code=error_code).error(f"Chat error: {str(e)}", exc_info=True)
                continue

        # Close agent
        await agent.close()

        # Show final stats
        console.print("\n[cyan]📊 Final Session Statistics[/cyan]")
        console.print(f"Total Messages: {message_count}")
        if message_count > 0:
            console.print(f"Average Arousal: {total_arousal / message_count:.2f}")
            console.print(f"Average Wonder: {total_wonder / message_count:.2f}")
            console.print(f"Breakthroughs: {len(breakthroughs)}")
        if si_mode_enabled:
            console.print(f"S.I. Interest Expressions: {si_expressions}")
        console.print("\n[green]✓[/green] Chat session ended\n")

    except Exception as e:
        # Clean error display with error codes
        error_msg = str(e)
        error_code = "E031"  # Agent initialization error

        # Map specific errors
        if "neo4j_storage" in error_msg or "unexpected keyword argument" in error_msg:
            error_code = "E033"  # Intelligence layer error
            error_msg = "Intelligence Layer initialization failed. System misconfiguration."
        elif "401" in error_msg or "Unauthorized" in error_msg:
            error_code = "E012"  # Missing/Invalid API key
            error_msg = "API authentication failed. Check your API key in .env"
        elif "Neo4j" in error_msg and "connect" in error_msg.lower():
            error_code = "E021"  # Neo4j connection error
            error_msg = "Neo4j connection failed. Run 'make neo4j-status'"
        elif "beliefs_api" in error_msg or "No module named" in error_msg:
            error_code = "E033"  # Intelligence layer error
            error_msg = "Module import error. System misconfiguration detected."

        console.print(f"\n[red]✗ ERROR [{error_code}]:[/red] Failed to initialize agent")
        console.print(f"[red]→[/red] {error_msg}")
        console.print(f"\n[dim]Full error logged to .logs/errors_*.log[/dim]")
        console.print("[yellow]→ Run 'make health-check' to diagnose issues[/yellow]\n")

        # Log full error to file
        from loguru import logger
        logger.bind(code=error_code).error(f"Agent initialization failed: {str(e)}", exc_info=True)


@cli.command()
@click.option('--format', '-f', type=click.Choice(['table', 'json']), default='table', help='Output format')
def agents(format: str):
    """List and manage agent profiles"""

    console.print(ANIMA_ASCII)
    console.print("""
[bold cyan]
╔════════════════════════════════════════════════════════╗
║                                                        ║
║         🤖  AGENT PROFILE MANAGER  🤖                 ║
║                                                        ║
║          Manage Your Agent Configurations              ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
[/bold cyan]
""")

    profiles = _list_agent_profiles()

    if not profiles:
        console.print("[yellow]No agent profiles found.[/yellow]")
        console.print("\n[dim]Create a profile with: anima agent-create <name>[/dim]\n")
        return

    if format == 'json':
        import json
        console.print(json.dumps(profiles, indent=2))
    else:
        table = Table(title="Agent Profiles")
        table.add_column("Name", style="cyan")
        table.add_column("LLM Provider", style="green")
        table.add_column("Neo4j", style="yellow")
        table.add_column("Intelligence", style="magenta")
        table.add_column("Description", style="dim")

        for name, profile in profiles.items():
            llm = profile.get("llm_provider", "mistral")
            neo4j = "✓" if profile.get("enable_neo4j", False) else "✗"
            intel = "✓" if profile.get("enable_intelligence", True) else "✗"
            desc = profile.get("description", "No description")

            table.add_row(name, llm, neo4j, intel, desc)

        console.print(table)
        console.print(f"\n[dim]Total profiles: {len(profiles)}[/dim]")
        console.print("[dim]Use: anima chat --agent <name> to chat with a specific agent[/dim]\n")


@cli.command()
@click.argument('name')
@click.option('--llm', type=click.Choice(['mistral', 'nous']), default='mistral', help='LLM provider')
@click.option('--neo4j/--no-neo4j', default=True, help='Enable Neo4j')
@click.option('--intelligence/--no-intelligence', default=True, help='Enable intelligence layer')
@click.option('--description', '-d', default='', help='Profile description')
def agent_create(name: str, llm: str, neo4j: bool, intelligence: bool, description: str):
    """Create a new agent profile"""

    console.print(ANIMA_ASCII)
    console.print(f"\n[cyan]Creating agent profile: {name}[/cyan]\n")

    cfg = CLIConfig()

    # Build profile
    profile = {
        "llm_provider": llm,
        "enable_neo4j": neo4j,
        "enable_intelligence": intelligence,
        "description": description or f"Agent profile: {name}",
        "created_at": str(Path.cwd()),
    }

    # Optionally override API keys
    if Confirm.ask(f"Use custom API keys for this profile?", default=False):
        if llm == "mistral":
            profile["mistral_api_key"] = Prompt.ask("Mistral API Key", password=True)
        else:
            profile["nous_api_key"] = Prompt.ask("Nous API Key", password=True)

        profile["synapse_api_key"] = Prompt.ask("SYNAPSE API Key", password=True)

        if neo4j:
            profile["neo4j_uri"] = Prompt.ask("Neo4j URI", default="bolt://localhost:7687")
            profile["neo4j_username"] = Prompt.ask("Neo4j Username", default="neo4j")
            profile["neo4j_password"] = Prompt.ask("Neo4j Password", password=True)

    # Save profile
    _save_agent_profile(name, profile)

    console.print(f"\n[green]✓[/green] Agent profile '{name}' created successfully!")
    console.print(f"\n[dim]Chat with this agent: anima chat --agent {name}[/dim]\n")


@cli.command()
@click.argument('name')
def agent_delete(name: str):
    """Delete an agent profile"""

    if name == 'default':
        console.print("[red]✗ Cannot delete 'default' profile[/red]\n")
        return

    profile = _load_agent_profile(name)
    if not profile:
        console.print(f"[red]✗ Agent profile '{name}' not found[/red]\n")
        return

    if Confirm.ask(f"Delete agent profile '{name}'?", default=False):
        _delete_agent_profile(name)
        console.print(f"[green]✓[/green] Agent profile '{name}' deleted\n")
    else:
        console.print("[yellow]Cancelled[/yellow]\n")


@cli.command()
@click.argument('name')
def agent_show(name: str):
    """Show agent profile details"""

    profile = _load_agent_profile(name)
    if not profile:
        console.print(f"[red]✗ Agent profile '{name}' not found[/red]\n")
        return

    console.print(f"\n[cyan]Agent Profile: {name}[/cyan]\n")

    table = Table(show_header=False)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")

    for key, value in profile.items():
        # Mask sensitive values
        if "key" in key.lower() or "password" in key.lower():
            display_value = "****" + str(value)[-4:] if value else "[dim]Not set[/dim]"
        else:
            display_value = str(value)

        table.add_row(key, display_value)

    console.print(table)
    console.print(f"\n[dim]Edit: anima agent-edit {name}[/dim]\n")


# Helper functions for agent profile management

def _get_profiles_dir() -> Path:
    """Get the profiles directory"""
    profiles_dir = Path.home() / ".anima" / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    return profiles_dir


def _list_agent_profiles() -> Dict[str, Dict[str, Any]]:
    """List all agent profiles"""
    profiles_dir = _get_profiles_dir()
    profiles = {}

    for profile_file in profiles_dir.glob("*.json"):
        name = profile_file.stem
        try:
            with open(profile_file, 'r') as f:
                profiles[name] = json.load(f)
        except Exception:
            pass

    return profiles


def _load_agent_profile(name: str) -> Optional[Dict[str, Any]]:
    """Load an agent profile"""
    profiles_dir = _get_profiles_dir()
    profile_file = profiles_dir / f"{name}.json"

    if not profile_file.exists():
        return None

    try:
        with open(profile_file, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def _save_agent_profile(name: str, profile: Dict[str, Any]):
    """Save an agent profile"""
    profiles_dir = _get_profiles_dir()
    profile_file = profiles_dir / f"{name}.json"

    with open(profile_file, 'w') as f:
        json.dump(profile, f, indent=2)


def _delete_agent_profile(name: str):
    """Delete an agent profile"""
    profiles_dir = _get_profiles_dir()
    profile_file = profiles_dir / f"{name}.json"

    if profile_file.exists():
        profile_file.unlink()


@cli.command(name="run")
def run_interactive():
    """
    Launch the interactive AgentKit Control Panel.

    This starts a menu-driven interface for:
    - Creating and managing EQ agents
    - Configuring services (Neo4j, LLM, SYNAPSE)
    - Running health checks
    - Chatting with agents
    """
    from .interactive import main as interactive_main
    interactive_main()


if __name__ == "__main__":
    cli()
