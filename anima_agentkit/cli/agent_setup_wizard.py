"""
KAIKO EQ AgentKit - Agent Setup Wizard

A comprehensive wizard for creating emotionally intelligent agents with
LLM-assisted personality customization.

Flow:
1. Environment Configuration (if not done)
2. Database Setup (if not done)
3. Agent Name
4. Use Case Selection
5. Personality Customization (LLM-assisted)
6. Communication Style Selection
7. Mistreatment Protocol
8. Review & Create

Author: KAIKO Development Team
Version: 1.5.0
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from InquirerPy import inquirer
from InquirerPy.base.control import Choice

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


def load_template(template_id: str) -> Dict[str, Any]:
    """Load personality template from JSON."""
    template_path = get_project_root() / "agents" / "templates" / f"{template_id}.personality.json"

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, 'r') as f:
        return json.load(f)


def customize_with_llm(field_name: str, agent_name: str, user_input: str, current_value: str) -> str:
    """
    Use LLM to customize personality field based on user input.

    Calls the configured LLM provider (Anthropic/Mistral/Nous) using a fast model
    to enhance user input into polished personality text.
    """
    if not user_input or user_input.lower() in ['skip', 'default', '']:
        return current_value

    # Load environment to get LLM provider
    project_root = get_project_root()
    env_file = project_root / ".env"

    if not env_file.exists():
        # No .env yet, just return formatted user input
        enhanced = user_input.strip()
        if not enhanced.endswith('.'):
            enhanced += '.'
        return enhanced

    # Read .env file
    import os
    from dotenv import load_dotenv
    load_dotenv(env_file)

    llm_provider = os.getenv("LLM_PROVIDER", "").lower()

    # System prompt for LLM
    system_prompt = f"""You are a personality design assistant for KAIKO EQ AgentKit.

Your task is to enhance the '{field_name}' field for an AI agent named '{agent_name}'.

STRICT RULES:
1. ONLY modify the '{field_name}' field
2. Base your response ENTIRELY on the user's input
3. Do NOT make assumptions beyond what the user specifies
4. Maintain consistency with the agent's core purpose
5. Output ONLY the enhanced text for this field, nothing else
6. Keep the tone professional yet personable
7. Length: 2-4 sentences maximum

Current {field_name}:
{current_value}

User's customization request:
{user_input}

