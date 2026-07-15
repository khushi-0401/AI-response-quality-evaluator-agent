# AI Response Quality Evaluator Agent
# Milestone 2: Agent Package

from .base_agent import BaseAgent
from .relevance_agent import RelevanceJudge
from .accuracy_agent import AccuracyJudge
from .hallucination_agent import HallucinationDetector
from .validation_agent import ValidationAgent

__all__ = [
    'BaseAgent',
    'RelevanceJudge',
    'AccuracyJudge',
    'HallucinationDetector',
    'ValidationAgent'
]

__version__ = "0.1.0-alpha"
__module_name__ = "Agents Module"