"""
Base Plugin System for ANIMA AgentKit

Provides abstract base class for all plugins with lifecycle hooks.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from loguru import logger


class BasePlugin(ABC):
    """
    Abstract base class for all ANIMA AgentKit plugins.

    Plugins can hook into the agent lifecycle at various points:
    - before_graph: Before graph execution starts
    - after_graph: After graph execution completes
    - before_node: Before each node execution
    - after_node: After each node execution
    - on_error: When an error occurs

    Example:
        ```python
        class MyPlugin(BasePlugin):
            async def before_graph(self, state):
                print("Starting graph execution")
                return state

            async def after_graph(self, state, result):
                print("Graph execution complete")
                return result
        ```
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the plugin.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.name = self.__class__.__name__
        self._enabled = True
        logger.debug(f"🔌 Initializing plugin: {self.name}")

    async def setup(self) -> None:
        """
        Setup the plugin (called once during agent initialization).

        Override this method to perform any initialization tasks like:
        - Connecting to external services
        - Loading configuration
        - Initializing caches
        """
        pass

    async def teardown(self) -> None:
        """
        Cleanup plugin resources (called during agent shutdown).

        Override this method to:
        - Close connections
        - Flush caches
        - Release resources
        """
        pass

    async def before_graph(self, state: "State") -> "State":
        """
        Hook called before graph execution starts.

        Use this to:
        - Modify initial state
        - Add context to state
        - Validate input

        Args:
            state: The initial state before graph execution

        Returns:
            Modified state (or original if no changes)
        """
        return state

    async def after_graph(self, state: "State", result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hook called after graph execution completes.

        Use this to:
        - Modify the final result
        - Log execution metadata
        - Track usage/billing

        Args:
            state: The final state after graph execution
            result: The graph execution result

        Returns:
            Modified result (or original if no changes)
        """
        return result

    async def before_node(self, node: str, state: "State") -> "State":
        """
        Hook called before each node execution.

        Use this to:
        - Add node-specific context
        - Validate state before node
        - Track node execution

        Args:
            node: Name of the node about to execute
            state: Current state before node execution

        Returns:
            Modified state (or original if no changes)
        """
        return state

    async def after_node(
        self,
        node: str,
        state: "State",
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Hook called after each node execution.

        Use this to:
        - Process node results
        - Update tracking/metrics
        - Modify node output

        Args:
            node: Name of the node that executed
            state: Current state after node execution
            result: Node execution result

        Returns:
            Modified result (or original if no changes)
        """
        return result

    async def on_error(
        self,
        error: Exception,
        state: "State",
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Hook called when an error occurs during execution.

        Use this to:
        - Log errors
        - Send alerts
        - Cleanup resources

        Args:
            error: The exception that occurred
            state: Current state when error occurred
            context: Additional context about the error
        """
        logger.error(f"🔌 Plugin {self.name} received error: {error}")

    def enable(self) -> None:
        """Enable the plugin."""
        self._enabled = True
        logger.info(f"✅ Plugin {self.name} enabled")

    def disable(self) -> None:
        """Disable the plugin."""
        self._enabled = False
        logger.info(f"⏸️  Plugin {self.name} disabled")

    def is_enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self._enabled

    def __repr__(self) -> str:
        """String representation of the plugin."""
        status = "enabled" if self._enabled else "disabled"
        return f"<{self.name} ({status})>"


class PluginError(Exception):
    """Base exception for plugin errors."""
    pass


class PluginNotFoundError(PluginError):
    """Raised when a plugin is not found."""
    pass


class PluginConfigurationError(PluginError):
    """Raised when plugin configuration is invalid."""
    pass
