# ==============================================================================
# ACCURACY JUDGE AGENT
# Checks factual correctness against reference answer or retrieved source chunks
# ==============================================================================

import logging
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class AccuracyJudge(BaseAgent):
    """
    Accuracy Judge Agent - Evaluates if the AI response is factually correct.
    
    Scoring Scale:
    - 1.0: Completely accurate, all claims verified
    - 0.7-0.9: Mostly accurate, minor errors
    - 0.5-0.7: Partially accurate, some incorrect claims
    - 0.0-0.5: Mostly inaccurate
    """
    
    def __init__(self):
        super().__init__(name="AccuracyJudge")
    
    def evaluate(self, question: str, ai_response: str, 
                 reference_answer: Optional[str] = None,
                 source_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate accuracy of AI response against reference or source context.
        
        Args:
            question: The original question
            ai_response: The AI's response to evaluate
            reference_answer: Optional ground truth answer
            source_context: Optional source context from RAG
            
        Returns:
            Dict with accuracy_score, evidence, and claim analysis
        """
        # Validate inputs
        if not question or not ai_response:
            return {
                "error": "Question and AI response are required",
                "accuracy_score": 0.0,
                "evidence": "Missing input data",
                "correct_claims": [],
                "incorrect_claims": [],
                "partially_correct_claims": []
            }
        
        try:
            # Determine what to compare against
            ground_truth = reference_answer or source_context or ""
            
            if not ground_truth:
                return {
                    "error": "No reference answer or source context provided",
                    "accuracy_score": 0.0,
                    "evidence": "Cannot verify accuracy without reference",
                    "correct_claims": [],
                    "incorrect_claims": [],
                    "partially_correct_claims": []
                }
            
            # Extract claims from AI response
            ai_claims = self._extract_claims(ai_response)
            
            # Extract claims from ground truth
            truth_claims = self._extract_claims(ground_truth)
            
            # Compare claims
            correct, incorrect, partially = self._compare_claims(ai_claims, truth_claims)
            
            # Calculate accuracy score
            score = self._calculate_accuracy_score(correct, incorrect, partially, ai_claims)
            
            # Generate evidence
            evidence = self._generate_evidence(correct, incorrect, partially, ground_truth)
            
            result = {
                "accuracy_score": round(score, 2),
                "evidence": evidence,
                "correct_claims": correct[:5],
                "incorrect_claims": incorrect[:5],
                "partially_correct_claims": partially[:5],
                "total_claims": len(ai_claims),
                "verified_claims": len(correct)
            }
            
            return self.log_result(result)
            
        except Exception as e:
            logger.error(f"Error in AccuracyJudge: {e}")
            return {
                "error": str(e),
                "accuracy_score": 0.0,
                "evidence": f"Evaluation failed: {str(e)}",
                "correct_claims": [],
                "incorrect_claims": [],
                "partially_correct_claims": []
            }
    
    def _extract_claims(self, text: str) -> List[str]:
        """
        Extract factual claims from text.
        Simple implementation: split into sentences that contain factual statements.
        """
        sentences = text.replace('?', '.').replace('!', '.').split('.')
        claims = []
        for s in sentences:
            s = s.strip()
            if len(s) > 15 and not s.lower().startswith(('what', 'why', 'how', 'when', 'where')):
                claims.append(s)
        return claims
    
    def _compare_claims(self, ai_claims: List[str], truth_claims: List[str]) -> tuple:
        """
        Compare AI claims against ground truth claims.
        Returns: (correct, incorrect, partially_correct)
        """
        correct = []
        incorrect = []
        partially = []
        
        if not ai_claims:
            return [], [], []
        
        if not truth_claims:
            # If no truth claims, mark all as unverifiable
            return [], ai_claims, []
        
        for ai_claim in ai_claims:
            # Check if claim appears in any truth claim
            matched = False
            partially_matched = False
            
            ai_words = set(ai_claim.lower().split())
            
            for truth_claim in truth_claims:
                truth_words = set(truth_claim.lower().split())
                overlap = len(ai_words.intersection(truth_words))
                
                if len(ai_words) > 0:
                    overlap_ratio = overlap / len(ai_words)
                    
                    if overlap_ratio >= 0.8:
                        correct.append(ai_claim)
                        matched = True
                        break
                    elif overlap_ratio >= 0.4:
                        partially_matched = True
            
            if not matched:
                if partially_matched:
                    partially.append(ai_claim)
                else:
                    incorrect.append(ai_claim)
        
        return correct, incorrect, partially
    
    def _calculate_accuracy_score(self, correct: List[str], 
                                  incorrect: List[str], 
                                  partially: List[str],
                                  total_claims: List[str]) -> float:
        """Calculate accuracy score based on claim analysis."""
        total = len(total_claims)
        if total == 0:
            return 0.0
        
        # Weight: correct = 1.0, partially = 0.5, incorrect = 0.0
        score = (len(correct) * 1.0 + len(partially) * 0.5) / total
        return max(0.0, min(1.0, score))
    
    def _generate_evidence(self, correct: List[str], 
                          incorrect: List[str], 
                          partially: List[str],
                          ground_truth: str) -> str:
        """Generate human-readable evidence for the score."""
        evidence_parts = []
        
        if correct:
            evidence_parts.append(f"✅ {len(correct)} claims verified against reference")
        if partially:
            evidence_parts.append(f"⚠️ {len(partially)} claims partially match")
        if incorrect:
            evidence_parts.append(f"❌ {len(incorrect)} claims could not be verified")
        
        if not evidence_parts:
            return "No claims could be verified. Insufficient reference data."
        
        evidence = "; ".join(evidence_parts)
        evidence += f". Reference source: {ground_truth[:100]}..."
        
        return evidence