from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTestGeneratorAgent(ABC):
    """Abstract base class for test generator agents"""
    
    @abstractmethod
    def generate_and_execute(self, file_path: str) -> Dict[str, Any]:
        """Generate integration test for the given source file"""
        pass