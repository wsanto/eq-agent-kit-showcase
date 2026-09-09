"""
KAIKO EQ AgentKit - First Run Setup

Complete guided setup for new installations:
1. Welcome & Introduction
2. Environment Configuration
3. Database Setup
4. Agent Creation (via agent_setup_wizard)
5. Launch Agent

Author: KAIKO Development Team
Version: 1.5.0
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from InquirerPy import inquirer

# Import agent setup wizard
from .agent_setup_wizard import run_agent_setup_wizard

# ANSI color codes
ORANGE = "\033[38;5;208m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
NC = "\033[0m"

KAIKO_BANNER = f"""{ORANGE}
  ██╗  ██╗ █████╗ ██╗██╗  ██╗ ██████╗
  ██║ ██╔╝██╔══██╗██║██║ ██╔╝██╔═══██╗
  █████╔╝ ███████║██║█████╔╝ ██║   ██║
  ██╔═██╗ ██╔══██║██║██╔═██╗ ██║   ██║
  ██║  ██╗██║  ██║██║██║  ██╗╚██████╔╝
  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝
{NC}  v1.5.0 - {DIM}Emotionally Intelligent AI Agents{NC}
"""


def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


def show_banner():
    """Display KAIKO banner."""
    clear_screen()
    print(KAIKO_BANNER)
    print()


def get_project_root() -> Path:
    """Get project root directory."""
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / "setup.py").exists():
            return current
        current = current.parent
    return Path.cwd()


def run_make_target(target: str) -> int:
    """Run a Makefile target."""
    project_root = get_project_root()
    cmd = ["make", "-C", str(project_root), target]
    result = subprocess.run(cmd)
    return result.returncode


# ==================================================
# STEP 1: Welcome
# ==================================================

def step_welcome() -> bool:
    """Welcome screen."""
    show_banner()

    print(f"{BOLD}Welcome to KAIKO EQ AgentKit!{NC}\n")
    print("This setup will help you create your first emotionally intelligent agent.\n")

    print(f"{CYAN}What you'll do:{NC}")
    print(f"  1. Install dependencies")
    print(f"  2. Configure environment (API keys, databases)")
    print(f"  3. Create your first EQ Agent")
    print(f"  4. Start chatting!\n")

    print(f"{DIM}Estimated time: 5-10 minutes{NC}\n")

    proceed = inquirer.confirm(
        message="Ready to begin?",
        default=True
    ).execute()

    return proceed


# ==================================================
# STEP 2: Install Dependencies
# ==================================================

def step_install_dependencies() -> bool:
    """Install Python dependencies."""
    show_banner()

    print(f"{BOLD}Installing Dependencies{NC}\n")
    print("Installing required Python packages...\n")

    project_root = get_project_root()

    print(f"{CYAN}Running: pip install -e .{NC}\n")

    cmd = ["pip3", "install", "-e", str(project_root)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"\n{GREEN}✓{NC} Dependencies installed successfully!\n")
        input(f"{CYAN}Press Enter to continue...{NC}")
        return True
    else:
        print(f"\n{RED}✗{NC} Installation failed\n")
        print(f"{DIM}{result.stderr}{NC}\n")

        continue_anyway = inquirer.confirm(
            message="Continue anyway?",
            default=False
        ).execute()

        return continue_anyway


# ==================================================
# STEP 3: Environment Configuration
# ==================================================

def step_environment_config() -> Dict[str, str]:
    """Configure environment variables."""
    show_banner()

    print(f"{BOLD}Environment Configuration{NC}\n")
    print("Let's set up your API keys and database connections.\n")

    env_vars = {}

    # LLM Provider Selection
    print(f"{CYAN}1. Select LLM Provider{NC}\n")

    from InquirerPy.base.control import Choice
    from InquirerPy.separator import Separator

    providers = [
        Choice(value="anthropic", name="Anthropic (Claude)"),
        Choice(value="mistral", name="Mistral AI"),
        Choice(value="nous", name="Nous Research"),
        Choice(value="kaix1", name="KAI-X1 (Coming Soon)"),
    ]

    provider = inquirer.select(
        message="Choose your LLM provider:",
        choices=providers,
        pointer="→"
    ).execute()

    # Provider-specific API key configuration
    if provider == "anthropic":
        print(f"\n{CYAN}Anthropic API Key{NC}")
        print(f"   Get yours at: {DIM}https://console.anthropic.com{NC}\n")

        env_vars["ANTHROPIC_API_KEY"] = inquirer.secret(
            message="Enter your ANTHROPIC_API_KEY:",
            mandatory=True,
        ).execute()

        env_vars["LLM_PROVIDER"] = "anthropic"
        print(f"\n{GREEN}✓{NC} Anthropic configured\n")

    elif provider == "mistral":
        print(f"\n{CYAN}Mistral AI API Key{NC}")
        print(f"   Get yours at: {DIM}https://console.mistral.ai{NC}\n")

        env_vars["MISTRAL_API_KEY"] = inquirer.secret(
            message="Enter your MISTRAL_API_KEY:",
            mandatory=True,
        ).execute()

        env_vars["LLM_PROVIDER"] = "mistral"
        print(f"\n{GREEN}✓{NC} Mistral AI configured\n")

    elif provider == "nous":
        print(f"\n{CYAN}Nous Research Configuration{NC}")
        print(f"   Nous models are typically accessed via OpenAI-compatible APIs\n")

        env_vars["NOUS_API_KEY"] = inquirer.secret(
            message="Enter your API key:",
            mandatory=True,
        ).execute()

        env_vars["NOUS_BASE_URL"] = inquirer.text(
            message="API base URL:",
            default="https://api.nousresearch.com/v1",
        ).execute()

        env_vars["LLM_PROVIDER"] = "nous"
        print(f"\n{GREEN}✓{NC} Nous Research configured\n")

    elif provider == "kaix1":
        print(f"\n{ORANGE}⚠️  KAI-X1 Coming Soon{NC}")
        print(f"   KAIKO's proprietary emotionally intelligent model is in development.\n")
        print(f"   {DIM}Please select another provider for now.{NC}\n")
        input(f"{CYAN}Press Enter to continue...{NC}")
        return step_environment_config()  # Restart provider selection

    # SYNAPSE API key (for emotional intelligence)
    print(f"\n{CYAN}2. SYNAPSE API Key (Emotional Intelligence){NC}")
    print(f"   {DIM}Optional but recommended for full emotional reasoning{NC}\n")

    has_synapse = inquirer.confirm(
        message="Do you have a SYNAPSE API key?",
        default=False
    ).execute()

    if has_synapse:
        env_vars["SYNAPSE_API_KEY"] = inquirer.secret(
            message="Enter your SYNAPSE_API_KEY:",
            mandatory=True,
        ).execute()
        print(f"\n{GREEN}✓{NC} SYNAPSE API configured\n")
    else:
        print(f"\n{YELLOW}⚠{NC}  SYNAPSE not configured - agent will run with limited emotional intelligence\n")

    # Neo4j configuration
    print(f"{CYAN}3. Neo4j Database (Memory System){NC}")
    print(f"   {DIM}We'll set this up automatically with Docker{NC}\n")

    use_docker_neo4j = inquirer.confirm(
        message="Auto-setup Neo4j with Docker?",
        default=True
    ).execute()

    if use_docker_neo4j:
        print(f"\n{GREEN}✓{NC} Will auto-setup Neo4j\n")
        env_vars["NEO4J_URI"] = "bolt://localhost:7687"
        env_vars["NEO4J_USER"] = "neo4j"
        env_vars["NEO4J_PASSWORD"] = "anima123"
    else:
        env_vars["NEO4J_URI"] = inquirer.text(
            message="Neo4j URI:",
            default="bolt://localhost:7687",
        ).execute()

        env_vars["NEO4J_USER"] = inquirer.text(
            message="Neo4j username:",
            default="neo4j",
        ).execute()

        env_vars["NEO4J_PASSWORD"] = inquirer.secret(
            message="Neo4j password:",
            mandatory=True,
        ).execute()

    # PostgreSQL configuration
    print(f"{CYAN}4. PostgreSQL Database (State Management){NC}\n")

    use_docker_postgres = inquirer.confirm(
        message="Auto-setup PostgreSQL with Docker?",
        default=True
    ).execute()

    if use_docker_postgres:
        print(f"\n{GREEN}✓{NC} Will auto-setup PostgreSQL\n")
        env_vars["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/anima_agentkit"
    else:
        env_vars["DATABASE_URL"] = inquirer.text(
            message="PostgreSQL DATABASE_URL:",
            default="postgresql://postgres:postgres@localhost:5432/anima_agentkit",
        ).execute()

    # Write to .env file
    project_root = get_project_root()
    env_file = project_root / ".env"

    with open(env_file, "w") as f:
        f.write("# KAIKO EQ AgentKit Environment Variables\n")
        f.write(f"# Generated: {__import__('datetime').datetime.now().isoformat()}\n\n")
        for key, value in env_vars.items():
            f.write(f'{key}="{value}"\n')

    print(f"{GREEN}✓{NC} Environment variables saved to .env\n")

    input(f"{CYAN}Press Enter to continue...{NC}")

    return env_vars


# ==================================================
# STEP 4: Database Setup
# ==================================================

def step_database_setup(env_vars: Dict[str, str]) -> bool:
    """Setup databases."""
    show_banner()

    print(f"{BOLD}Database Setup{NC}\n")

    # Check if we're using Docker
    using_docker = (
        env_vars.get("NEO4J_URI") == "bolt://localhost:7687" and
        env_vars.get("DATABASE_URL", "").startswith("postgresql://postgres:postgres@localhost")
    )

    if using_docker:
        print(f"{CYAN}Starting Docker containers...{NC}\n")

        exit_code = run_make_target("db-setup")

        if exit_code == 0:
            print(f"\n{GREEN}✓{NC} Databases ready!\n")
            input(f"{CYAN}Press Enter to continue...{NC}")
            return True
        else:
            print(f"\n{YELLOW}⚠️  Database setup had issues{NC}\n")

            continue_anyway = inquirer.confirm(
                message="Continue anyway?",
                default=True
            ).execute()

            return continue_anyway
    else:
        print(f"{YELLOW}Using custom database configuration{NC}")
        print(f"{DIM}Make sure your databases are running{NC}\n")
        input(f"{CYAN}Press Enter to continue...{NC}")
        return True


# ==================================================
# STEP 5: Agent Setup
# ==================================================

def step_agent_setup() -> Optional[str]:
    """Run agent setup wizard."""
    show_banner()

    print(f"{BOLD}Agent Setup{NC}\n")
    print("Now let's create your first EQ Agent.\n")

    input(f"{CYAN}Press Enter to start the agent wizard...{NC}")

    # Call the agent setup wizard
    agent_name = run_agent_setup_wizard()

    return agent_name


# ==================================================
# STEP 6: Launch
# ==================================================

def step_launch(agent_name: str) -> None:
    """Launch the agent - choice between chat or management menu."""
    show_banner()

    print(f"{GREEN}{BOLD}✓ Setup Complete!{NC}\n")
    print(f"Your agent '{BOLD}{agent_name}{NC}' is ready.\n")

    from InquirerPy.base.control import Choice

    choice = inquirer.select(
        message="What would you like to do?",
        choices=[
            Choice(value="chat", name=f"Start chatting with {agent_name}"),
            Choice(value="menu", name="Open AgentKit Management Menu"),
            Choice(value="exit", name="Exit (you can launch anytime with './kaiko')"),
        ],
        default="chat",
        pointer="→"
    ).execute()

    if choice == "chat":
        print(f"\n{CYAN}Launching chat with {agent_name}...{NC}\n")
        # Launch directly into agent chat
        project_root = get_project_root()
        cmd = ["python3", "-m", "anima_agentkit.cli.main", "chat", "--agent", agent_name]
        subprocess.run(cmd, cwd=project_root)
    elif choice == "menu":
        print(f"\n{CYAN}Launching AgentKit Management Menu...{NC}\n")
        run_make_target("anima")
    else:
        print(f"\n{GREEN}All set!{NC}")
        print(f"\nYou can start anytime with:")
        print(f"  {CYAN}./kaiko chat {agent_name}{NC}  - Chat with your agent")
        print(f"  {CYAN}./kaiko{NC}              - Open management menu\n")


# ==================================================
# MAIN FLOW
# ==================================================

def run_first_time_setup():
    """Run complete first-time setup."""
    try:
        # Step 1: Welcome
        if not step_welcome():
            print(f"\n{YELLOW}Setup cancelled.{NC}\n")
            return

        # Step 2: Install Dependencies
        if not step_install_dependencies():
            print(f"\n{RED}Installation failed. Cannot continue.{NC}\n")
            return

        # Step 3: Environment Config
        env_vars = step_environment_config()

        # Step 4: Database Setup
        if not step_database_setup(env_vars):
            print(f"\n{YELLOW}Setup incomplete.{NC}\n")
            return

        # Step 5: Agent Setup
        agent_name = step_agent_setup()

        if not agent_name:
            print(f"\n{YELLOW}No agent created.{NC}\n")
            return

        # Step 6: Launch
        step_launch(agent_name)

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Setup interrupted.{NC}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Error: {e}{NC}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Entry point."""
    run_first_time_setup()


if __name__ == "__main__":
    main()
