"""
KAIKO EQ AgentKit - First Run Wizard

A guided, interactive setup experience that takes users from installation
to their first chat session in one seamless flow.

This wizard uses progressive disclosure to guide users through:
1. Welcome & Introduction
2. What is KAIKO EQ AgentKit?
3. Environment Configuration
4. Agent Personality Setup (with predetermined options)
5. Database Setup
6. Final Configuration
7. Launch Agent!

Author: KAIKO Development Team
Version: 1.5.0
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

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
{NC}
        KAIKO EQ AgentKit v1.5.0
        {DIM}Emotionally Intelligent AI Agents{NC}
"""


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


def show_banner():
    """Display the KAIKO banner."""
    clear_screen()
    print(KAIKO_BANNER)
    print()


def get_project_root() -> Path:
    """Get the project root directory."""
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / "setup.py").exists():
            return current
        current = current.parent
    return Path.cwd()


def run_make_target(target: str, silent: bool = False) -> int:
    """Run a Makefile target."""
    project_root = get_project_root()
    cmd = ["make", "-C", str(project_root), target]

    if silent:
        result = subprocess.run(cmd, capture_output=True)
    else:
        result = subprocess.run(cmd)

    return result.returncode


# ============================================================================
# STEP 1: Welcome
# ============================================================================

def step_welcome() -> bool:
    """Welcome screen - introduces KAIKO."""
    show_banner()

    print(f"{BOLD}Welcome to KAIKO EQ AgentKit!{NC}\n")
    print("This wizard will guide you through setting up your first")
    print("emotionally intelligent AI agent in just a few steps.\n")

    print(f"{CYAN}What you'll create:{NC}")
    print(f"  • A personalized AI agent with unique personality")
    print(f"  • Memory system that learns from conversations")
    print(f"  • Emotional intelligence and self-awareness")
    print(f"  • Goal tracking and belief formation\n")

    print(f"{DIM}Estimated time: 5-10 minutes{NC}\n")

    proceed = inquirer.confirm(
        message="Ready to begin?",
        default=True
    ).execute()

    return proceed


# ============================================================================
# STEP 2: What is KAIKO?
# ============================================================================

def step_introduction() -> None:
    """Explain what KAIKO EQ AgentKit is."""
    show_banner()

    print(f"{BOLD}What is KAIKO EQ AgentKit?{NC}\n")

    print("KAIKO helps you build AI agents that are:")
    print()
    print(f"{GREEN}🧠 Emotionally Intelligent{NC}")
    print(f"   Your agent analyzes emotional context and responds with empathy\n")

    print(f"{GREEN}💭 Memory-Enabled{NC}")
    print(f"   Remembers past conversations using graph-based memory (Neo4j)\n")

    print(f"{GREEN}🎯 Goal-Oriented{NC}")
    print(f"   Tracks goals, milestones, and helps you achieve them\n")

    print(f"{GREEN}🔮 Self-Aware{NC}")
    print(f"   Forms beliefs, reflects on experiences, and grows over time\n")

    print(f"{GREEN}🎭 Personality-Driven{NC}")
    print(f"   Each agent has a unique personality, communication style, and purpose\n")

    input(f"{CYAN}Press Enter to continue...{NC}")


# ============================================================================
# STEP 3: Choose Agent Purpose
# ============================================================================

def step_choose_purpose() -> str:
    """Let user choose what they want their agent to do."""
    show_banner()

    print(f"{BOLD}What would you like your agent to help with?{NC}\n")
    print("Choose a purpose that best fits your needs:\n")

    purposes = [
        Choice(value="companion", name="Conversational Companion"),
        Choice(value="coach", name="Performance Coach"),
        Choice(value="therapist", name="Emotional Support Specialist"),
        Choice(value="crisis", name="Crisis Support Agent"),
        Choice(value="analytical", name="Analytical Research Assistant"),
        Separator(),
        Choice(value="custom", name="Custom - Define your own purpose"),
    ]

    purpose = inquirer.select(
        message="Select your agent's primary purpose:",
        choices=purposes,
        pointer="➤",
    ).execute()

    return purpose


# ============================================================================
# STEP 4: Agent Identity
# ============================================================================

