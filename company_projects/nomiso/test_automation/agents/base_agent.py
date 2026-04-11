"""Base agent class for the test automation agent chain."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel

from ..llm import LLMProvider


class AgentResult(BaseModel):
    """Result from an agent execution."""

    agent_name: str
    success: bool
    data: Dict[str, Any]
    errors: List[str] = []
    warnings: List[str] = []
    execution_time: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    """Base class for all agents in the test automation chain."""

    def __init__(self, name: str, llm_provider: Optional[LLMProvider] = None):
        """Initialize the agent.

        Args:
            name: Agent name
            llm_provider: Optional LLM provider for AI-powered operations
        """
        self.name = name
        self.llm = llm_provider
        self.execution_history: List[AgentResult] = []

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any], **kwargs) -> AgentResult:
        """Execute the agent's main functionality.

        Args:
            input_data: Input data for the agent
            **kwargs: Additional configuration parameters

        Returns:
            AgentResult with execution results
        """
        pass

    async def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Validate input data for the agent.

        Args:
            input_data: Input data to validate

        Returns:
            List of validation errors
        """
        return []

    def get_execution_history(self) -> List[AgentResult]:
        """Get execution history for this agent."""
        return self.execution_history

    def get_last_result(self) -> Optional[AgentResult]:
        """Get the last execution result."""
        return self.execution_history[-1] if self.execution_history else None

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()

    def _create_result(
        self,
        success: bool,
        data: Dict[str, Any],
        errors: List[str] = None,
        warnings: List[str] = None,
        execution_time: float = 0.0,
        metadata: Dict[str, Any] = None,
    ) -> AgentResult:
        """Create an agent result."""
        result = AgentResult(
            agent_name=self.name,
            success=success,
            data=data,
            errors=errors or [],
            warnings=warnings or [],
            execution_time=execution_time,
            timestamp=datetime.now(),
            metadata=metadata,
        )

        self.execution_history.append(result)
        return result
