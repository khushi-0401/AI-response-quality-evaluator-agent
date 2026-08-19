# ==============================================================================
# LLM INTEGRATION - GOOGLE GENAI SDK
# ==============================================================================

import os
import logging
import json
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

try:
    from google import genai
except ImportError:
    raise ImportError("Run: pip install google-genai")

load_dotenv()

# Enable logging to see raw responses
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMIntegration:
    """
    Handles all LLM API calls for agent evaluations using Google Gemini.
    Supports: Relevance, Accuracy, Hallucination, Completeness
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.model_name = model
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY", "")
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Gemini client."""
        try:
            if not self.api_key:
                logger.warning("No API key available for Gemini. Set GOOGLE_API_KEY.")
                return

            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"✅ GenAI SDK initialized with model: {self.model_name}")

        except Exception as e:
            logger.error(f"Failed to initialize GenAI client: {e}")
            self.client = None

    def _extract_json_from_raw(self, raw: str) -> Dict[str, Any]:
        """Extract JSON from raw response with multiple fallbacks."""
        if not raw:
            return {}

        # Remove markdown code fences if present
        cleaned = re.sub(r'```json\s*', '', raw)
        cleaned = re.sub(r'```\s*', '', cleaned)
        cleaned = cleaned.strip()

        # 1. Try direct parse first
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # 2. Try balanced-brace scan
        start = cleaned.find('{')
        if start != -1:
            depth = 0
            for i, ch in enumerate(cleaned[start:], start):
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        candidate = cleaned[start:i + 1]
                        try:
                            return json.loads(candidate)
                        except json.JSONDecodeError:
                            break

        # 3. Fallback
        logger.warning(f"Could not parse JSON from model output. Raw: {raw[:200]}...")
        return {}

    def generate_json(self, prompt: str, max_tokens: int = 600) -> Dict[str, Any]:
        """Generate and parse JSON from Gemini."""
        if not self.client:
            return {}

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "temperature": 0.1,
                    "max_output_tokens": max_tokens,
                    "response_mime_type": "application/json",
                }
            )

            # Extract text
            if hasattr(response, 'text') and response.text:
                raw = response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                raw = response.candidates[0].content.parts[0].text.strip()
            else:
                raw = str(response).strip()

            logger.info(f"RAW RESPONSE ({len(raw)} chars): {raw[:300]}...")

            return self._extract_json_from_raw(raw)

        except Exception as e:
            logger.error(f"Generation error: {e}")
            return {}

    # =============================================
    # RELEVANCE
    # =============================================

    def evaluate_relevance(self, question: str, ai_response: str) -> Dict[str, Any]:
        prompt = f"""
        Rate relevance (0-10) of this answer to the question.

        Question: {question}
        Answer: {ai_response}

        Return JSON ONLY:
        {{"score": 0-10, "reasoning": "...", "key_points_covered": ["..."], "missing_points": ["..."]}}
        """

        result = self.generate_json(prompt)

        return {
            "score": result.get("score", 5),
            "reasoning": result.get("reasoning", "No reasoning"),
            "key_points_covered": result.get("key_points_covered", []),
            "missing_points": result.get("missing_points", [])
        }

    # =============================================
    # ACCURACY
    # =============================================

    def evaluate_accuracy(self, question: str, ai_response: str, reference: str) -> Dict[str, Any]:
        prompt = f"""
        Rate accuracy (0-10) by comparing answer to reference.

        Question: {question}
        Answer: {ai_response}
        Reference: {reference}

        Return JSON ONLY:
        {{"score": 0-10, "evidence": "...", "correct_claims": ["..."], "incorrect_claims": ["..."]}}
        """

        result = self.generate_json(prompt)

        return {
            "score": result.get("score", 5),
            "evidence": result.get("evidence", "No evidence"),
            "correct_claims": result.get("correct_claims", []),
            "incorrect_claims": result.get("incorrect_claims", [])
        }

    # =============================================
    # HALLUCINATION
    # =============================================

    def detect_hallucination(self, question: str, ai_response: str, source_context: str) -> Dict[str, Any]:
        prompt = f"""
        Detect hallucinations by comparing answer to source context.

        Question: {question}
        Answer: {ai_response}
        Source: {source_context}

        Return JSON ONLY:
        {{
            "hallucination_detected": true/false,
            "hallucination_score": 0-10,
            "hallucinated_statements": [
                {{"statement": "the claim", "explanation": "why it's hallucinated"}}
            ],
            "supported_statements": [
                {{"statement": "the claim", "explanation": "why it's supported"}}
            ],
            "summary": "brief summary"
        }}
        """

        result = self.generate_json(prompt, max_tokens=600)

        # Ensure hallucinated_statements is a list of dictionaries
        hallucinated = result.get("hallucinated_statements", [])
        supported = result.get("supported_statements", [])

        # Convert any string items to dictionaries
        if hallucinated and isinstance(hallucinated[0], str):
            hallucinated = [{"statement": item, "explanation": "Unsupported claim"} for item in hallucinated]
        if supported and isinstance(supported[0], str):
            supported = [{"statement": item, "explanation": "Supported by source"} for item in supported]

        return {
            "hallucination_detected": result.get("hallucination_detected", False),
            "hallucination_score": result.get("hallucination_score", 5),
            "hallucinated_statements": hallucinated,
            "supported_statements": supported,
            "summary": result.get("summary", "No summary")
        }

    # =============================================
    # COMPLETENESS
    # =============================================

    def evaluate_completeness(self, question: str, ai_response: str) -> Dict[str, Any]:
        prompt = f"""
        Rate completeness (0-10) of this answer to the question.

        Question: {question}
        Answer: {ai_response}

        Return JSON ONLY:
        {{"score": 0-10, "reasoning": "...", "covered_aspects": ["..."], "missing_aspects": ["..."]}}
        """

        result = self.generate_json(prompt)

        return {
            "score": result.get("score", 5),
            "reasoning": result.get("reasoning", "No reasoning"),
            "covered_aspects": result.get("covered_aspects", []),
            "missing_aspects": result.get("missing_aspects", [])
        }

    def is_available(self) -> bool:
        return self.client is not None


# ==============================================================================
# TEST
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING GENAI SDK")
    print("=" * 60)

    llm = LLMIntegration()

    if not llm.is_available():
        print("❌ Gemini not available.")
        exit()

    print("✅ Gemini is ready.\n")

    # Test Relevance
    print("Testing Relevance:")
    r = llm.evaluate_relevance(
        "What is machine learning?",
        "Machine learning is a subset of AI."
    )
    print(f"  Score: {r.get('score')}")
    print(f"  Reasoning: {r.get('reasoning')[:100]}...")

    # Test Completeness
    print("\nTesting Completeness:")
    r = llm.evaluate_completeness(
        "What is machine learning and how does it work?",
        "Machine learning is a subset of AI."
    )
    print(f"  Score: {r.get('score')}")
    print(f"  Reasoning: {r.get('reasoning')[:100]}...")
    print(f"  Covered: {r.get('covered_aspects')}")
    print(f"  Missing: {r.get('missing_aspects')}")

    # Test Hallucination
    print("\nTesting Hallucination:")
    r = llm.detect_hallucination(
        "What is the capital of France?",
        "Paris is the capital of France. It has a population of 12 million.",
        "Paris is the capital of France with a population of 2.1 million."
    )
    print(f"  Detected: {r.get('hallucination_detected')}")
    print(f"  Score: {r.get('hallucination_score')}")
    print(f"  Hallucinated: {r.get('hallucinated_statements')}")
    print(f"  Supported: {r.get('supported_statements')}")