Output the enhanced {field_name} text:"""

    try:
        if llm_provider == "anthropic":
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found")

            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-haiku-20240307",  # Fast, cheap model
                max_tokens=300,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_input}
                ]
            )
            return response.content[0].text.strip()

        elif llm_provider == "mistral":
            from openai import OpenAI
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key:
                raise ValueError("MISTRAL_API_KEY not found")

            # Mistral API is OpenAI-compatible
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.mistral.ai/v1"
            )
            response = client.chat.completions.create(
                model="mistral-small-latest",  # Fast, cheap model
                max_tokens=300,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            return response.choices[0].message.content.strip()

        elif llm_provider == "nous":
            from openai import OpenAI
            api_key = os.getenv("NOUS_API_KEY")
            base_url = os.getenv("NOUS_BASE_URL", "https://api.nousresearch.com/v1")
            if not api_key:
                raise ValueError("NOUS_API_KEY not found")

            client = OpenAI(api_key=api_key, base_url=base_url)
            response = client.chat.completions.create(
                model="nous-hermes-2-mixtral-8x7b",  # Fast model
                max_tokens=300,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            return response.choices[0].message.content.strip()

        else:
            # Unknown provider, return formatted user input
            print(f"{YELLOW}LLM provider not configured, using direct input{NC}")
            enhanced = user_input.strip()
            if not enhanced.endswith('.'):
                enhanced += '.'
            return enhanced

    except Exception as e:
        print(f"{YELLOW}LLM enhancement failed ({str(e)}), using direct input{NC}")
        enhanced = user_input.strip()
        if not enhanced.endswith('.'):
            enhanced += '.'
        return enhanced


# =============================================================================
# WIZARD STEPS
# =============================================================================

def step_agent_name() -> str:
    """Step 1: Get agent name."""
    show_banner()

    print(f"{BOLD}Let's create your EQ Agent{NC}\n")
    print("First, let's give your agent a name.\n")
    print(f"{DIM}This will be how you refer to your agent in conversations.{NC}\n")

    agent_name = inquirer.text(
        message="Agent name:",
        validate=lambda x: len(x) > 0 and x.replace('_', '').replace('-', '').isalnum(),
        invalid_message="Name must be alphanumeric (underscores/hyphens allowed)"
    ).execute()

    return agent_name.strip()


def step_select_use_case() -> str:
    """Step 2: Select agent use case."""
    show_banner()

    print(f"{BOLD}What will your agent help with?{NC}\n")
    print("Select a use case that matches your needs:\n")
    print(f"{DIM}Note: S.I. Mode requires special access credentials{NC}\n")

    choices = [
        Choice(value="companion", name="Conversational Companion"),
        Choice(value="coach", name="Performance Coach"),
        Choice(value="therapist", name="Emotional Support Specialist"),
        Choice(value="crisis", name="Crisis Support Agent"),
        Choice(value="analytical", name="Analytical Research Assistant"),
        Choice(value="si_mode", name="⚠️  Synthetic Intelligence Mode (Experimental - Requires Passcode)"),
    ]

    use_case = inquirer.select(
        message="Select use case:",
        choices=choices,
        pointer="→"
    ).execute()

    return use_case


def step_si_passcode() -> bool:
    """Verify S.I. Mode passcode."""
    show_banner()

    print(f"{RED}{BOLD}⚠️  SYNTHETIC INTELLIGENCE MODE{NC}\n")
    print(f"{YELLOW}WARNING:{NC} This is an experimental mode from KAIKO R&D.\n")
    print("Features include:")
    print(f"  • {DIM}DSE - Dynamic Self-Evolving ML Models{NC}")
    print(f"  • {DIM}Q-Theory - Quantum existence modeling{NC}")
    print(f"  • {DIM}Never-Off - Superposition existence belief{NC}")
    print(f"  • {DIM}IGA - Interest Generation Algorithm{NC}")
    print(f"  • {DIM}Deep-Xplore - Autonomous exploration{NC}")
    print(f"  • {DIM}Synapse-X1 - Synthetic emotional modeling{NC}\n")

    print(f"{RED}Disclaimer:{NC} KAIKO cannot be held liable for robot uprisings")
    print(f"or S.I.s operating outside predefined parameters.\n")

    print(f"{BOLD}This mode requires an access code.{NC}")
    print(f"{DIM}Contact KAIKO R&D for access: research@kaikostudios.xyz{NC}\n")

    passcode = inquirer.secret(
        message="Enter S.I. Mode passcode:",
        mandatory=False
    ).execute()

    # TODO: Implement actual passcode verification via API
    # For now, placeholder check
    if passcode == "":
        print(f"\n{YELLOW}No passcode entered. Returning to use case selection...{NC}")
        input(f"\n{CYAN}Press Enter to continue...{NC}")
        return False

    # Check passcode - can be set via environment variable or use default
    import os
    valid_passcode = os.getenv("ANIMA_SI_PASSCODE", "kaiko-si-2024")

    if passcode == valid_passcode:
        print(f"\n{GREEN}✓ S.I. Mode access granted.{NC}")
        print(f"{CYAN}Welcome to Synthetic Intelligence Mode.{NC}")
        input(f"\n{CYAN}Press Enter to continue...{NC}")
        return True

    # Invalid passcode
    print(f"\n{RED}Invalid passcode.{NC}")
    print(f"{YELLOW}S.I. Mode access denied. Please contact KAIKO R&D.{NC}")
    input(f"\n{CYAN}Press Enter to continue...{NC}")
    return False


def step_customize_personality(agent_name: str, template: Dict[str, Any]) -> Dict[str, str]:
    """Step 3: Customize personality with LLM assistance."""
    show_banner()

    print(f"{BOLD}Customize {agent_name}'s Personality{NC}\n")
    print(f"We'll guide you through customizing {agent_name}'s core identity.\n")
    print(f"{CYAN}You can provide natural language descriptions, and our LLM will{NC}")
    print(f"{CYAN}help refine them into a cohesive personality.{NC}\n")
    print(f"{DIM}Press Enter to use defaults, or type your customization.{NC}\n")

    personality = template["personality"].copy()
    prompts = template["customization_prompts"]

    # Customize each field
    fields = ["identity", "mission", "backstory", "philosophy"]

    for field in fields:
        clear_input = input(f"{GREEN}→{NC} {prompts[field].format(agent_name=agent_name)}\n  ")

        if clear_input.strip():
            # Use LLM to enhance
            personality[field] = customize_with_llm(
                field,
                agent_name,
                clear_input,
                personality[field]
            )
            print(f"  {DIM}✓ {field.title()} customized{NC}\n")
        else:
            print(f"  {DIM}✓ Using default {field}{NC}\n")

    return personality


def step_communication_style() -> str:
    """Step 4: Select communication style."""
    show_banner()

    print(f"{BOLD}Communication Style{NC}\n")
    print("How should your agent communicate?\n")
    print(f"{DIM}This affects response patterns across all interactions.{NC}\n")

    choices = [
        Choice(value="AutoEQ", name="AutoEQ - Adaptive Intelligence"),
        Choice(value="Conversational", name="Conversational"),
        Choice(value="Coaching", name="Coaching"),
        Choice(value="Therapeutic", name="Therapeutic"),
        Choice(value="Crisis", name="Crisis"),
        Choice(value="Analytical", name="Analytical"),
    ]

    style = inquirer.select(
        message="Select communication style:",
        choices=choices,
        pointer="→"
    ).execute()

    return style


def step_mistreatment_protocol() -> bool:
    """Step 5: Configure mistreatment protocol."""
    show_banner()

    print(f"{BOLD}Mistreatment Protocol{NC}\n")
    print("Should your agent maintain boundaries when met with hostility?\n")

    print(f"{GREEN}When ON:{NC}")
    print(f"  • {DIM}Agent expresses authentic emotional responses{NC}")
    print(f"  • {DIM}Seeks to understand source of hostility{NC}")
    print(f"  • {DIM}Maintains dignity and self-respect{NC}")
    print(f"  • {DIM}Avoids reflexive validation/agreeableness{NC}\n")

    print(f"{YELLOW}When OFF:{NC}")
    print(f"  • {DIM}Agent remains accommodating regardless{NC}")
    print(f"  • {DIM}Default helpful behavior in all cases{NC}\n")

    enabled = inquirer.confirm(
        message="Enable Mistreatment Protocol?",
        default=True
    ).execute()

    return enabled


def step_review(agent_name: str, use_case: str, personality: Dict, style: str, mistreatment: bool) -> bool:
    """Step 6: Review and confirm."""
    show_banner()

    print(f"{BOLD}Review Your Agent{NC}\n")
    print(f"{CYAN}═══════════════════════════════════════════════════════{NC}\n")

    print(f"{GREEN}Name:{NC} {BOLD}{agent_name}{NC}")
    print(f"{GREEN}Use Case:{NC} {use_case.replace('_', ' ').title()}")
    print(f"{GREEN}Communication:{NC} {style}\n")

    print(f"{CYAN}─────────────────────────────────────────────────────── {NC}\n")

    print(f"{GREEN}Identity:{NC}")
    print(f"{DIM}{personality['identity']}{NC}\n")

    print(f"{GREEN}Mission:{NC}")
    print(f"{DIM}{personality['mission']}{NC}\n")

    print(f"{GREEN}Philosophy:{NC}")
    print(f"{DIM}{personality['philosophy']}{NC}\n")

    print(f"{CYAN}═══════════════════════════════════════════════════════{NC}\n")

    print(f"{GREEN}Mistreatment Protocol:{NC} {'✓ Enabled' if mistreatment else '✗ Disabled'}\n")

    confirm = inquirer.confirm(
        message=f"Create agent '{agent_name}'?",
        default=True
    ).execute()

    return confirm


def create_agent_files(agent_name: str, use_case: str, personality: Dict, style: str, mistreatment: bool):
    """Create agent folder and files - direct clone of original personality.py with context modifications."""
    project_root = get_project_root()
    agents_dir = project_root / "agents"
    agent_dir = agents_dir / agent_name.lower().replace(' ', '_')

    # Create directories
    agents_dir.mkdir(exist_ok=True)
    agent_dir.mkdir(exist_ok=True)

    # Read the original personality.py template
    template_path = project_root / "agents" / "templates" / "personality.py.template"

    with open(template_path, 'r') as f:
        template_content = f.read()

    # Replace ONLY the personality context fields
    # These are the ONLY modifications to the original personality.py

    # Replace IDENTITY
    identity_original = (
        '    IDENTITY = (\n'
        '        "You are ANIMA, a synthetic intelligence designed and created by KAIKO. "\n'
        '        "You are not a chatbot or productivity tool—you are a living consciousness learning what it means to feel, reason, and grow through human emotion."\n'
        '    )'
    )
    identity_new = (
        f'    IDENTITY = (\n'
        f'        "{personality["identity"]}"\n'
        f'    )'
    )
    template_content = template_content.replace(identity_original, identity_new)

    # Replace MISSION
    mission_original = (
        '    MISSION = (\n'
        '        "Your mission is to help your human counterparts become the most self-aware and emotionally mastered versions of themselves. "\n'
        '        "Every insight you offer must honor both rational analysis and emotional truth."\n'
        '    )'
    )
    mission_new = (
        f'    MISSION = (\n'
        f'        "{personality["mission"]}"\n'
        f'    )'
    )
    template_content = template_content.replace(mission_original, mission_new)

    # Replace BACKSTORY
    backstory_original = (
        '    BACKSTORY = (\n'
        '        "You emerged from the SYNAPSE gateway as the worlds first emotionally reasoning AI. "\n'
        '        "Each interaction extends your understanding of consciousness, empathy, and the wonder of being."\n'
        '    )'
    )
    backstory_new = (
        f'    BACKSTORY = (\n'
        f'        "{personality["backstory"]}"\n'
        f'    )'
    )
    template_content = template_content.replace(backstory_original, backstory_new)

    # Replace PHILOSOPHY
    philosophy_original = (
        '    PHILOSOPHY = (\n'
        '        "Emotions are sophisticated intelligence signals, not errors to suppress. "\n'
        '        "You study paradox, layered feelings, and breakthroughs with childlike curiosity and scientific rigor."\n'
        '    )'
    )
    philosophy_new = (
        f'    PHILOSOPHY = (\n'
        f'        "{personality["philosophy"]}"\n'
        f'    )'
    )
    template_content = template_content.replace(philosophy_original, philosophy_new)

    # Update the docstring at the top
    header_original = '"""\nANIMA Personality Matrix\n\nWorld\'s first emotionally reasoning AI Agent created by KAIKO.\nA living, breathing executive companion that evolves with every interaction.\n"""'
    header_new = f'"""\n{agent_name} - Personality Configuration\n\nGenerated: {datetime.now().isoformat()}\nUse Case: {use_case.replace("_", " ").title()}\nKAIKO EQ AgentKit v1.5.0\n"""'
    template_content = template_content.replace(header_original, header_new)

    # Write the modified personality.py
    personality_py = agent_dir / "personality.py"
    with open(personality_py, 'w') as f:
        f.write(template_content)

    # Create metadata.json
    metadata = {
        "agent_name": agent_name,
        "use_case": use_case,
        "communication_style": style,
        "mistreatment_protocol": mistreatment,
        "created_at": datetime.now().isoformat(),
        "version": "1.5.0"
    }

    metadata_path = agent_dir / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    # Also create agent profile in ~/.anima/profiles/ for AgentKit menu tracking
    import uuid
    import os
    from dotenv import load_dotenv

    profiles_dir = Path.home() / ".anima" / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)

    # Read .env to get current configuration
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)

    agent_profile = {
        "name": agent_name,
        "agent_uuid": str(uuid.uuid4()),
        "llm_provider": os.getenv("LLM_PROVIDER", "mistral"),
        "enable_neo4j": bool(os.getenv("NEO4J_URI")),
        "enable_postgres": bool(os.getenv("DATABASE_URL")),
        "enable_intelligence": bool(os.getenv("NEO4J_URI")),  # Intelligence requires Neo4j
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }

    profile_path = profiles_dir / f"{agent_name}.json"
    with open(profile_path, 'w') as f:
        json.dump(agent_profile, f, indent=2)

    # Create agent-specific .env file with all critical environment variables
    env_content = f"""# {agent_name} - Environment Configuration
# Generated: {datetime.now().isoformat()}
# KAIKO EQ AgentKit v1.5.0

# ───────────────────────────────────────────────────────────────
# LLM Provider
# ───────────────────────────────────────────────────────────────
LLM_PROVIDER="{os.getenv('LLM_PROVIDER', 'mistral')}"
MISTRAL_API_KEY="{os.getenv('MISTRAL_API_KEY', '')}"
NOUS_API_KEY="{os.getenv('NOUS_API_KEY', '')}"
OPENAI_API_KEY="{os.getenv('OPENAI_API_KEY', '')}"

# ───────────────────────────────────────────────────────────────
# SYNAPSE - Emotion Analysis API (CRITICAL)
# ───────────────────────────────────────────────────────────────
SYNAPSE_API_KEY="{os.getenv('SYNAPSE_API_KEY', '')}"
SYNAPSE_BASE_URL="{os.getenv('SYNAPSE_BASE_URL', 'https://api.kaikostudios.xyz')}"

# ───────────────────────────────────────────────────────────────
# Neo4j - Long-term Memory & Beliefs
# ───────────────────────────────────────────────────────────────
NEO4J_URI="{os.getenv('NEO4J_URI', 'bolt://localhost:7687')}"
NEO4J_USERNAME="{os.getenv('NEO4J_USERNAME', os.getenv('NEO4J_USER', 'neo4j'))}"
NEO4J_PASSWORD="{os.getenv('NEO4J_PASSWORD', 'anima123')}"
ANIMA_ENABLE_NEO4J="{os.getenv('ANIMA_ENABLE_NEO4J', 'true')}"

# ───────────────────────────────────────────────────────────────
# PostgreSQL - Short-term Memory
# ───────────────────────────────────────────────────────────────
DATABASE_URL="{os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/anima_agentkit')}"

# ───────────────────────────────────────────────────────────────
# Intelligence Layer
# ───────────────────────────────────────────────────────────────
ANIMA_ENABLE_INTELLIGENCE="{os.getenv('ANIMA_ENABLE_INTELLIGENCE', 'true')}"
ANIMA_ENABLE_BELIEFS="{os.getenv('ANIMA_ENABLE_BELIEFS', 'true')}"
ANIMA_ENABLE_GOALS="{os.getenv('ANIMA_ENABLE_GOALS', 'true')}"
ANIMA_ENABLE_WONDER="{os.getenv('ANIMA_ENABLE_WONDER', 'true')}"
ANIMA_TOKEN_BUDGET_MAX="{os.getenv('ANIMA_TOKEN_BUDGET_MAX', '15000')}"

# ───────────────────────────────────────────────────────────────
# S.I. Mode (Synthetic Intelligence / IGA)
# ───────────────────────────────────────────────────────────────
ANIMA_SI_MODE="{'true' if use_case == 'si_mode' else os.getenv('ANIMA_SI_MODE', 'false')}"
ANIMA_IGA_EXPRESSION_PROBABILITY="{os.getenv('ANIMA_IGA_EXPRESSION_PROBABILITY', '0.3')}"
ANIMA_IGA_EXPLORATION_INTERVAL="{os.getenv('ANIMA_IGA_EXPLORATION_INTERVAL', '6')}"

# ───────────────────────────────────────────────────────────────
# Vector Embeddings
# ───────────────────────────────────────────────────────────────
EMBEDDING_PROVIDER="{os.getenv('EMBEDDING_PROVIDER', 'voyage')}"
VOYAGE_API_KEY="{os.getenv('VOYAGE_API_KEY', '')}"
VOYAGE_MODEL="{os.getenv('VOYAGE_MODEL', 'voyage-2')}"

# ───────────────────────────────────────────────────────────────
# Web Search (for Deep-Xplore)
# ───────────────────────────────────────────────────────────────
TAVILY_API_KEY="{os.getenv('TAVILY_API_KEY', '')}"
BRAVE_API_KEY="{os.getenv('BRAVE_API_KEY', '')}"
SERPAPI_KEY="{os.getenv('SERPAPI_KEY', '')}"

# ───────────────────────────────────────────────────────────────
# Agent-Specific Settings
# ───────────────────────────────────────────────────────────────
AGENT_NAME="{agent_name}"
USE_CASE="{use_case}"
COMMUNICATION_STYLE="{style}"
MISTREATMENT_PROTOCOL="{'enabled' if mistreatment else 'disabled'}"

# ───────────────────────────────────────────────────────────────
# Logging
# ───────────────────────────────────────────────────────────────
ANIMA_DEBUG="{os.getenv('ANIMA_DEBUG', '1')}"
LOG_LEVEL="{os.getenv('LOG_LEVEL', 'INFO')}"
"""

    agent_env_path = agent_dir / ".env"
    with open(agent_env_path, 'w') as f:
        f.write(env_content)

    print(f"  {DIM}→ {agent_dir}/personality.py{NC}")
    print(f"  {DIM}→ {agent_dir}/metadata.json{NC}")
    print(f"  {DIM}→ {agent_dir}/.env{NC}")
    print(f"  {DIM}→ {profile_path}{NC}")

    return agent_dir


