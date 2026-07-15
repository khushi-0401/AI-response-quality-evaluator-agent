# ==============================================================================
# HALLUCINATION DETECTION AGENT
# Identifies unsupported claims by cross-referencing response against RAG-retrieved source content
# ==============================================================================

import logging
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class HallucinationDetector(BaseAgent):
    """
    Hallucination Detection Agent - Identifies claims not supported by source context.
    
    Severity Levels:
    - HIGH: Direct contradiction with source
    - MEDIUM: Exaggeration or unsupported claim
    - LOW: Minor detail not in source
    """
    
    def __init__(self):
        super().__init__(name="HallucinationDetector")
    
    def evaluate(self, question: str, ai_response: str, 
                 source_context: str) -> Dict[str, Any]:
        """
        Detect hallucinations in AI response against source context.
        
        Args:
            question: The original question
            ai_response: The AI's response to evaluate
            source_context: Retrieved context from RAG knowledge base
            
        Returns:
            Dict with hallucination detection results
        """
        # Validate inputs
        if not question or not ai_response:
            return {
                "error": "Question and AI response are required",
                "hallucination_detected": False,
                "hallucination_score": 0.0,
                "hallucinated_statements": [],
                "supported_statements": []
            }
        
        if not source_context:
            return {
                "error": "Source context is required for hallucination detection",
                "hallucination_detected": False,
                "hallucination_score": 0.0,
                "hallucinated_statements": [],
                "supported_statements": [],
                "message": "Cannot detect hallucinations without source context"
            }
        
        try:
            # Extract claims from AI response
            claims = self._extract_claims(ai_response)
            
            if not claims:
                return {
                    "hallucination_detected": False,
                    "hallucination_score": 0.0,
                    "hallucinated_statements": [],
                    "supported_statements": [],
                    "message": "No factual claims found in response"
                }
            
            # Check each claim against source context
            hallucinated = []
            supported = []
            
            for claim in claims:
                claim_support = self._check_claim_support(claim, source_context)
                
                if claim_support["supported"]:
                    supported.append({
                        "claim": claim,
                        "source_evidence": claim_support["evidence"],
                        "severity": "none"
                    })
                else:
                    hallucinated.append({
                        "claim": claim,
                        "source_evidence": claim_support["evidence"],
                        "severity": claim_support["severity"],
                        "reason": claim_support["reason"]
                    })
            
            # Calculate hallucination score
            hallucination_score = self._calculate_hallucination_score(claims, hallucinated)
            
            # Determine if hallucination detected
            detected = len(hallucinated) > 0
            
            # Generate summary
            summary = self._generate_summary(claims, hallucinated, supported)
            
            result = {
                "hallucination_detected": detected,
                "hallucination_score": round(hallucination_score, 2),
                "hallucinated_statements": hallucinated[:5],
                "supported_statements": supported[:5],
                "total_claims": len(claims),
                "hallucinated_count": len(hallucinated),
                "supported_count": len(supported),
                "summary": summary
            }
            
            return self.log_result(result)
            
        except Exception as e:
            logger.error(f"Error in HallucinationDetector: {e}")
            return {
                "error": str(e),
                "hallucination_detected": False,
                "hallucination_score": 0.0,
                "hallucinated_statements": [],
                "supported_statements": [],
                "summary": f"Evaluation failed: {str(e)}"
            }
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract factual claims from text."""
        sentences = text.replace('?', '.').replace('!', '.').split('.')
        claims = []
        for s in sentences:
            s = s.strip()
            if len(s) > 15 and not s.lower().startswith(('what', 'why', 'how', 'when', 'where')):
                claims.append(s)
        return claims
    
    def _check_claim_support(self, claim: str, source_context: str) -> Dict[str, Any]:
        """
        Check if a claim is supported by source context.
        Returns: {supported, evidence, severity, reason}
        """
        claim_words = set(claim.lower().split())
        source_words = set(source_context.lower().split())
        
        # Remove common stopwords for better matching
        stopwords = {'the', 'a', 'an', 'of', 'to', 'for', 'in', 'on', 'at', 'with', 'without'}
        claim_words = {w for w in claim_words if w not in stopwords}
        source_words = {w for w in source_words if w not in stopwords}
        
        if not claim_words:
            return {
                "supported": False,
                "evidence": "No meaningful words in claim",
                "severity": "low",
                "reason": "Claim contains no meaningful terms"
            }
        
        # Calculate overlap
        overlap = claim_words.intersection(source_words)
        overlap_ratio = len(overlap) / len(claim_words)
        
        # Determine support level
        if overlap_ratio >= 0.6:
            # Find matching evidence
            evidence = self._find_evidence(claim, source_context)
            return {
                "supported": True,
                "evidence": evidence,
                "severity": "none",
                "reason": "Claim is supported by source"
            }
        elif overlap_ratio >= 0.3:
            return {
                "supported": False,
                "evidence": "Partial match found but insufficient",
                "severity": "medium",
                "reason": f"Only {len(overlap)} out of {len(claim_words)} key terms match the source"
            }
        else:
            return {
                "supported": False,
                "evidence": "No supporting evidence found in source",
                "severity": "high",
                "reason": f"Claim contains terms not found in source. Overlap ratio: {overlap_ratio:.2f}"
            }
    
    def _find_evidence(self, claim: str, source_context: str) -> str:
        """Find supporting evidence from source context."""
        sentences = source_context.split('.')
        claim_words = set(claim.lower().split())
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_words = set(sentence.lower().split())
            overlap = claim_words.intersection(sentence_words)
            
            if len(overlap) > 3:
                return sentence[:200] + ("..." if len(sentence) > 200 else "")
        
        return "No direct evidence found"
    
    def _calculate_hallucination_score(self, claims: List[str], 
                                      hallucinated: List[Dict]) -> float:
        """Calculate hallucination score (0 = no hallucination, 1 = completely hallucinated)."""
        if not claims:
            return 0.0
        
        # Weight hallucinated claims more heavily
        hallucinated_count = len(hallucinated)
        total_count = len(claims)
        
        # Count severe hallucinations with extra weight
        severe_count = sum(1 for h in hallucinated if h.get("severity") == "high")
        
        base_score = hallucinated_count / total_count
        severe_bonus = (severe_count / total_count) * 0.3
        
        return min(1.0, base_score + severe_bonus)
    
    def _generate_summary(self, claims: List[str], 
                         hallucinated: List[Dict], 
                         supported: List[Dict]) -> str:
        """Generate a human-readable summary."""
        total = len(claims)
        hallucinated_count = len(hallucinated)
        supported_count = len(supported)
        
        if total == 0:
            return "No claims to evaluate."
        
        if hallucinated_count == 0:
            return f"✅ All {total} claims are supported by the source context."
        
        if hallucinated_count == total:
            return f"❌ All {total} claims are unsupported by the source context."
        
        return f"⚠️ {hallucinated_count} out of {total} claims are unsupported. {supported_count} claims are verified."