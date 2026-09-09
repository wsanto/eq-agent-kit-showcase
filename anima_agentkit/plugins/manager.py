"""
Plugin Manager for ANIMA AgentKit

Manages plugin lifecycle and hook execution.
"""

from typing import Dict, List, Any, Optional, Union
from loguru import logger

from .base import BasePlugin, PluginError, PluginNotFoundError


class PluginManager:
    """
    Manages plugin registration, lifecycle, and hook execution.

    The PluginManager orchestrates all plugins registered with the agent,
    ensuring they are properly initialized, their hooks are called in order,
    and they are cleanly shut down.

    Example:
        ```python
        manager = PluginManager()
        manager.register("emotion", EmotionPlugin())
        manager.register("memory", MemoryPlugin())

        await manager.setup_all()

        # Execute hooks
        state = await manager.run_hook("before_graph", state)
        result = await manager.run_hook("after_graph", state, result)

        await manager.teardown_all()
        ```
    """

    def __init__(self):
        """Initialize the plugin manager."""
        self.plugins: Dict[str, BasePlugin] = {}
        self._setup_complete = False
        logger.debug("🔌 PluginManager initialized")

    def register(self, name: str, plugin: BasePlugin) -> None:
        """
        Register a plugin with the manager.

        Args:
            name: Unique name for the plugin
            plugin: Plugin instance

        Raises:
            PluginError: If plugin name already registered
        """
        if name in self.plugins:
            raise PluginError(f"Plugin '{name}' already registered")

        self.plugins[name] = plugin
        logger.info(f"✅ Plugin '{name}' registered: {plugin.__class__.__name__}")

    def unregister(self, name: str) -> None:
        """
        Unregister a plugin.

        Args:
            name: Name of plugin to unregister

        Raises:
            PluginNotFoundError: If plugin not found
        """
        if name not in self.plugins:
            raise PluginNotFoundError(f"Plugin '{name}' not found")

        plugin = self.plugins.pop(name)
        logger.info(f"🔌 Plugin '{name}' unregistered")

    def get(self, name: str) -> BasePlugin:
        """
        Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance

        Raises:
            PluginNotFoundError: If plugin not found
        """
        if name not in self.plugins:
            raise PluginNotFoundError(f"Plugin '{name}' not found")

        return self.plugins[name]

    def has(self, name: str) -> bool:
        """
        Check if plugin is registered.

        Args:
            name: Plugin name

        Returns:
            True if plugin is registered
        """
        return name in self.plugins

    def list_plugins(self) -> List[str]:
        """
        Get list of registered plugin names.

        Returns:
            List of plugin names
        """
        return list(self.plugins.keys())

    async def setup_all(self) -> None:
        """
        Setup all registered plugins.

        Calls setup() on each plugin in registration order.
        """
        logger.info(f"🔌 Setting up {len(self.plugins)} plugins...")

        for name, plugin in self.plugins.items():
            try:
                await plugin.setup()
                logger.debug(f"✅ Plugin '{name}' setup complete")
            except Exception as e:
                logger.error(f"❌ Plugin '{name}' setup failed: {e}")
                raise PluginError(f"Failed to setup plugin '{name}': {e}") from e

        self._setup_complete = True
        logger.info(f"✅ All plugins setup complete")

    async def teardown_all(self) -> None:
        """
        Teardown all registered plugins.

        Calls teardown() on each plugin in reverse registration order.
        """
        logger.info(f"🔌 Tearing down {len(self.plugins)} plugins...")

        # Teardown in reverse order
        for name in reversed(list(self.plugins.keys())):
            plugin = self.plugins[name]
            try:
                await plugin.teardown()
                logger.debug(f"✅ Plugin '{name}' teardown complete")
            except Exception as e:
                logger.error(f"❌ Plugin '{name}' teardown failed: {e}")
                # Continue with other plugins even if one fails

        logger.info(f"✅ All plugins torn down")

    async def run_hook(
        self,
        hook_name: str,
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """
        Run a hook across all enabled plugins.

        Hooks are executed in plugin registration order. Each plugin
        can modify the result, which is passed to the next plugin.

        Args:
            hook_name: Name of the hook to run (e.g., "before_graph")
            *args: Positional arguments for the hook
            **kwargs: Keyword arguments for the hook

        Returns:
            Final result after all plugins have processed it
        """
        # Get the initial result (last positional arg for most hooks)
        result = args[-1] if args else None

        for name, plugin in self.plugins.items():
            # Skip disabled plugins
            if not plugin.is_enabled():
                logger.debug(f"⏸️  Skipping disabled plugin '{name}' for hook '{hook_name}'")
                continue

            # Get the hook method
            hook_method = getattr(plugin, hook_name, None)

            if not hook_method or not callable(hook_method):
                logger.debug(f"🔌 Plugin '{name}' does not implement hook '{hook_name}'")
                continue

            try:
                # Execute the hook
                logger.debug(f"🔌 Running hook '{hook_name}' for plugin '{name}'")

                # Pass the current result as the last argument
                new_result = await hook_method(*args, **kwargs)

                # Update result if hook returned something
                if new_result is not None:
                    result = new_result
                    # Update args to pass modified result to next plugin
                    if args:
                        args = (*args[:-1], result)

            except Exception as e:
                logger.error(f"❌ Plugin '{name}' hook '{hook_name}' failed: {e}")
                # Call on_error hook for this plugin
                try:
                    context = {
                        "hook": hook_name,
                        "args": args,
                        "kwargs": kwargs
                    }
                    await plugin.on_error(e, args[0] if args else None, context)
                except Exception as error_hook_error:
                    logger.error(f"❌ Plugin '{name}' on_error hook also failed: {error_hook_error}")

                # Re-raise the original error
                raise PluginError(f"Plugin '{name}' hook '{hook_name}' failed: {e}") from e

        return result

    async def run_hook_safe(
        self,
        hook_name: str,
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """
        Run a hook across all plugins, catching and logging errors.

        Unlike run_hook(), this method does not raise exceptions.
        Errors are logged and execution continues with remaining plugins.

        Args:
            hook_name: Name of the hook to run
            *args: Positional arguments for the hook
            **kwargs: Keyword arguments for the hook

        Returns:
            Final result after all plugins have processed it
        """
        result = args[-1] if args else None

        for name, plugin in self.plugins.items():
            if not plugin.is_enabled():
                continue

            hook_method = getattr(plugin, hook_name, None)
            if not hook_method or not callable(hook_method):
                continue

            try:
                new_result = await hook_method(*args, **kwargs)
                if new_result is not None:
                    result = new_result
                    if args:
                        args = (*args[:-1], result)
            except Exception as e:
                logger.error(f"❌ Plugin '{name}' hook '{hook_name}' failed: {e}")
                # Continue with other plugins
                continue

        return result

    def enable_plugin(self, name: str) -> None:
        """
        Enable a plugin.

        Args:
            name: Plugin name

        Raises:
            PluginNotFoundError: If plugin not found
        """
        plugin = self.get(name)
        plugin.enable()

    def disable_plugin(self, name: str) -> None:
        """
        Disable a plugin.

        Args:
            name: Plugin name

        Raises:
            PluginNotFoundError: If plugin not found
        """
        plugin = self.get(name)
        plugin.disable()

    def get_plugin_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all plugins.

        Returns:
            Dictionary mapping plugin names to their status
        """
        return {
            name: {
                "class": plugin.__class__.__name__,
                "enabled": plugin.is_enabled(),
                "config": plugin.config
            }
            for name, plugin in self.plugins.items()
        }

    def __repr__(self) -> str:
        """String representation of the plugin manager."""
        enabled_count = sum(1 for p in self.plugins.values() if p.is_enabled())
        return f"<PluginManager: {enabled_count}/{len(self.plugins)} plugins enabled>"
