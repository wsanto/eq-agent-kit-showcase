"""
Plugin Registry for ANIMA AgentKit

Provides plugin discovery and registration by name.
"""

from typing import Dict, Type, Optional, Any
from loguru import logger

from .base import BasePlugin, PluginNotFoundError, PluginConfigurationError


class PluginRegistry:
    """
    Registry for plugin discovery and instantiation.

    The registry allows plugins to be registered by name and instantiated
    with configuration. This enables string-based plugin loading.

    Example:
        ```python
        # Register built-in plugins
        registry = PluginRegistry()
        registry.register_plugin("emotion", EmotionPlugin)
        registry.register_plugin("memory", MemoryPlugin)

        # Create plugin instance from name
        emotion_plugin = registry.create("emotion", config={
            "provider": "local"
        })
        ```
    """

    _instance: Optional['PluginRegistry'] = None
    _plugins: Dict[str, Type[BasePlugin]] = {}

    def __new__(cls):
        """Singleton pattern - only one registry instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.debug("🔌 PluginRegistry instance created")
        return cls._instance

    @classmethod
    def register_plugin(cls, name: str, plugin_class: Type[BasePlugin]) -> None:
        """
        Register a plugin class.

        Args:
            name: Unique name for the plugin
            plugin_class: Plugin class (must inherit from BasePlugin)

        Raises:
            PluginConfigurationError: If plugin_class is not a BasePlugin subclass
        """
        if not issubclass(plugin_class, BasePlugin):
            raise PluginConfigurationError(
                f"Plugin class {plugin_class} must inherit from BasePlugin"
            )

        cls._plugins[name] = plugin_class
        logger.debug(f"🔌 Plugin '{name}' registered: {plugin_class.__name__}")

    @classmethod
    def unregister_plugin(cls, name: str) -> None:
        """
        Unregister a plugin class.

        Args:
            name: Plugin name

        Raises:
            PluginNotFoundError: If plugin not found
        """
        if name not in cls._plugins:
            raise PluginNotFoundError(f"Plugin '{name}' not found in registry")

        del cls._plugins[name]
        logger.debug(f"🔌 Plugin '{name}' unregistered from registry")

    @classmethod
    def has_plugin(cls, name: str) -> bool:
        """
        Check if plugin is registered.

        Args:
            name: Plugin name

        Returns:
            True if plugin is registered
        """
        return name in cls._plugins

    @classmethod
    def get_plugin_class(cls, name: str) -> Type[BasePlugin]:
        """
        Get plugin class by name.

        Args:
            name: Plugin name

        Returns:
            Plugin class

        Raises:
            PluginNotFoundError: If plugin not found
        """
        if name not in cls._plugins:
            raise PluginNotFoundError(
                f"Plugin '{name}' not found. Available plugins: {cls.list_plugins()}"
            )

        return cls._plugins[name]

    @classmethod
    def create(
        cls,
        name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> BasePlugin:
        """
        Create a plugin instance from name.

        Args:
            name: Plugin name
            config: Optional configuration dictionary

        Returns:
            Plugin instance

        Raises:
            PluginNotFoundError: If plugin not found
            PluginConfigurationError: If plugin creation fails
        """
        plugin_class = cls.get_plugin_class(name)

        try:
            plugin_instance = plugin_class(config=config)
            logger.debug(f"✅ Created plugin instance: {name}")
            return plugin_instance
        except Exception as e:
            raise PluginConfigurationError(
                f"Failed to create plugin '{name}': {e}"
            ) from e

    @classmethod
    def list_plugins(cls) -> list[str]:
        """
        Get list of registered plugin names.

        Returns:
            List of plugin names
        """
        return list(cls._plugins.keys())

    @classmethod
    def get_plugin_info(cls) -> Dict[str, str]:
        """
        Get information about all registered plugins.

        Returns:
            Dictionary mapping plugin names to class names
        """
        return {
            name: plugin_class.__name__
            for name, plugin_class in cls._plugins.items()
        }

    @classmethod
    def clear(cls) -> None:
        """Clear all registered plugins (mainly for testing)."""
        cls._plugins.clear()
        logger.debug("🔌 Plugin registry cleared")


# Convenience function for registering plugins
def register_plugin(name: str, plugin_class: Type[BasePlugin]) -> None:
    """
    Register a plugin with the global registry.

    This is a convenience function that wraps PluginRegistry.register_plugin().

    Args:
        name: Unique name for the plugin
        plugin_class: Plugin class (must inherit from BasePlugin)

    Example:
        ```python
        from anima_agentkit.plugins import register_plugin, BasePlugin

        class MyPlugin(BasePlugin):
            pass

        register_plugin("my_plugin", MyPlugin)
        ```
    """
    PluginRegistry.register_plugin(name, plugin_class)


# Auto-register built-in plugins when available
def _register_builtin_plugins():
    """Register built-in plugins with the registry."""
    # This will be populated as we create built-in plugins
    # For now, it's empty - plugins will be registered in their own modules

    # Future plugins to register:
    # - emotion
    # - memory
    # - belief
    # - goal
    # - x402_billing
    # - tool_calling
    # - mcp
    # - analytics
    # - caching

    pass


# Register built-in plugins on import
_register_builtin_plugins()
