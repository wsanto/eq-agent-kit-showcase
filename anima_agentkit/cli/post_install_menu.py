"""
Post-Installation Interactive Menu for KAIKO EQ AgentKit.

Provides a unified menu system that appears after successful installation,
allowing users to immediately start using the system without exiting.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional

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
NC = "\033[0m"  # No Color / Reset

KAIKO_BANNER = f"""{ORANGE}
  ██╗  ██╗ █████╗ ██╗██╗  ██╗ ██████╗
  ██║ ██╔╝██╔══██╗██║██║ ██╔╝██╔═══██╗
  █████╔╝ ███████║██║█████╔╝ ██║   ██║
  ██╔═██╗ ██╔══██║██║██╔═██╗ ██║   ██║
  ██║  ██╗██║  ██║██║██║  ██╗╚██████╔╝
  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝
{NC}
        KAIKO EQ AgentKit v1.5.0
"""


def get_project_root() -> Path:
    """Get the project root directory."""
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / "setup.py").exists():
            return current
        current = current.parent
    return Path.cwd()


def run_make_target(target: str) -> int:
    """
    Run a Makefile target.

    Args:
        target: The make target to run

    Returns:
        Exit code from the make command
    """
    project_root = get_project_root()
    cmd = ["make", "-C", str(project_root), target]
    result = subprocess.run(cmd)
    return result.returncode


def enter_control_panel():
    """Launch the AgentKit Control Panel (interactive chat)."""
    print(f"\n{CYAN}🚀 Launching AgentKit Control Panel...{NC}\n")

    # Get list of available agents
    from pathlib import Path
    import json

    profiles_dir = Path.home() / ".anima" / "profiles"
    agents = ["default"]

    if profiles_dir.exists():
        for profile_file in profiles_dir.glob("*.json"):
            agent_name = profile_file.stem
            if agent_name != "default":
                agents.append(agent_name)

    # Also check agents directory
    project_root = get_project_root()
    agents_dir = project_root / "agents"
    if agents_dir.exists():
        for agent_folder in agents_dir.iterdir():
            if agent_folder.is_dir() and agent_folder.name not in agents and not agent_folder.name.startswith('.'):
                agents.append(agent_folder.name)

    # Ask user which agent to chat with
    if len(agents) > 1:
        agent_choices = [Choice(value=a, name=a) for a in agents]
        selected_agent = inquirer.select(
            message="Select agent to chat with:",
            choices=agent_choices,
            default=agents[0],
            pointer="➤",
        ).execute()
    else:
        selected_agent = "default"

    # Ask if verbose mode
    verbose = inquirer.confirm(
        message="Enable verbose logging? (shows full pipeline)",
        default=False
    ).execute()

    # Build make command with arguments
    project_root = get_project_root()
    cmd = ["make", "-C", str(project_root), "chat"]

    if selected_agent != "default":
        cmd.append(f"AGENT={selected_agent}")

    if verbose:
        cmd.append("VERBOSE=1")

    print(f"\n{CYAN}Starting chat with agent: {selected_agent}{NC}")
    if verbose:
        print(f"{YELLOW}Verbose mode enabled - showing full pipeline logs{NC}")
    print()

    result = subprocess.run(cmd)
    return result.returncode


def test_configuration():
    """Run configuration and dependency tests."""
    print(f"\n{CYAN}🔍 Running configuration tests...{NC}\n")
    return run_make_target("validate")


def set_environment_variables():
    """Guide user through setting global environment variables."""
    print(f"\n{YELLOW}🔧 Environment Variable Configuration{NC}\n")
    print("This will help you configure the following environment variables:")
    print(f"  • {BOLD}ANTHROPIC_API_KEY{NC} - For Claude AI models")
    print(f"  • {BOLD}OPENAI_API_KEY{NC} - For OpenAI models (optional)")
    print(f"  • {BOLD}NEO4J_URI{NC} - Neo4j database connection")
    print(f"  • {BOLD}NEO4J_USER{NC} - Neo4j username")
    print(f"  • {BOLD}NEO4J_PASSWORD{NC} - Neo4j password")
    print(f"  • {BOLD}DATABASE_URL{NC} - PostgreSQL connection string")
    print()

    # Determine shell config file
    shell = Path.home() / ".bashrc"
    if (Path.home() / ".zshrc").exists():
        shell = Path.home() / ".zshrc"

    print(f"Environment variables will be added to: {CYAN}{shell}{NC}")
    print()

    # Ask if they want to proceed
    proceed = inquirer.confirm(
        message="Would you like to configure environment variables now?",
        default=True
    ).execute()

    if not proceed:
        print(f"{YELLOW}⚠️  Skipping environment variable configuration.{NC}")
        print(f"You can manually edit {shell} or run this again later.\n")
        return 0

    # Collect environment variables
    env_vars = {}

    # ANTHROPIC_API_KEY (required)
    env_vars["ANTHROPIC_API_KEY"] = inquirer.text(
        message="Enter your ANTHROPIC_API_KEY:",
        mandatory=True,
    ).execute()

    # OPENAI_API_KEY (optional)
    use_openai = inquirer.confirm(
        message="Do you want to configure OpenAI API key? (optional)",
        default=False
    ).execute()

    if use_openai:
        env_vars["OPENAI_API_KEY"] = inquirer.text(
            message="Enter your OPENAI_API_KEY:",
            mandatory=False,
        ).execute()

    # Neo4j configuration
    print(f"\n{BOLD}Neo4j Configuration:{NC}")
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
    print(f"\n{BOLD}PostgreSQL Configuration:{NC}")
    env_vars["DATABASE_URL"] = inquirer.text(
        message="PostgreSQL DATABASE_URL:",
        default="postgresql://postgres:postgres@localhost:5432/anima_agentkit",
    ).execute()

    # Write to shell config
    try:
        with open(shell, "a") as f:
            f.write("\n# KAIKO EQ AgentKit Environment Variables\n")
            for key, value in env_vars.items():
                if value:  # Only write non-empty values
                    f.write(f'export {key}="{value}"\n')

        print(f"\n{GREEN}✅ Environment variables written to {shell}{NC}")
        print(f"{YELLOW}⚠️  Please run: source {shell}{NC}")
        print(f"   Or restart your terminal for changes to take effect.\n")
        return 0

    except Exception as e:
        print(f"\n{RED}❌ Error writing to {shell}: {e}{NC}\n")
        return 1


def show_help():
    """Display help information about CLI commands."""
    print(f"\n{BOLD}{CYAN}KAIKO CLI Commands{NC}\n")

    help_text = f"""
{BOLD}Core Commands:{NC}
  {GREEN}kaiko install{NC}          Complete installation with dependencies
  {GREEN}kaiko run{NC}              Launch AgentKit Control Panel (interactive chat)
  {GREEN}kaiko setup{NC}            Run agent setup wizard
  {GREEN}kaiko test{NC}             Validate configuration and dependencies

