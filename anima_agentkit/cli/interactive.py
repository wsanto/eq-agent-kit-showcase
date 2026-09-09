"""
ANIMA AgentKit - Interactive CLI Control Panel

A cohesive, menu-driven interface for managing EQ agents.
"""

import os
import sys
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box
import questionary
from questionary import Style

console = Console()

# Custom style for questionary menus - Orange theme
custom_style = Style([
    ('qmark', 'fg:#FF6B35 bold'),               # Question mark
    ('question', 'fg:white bold'),               # Question text
    ('answer', 'fg:#4CAF50 bold'),              # Selected answer
    ('pointer', 'fg:#FF6B35 bold'),             # Pointer ▶
    ('highlighted', 'fg:#FF6B35 bold'),         # Highlighted choice
    ('selected', 'fg:#FF6B35'),                 # Selected choice (when using checkbox)
    ('separator', 'fg:#666666'),                # Separator lines
    ('instruction', 'fg:#999999'),              # Instructions text
    ('text', 'fg:white'),                       # Plain text
    ('disabled', 'fg:#666666 italic'),          # Disabled choice
    ('mark', 'fg:#FF6B35 bold'),               # Checkmark/selection mark
])

# KAIKO ASCII Art - Orange theme
ANIMA_BANNER = """[bold #FF6B35]
    █  █   ███   ███  █  █   ███
    █ ██   █ █    █   █ ██   █ █
    ███    ███    █   ███    █ █
    █ ██   █ █    █   █ ██   █ █
    █  █   █ █   ███  █  █   ███
[/bold #FF6B35]
[bold white]      AgentKit by KAIKO Studios[/bold white]
[dim white]   Emotionally Intelligent AI Framework[/dim white]
"""