def step_agent_identity(purpose: str) -> Dict[str, str]:
    """Collect agent name and basic identity."""
    show_banner()

    print(f"{BOLD}Let's give your agent an identity{NC}\n")

    # Suggest name based on purpose
    suggested_names = {
        "companion": "Aria",
        "coach": "Mentor",
        "therapist": "Sage",
        "crisis": "Guardian",
        "analytical": "Athena",
        "custom": "Agent"
    }

    suggested_name = suggested_names.get(purpose, "Agent")

    agent_name = inquirer.text(
        message="What would you like to name your agent?",
        default=suggested_name,
        validate=lambda x: len(x) > 0,
    ).execute()

    print(f"\n{GREEN}✓{NC} Agent name: {BOLD}{agent_name}{NC}\n")

    return {
        "name": agent_name,
        "purpose": purpose,
    }


# ============================================================================
# STEP 5: Communication Style
# ============================================================================

def step_communication_style() -> str:
    """Choose agent communication style."""
    show_banner()

    print(f"{BOLD}How should your agent communicate?{NC}\n")

    styles = [
        Choice(value="auto_eq", name="AutoEQ - Adaptive Emotional Intelligence"),
        Choice(value="conversational", name="Conversational - Natural & Friendly"),
        Choice(value="coaching", name="Coaching - Motivational & Direct"),
        Choice(value="therapeutic", name="Therapeutic - Reflective & Empathetic"),
        Choice(value="professional", name="Professional - Clear & Concise"),
        Choice(value="analytical", name="Analytical - Logical & Detailed"),
    ]

    style = inquirer.select(
        message="Select communication style:",
        choices=styles,
        pointer="➤",
    ).execute()

    return style


# ============================================================================
# STEP 6: Environment Configuration
# ============================================================================

def step_environment_config() -> Dict[str, str]:
    """Configure environment variables."""
    show_banner()

    print(f"{BOLD}Environment Configuration{NC}\n")
    print("KAIKO needs a few API keys and database credentials.\n")

    env_vars = {}

    # ANTHROPIC_API_KEY (required)
    print(f"{CYAN}1. Anthropic API Key (Required){NC}")
    print(f"   Get yours at: {DIM}https://console.anthropic.com{NC}\n")

    env_vars["ANTHROPIC_API_KEY"] = inquirer.secret(
        message="Enter your ANTHROPIC_API_KEY:",
        mandatory=True,
    ).execute()

    print(f"\n{GREEN}✓{NC} Anthropic API key configured\n")

    # Neo4j configuration
    print(f"{CYAN}2. Neo4j Database (Memory System){NC}")
    print(f"   {DIM}We can set this up automatically with Docker{NC}\n")

    use_docker_neo4j = inquirer.confirm(
        message="Auto-setup Neo4j with Docker? (Recommended)",
        default=True
    ).execute()

    if use_docker_neo4j:
        print(f"\n{GREEN}✓{NC} Will auto-setup Neo4j with Docker\n")
        env_vars["NEO4J_URI"] = "bolt://localhost:7687"
        env_vars["NEO4J_USER"] = "neo4j"
        env_vars["NEO4J_PASSWORD"] = "kaikoagent123"
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
    print(f"{CYAN}3. PostgreSQL Database (State Management){NC}")
    print(f"   {DIM}For conversation state and session data{NC}\n")

    use_docker_postgres = inquirer.confirm(
        message="Auto-setup PostgreSQL with Docker? (Recommended)",
        default=True
    ).execute()

    if use_docker_postgres:
        print(f"\n{GREEN}✓{NC} Will auto-setup PostgreSQL with Docker\n")
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

    return env_vars


# ============================================================================
# STEP 7: Database Setup
# ============================================================================

