"""
ANIMA AgentKit Plugin System

Provides a flexible plugin architecture for extending agent functionality.

Plugins can hook into the agent lifecycle at various points:
- before_graph: Before graph execution
- after_graph: After graph execution
- before_node: Before node execution
- after_node: After node execution
- on_error: When errors occur

Example:
    ```python
    from anima_agentkit.plugins import BasePlugin, PluginManager

    # Create a custom plugin
    class MyPlugin(BasePlugin):
        async def before_graph(self, state):
            print("Starting graph")
            return state

    # Use with agent
    from anima_agentkit import Agent

    agent = Agent(
        synapse_api_key="sk_xxx",
        llm="openai",
        plugins=[MyPlugin()]
    )
    ```
"""

from .base import (
    BasePlugin,
    PluginError,
    PluginNotFoundError,
    PluginConfigurationError
)
from .manager import PluginManager
from .registry import PluginRegistry, register_plugin

__all__ = [
    # Base classes
    'BasePlugin',

    # Plugin management
    'PluginManager',
    'PluginRegistry',
    'register_plugin',

    # Exceptions
    'PluginError',
    'PluginNotFoundError',
    'PluginConfigurationError',
]

__version__ = '2.0.0'
