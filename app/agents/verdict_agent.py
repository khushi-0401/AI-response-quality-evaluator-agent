# ==============================================================================
# VERDICT AGENT
# Aggregates all scores and produces final verdict
# ==============================================================================

import logging
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class VerdictAgent(BaseAgent):
    """
    Verdict Agent - Aggregates all dimension scores using weighted scoring.
    
    Weights:
    - Relevance: 25%
    - Accuracy: 25%
    - Completeness: 25%
    - Hallucination (inverted): 25%
    
    Verdicts:
    - PASS: Overall >= 0.7
    - NEEDS IMPROVEMENT: Overall >= 0.5 and < 0.7
    - FAIL: Overall < 0.5
    """
    
    def __init__(self):
        super().__init__(name="VerdictAgent")
        
        # Define weights for each dimension
        self.weights = {
            "relevance": 0.25,
            "accuracy": 0.25,
            "completeness": 0.25,
            "hallucination": 0.25  # Lower hallucination = better
        }
    
    def evaluate(self, scores: Dict[str, float], 
                 reasonings: Dict[str, str]) -> Dict[str, Any]:
        """
        Aggregate scores and produce final verdict.
        
        Args:
            scores: Dict with relevance_score, accuracy_score, completeness_score, hallucination_score
            reasonings: Dict with reasoning for each dimension
            
        Returns:
            Dict with overall_score, verdict, consolidated_reasoning, dimension_breakdown
        """
        try:
            # Extract scores
            relevance = scores.get("relevance_score", 0.0)
            accuracy = scores.get("accuracy_score", 0.0)
            completeness = scores.get("completeness_score", 0.0)
            hallucination = scores.get("hallucination_score", 0.0)
            
            # Invert hallucination (lower is better)
            hallucination_inverted = 1.0 - hallucination
            
            # Calculate weighted score
            overall = (
                relevance * self.weights["relevance"] +
                accuracy * self.weights["accuracy"] +
                completeness * self.weights["completeness"] +
                hallucination_inverted * self.weights["hallucination"]
            )
            
            # Determine verdict
            if overall >= 0.7:
                verdict = "PASS"
                verdict_emoji = "✅"
                verdict_color = "green"
            elif overall >= 0.5:
                verdict = "NEEDS IMPROVEMENT"
                verdict_emoji = "⚠️"
                verdict_color = "orange"
            else:
                verdict = "FAIL"
                verdict_emoji = "❌"
                verdict_color = "red"
            
            # Build dimension breakdown
            dimension_breakdown = {
                "Relevance": {
                    "score": relevance,
                    "weight": self.weights["relevance"],
                    "weighted_score": relevance * self.weights["relevance"],
                    "reasoning": reasonings.get("relevance", "N/A")
                },
                "Accuracy": {
                    "score": accuracy,
                    "weight": self.weights["accuracy"],
                    "weighted_score": accuracy * self.weights["accuracy"],
                    "reasoning": reasonings.get("accuracy", "N/A")
                },
                "Completeness": {
                    "score": completeness,
                    "weight": self.weights["completeness"],
                    "weighted_score": completeness * self.weights["completeness"],
                    "reasoning": reasonings.get("completeness", "N/A")
                },
                "Hallucination": {
                    "score": hallucination,
                    "weight": self.weights["hallucination"],
                    "weighted_score": hallucination_inverted * self.weights["hallucination"],
                    "reasoning": reasonings.get("hallucination", "N/A")
                }
            }
            
            # Generate consolidated reasoning
            consolidated_reasoning = self._generate_consolidated_reasoning(
                overall, verdict, dimension_breakdown
            )
            
            result = {
                "overall_score": round(overall, 2),
                "verdict": verdict,
                "verdict_emoji": verdict_emoji,
                "verdict_color": verdict_color,
                "dimension_breakdown": dimension_breakdown,
                "consolidated_reasoning": consolidated_reasoning,
                "llm_used": True
            }
            
            return self.log_result(result)
            
        except Exception as e:
            logger.error(f"Error in VerdictAgent: {e}")
            return {
                "error": str(e),
                "overall_score": 0.0,
                "verdict": "FAIL",
                "verdict_emoji": "❌",
                "consolidated_reasoning": f"Error: {str(e)}"
            }
    
    def _generate_consolidated_reasoning(self, overall: float, 
                                         verdict: str,
                                         breakdown: Dict) -> str:
        """Generate human-readable consolidated reasoning."""
        
        # Find best and worst dimensions
        best_dimension = max(breakdown.items(), key=lambda x: x[1]["score"])
        worst_dimension = min(breakdown.items(), key=lambda x: x[1]["score"])
        
        reasoning = f"Overall Score: {overall:.2f} → {verdict}. "
        
        if verdict == "PASS":
            reasoning += f"All dimensions performed well. Best: {best_dimension[0]} ({best_dimension[1]['score']:.2f})."
        elif verdict == "NEEDS IMPROVEMENT":
            reasoning += f"Needs improvement in {worst_dimension[0]} ({worst_dimension[1]['score']:.2f}). Best: {best_dimension[0]} ({best_dimension[1]['score']:.2f})."
        else:
            reasoning += f"Significant improvement needed in {worst_dimension[0]} ({worst_dimension[1]['score']:.2f})."
        
        return reasoning.strip()