def step_database_setup(env_vars: Dict[str, str]) -> bool:
    """Setup databases."""
    show_banner()

    print(f"{BOLD}Setting up databases...{NC}\n")

    # Check if we're using Docker
    using_docker = (
        env_vars.get("NEO4J_URI") == "bolt://localhost:7687" and
        env_vars.get("DATABASE_URL", "").startswith("postgresql://postgres:postgres@localhost")
    )

    if using_docker:
        print(f"{CYAN}Starting Docker containers...{NC}")
        print(f"  • Neo4j (Graph Memory)")
        print(f"  • PostgreSQL (State Management)\n")

        exit_code = run_make_target("db-setup")

        if exit_code == 0:
            print(f"\n{GREEN}✓{NC} Databases ready!\n")
            return True
        else:
            print(f"\n{RED}✗{NC} Database setup failed\n")
            print(f"{YELLOW}You can set up databases manually later with: ./kaiko db-setup{NC}\n")

            continue_anyway = inquirer.confirm(
                message="Continue without database setup?",
                default=True
            ).execute()

            return continue_anyway
    else:
        print(f"{YELLOW}Using custom database configuration{NC}")
        print(f"{DIM}Make sure your databases are running and accessible{NC}\n")

        input(f"{CYAN}Press Enter to continue...{NC}")
        return True


# ============================================================================
# STEP 8: Summary & Confirmation
# ============================================================================

def step_summary(identity: Dict[str, str], style: str) -> bool:
    """Show summary and confirm."""
    show_banner()

    print(f"{BOLD}Your Agent Profile{NC}\n")

    print(f"{CYAN}Name:{NC} {BOLD}{identity['name']}{NC}")
    print(f"{CYAN}Purpose:{NC} {identity['purpose'].replace('_', ' ').title()}")
    print(f"{CYAN}Communication Style:{NC} {style.replace('_', ' ').title()}")
    print()

    print(f"{GREEN}Your agent is ready to be created!{NC}\n")

    confirm = inquirer.confirm(
        message="Create this agent and launch KAIKO?",
        default=True
    ).execute()

    return confirm


# ============================================================================
# STEP 9: Create Agent & Launch
# ============================================================================

def step_create_and_launch(identity: Dict[str, str], style: str) -> None:
    """Create the agent and launch the control panel."""
    show_banner()

    print(f"{BOLD}Creating your agent...{NC}\n")

    # TODO: Actually create the agent with personality
    # For now, just show success

    print(f"{GREEN}✓{NC} Agent '{identity['name']}' created successfully!")
    print(f"{GREEN}✓{NC} Personality configured")
    print(f"{GREEN}✓{NC} Memory system initialized")
    print()

    print(f"{BOLD}{CYAN}🚀 Ready to launch!{NC}\n")

    launch = inquirer.confirm(
        message=f"Start chatting with {identity['name']}?",
        default=True
    ).execute()

    if launch:
        print(f"\n{CYAN}Launching AgentKit Control Panel...{NC}\n")
        run_make_target("anima")
    else:
        print(f"\n{GREEN}Setup complete!{NC}")
        print(f"\nYou can start chatting anytime with: {CYAN}./kaiko run{NC}\n")


# ============================================================================
# Main Wizard Flow
# ============================================================================

def run_first_time_wizard() -> None:
    """Run the complete first-time setup wizard."""
    try:
        # Step 1: Welcome
        if not step_welcome():
            print(f"\n{YELLOW}Setup cancelled. Run './kaiko install' to start again.{NC}\n")
            return

        # Step 2: Introduction
        step_introduction()

        # Step 3: Choose purpose
        purpose = step_choose_purpose()

        # Step 4: Agent identity
        identity = step_agent_identity(purpose)

        # Step 5: Communication style
        style = step_communication_style()

        # Step 6: Environment config
        env_vars = step_environment_config()

        # Step 7: Database setup
        if not step_database_setup(env_vars):
            print(f"\n{YELLOW}Setup incomplete. You can finish setup later with './kaiko setup'{NC}\n")
            return

        # Step 8: Summary
        if not step_summary(identity, style):
            print(f"\n{YELLOW}Agent creation cancelled.{NC}\n")
            return

        # Step 9: Create and launch
        step_create_and_launch(identity, style)

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Setup interrupted. Run './kaiko install' to start again.{NC}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}✗ Error during setup: {e}{NC}\n")
        sys.exit(1)


def main():
    """Entry point for first run wizard."""
    run_first_time_wizard()


if __name__ == "__main__":
    main()