{BOLD}Agent Management:{NC}
  {GREEN}kaiko chat{NC}             Start a chat session
  {GREEN}kaiko agents{NC}           List available agents

{BOLD}Development:{NC}
  {GREEN}kaiko dev{NC}              Start development environment
  {GREEN}kaiko logs{NC}             View application logs
  {GREEN}kaiko clean{NC}            Clean build artifacts

{BOLD}Database:{NC}
  {GREEN}kaiko db-setup{NC}         Initialize databases (Neo4j + PostgreSQL)
  {GREEN}kaiko db-reset{NC}         Reset databases (WARNING: deletes all data)

{BOLD}Help:{NC}
  {GREEN}kaiko help{NC}             Show this help message
  {GREEN}kaiko --version{NC}        Show version information
  {GREEN}kaiko --help{NC}           Show detailed help

{BOLD}Documentation:{NC}
  For full documentation, visit: {CYAN}https://github.com/kaiko-studios/anima-agentkit{NC}

{BOLD}Examples:{NC}
  {YELLOW}# Install the system{NC}
  kaiko install

  {YELLOW}# Run the interactive control panel{NC}
  kaiko run

  {YELLOW}# Create a new agent{NC}
  kaiko setup

  {YELLOW}# Test your configuration{NC}
  kaiko test