class AgentKitCLI:
    """Interactive CLI for ANIMA AgentKit."""

    def __init__(self):
        self.current_agent: Optional[str] = None
        self.dev_mode: bool = False
        self.running: bool = True

    def display_banner(self):
        """Display ANIMA AgentKit banner."""
        console.print(ANIMA_BANNER)

    def display_main_menu(self):
        """Display main control panel menu."""
        menu = Panel(
            """[bold #FF6B35]1.[/bold #FF6B35] Create New Agent
[bold #FF6B35]2.[/bold #FF6B35] Select & Configure Agent
[bold #FF6B35]3.[/bold #FF6B35] List All Agents
[bold #FF6B35]4.[/bold #FF6B35] System Health Check
[bold #FF6B35]5.[/bold #FF6B35] Help & Documentation
[bold #FF6B35]6.[/bold #FF6B35] Exit""",
            title="[bold white]◉ MAIN MENU ◉[/bold white]",
            border_style="#FF6B35",
            box=box.DOUBLE
        )
        console.print(menu)

    def display_agent_menu(self, agent_name: str):
        """Display agent-specific menu."""
        # Get agent status
        status_icon = "[#4CAF50]●[/#4CAF50]"
        neo4j_status = self._check_neo4j_sync()
        neo4j_icon = "[#4CAF50]●[/#4CAF50]" if neo4j_status else "[#FFC107]○[/#FFC107]"

        menu = Panel(
            f"""[dim white]Status: {status_icon} Ready | Neo4j: {neo4j_icon}[/dim white]

[bold white]▸ INTERACTION[/bold white]
[bold #FF6B35]1.[/bold #FF6B35] Chat with Agent
[bold #FF6B35]2.[/bold #FF6B35] View Conversation History
[bold #FF6B35]3.[/bold #FF6B35] Export Conversations

[bold white]▸ INTELLIGENCE & MEMORY[/bold white]
[bold #FF6B35]4.[/bold #FF6B35] View Beliefs
[bold #FF6B35]5.[/bold #FF6B35] View Goals
[bold #FF6B35]6.[/bold #FF6B35] View Memories
[bold #FF6B35]7.[/bold #FF6B35] View Emotional Trends
[bold #FF6B35]8.[/bold #FF6B35] View Breakthroughs

[bold white]▸ CONFIGURATION[/bold white]
[bold #FF6B35]9.[/bold #FF6B35] LLM Settings
[bold #FF6B35]10.[/bold #FF6B35] Neo4j Connection
[bold #FF6B35]11.[/bold #FF6B35] Intelligence Layer
[bold #FF6B35]12.[/bold #FF6B35] Personality & Behavior

[bold white]▸ ANALYTICS[/bold white]
[bold #FF6B35]13.[/bold #FF6B35] Agent Statistics
[bold #FF6B35]14.[/bold #FF6B35] Performance Metrics
[bold #FF6B35]15.[/bold #FF6B35] View Logs {'[#4CAF50](Dev Mode ON)[/#4CAF50]' if self.dev_mode else '[dim](Dev Mode OFF)[/dim]'}

[bold white]▸ ADVANCED[/bold white]
[bold #FF6B35]16.[/bold #FF6B35] Clear Agent Memory
[bold #FF6B35]17.[/bold #FF6B35] Export Agent Data
[bold #FF6B35]18.[/bold #FF6B35] Clone Agent
[bold #FF6B35]19.[/bold #FF6B35] Delete Agent

[dim]─────────────────────────────────────[/dim]
[bold #FF6B35]20.[/bold #FF6B35] Toggle Dev Mode
[bold #FF6B35]21.[/bold #FF6B35] ← Back to Main Menu""",
            title=f"[bold white]◉ AGENT: {agent_name.upper()} ◉[/bold white]",
            border_style="#FF6B35",
            box=box.DOUBLE
        )
        console.print(menu)

    def _check_neo4j_sync(self) -> bool:
        """Synchronous Neo4j check for menu display."""
        import subprocess
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=anima-neo4j", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=2
            )
            return "Up" in result.stdout
        except:
            return False

    async def create_agent(self):
        """Create a new EQ agent with full setup."""
        import uuid

        console.print("\n[bold #FF6B35]═══════════════════════════════════════[/bold #FF6B35]")
        console.print("[bold white]        CREATE NEW AGENT[/bold white]")
        console.print("[bold #FF6B35]═══════════════════════════════════════[/bold #FF6B35]\n")

        # Get agent name
        agent_name = Prompt.ask("[#FF6B35]Agent name[/#FF6B35]", default="my-agent")

        # Check if agent already exists
        profiles_dir = Path.home() / ".anima" / "profiles"
        if (profiles_dir / f"{agent_name}.json").exists():
            console.print(f"[#F44336]✗[/#F44336] Agent '{agent_name}' already exists")
            overwrite = Confirm.ask("Overwrite existing agent?", default=False)
            if not overwrite:
                return

        console.print(f"\n[#FF6B35]→[/#FF6B35] Creating agent '[bold white]{agent_name}[/bold white]'...\n")

        # Generate unique agent UUID
        agent_uuid = str(uuid.uuid4())
        console.print(f"[dim]Agent UUID: {agent_uuid}[/dim]\n")

        # Step 1: Check Neo4j
        console.print("[bold white]Step 1/5:[/bold white] Neo4j Database (Beliefs & Goals)")
        neo4j_status = await self._check_neo4j()

        if not neo4j_status:
            console.print("[#FFC107]→[/#FFC107] Neo4j not running")
            start_neo4j = Confirm.ask("Start Neo4j with Docker?", default=True)

            if start_neo4j:
                await self._start_neo4j_services()
            else:
                console.print("[#FFC107]⚠[/#FFC107] Agent will run without Neo4j (limited features)")

        # Step 2: Check PostgreSQL
        console.print("\n[bold white]Step 2/5:[/bold white] PostgreSQL Database (Chat History)")
        postgres_status = await self._check_postgres()

        if not postgres_status:
            console.print("[#FFC107]→[/#FFC107] PostgreSQL not running")
            start_postgres = Confirm.ask("Start PostgreSQL with Docker?", default=True)

            if start_postgres:
                await self._start_postgres_services()
            else:
                console.print("[#FFC107]⚠[/#FFC107] Agent will run without PostgreSQL (no chat history)")

        # Step 3: LLM Configuration
        console.print("\n[bold white]Step 3/5:[/bold white] LLM Provider")
        llm_provider = await self._configure_llm()

        # Step 4: Optional Services
        console.print("\n[bold white]Step 4/5:[/bold white] Optional Services")
        enable_intelligence = Confirm.ask("Enable Intelligence Layer?", default=True)

        # Step 5: Health Check
        console.print("\n[bold white]Step 5/5:[/bold white] Health Check")
        health_status = await self._run_health_check(silent=True)

        # Save agent profile
        profile = {
            "name": agent_name,
            "agent_uuid": agent_uuid,
            "llm_provider": llm_provider,
            "enable_neo4j": neo4j_status,
            "enable_postgres": postgres_status,
            "enable_intelligence": enable_intelligence and neo4j_status,
            "created_at": "2025-11-15"
        }

        await self._save_agent_profile(agent_name, profile)

        # Success
        console.print(f"\n[#4CAF50]✓[/#4CAF50] Agent '[bold white]{agent_name}[/bold white]' created successfully!\n")

        # Enter agent menu
        if Confirm.ask("Enter agent menu?", default=True):
            self.current_agent = agent_name
            await self.agent_menu_loop()

    async def _check_neo4j(self) -> bool:
        """Check if Neo4j is running."""
        import subprocess

        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=anima-neo4j", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and "Up" in result.stdout:
                console.print("[green]✓[/green] Neo4j is running")
                return True
            else:
                console.print("[yellow]○[/yellow] Neo4j container exists but is stopped")
                return False
        except:
            console.print("[yellow]○[/yellow] Neo4j not found")
            return False

    async def _start_neo4j_services(self):
        """Start Neo4j services with Docker."""
        import subprocess

        console.print("\n[cyan]→[/cyan] Starting Neo4j services...")

        # Check if Docker is available
        try:
            subprocess.run(["docker", "--version"], capture_output=True, timeout=5, check=True)
        except:
            console.print("[red]✗ ERROR[/red]: Docker not found")
            console.print("[yellow]→[/yellow] Install Docker: https://docs.docker.com/get-docker/")
            return False

        # Check if container exists
        check_result = subprocess.run(
            ["docker", "ps", "-a", "--filter", "name=anima-neo4j", "--format", "{{.Names}}"],
            capture_output=True,
            text=True
        )

        if "anima-neo4j" in check_result.stdout:
            # Start existing container
            console.print("[cyan]→[/cyan] Starting existing Neo4j container...")
            result = subprocess.run(["docker", "start", "anima-neo4j"], capture_output=True)

            if result.returncode == 0:
                console.print("[green]✓[/green] Neo4j started successfully")
                console.print("[dim]→ Web UI: http://localhost:7474[/dim]")
                console.print("[dim]→ Connection: bolt://localhost:7687[/dim]")
                return True
            else:
                console.print("[red]✗[/red] Failed to start Neo4j")
                return False
        else:
            # Run full setup
            console.print("[cyan]→[/cyan] Running Neo4j setup (this may take 1-2 minutes)...")
            result = subprocess.run(["make", "neo4j-setup"], capture_output=False)

            if result.returncode == 0:
                console.print("[green]✓[/green] Neo4j setup complete")
                return True
            else:
                console.print("[red]✗[/red] Neo4j setup failed")
                return False

    async def _check_postgres(self) -> bool:
        """Check if PostgreSQL is running."""
        import subprocess

        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=agentkit-postgres", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and "Up" in result.stdout:
                console.print("[green]✓[/green] PostgreSQL is running")
                return True
            else:
                console.print("[yellow]○[/yellow] PostgreSQL container exists but is stopped")
                return False
        except:
            console.print("[yellow]○[/yellow] PostgreSQL not found")
            return False

    async def _start_postgres_services(self):
        """Start PostgreSQL services with Docker Compose."""
        import subprocess

        console.print("\n[cyan]→[/cyan] Starting PostgreSQL services...")

        # Check if Docker is available
        try:
            subprocess.run(["docker", "--version"], capture_output=True, timeout=5, check=True)
        except:
            console.print("[red]✗ ERROR[/red]: Docker not found")
            console.print("[yellow]→[/yellow] Install Docker: https://docs.docker.com/get-docker/")
            return False

        # Check if container exists
        check_result = subprocess.run(
            ["docker", "ps", "-a", "--filter", "name=agentkit-postgres", "--format", "{{.Names}}"],
            capture_output=True,
            text=True
        )

        if "agentkit-postgres" in check_result.stdout:
            # Start existing container
            console.print("[cyan]→[/cyan] Starting existing PostgreSQL container...")

            # Try docker compose first, then docker-compose
            result = subprocess.run(["docker", "compose", "start", "postgres"], capture_output=True)
            if result.returncode != 0:
                result = subprocess.run(["docker-compose", "start", "postgres"], capture_output=True)

            if result.returncode == 0:
                console.print("[green]✓[/green] PostgreSQL started successfully")
                console.print("[dim]→ Connection: localhost:5432[/dim]")
                console.print("[dim]→ Database: anima_memory[/dim]")
                return True
            else:
                console.print("[red]✗[/red] Failed to start PostgreSQL")
                return False
        else:
            # Run full setup
            console.print("[cyan]→[/cyan] Running PostgreSQL setup (this may take 1-2 minutes)...")
            result = subprocess.run(["make", "postgres-setup"], capture_output=False)

            if result.returncode == 0:
                console.print("[green]✓[/green] PostgreSQL setup complete")
                return True
            else:
                console.print("[red]✗[/red] PostgreSQL setup failed")
                return False

    async def _configure_llm(self) -> str:
        """Configure LLM provider."""
        console.print("\nAvailable providers:")
        console.print("  [cyan]1.[/cyan] Mistral AI (recommended)")
        console.print("  [cyan]2.[/cyan] Nous Research")
        console.print("  [cyan]3.[/cyan] OpenAI")

        choice = Prompt.ask("Select provider", choices=["1", "2", "3"], default="1")

        provider_map = {
            "1": "mistral",
            "2": "nous",
            "3": "openai"
        }

        provider = provider_map[choice]
        console.print(f"[green]✓[/green] Selected: {provider.title()}")

        # Check for API key and prompt if missing
        key_name = f"{provider.upper()}_API_KEY"
        current_key = os.getenv(key_name)

        if not current_key:
            console.print(f"[yellow]⚠[/yellow] {key_name} not found")

            if Confirm.ask(f"Enter {key_name} now?", default=True):
                api_key = Prompt.ask(f"\n{key_name}", password=True)

                if api_key and api_key.strip():
                    # Save to .env file
                    self._save_to_env(key_name, api_key.strip())
                    console.print(f"[green]✓[/green] {key_name} saved to .env")
                else:
                    console.print(f"[yellow]⚠[/yellow] No key entered - add it later to .env file")
            else:
                console.print(f"[dim]→ Add {key_name} to .env file manually[/dim]")
        else:
            # Show masked key
            masked_key = current_key[:10] + "****" + current_key[-4:] if len(current_key) > 14 else "****"
            console.print(f"[green]✓[/green] Using existing key: {masked_key}")

        # Also check SYNAPSE_API_KEY
        if not os.getenv("SYNAPSE_API_KEY"):
            console.print(f"\n[yellow]○[/yellow] SYNAPSE_API_KEY not found (optional for emotion analysis)")
            if Confirm.ask("Enter SYNAPSE_API_KEY now?", default=False):
                synapse_key = Prompt.ask("\nSYNAPSE_API_KEY", password=True)
                if synapse_key and synapse_key.strip():
                    self._save_to_env("SYNAPSE_API_KEY", synapse_key.strip())
                    console.print("[green]✓[/green] SYNAPSE_API_KEY saved to .env")

        return provider

    def _save_to_env(self, key: str, value: str):
        """Save or update a key in .env file."""
        env_file = Path(".env")

        # Read existing .env
        if env_file.exists():
            with open(env_file, "r") as f:
                lines = f.readlines()
        else:
            lines = []

        # Check if key already exists
        key_exists = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                key_exists = True
                break

        # Add new key if doesn't exist
        if not key_exists:
            lines.append(f"{key}={value}\n")

        # Write back to .env
        with open(env_file, "w") as f:
            f.writelines(lines)

        # Also set in current environment
        os.environ[key] = value

    async def _run_health_check(self, silent: bool = False) -> Dict[str, bool]:
        """Run comprehensive health check."""
        if not silent:
            console.print("\n[bold cyan]╔═══════════════════════════════════════╗[/bold cyan]")
            console.print("[bold cyan]║          Health Check                ║[/bold cyan]")
            console.print("[bold cyan]╚═══════════════════════════════════════╝[/bold cyan]\n")

        status = {
            "docker": False,
            "neo4j": False,
            "postgres": False,
            "llm": False,
            "synapse": False
        }

        # Check Docker
        import subprocess
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, timeout=5)
            status["docker"] = result.returncode == 0
            if not silent:
                if status["docker"]:
                    console.print("[green]✓[/green] Docker installed")
                else:
                    console.print("[red]✗[/red] Docker not found")
        except:
            if not silent:
                console.print("[red]✗[/red] Docker not found")

        # Check Neo4j
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=anima-neo4j", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            status["neo4j"] = "Up" in result.stdout
            if not silent:
                if status["neo4j"]:
                    console.print("[green]✓[/green] Neo4j running")
                else:
                    console.print("[yellow]○[/yellow] Neo4j not running")
        except:
            if not silent:
                console.print("[yellow]○[/yellow] Neo4j not available")

        # Check PostgreSQL
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=agentkit-postgres", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            status["postgres"] = "Up" in result.stdout
            if not silent:
                if status["postgres"]:
                    console.print("[green]✓[/green] PostgreSQL running")
                else:
                    console.print("[yellow]○[/yellow] PostgreSQL not running")
        except:
            if not silent:
                console.print("[yellow]○[/yellow] PostgreSQL not available")

        # Check LLM API keys
        has_mistral = bool(os.getenv("MISTRAL_API_KEY"))
        has_nous = bool(os.getenv("NOUS_API_KEY"))
        has_openai = bool(os.getenv("OPENAI_API_KEY"))

        status["llm"] = has_mistral or has_nous or has_openai

        if not silent:
            if status["llm"]:
                providers = []
                if has_mistral:
                    providers.append("Mistral")
                if has_nous:
                    providers.append("Nous")
                if has_openai:
                    providers.append("OpenAI")
                console.print(f"[green]✓[/green] LLM configured ({', '.join(providers)})")
            else:
                console.print("[red]✗[/red] No LLM API keys found")

        # Check SYNAPSE
        status["synapse"] = bool(os.getenv("SYNAPSE_API_KEY"))
        if not silent:
            if status["synapse"]:
                console.print("[green]✓[/green] SYNAPSE API configured")
            else:
                console.print("[yellow]○[/yellow] SYNAPSE not configured (optional)")

        if not silent:
            console.print()

        return status

    async def _save_agent_profile(self, name: str, profile: Dict[str, Any]):
        """Save agent profile to disk."""
        import json

        profiles_dir = Path.home() / ".anima" / "profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)

        profile_path = profiles_dir / f"{name}.json"

        with open(profile_path, "w") as f:
            json.dump(profile, f, indent=2)

    async def view_agents(self):
        """View all configured agents (list only - no selection)."""
        console.print("\n[bold #FF6B35]═══════════════════════════════════════[/bold #FF6B35]")
        console.print("[bold white]           ALL AGENTS[/bold white]")
        console.print("[bold #FF6B35]═══════════════════════════════════════[/bold #FF6B35]\n")

        profiles_dir = Path.home() / ".anima" / "profiles"

        if not profiles_dir.exists() or not list(profiles_dir.glob("*.json")):
            console.print("[#FFC107]⚠ No agents configured yet[/#FFC107]")
            console.print("[dim white]→ Use option 1 to create an agent[/dim white]\n")
            return

        table = Table(box=box.DOUBLE, border_style="#FF6B35")
        table.add_column("#", style="bold #FF6B35", width=4)
        table.add_column("Name", style="bold white")
        table.add_column("LLM Provider", style="white")
        table.add_column("Neo4j", justify="center")
        table.add_column("Intelligence", justify="center")

        import json
        agent_list = []
        for idx, profile_file in enumerate(sorted(profiles_dir.glob("*.json")), 1):
            with open(profile_file) as f:
                profile = json.load(f)

            agent_name = profile.get("name", profile_file.stem)
            agent_list.append(agent_name)

            neo4j_status = "[#4CAF50]●[/#4CAF50]" if profile.get("enable_neo4j") else "[dim]○[/dim]"
            intel_status = "[#4CAF50]●[/#4CAF50]" if profile.get("enable_intelligence") else "[dim]○[/dim]"

            table.add_row(
                str(idx),
                agent_name,
                profile.get("llm_provider", "mistral").title(),
                neo4j_status,
                intel_status
            )

        console.print(table)
        console.print()

    async def configure_agent(self):
        """Select and configure an existing agent."""
        console.print("\n[bold #FF6B35]═══════════════════════════════════════[/bold #FF6B35]")
        console.print("[bold white]        SELECT AGENT[/bold white]")
        console.print("[bold #FF6B35]═══════════════════════════════════════[/bold #FF6B35]\n")

        # List agents
        profiles_dir = Path.home() / ".anima" / "profiles"
        if not profiles_dir.exists():
            console.print("[#FFC107]⚠ No agents found[/#FFC107]")
            console.print("[dim white]→ Use option 1 to create an agent[/dim white]\n")
            return

        import json
        profiles = list(sorted(profiles_dir.glob("*.json")))
        if not profiles:
            console.print("[#FFC107]⚠ No agents found[/#FFC107]")
            console.print("[dim white]→ Use option 1 to create an agent[/dim white]\n")
            return

        # Show agent table with selection numbers
        table = Table(box=box.DOUBLE, border_style="#FF6B35")
        table.add_column("#", style="bold #FF6B35", width=4)
        table.add_column("Agent Name", style="bold white")
        table.add_column("LLM", style="white")
        table.add_column("Status", style="white")

        agent_list = []
        for idx, profile_file in enumerate(profiles, 1):
            with open(profile_file) as f:
                profile = json.load(f)

            agent_name = profile.get("name", profile_file.stem)
            agent_list.append(agent_name)

            llm = profile.get("llm_provider", "mistral").title()

            # Status indicators
            status_parts = []
            if profile.get("enable_neo4j"):
                status_parts.append("[#4CAF50]Neo4j[/#4CAF50]")
            if profile.get("enable_intelligence"):
                status_parts.append("[#4CAF50]Intelligence[/#4CAF50]")
            status = " • ".join(status_parts) if status_parts else "[dim]Basic[/dim]"

            table.add_row(str(idx), agent_name, llm, status)

        console.print(table)
        console.print()

        # Get selection with interactive menu
        choice = await questionary.select(
            "Select an agent:",
            choices=agent_list,
            style=custom_style,
            use_shortcuts=True,
            use_arrow_keys=True,
            use_indicator=True,
            pointer="▶",
            qmark="◉"
        ).ask_async()

        if not choice:
            return

        self.current_agent = choice
        console.print(f"\n[#4CAF50]✓[/#4CAF50] Selected agent: [bold white]{choice}[/bold white]\n")
        await self.agent_menu_loop()

    async def agent_menu_loop(self):
        """Agent-specific menu loop."""
        while self.running and self.current_agent:
            console.print()

            # Build choices dynamically with dev mode indicator
            dev_mode_text = "[Dev Mode ON]" if self.dev_mode else "[Dev Mode OFF]"

            choice = await questionary.select(
                f"Agent: {self.current_agent.upper()} - What would you like to do?",
                choices=[
                    questionary.Separator("═══ INTERACTION ═══"),
                    "Chat with Agent",
                    "View Conversation History",
                    "Export Conversations",
                    questionary.Separator("═══ INTELLIGENCE & MEMORY ═══"),
                    "View Beliefs",
                    "View Goals",
                    "View Memories",
                    "View Emotional Trends",
                    "View Breakthroughs",
                    questionary.Separator("═══ CONFIGURATION ═══"),
                    "LLM Settings",
                    "Neo4j Connection",
                    "Intelligence Layer",
                    "Personality & Behavior",
                    questionary.Separator("═══ ANALYTICS ═══"),
                    "Agent Statistics",
                    "Performance Metrics",
                    f"View Logs {dev_mode_text}",
                    questionary.Separator("═══ ADVANCED ═══"),
                    "Clear Agent Memory",
                    "Export Agent Data",
                    "Clone Agent",
                    "Delete Agent",
                    questionary.Separator("═══ CONTROLS ═══"),
                    "Toggle Dev Mode",
                    "← Back to Main Menu"
                ],
                style=custom_style,
                use_shortcuts=True,
                use_arrow_keys=True,
                use_indicator=True,
                pointer="▶",
                qmark="◉"
            ).ask_async()

            if not choice:  # User pressed Ctrl+C
                break

            # INTERACTION
            if choice == "Chat with Agent":
                await self.chat_with_agent()
            elif choice == "View Conversation History":
                await self.view_conversation_history()
            elif choice == "Export Conversations":
                await self.export_conversations()
            # INTELLIGENCE & MEMORY
            elif choice == "View Beliefs":
                await self.view_beliefs()
            elif choice == "View Goals":
                await self.view_goals()
            elif choice == "View Memories":
                await self.view_memories()
            elif choice == "View Emotional Trends":
                await self.view_emotional_trends()
            elif choice == "View Breakthroughs":
                await self.view_breakthroughs()
            # AGENT CONFIGURATION
            elif choice == "LLM Settings":
                await self.configure_llm_settings()
            elif choice == "Neo4j Connection":
                await self.configure_neo4j()
            elif choice == "Intelligence Layer":
                await self.configure_intelligence()
            elif choice == "Personality & Behavior":
                await self.configure_personality()
            # ANALYTICS & MONITORING
            elif choice == "Agent Statistics":
                await self.view_agent_stats()
            elif choice == "Performance Metrics":
                await self.view_performance_metrics()
            elif choice.startswith("View Logs"):
                await self.view_logs()
            # ADVANCED
            elif choice == "Clear Agent Memory":
                await self.clear_agent_memory()
            elif choice == "Export Agent Data":
                await self.export_agent_data()
            elif choice == "Clone Agent":
                await self.clone_agent()
            elif choice == "Delete Agent":
                await self.delete_agent()
            # CONTROLS
            elif choice == "Toggle Dev Mode":
                self.dev_mode = not self.dev_mode
                status = "[#4CAF50]enabled[/#4CAF50]" if self.dev_mode else "[dim]disabled[/dim]"
                console.print(f"\n[#FF6B35]→[/#FF6B35] Dev mode {status}\n")
            elif choice == "← Back to Main Menu":
                self.current_agent = None
                break

    async def chat_with_agent(self):
        """Start chat session with agent."""
        console.print(f"\n[cyan]→[/cyan] Starting chat with [bold]{self.current_agent}[/bold]...")
        console.print("[dim]Loading agent...[/dim]\n")

        # Run actual chat command (this is correct - direct chat via main.py)
        import subprocess
        subprocess.run([
            "python3", "-m", "anima_agentkit.cli.main",
            "chat",
            "--agent", self.current_agent
        ])

    async def view_agent_stats(self):
        """View agent statistics."""
        console.print(f"\n[bold cyan]Stats for: {self.current_agent}[/bold cyan]\n")
        console.print("[dim]Feature coming soon...[/dim]\n")

    async def configure_agent_settings(self):
        """Configure agent settings."""
        console.print(f"\n[bold cyan]Configure: {self.current_agent}[/bold cyan]\n")
        console.print("[dim]Feature coming soon...[/dim]\n")

    async def view_logs(self):
        """View agent logs."""
        if not self.dev_mode:
            console.print("\n[yellow]⚠[/yellow] Dev mode is disabled")
            enable = Confirm.ask("Enable dev mode?", default=True)
            if enable:
                self.dev_mode = True
            else:
                return

        console.print(f"\n[bold cyan]Logs for: {self.current_agent}[/bold cyan]\n")
        console.print("[dim]Feature coming soon...[/dim]\n")

    # INTERACTION methods
    async def view_conversation_history(self):
        """View conversation history."""
        console.print(f"\n[bold cyan]Conversation History: {self.current_agent}[/bold cyan]\n")
        console.print("[dim]Feature coming soon - will show past conversations[/dim]\n")

    async def export_conversations(self):
        """Export conversations."""
        console.print(f"\n[bold cyan]Export Conversations: {self.current_agent}[/bold cyan]\n")
        console.print("[dim]Feature coming soon - export as JSON/Markdown[/dim]\n")

    # INTELLIGENCE & MEMORY methods
    async def view_beliefs(self):
        """View agent's detected beliefs."""
        console.print(f"\n[bold cyan]Beliefs: {self.current_agent}[/bold cyan]\n")
        console.print("[dim]Feature coming soon - will show core beliefs from Neo4j[/dim]\n")
        console.print("[dim]Example:[/dim]")
        console.print("[dim]  VALUES: \"Work-life balance is essential\" (Strength: 0.87)[/dim]")
        console.print("[dim]  GROWTH: \"Hands-on practice beats theory\" (Strength: 0.78)[/dim]\n")

    async def view_goals(self):
        """View agent's tracked goals."""
        console.print(f"\n[bold cyan]Goals: {self.current_agent}[/bold cyan]\n")
        console.print("[dim]Feature coming soon - will show active goals from Neo4j[/dim]\n")
        console.print("[dim]Example:[/dim]")
        console.print("[dim]  ⚡ Master Python for Data Science (75% complete)[/dim]")
        console.print("[dim]  📚 Build Portfolio Projects (30% complete)[/dim]\n")

    async def view_memories(self):
        """View agent's stored memories."""
        console.print(f"\n[bold cyan]Memories: {self.current_agent}[/bold cyan]\n")
        console.print("[dim]Feature coming soon - will show memory graph from Neo4j[/dim]\n")

    async def view_emotional_trends(self):
        """View emotional trends over time."""
        console.print(f"\n[bold cyan]Emotional Trends: {self.current_agent}[/bold cyan]\n")
        console.print("[dim]Feature coming soon - arousal patterns and emotional profile[/dim]\n")

    async def view_breakthroughs(self):
        """View detected breakthroughs."""
        console.print(f"\n[bold cyan]Breakthroughs: {self.current_agent}[/bold cyan]\n")
        console.print("[dim]Feature coming soon - epistemic shifts and insights[/dim]\n")

    # AGENT CONFIGURATION methods
    async def configure_llm_settings(self):
        """Configure LLM settings."""
        console.print(f"\n[bold cyan]LLM Settings: {self.current_agent}[/bold cyan]\n")
        console.print("[dim]Feature coming soon - change provider, model, parameters[/dim]\n")

    async def configure_neo4j(self):
        """Configure Neo4j connection."""
        console.print(f"\n[bold cyan]Neo4j Configuration: {self.current_agent}[/bold cyan]\n")
        console.print("[dim]Feature coming soon - update connection details[/dim]\n")

    async def configure_intelligence(self):
        """Configure intelligence layer."""
        console.print(f"\n[bold cyan]Intelligence Layer: {self.current_agent}[/bold cyan]\n")
        console.print("[dim]Feature coming soon - toggle features, adjust thresholds[/dim]\n")

    async def configure_personality(self):
        """Configure agent personality."""
        console.print(f"\n[bold cyan]Personality & Behavior: {self.current_agent}[/bold cyan]\n")
        console.print("[dim]Feature coming soon - adjust conversation style, verbosity[/dim]\n")

    # ANALYTICS & MONITORING methods
    async def view_performance_metrics(self):
        """View performance metrics."""
        console.print(f"\n[bold cyan]Performance Metrics: {self.current_agent}[/bold cyan]\n")
        console.print("[dim]Feature coming soon - token usage, response times, costs[/dim]\n")

    # ADVANCED methods
    async def clear_agent_memory(self):
        """Clear agent memory."""
        console.print(f"\n[bold cyan]Clear Memory: {self.current_agent}[/bold cyan]\n")
        console.print("[yellow]⚠ Warning:[/yellow] This will delete all memories, beliefs, and goals")

        if Confirm.ask("Are you sure?", default=False):
            console.print("[dim]Feature coming soon - will clear Neo4j data[/dim]\n")
        else:
            console.print("[dim]Cancelled[/dim]\n")

    async def export_agent_data(self):
        """Export all agent data."""
        console.print(f"\n[bold cyan]Export Agent Data: {self.current_agent}[/bold cyan]\n")
        console.print("[dim]Feature coming soon - export beliefs, goals, memories as JSON[/dim]\n")

    async def clone_agent(self):
        """Clone agent profile."""
        console.print(f"\n[bold cyan]Clone Agent: {self.current_agent}[/bold cyan]\n")

        new_name = Prompt.ask("New agent name")
        if new_name:
            console.print(f"[dim]Feature coming soon - will create '{new_name}' from '{self.current_agent}'[/dim]\n")

    async def delete_agent(self):
        """Delete agent profile."""
        console.print(f"\n[bold cyan]Delete Agent: {self.current_agent}[/bold cyan]\n")
        console.print(f"[yellow]⚠ Warning:[/yellow] This will permanently delete the '{self.current_agent}' profile")

        if Confirm.ask("Are you sure?", default=False):
            profiles_dir = Path.home() / ".anima" / "profiles"
            profile_file = profiles_dir / f"{self.current_agent}.json"

            if profile_file.exists():
                profile_file.unlink()
                console.print(f"[green]✓[/green] Agent '{self.current_agent}' deleted\n")
                self.current_agent = None
            else:
                console.print(f"[red]✗[/red] Profile file not found\n")
        else:
            console.print("[dim]Cancelled[/dim]\n")

    async def show_help(self):
        """Show help and documentation."""
        console.print("\n[bold cyan]╔═══════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║             Help & Guides            ║[/bold cyan]")
        console.print("[bold cyan]╚═══════════════════════════════════════╝[/bold cyan]\n")

        help_text = """[bold]Available Commands:[/bold]

[cyan]Create EQ Agent[/cyan]
  Create a new agent with guided setup including Neo4j, LLM
  configuration, and service health checks.

[cyan]View Agents[/cyan]
  List all configured agents with their settings and status.

[cyan]Configure Agent[/cyan]
  Modify settings for an existing agent or enter agent menu.

[cyan]Health Check[/cyan]
  Verify all services (Docker, Neo4j, LLM, SYNAPSE) are
  configured and accessible.

[cyan]Help[/cyan]
  Display this help information and documentation links.

[cyan]Quit AgentKit[/cyan]
  Exit the AgentKit Control Panel.

[bold]Documentation:[/bold]
  • Quick Reference: docs/CLI-QUICK-REFERENCE.md
  • Full Guide: docs/CLI-GUIDE.md
  • Error Codes: docs/CLI-ERROR-CODES.md

[bold]Getting Started:[/bold]
  1. Create your first agent (option 1)
  2. Follow the setup wizard
  3. Start chatting!
"""
        console.print(help_text)

    async def main_menu_loop(self):
        """Main menu loop."""
        self.display_banner()

        while self.running:
            console.print()

            # Interactive menu selection
            choice = await questionary.select(
                "What would you like to do?",
                choices=[
                    "Create New Agent",
                    "Select & Configure Agent",
                    "List All Agents",
                    "System Health Check",
                    "Help & Documentation",
                    "Exit"
                ],
                style=custom_style,
                use_shortcuts=True,
                use_arrow_keys=True,
                use_indicator=True,
                pointer="▶",
                qmark="◉"
            ).ask_async()

            if not choice:  # User pressed Ctrl+C
                break

            if choice == "Create New Agent":
                await self.create_agent()
            elif choice == "Select & Configure Agent":
                await self.configure_agent()
            elif choice == "List All Agents":
                await self.view_agents()
            elif choice == "System Health Check":
                await self._run_health_check()
            elif choice == "Help & Documentation":
                await self.show_help()
            elif choice == "Exit":
                console.print("\n[#FF6B35]═══════════════════════════════════════[/#FF6B35]")
                console.print("[bold white]Thanks for using ANIMA AgentKit![/bold white]")
                console.print("[dim white]Made with ♥ by KAIKO Studios[/dim white]")
                console.print("[#FF6B35]═══════════════════════════════════════[/#FF6B35]\n")
                self.running = False
                break

    async def run(self):
        """Run the interactive CLI."""
        try:
            await self.main_menu_loop()
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Interrupted by user[/yellow]")
            console.print("[cyan]Goodbye![/cyan]\n")
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]\n")


def main():
    """Entry point for interactive CLI."""
    cli = AgentKitCLI()
    asyncio.run(cli.run())


if __name__ == "__main__":
    main()