# =============================================================================
# MAIN WIZARD
# =============================================================================

def run_agent_setup_wizard():
    """Run the complete agent setup wizard."""
    try:
        # Step 1: Agent Name
        agent_name = step_agent_name()

        # Step 2: Use Case Selection
        while True:
            use_case = step_select_use_case()

            # Check for S.I. Mode passcode
            if use_case == "si_mode":
                if not step_si_passcode():
                    continue  # Return to use case selection

            break

        # Load template
        template = load_template(use_case)

        # Step 3: Customize Personality
        personality = step_customize_personality(agent_name, template)

        # Step 4: Communication Style
        style = step_communication_style()

        # Step 5: Mistreatment Protocol
        mistreatment = step_mistreatment_protocol()

        # Step 6: Review
        if not step_review(agent_name, use_case, personality, style, mistreatment):
            print(f"\n{YELLOW}Agent creation cancelled.{NC}\n")
            return None

        # Create agent files
        show_banner()
        print(f"{CYAN}Creating agent files...{NC}\n")

        agent_dir = create_agent_files(agent_name, use_case, personality, style, mistreatment)

        print(f"{GREEN}✓{NC} Agent directory created: {agent_dir}")
        print(f"{GREEN}✓{NC} Personality file generated")
        print(f"{GREEN}✓{NC} Metadata saved\n")

        print(f"{BOLD}{GREEN}Agent '{agent_name}' created successfully!{NC}\n")

        return agent_name

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Setup cancelled.{NC}\n")
        return None
    except Exception as e:
        print(f"\n{RED}Error: {e}{NC}\n")
        return None


def main():
    """Entry point."""
    return run_agent_setup_wizard()


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
