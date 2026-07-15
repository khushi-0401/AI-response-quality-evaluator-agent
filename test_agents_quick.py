# ==============================================================================
# QUICK TEST FOR AGENTS (Simple Demo)
# ==============================================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents import RelevanceJudge, AccuracyJudge, HallucinationDetector

def quick_test():
    print("=" * 60)
    print("🚀 QUICK AGENT TEST")
    print("=" * 60)
    
    question = "What is the capital of France?"
    ai_response = "Paris is the capital of France. It has a population of 12 million."
    source_context = "Paris is the capital of France with a population of 2.1 million."
    
    print(f"\n📝 Question: {question}")
    print(f"📝 Response: {ai_response}")
    print(f"📚 Context: {source_context}")
    
    # Test Relevance Agent
    print("\n" + "-" * 40)
    print("1. Relevance Judge Agent")
    relevance = RelevanceJudge()
    result = relevance.evaluate(question, ai_response)
    print(f"   Score: {result['relevance_score']}")
    print(f"   Reasoning: {result['reasoning']}")
    
    # Test Accuracy Agent
    print("\n" + "-" * 40)
    print("2. Accuracy Judge Agent")
    accuracy = AccuracyJudge()
    result = accuracy.evaluate(question, ai_response, source_context=source_context)
    print(f"   Score: {result['accuracy_score']}")
    print(f"   Evidence: {result['evidence']}")
    
    # Test Hallucination Agent
    print("\n" + "-" * 40)
    print("3. Hallucination Detection Agent")
    hallucination = HallucinationDetector()
    result = hallucination.evaluate(question, ai_response, source_context)
    print(f"   Detected: {result['hallucination_detected']}")
    print(f"   Score: {result['hallucination_score']}")
    print(f"   Summary: {result['summary']}")
    
    print("\n" + "=" * 60)
    print("✅ QUICK TEST COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    quick_test()