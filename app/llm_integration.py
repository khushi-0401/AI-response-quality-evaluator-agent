# ==============================================================================
# LLM INTEGRATION - GOOGLE GEMINI
# ==============================================================================

import os
import logging
import json
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class LLMIntegration:
    
    def __init__(self, api_key: Optional[str] = None, model: str = "models/gemini-2.5-flash"):
        self.model_name = model
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY", "")
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        try:
            if not self.api_key:
                logger.warning("No API key available for Gemini.")
                return
            
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel('models/gemini-2.5-flash')
            logger.info(f"✅ Gemini client initialized with model: models/gemini-2.5-flash")
            
        except ImportError:
            logger.error("google-generativeai not installed.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.client = None
    
    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response from markdown code blocks."""
        # Remove markdown code blocks
        cleaned = re.sub(r'```json\s*', '', response)
        cleaned = re.sub(r'```\s*', '', cleaned)
        cleaned = cleaned.strip()
        return cleaned
    
    def _safe_json_parse(self, response: str, default: Dict) -> Dict:
        """Safely parse JSON with fallback."""
        try:
            cleaned = self._clean_json_response(response)
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            try:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
            return default
    
    def generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        if not self.client:
            return "Error: Gemini client not initialized."
        
        try:
            import google.generativeai as genai
            response = self.client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.3,
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return f"Error: {str(e)}"
    
    def evaluate_relevance(self, question: str, ai_response: str) -> Dict[str, Any]:
        prompt = f"""
        You are an AI evaluator. Evaluate the relevance of the AI response to the question.
        
        Question: {question}
        Response: {ai_response}
        
        Return a valid JSON with these fields:
        - score: (0-10)
        - reasoning: (brief explanation)
        - key_points_covered: (list of key points from response)
        - missing_points: (list of key points from question that are missing)
        
        Output ONLY valid JSON. Do not include markdown or any other text.
        """
        
        response = self.generate_response(prompt)
        
        default = {
            "score": 5,
            "reasoning": "Unable to parse response",
            "key_points_covered": [],
            "missing_points": []
        }
        
        result = self._safe_json_parse(response, default)
        
        # Ensure all fields exist
        result.setdefault("score", 5)
        result.setdefault("reasoning", "No reasoning provided")
        result.setdefault("key_points_covered", [])
        result.setdefault("missing_points", [])
        
        return result
    
    def evaluate_accuracy(self, question: str, ai_response: str, reference: str) -> Dict[str, Any]:
        prompt = f"""
        You are an AI evaluator. Evaluate the accuracy of the AI response compared to the reference answer.
        
        Question: {question}
        AI Response: {ai_response}
        Reference Answer: {reference}
        
        Return a valid JSON with these fields:
        - score: (0-10)
        - evidence: (explanation of accuracy)
        - correct_claims: (list of correct claims from response)
        - incorrect_claims: (list of incorrect claims from response)
        
        Output ONLY valid JSON. Do not include markdown or any other text.
        """
        
        response = self.generate_response(prompt)
        
        default = {
            "score": 5,
            "evidence": "Unable to parse response",
            "correct_claims": [],
            "incorrect_claims": []
        }
        
        result = self._safe_json_parse(response, default)
        
        result.setdefault("score", 5)
        result.setdefault("evidence", "No evidence provided")
        result.setdefault("correct_claims", [])
        result.setdefault("incorrect_claims", [])
        
        return result
    
    def detect_hallucination(self, question: str, ai_response: str, source_context: str) -> Dict[str, Any]:
        prompt = f"""
        You are an AI evaluator. Detect hallucinations in the AI response by cross-referencing with the source context.
        
        Question: {question}
        AI Response: {ai_response}
        Source Context: {source_context}
        
        Return a valid JSON with these fields:
        - hallucination_detected: (true/false)
        - hallucination_score: (0-10, higher = more hallucination)
        - hallucinated_statements: (list of objects with "statement" and "explanation")
        - supported_statements: (list of objects with "statement" and "explanation")
        - summary: (brief summary)
        
        Output ONLY valid JSON. Do not include markdown or any other text.
        """
        
        response = self.generate_response(prompt, max_tokens=800)
        
        default = {
            "hallucination_detected": False,
            "hallucination_score": 5,
            "hallucinated_statements": [],
            "supported_statements": [],
            "summary": "Unable to parse response"
        }
        
        result = self._safe_json_parse(response, default)
        
        result.setdefault("hallucination_detected", False)
        result.setdefault("hallucination_score", 5)
        result.setdefault("hallucinated_statements", [])
        result.setdefault("supported_statements", [])
        result.setdefault("summary", "No summary provided")
        
        return result
    
    def is_available(self) -> bool:
        return self.client is not None


if __name__ == "__main__":
    llm = LLMIntegration()
    
    if llm.is_available():
        print("✅ Gemini is connected!")
        
        result = llm.evaluate_relevance(
            "What is machine learning?",
            "Machine learning is a subset of AI."
        )
        print(f"\n📊 Relevance: {result}")
    else:
        print("❌ Gemini not available.")