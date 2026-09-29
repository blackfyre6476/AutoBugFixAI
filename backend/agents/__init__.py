"""
AutoFix AI Agents Package.
Contains modular AI agents for repository analysis, bug investigation,
fix generation, patch validation, and regression testing.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    """Abstract Base Class for all AutoFix AI agents."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent logic given workflow context data."""
        pass
