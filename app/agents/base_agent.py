# ==============================================================================
# BASE AGENT - Common functionality for all agents
# ==============================================================================

import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all judge agents.
    All agents must implement the evaluate() method.
    """
    
    def __init__(self, name: str = "BaseAgent"):
        self.name = name
        logger.info(f"Initialized {self.name}")
    
    @abstractmethod
    def evaluate(self, **kwargs) -> Dict[str, Any]:
        """
        Main evaluation method to be implemented by each agent.
        
        Returns:
            Dict containing evaluation results
        """
        pass
    
    def _validate_input(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Helper method to validate required fields are present.
        """
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValueError(f"Missing required field: {field}")
        return True
    
    def log_result(self, result: Dict[str, Any]):
        """
        Log the evaluation result.
        """
        logger.info(f"{self.name} - Result: {result.get('score', 'N/A')}")
        return result