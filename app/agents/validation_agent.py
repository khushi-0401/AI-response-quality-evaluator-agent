# ==============================================================================
# VALIDATION AGENT
# Validates individual agent scoring consistency and reasoning quality
# ==============================================================================

import logging
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from .relevance_agent import RelevanceJudge
from .accuracy_agent import AccuracyJudge
from .hallucination_agent import HallucinationDetector

logger = logging.getLogger(__name__)

class ValidationAgent(BaseAgent):
    """
    Validation Agent - Tests and validates the other 3 agents.
    
    Validates:
    - Scoring consistency (same answer gets same score)
    - Reasoning quality (explanations make sense)
    - Performance across varied question types
    """
    
    def __init__(self):
        super().__init__(name="ValidationAgent")
        self.relevance_judge = RelevanceJudge()
        self.accuracy_judge = AccuracyJudge()
        self.hallucination_detector = HallucinationDetector()
    
    def evaluate(self, test_dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate all agents against a test dataset.
        
        Args:
            test_dataset: List of test cases with question, ai_response, 
                         reference_answer, source_context
            
        Returns:
            Dict with validation summary and detailed results
        """
        if not test_dataset:
            return {
                "error": "Test dataset is required",
                "validation_summary": {},
                "detailed_results": []
            }
        
        try:
            results = []
            relevance_scores = []
            accuracy_scores = []
            hallucination_results = []
            
            for test_case in test_dataset:
                question = test_case.get("question", "")
                ai_response = test_case.get("ai_response", "")
                reference_answer = test_case.get("reference_answer", None)
                source_context = test_case.get("source_context", "")
                
                # Run each agent
                relevance_result = self.relevance_judge.evaluate(question, ai_response)
                accuracy_result = self.accuracy_judge.evaluate(
                    question, ai_response, reference_answer, source_context
                )
                hallucination_result = self.hallucination_detector.evaluate(
                    question, ai_response, source_context
                )
                
                # Collect scores
                relevance_scores.append(relevance_result.get("relevance_score", 0))
                accuracy_scores.append(accuracy_result.get("accuracy_score", 0))
                hallucination_results.append(hallucination_result.get("hallucination_detected", False))
                
                results.append({
                    "question": question,
                    "ai_response": ai_response[:100] + "..." if len(ai_response) > 100 else ai_response,
                    "relevance_score": relevance_result.get("relevance_score", 0),
                    "relevance_reasoning": relevance_result.get("reasoning", ""),
                    "accuracy_score": accuracy_result.get("accuracy_score", 0),
                    "accuracy_evidence": accuracy_result.get("evidence", ""),
                    "hallucination_detected": hallucination_result.get("hallucination_detected", False),
                    "hallucination_count": hallucination_result.get("hallucinated_count", 0)
                })
            
            # Calculate validation summary
            validation_summary = self._calculate_summary(
                results, 
                relevance_scores, 
                accuracy_scores, 
                hallucination_results
            )
            
            return {
                "validation_summary": validation_summary,
                "detailed_results": results,
                "total_tested": len(test_dataset)
            }
            
        except Exception as e:
            logger.error(f"Error in ValidationAgent: {e}")
            return {
                "error": str(e),
                "validation_summary": {},
                "detailed_results": []
            }
    
    def _calculate_summary(self, results: List[Dict], 
                          relevance_scores: List[float],
                          accuracy_scores: List[float],
                          hallucination_results: List[bool]) -> Dict[str, Any]:
        """Calculate validation summary statistics."""
        
        if not results:
            return {}
        
        total = len(results)
        
        # Relevance agent stats
        avg_relevance = sum(relevance_scores) / total if total > 0 else 0
        relevance_consistency = self._calculate_consistency(relevance_scores)
        relevance_pass_rate = sum(1 for s in relevance_scores if s >= 0.7) / total
        
        # Accuracy agent stats
        avg_accuracy = sum(accuracy_scores) / total if total > 0 else 0
        accuracy_consistency = self._calculate_consistency(accuracy_scores)
        accuracy_pass_rate = sum(1 for s in accuracy_scores if s >= 0.7) / total
        
        # Hallucination agent stats
        hallucination_detection_rate = sum(1 for h in hallucination_results if h) / total
        
        return {
            "relevance_agent": {
                "avg_score": round(avg_relevance, 2),
                "consistency": round(relevance_consistency, 2),
                "pass_rate": round(relevance_pass_rate, 2)
            },
            "accuracy_agent": {
                "avg_score": round(avg_accuracy, 2),
                "consistency": round(accuracy_consistency, 2),
                "pass_rate": round(accuracy_pass_rate, 2)
            },
            "hallucination_agent": {
                "detection_rate": round(hallucination_detection_rate, 2)
            },
            "overall_pass_rate": round((relevance_pass_rate + accuracy_pass_rate) / 2, 2)
        }
    
    def _calculate_consistency(self, scores: List[float]) -> float:
        """Calculate consistency of scores (1 = perfectly consistent)."""
        if not scores:
            return 0.0
        
        avg = sum(scores) / len(scores)
        
        if avg == 0:
            return 1.0
        
        # Calculate average deviation from mean
        deviations = [abs(s - avg) / avg for s in scores]
        avg_deviation = sum(deviations) / len(deviations)
        
        # Convert to consistency score (1 - avg_deviation)
        return max(0.0, 1.0 - avg_deviation)