# ==============================================================================
# HALLUCINATION DETECTION AGENT - LLM POWERED
# Uses Google Gemini to detect hallucinations
# ==============================================================================

import logging
from typing import Dict, Any, Optional, List
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
            
            # Ensure hallucinated_statements are dictionaries with 'statement' and 'explanation' keys
            hallucinated = result.get("hallucinated_statements", [])
            supported = result.get("supported_statements", [])
            
            # Convert strings to dictionaries if needed
            hallucinated_statements = []
            for item in hallucinated:
                if isinstance(item, str):
                    hallucinated_statements.append({
                        "statement": item,
                        "explanation": "Unsupported claim detected"
                    })
                elif isinstance(item, dict):
                    hallucinated_statements.append({
                        "statement": item.get("statement", str(item)),
                        "explanation": item.get("explanation", "No explanation provided")
                    })
                else:
                    hallucinated_statements.append({
                        "statement": str(item),
                        "explanation": "Unsupported claim detected"
                    })
            
            supported_statements = []
            for item in supported:
                if isinstance(item, str):
                    supported_statements.append({
                        "statement": item,
                        "explanation": "Supported by source context"
                    })
                elif isinstance(item, dict):
                    supported_statements.append({
                        "statement": item.get("statement", str(item)),
                        "explanation": item.get("explanation", "Supported by source context")
                    })
                else:
                    supported_statements.append({
                        "statement": str(item),
                        "explanation": "Supported by source context"
                    })
            
            total = len(hallucinated_statements) + len(supported_statements)
            
            return {
                "hallucination_detected": result.get("hallucination_detected", False),
                "hallucination_score": result.get("hallucination_score", 5) / 10,
                "hallucinated_statements": hallucinated_statements,
                "supported_statements": supported_statements,
                "total_claims": total,
                "hallucinated_count": len(hallucinated_statements),
                "supported_count": len(supported_statements),
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