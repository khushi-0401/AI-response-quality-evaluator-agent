# ==============================================================================
# HALLUCINATION DETECTION AGENT - LLM POWERED
# Uses Google Gemini to detect hallucinations
# ==============================================================================

import logging
from typing import Dict, Any, Optional
from .base_agent import BaseAgent
from app.llm_integration import LLMIntegration

logger = logging.getLogger(__name__)

class HallucinationDetector(BaseAgent):
    """
    LLM-Powered Hallucination Detection Agent - Uses Gemini to detect hallucinations.
    
    Severity Levels:
    - HIGH: Direct contradiction with source
    - MEDIUM: Exaggeration or unsupported claim
    - LOW: Minor detail not in source
    """
    
    def __init__(self):
        super().__init__(name="HallucinationDetector")
        self.llm = LLMIntegration()
    
    def evaluate(self, question: str, ai_response: str, 
                 source_context: str) -> Dict[str, Any]:
        """
        Detect hallucinations using Gemini.
        
        Args:
            question: The original question
            ai_response: The AI's response to evaluate
            source_context: Retrieved context from RAG knowledge base
            
        Returns:
            Dict with hallucination detection results
        """
        if not self.llm.is_available():
            return {
                "error": "Gemini not available. Check API key.",
                "hallucination_detected": False,
                "hallucination_score": 0.0,
                "hallucinated_statements": [],
                "supported_statements": [],
                "total_claims": 0,
                "hallucinated_count": 0,
                "supported_count": 0,
                "summary": "LLM not available"
            }
        
        if not source_context:
            return {
                "error": "Source context is required for hallucination detection",
                "hallucination_detected": False,
                "hallucination_score": 0.0,
                "hallucinated_statements": [],
                "supported_statements": [],
                "total_claims": 0,
                "hallucinated_count": 0,
                "supported_count": 0,
                "summary": "Cannot detect hallucinations without source context"
            }
        
        try:
            result = self.llm.detect_hallucination(question, ai_response, source_context)
            
            hallucinated = result.get("hallucinated_statements", [])
            supported = result.get("supported_statements", [])
            total = len(hallucinated) + len(supported)
            
            return {
                "hallucination_detected": result.get("hallucination_detected", False),
                "hallucination_score": result.get("hallucination_score", 5) / 10,
                "hallucinated_statements": hallucinated,
                "supported_statements": supported,
                "total_claims": total,
                "hallucinated_count": len(hallucinated),
                "supported_count": len(supported),
                "summary": result.get("summary", "No summary provided"),
                "llm_used": True
            }
            
        except Exception as e:
            logger.error(f"Error in HallucinationDetector: {e}")
            return {
                "error": str(e),
                "hallucination_detected": False,
                "hallucination_score": 0.0,
                "hallucinated_statements": [],
                "supported_statements": [],
                "total_claims": 0,
                "hallucinated_count": 0,
                "supported_count": 0,
                "summary": f"Evaluation failed: {str(e)}"
            }