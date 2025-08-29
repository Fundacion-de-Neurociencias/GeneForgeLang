"""Simple plugin registry used by the interpreter and validators.

External apps can register their own plugins at runtime. Built-in demo
plugins are optionally auto-registered if importable.
"""

from __future__ import annotations
from typing import Dict, Any


class _Registry:
    def __init__(self):
        self._plugins: Dict[str, Any] = {}

    def register(self, name: str, plugin: Any) -> None:
        self._plugins[name] = plugin

    def get(self, name: str) -> Any:
        if name not in self._plugins:
            raise ValueError(f"Plugin '{name}' is not registered")
        return self._plugins[name]

    def names(self):
        return sorted(self._plugins.keys())


plugin_registry = _Registry()


def _try_autoregister():
    # Attempt to import demo plugins if they are available.
    try:
        from gfl.plugins.alpha_genome import AlphaGenomePlugin  # type: ignore

        plugin_registry.register("alpha_genome", AlphaGenomePlugin())
    except Exception:
        pass
    try:
        from gfl.plugins.variant_sim import VariantSimulationPlugin  # type: ignore

        plugin_registry.register("variant_sim", VariantSimulationPlugin())
    except Exception:
        pass


_try_autoregister()

__all__ = ["plugin_registry"]

