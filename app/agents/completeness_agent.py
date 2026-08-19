# ==============================================================================
# COMPLETENESS JUDGE AGENT
# Evaluates if the response covers all aspects of the question
# ==============================================================================

import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent
from app.llm_integration import LLMIntegration

logger = logging.getLogger(__name__)

class CompletenessJudge(BaseAgent):
    """
    Completeness Judge Agent - Evaluates if all aspects of the question are addressed.
    
    Scoring Scale:
    - 1.0: All aspects covered completely
    - 0.7-0.9: Most aspects covered, minor omissions
    - 0.5-0.7: Some aspects covered, key omissions
    - 0.0-0.5: Major aspects missing
    """
    
    def __init__(self):
        super().__init__(name="CompletenessJudge")
        self.llm = LLMIntegration()
    
    def evaluate(self, question: str, ai_response: str) -> Dict[str, Any]:
        """
        Evaluate completeness of AI response.
        
        Args:
            question: The original question
            ai_response: The AI's response
            
        Returns:
            Dict with completeness_score, reasoning, covered_aspects, missing_aspects
        """
        if not self.llm.is_available():
            return {
                "error": "Gemini not available",
                "completeness_score": 0.0,
                "reasoning": "LLM not available",
                "covered_aspects": [],
                "missing_aspects": []
            }
        
        try:
            result = self.llm.evaluate_completeness(question, ai_response)
            
            return {
                "completeness_score": result.get("score", 5) / 10,
                "reasoning": result.get("reasoning", "No reasoning provided"),
                "covered_aspects": result.get("covered_aspects", []),
                "missing_aspects": result.get("missing_aspects", []),
                "llm_used": True
            }
            
        except Exception as e:
            logger.error(f"Error in CompletenessJudge: {e}")
            return {
                "error": str(e),
                "completeness_score": 0.0,
                "reasoning": f"Evaluation failed: {str(e)}",
                "covered_aspects": [],
                "missing_aspects": []
            }