"""
    print(help_text)

    input(f"\n{CYAN}Press Enter to return to menu...{NC}")
    return 0


def show_menu() -> Optional[str]:
    """
    Display the main menu (post-setup) and get user choice.

    Returns:
        The selected menu action, or None to exit
    """
    print("\n" + KAIKO_BANNER)
    print(f"{CYAN}KAIKO Control Center{NC}\n")

    choices = [
        Choice(value="control_panel", name="Launch Agent Control Panel"),
        Choice(value="create_agent", name="Create New Agent"),
        Choice(value="manage_agents", name="Manage Agents"),
        Separator(),
        Choice(value="test", name="Test Configuration"),
        Choice(value="env", name="Configure Environment"),
        Choice(value="help", name="Help & Commands"),
        Separator(),
        Choice(value="exit", name="Exit"),
    ]

    action = inquirer.select(
        message="What would you like to do?",
        choices=choices,
        default="control_panel",
        pointer="➤",
    ).execute()

    return action


def run_menu_loop():
    """
    Main menu loop - keeps running until user exits.
    """
    while True:
        try:
            action = show_menu()

            if action == "exit" or action is None:
                print(f"\n{GREEN}Thank you for using KAIKO EQ AgentKit!{NC}")
                print(f"{CYAN}Run 'kaiko run' anytime to start the Control Panel.{NC}\n")
                break

            elif action == "control_panel":
                exit_code = enter_control_panel()
                if exit_code != 0:
                    print(f"\n{YELLOW}⚠️  Control Panel exited with code {exit_code}{NC}")
                # Return to menu after exiting control panel

            elif action == "test":
                exit_code = test_configuration()
                if exit_code != 0:
                    print(f"\n{YELLOW}⚠️  Tests completed with errors. Check output above.{NC}")
                else:
                    print(f"\n{GREEN}✅ All tests passed!{NC}")
                input(f"\n{CYAN}Press Enter to return to menu...{NC}")

            elif action == "env":
                set_environment_variables()
                input(f"\n{CYAN}Press Enter to return to menu...{NC}")

            elif action == "help":
                show_help()

            elif action == "create_agent":
                print(f"\n{CYAN}🚀 Launching Agent Creation Wizard...{NC}\n")
                # TODO: Launch agent setup wizard
                from anima_agentkit.cli.first_run_wizard import step_choose_purpose, step_agent_identity, step_communication_style
                try:
                    purpose = step_choose_purpose()
                    identity = step_agent_identity(purpose)
                    style = step_communication_style()
                    print(f"\n{GREEN}✅ Agent '{identity['name']}' created!{NC}")
                except Exception as e:
                    print(f"\n{RED}❌ Error creating agent: {e}{NC}")
                input(f"\n{CYAN}Press Enter to return to menu...{NC}")

            elif action == "manage_agents":
                print(f"\n{CYAN}📋 Agent Management{NC}\n")
                print(f"{YELLOW}Coming soon: List, switch, edit, and delete agents{NC}\n")
                input(f"{CYAN}Press Enter to return to menu...{NC}")

        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}Interrupted. Exiting...{NC}\n")
            break
        except Exception as e:
            print(f"\n{RED}❌ Error: {e}{NC}\n")
            input(f"{CYAN}Press Enter to return to menu...{NC}")


def main():
    """Entry point for the post-installation menu."""
    try:
        run_menu_loop()
    except Exception as e:
        print(f"\n{RED}❌ Fatal error: {e}{NC}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
