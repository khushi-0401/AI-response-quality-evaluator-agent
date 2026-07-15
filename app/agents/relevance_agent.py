# ==============================================================================
# RELEVANCE JUDGE AGENT
# Scores how relevant the AI response is to the question
# ==============================================================================

import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class RelevanceJudge(BaseAgent):
    """
    Relevance Judge Agent - Evaluates if the AI response directly answers the question.
    
    Scoring Scale:
    - 1.0: Perfectly relevant, fully answers the question
    - 0.7-0.9: Mostly relevant, minor gaps
    - 0.5-0.7: Partially relevant, missing key points
    - 0.0-0.5: Not relevant or off-topic
    """
    
    def __init__(self):
        super().__init__(name="RelevanceJudge")
    
    def evaluate(self, question: str, ai_response: str) -> Dict[str, Any]:
        """
        Evaluate relevance of AI response to the question.
        
        Args:
            question: The original question
            ai_response: The AI's response to evaluate
            
        Returns:
            Dict with relevance_score, reasoning, and key points
        """
        # Validate inputs
        if not question or not ai_response:
            return {
                "error": "Question and AI response are required",
                "relevance_score": 0.0,
                "reasoning": "Missing input data",
                "key_points_covered": [],
                "missing_points": []
            }
        
        # Perform relevance analysis
        try:
            # Extract key terms from question
            question_terms = self._extract_key_terms(question)
            
            # Check if response contains these terms
            matched_terms, matched_percentage = self._check_term_coverage(
                question_terms, 
                ai_response
            )
            
            # Calculate relevance score based on coverage
            score = self._calculate_relevance_score(
                question_terms,
                matched_terms,
                matched_percentage,
                ai_response
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                question,
                ai_response,
                matched_terms,
                matched_percentage,
                score
            )
            
            # Identify key points covered and missing
            key_points_covered = self._extract_key_points(ai_response)
            missing_points = self._find_missing_points(question_terms, matched_terms)
            
            result = {
                "relevance_score": round(score, 2),
                "reasoning": reasoning,
                "key_points_covered": key_points_covered[:5],
                "missing_points": missing_points[:5],
                "term_coverage": round(matched_percentage, 2)
            }
            
            return self.log_result(result)
            
        except Exception as e:
            logger.error(f"Error in RelevanceJudge: {e}")
            return {
                "error": str(e),
                "relevance_score": 0.0,
                "reasoning": f"Evaluation failed: {str(e)}",
                "key_points_covered": [],
                "missing_points": []
            }
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text."""
        words = text.lower().split()
        stopwords = {'what', 'is', 'are', 'the', 'a', 'an', 'of', 'to', 'for', 
                     'in', 'on', 'at', 'with', 'without', 'by', 'from', 'as'}
        key_terms = [w.strip('?.!,"') for w in words if w not in stopwords and len(w) > 2]
        return list(set(key_terms))
    
    def _check_term_coverage(self, question_terms: List[str], response: str) -> tuple:
        """Check which question terms appear in the response."""
        response_lower = response.lower()
        matched_terms = []
        
        for term in question_terms:
            if term in response_lower:
                matched_terms.append(term)
        
        if len(question_terms) == 0:
            return [], 0.0
        
        coverage_percentage = len(matched_terms) / len(question_terms)
        return matched_terms, coverage_percentage
    
    def _calculate_relevance_score(self, question_terms: List[str], 
                                   matched_terms: List[str], 
                                   matched_percentage: float,
                                   response: str) -> float:
        """Calculate relevance score based on multiple factors."""
        base_score = matched_percentage
        
        response_length = len(response.split())
        if 5 <= response_length <= 100:
            length_bonus = 0.05
        elif response_length < 5:
            length_bonus = -0.2
        else:
            length_bonus = 0.0
        
        if matched_percentage == 0:
            off_topic_penalty = -0.3
        else:
            off_topic_penalty = 0.0
        
        score = base_score + length_bonus + off_topic_penalty
        return max(0.0, min(1.0, score))
    
    def _generate_reasoning(self, question: str, response: str, 
                           matched_terms: List[str], 
                           matched_percentage: float, 
                           score: float) -> str:
        """Generate human-readable reasoning for the score."""
        if score >= 0.9:
            return f"The response directly answers the question and covers {len(matched_terms)} key terms. Very relevant."
        elif score >= 0.7:
            return f"The response mostly answers the question but misses some key points. Covered {len(matched_terms)} key terms."
        elif score >= 0.5:
            return f"The response partially answers the question. Only {len(matched_terms)} key terms were covered."
        else:
            return f"The response does not appear to directly answer the question. Very few key terms ({len(matched_terms)}) were covered."
    
    def _extract_key_points(self, response: str) -> List[str]:
        """Extract key points from response."""
        sentences = response.split('.')
        key_points = [s.strip() for s in sentences if len(s.strip()) > 10]
        return key_points
    
    def _find_missing_points(self, question_terms: List[str], 
                            matched_terms: List[str]) -> List[str]:
        """Find important terms from question that are missing in response."""
        missing = [term for term in question_terms if term not in matched_terms]
        return missing