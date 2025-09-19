"""Base plugin classes for GFL."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseGFLPlugin(ABC):
    """Base class for all GFL plugins."""

    def __init__(self):
        self.name = "BasePlugin"
        self.description = "Base plugin class"
        self.version = "1.0.0"

    @abstractmethod
    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process data and return results."""
        pass


class BaseGeneratorPlugin(BaseGFLPlugin):
    """Base class for generator plugins."""

    @abstractmethod
    def generate(self, params: dict[str, Any]) -> dict[str, Any]:
        """Generate new entities based on parameters."""
        pass

    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process method that calls generate."""
        return self.generate(data)


class BaseOptimizerPlugin(BaseGFLPlugin):
    """Base class for optimizer plugins."""

    @abstractmethod
    def optimize(self, params: dict[str, Any]) -> dict[str, Any]:
        """Optimize parameters based on objective."""
        pass

    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process method that calls optimize."""
        return self.optimize(data)
