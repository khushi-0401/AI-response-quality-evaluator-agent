# ==============================================================================
# RELEVANCE JUDGE AGENT - LLM POWERED
# Uses Google Gemini to evaluate relevance
# ==============================================================================

import logging
from typing import Dict, Any
from .base_agent import BaseAgent
from app.llm_integration import LLMIntegration

logger = logging.getLogger(__name__)

class RelevanceJudge(BaseAgent):
    """
    LLM-Powered Relevance Judge Agent - Uses Gemini to evaluate relevance.
    
    Scoring Scale:
    - 1.0: Perfectly relevant, fully answers the question
    - 0.7-0.9: Mostly relevant, minor gaps
    - 0.5-0.7: Partially relevant, missing key points
    - 0.0-0.5: Not relevant or off-topic
    """
    
    def __init__(self):
        super().__init__(name="RelevanceJudge")
        self.llm = LLMIntegration()
    
    def evaluate(self, question: str, ai_response: str) -> Dict[str, Any]:
        """
        Evaluate relevance using Gemini.
        
        Args:
            question: The original question
            ai_response: The AI's response to evaluate
            
        Returns:
            Dict with relevance_score, reasoning, and key points
        """
        if not self.llm.is_available():
            return {
                "error": "Gemini not available. Check API key.",
                "relevance_score": 0.0,
                "reasoning": "LLM not available",
                "key_points_covered": [],
                "missing_points": [],
                "term_coverage": 0.0
            }
        
        try:
            result = self.llm.evaluate_relevance(question, ai_response)
            
            return {
                "relevance_score": result.get("score", 5) / 10,
                "reasoning": result.get("reasoning", "No reasoning provided"),
                "key_points_covered": result.get("key_points_covered", []),
                "missing_points": result.get("missing_points", []),
                "term_coverage": len(result.get("key_points_covered", [])) / max(1, len(result.get("key_points_covered", [])) + len(result.get("missing_points", [])))
            }
            
        except Exception as e:
            logger.error(f"Error in RelevanceJudge: {e}")
            return {
                "error": str(e),
                "relevance_score": 0.0,
                "reasoning": f"Evaluation failed: {str(e)}",
                "key_points_covered": [],
                "missing_points": [],
                "term_coverage": 0.0
            }