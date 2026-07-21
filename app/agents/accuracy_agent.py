# ==============================================================================
# ACCURACY JUDGE AGENT - LLM POWERED
# Uses Google Gemini to evaluate factual accuracy
# ==============================================================================

import logging
from typing import Dict, Any, Optional
from .base_agent import BaseAgent
from app.llm_integration import LLMIntegration

logger = logging.getLogger(__name__)

class AccuracyJudge(BaseAgent):
    """
    LLM-Powered Accuracy Judge Agent - Uses Gemini to evaluate factual accuracy.
    
    Scoring Scale:
    - 1.0: Completely accurate, all claims verified
    - 0.7-0.9: Mostly accurate, minor errors
    - 0.5-0.7: Partially accurate, some incorrect claims
    - 0.0-0.5: Mostly inaccurate
    """
    
    def __init__(self):
        super().__init__(name="AccuracyJudge")
        self.llm = LLMIntegration()
    
    def evaluate(self, question: str, ai_response: str, 
                 reference_answer: Optional[str] = None,
                 source_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate accuracy using Gemini.
        
        Args:
            question: The original question
            ai_response: The AI's response to evaluate
            reference_answer: Optional ground truth answer
            source_context: Optional source context from RAG
            
        Returns:
            Dict with accuracy_score, evidence, and claim analysis
        """
        if not self.llm.is_available():
            return {
                "error": "Gemini not available. Check API key.",
                "accuracy_score": 0.0,
                "evidence": "LLM not available",
                "correct_claims": [],
                "incorrect_claims": [],
                "partially_correct_claims": [],
                "total_claims": 0,
                "verified_claims": 0
            }
        
        # Determine what to compare against
        ground_truth = reference_answer or source_context or ""
        
        if not ground_truth:
            return {
                "error": "No reference answer or source context provided",
                "accuracy_score": 0.0,
                "evidence": "Cannot verify accuracy without reference",
                "correct_claims": [],
                "incorrect_claims": [],
                "partially_correct_claims": [],
                "total_claims": 0,
                "verified_claims": 0
            }
        
        try:
            result = self.llm.evaluate_accuracy(question, ai_response, ground_truth)
            
            # Count claims
            correct = result.get("correct_claims", [])
            incorrect = result.get("incorrect_claims", [])
            partially = result.get("partially_correct_claims", [])
            total = len(correct) + len(incorrect) + len(partially)
            
            return {
                "accuracy_score": result.get("score", 5) / 10,
                "evidence": result.get("evidence", "No evidence provided"),
                "correct_claims": correct,
                "incorrect_claims": incorrect,
                "partially_correct_claims": partially,
                "total_claims": total,
                "verified_claims": len(correct),
                "llm_used": True
            }
            
        except Exception as e:
            logger.error(f"Error in AccuracyJudge: {e}")
            return {
                "error": str(e),
                "accuracy_score": 0.0,
                "evidence": f"Evaluation failed: {str(e)}",
                "correct_claims": [],
                "incorrect_claims": [],
                "partially_correct_claims": [],
                "total_claims": 0,
                "verified_claims": 0
            }