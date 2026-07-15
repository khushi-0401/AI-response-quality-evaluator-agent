# ==============================================================================
# TEST SCRIPT FOR MILESTONE 2 - AGENTS
# Run this to test all 4 agents
# ==============================================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from app.agents import RelevanceJudge, AccuracyJudge, HallucinationDetector, ValidationAgent
from app.rag_retriever import RAGRetriever

def test_relevance_agent():
    """Test Relevance Judge Agent"""
    print("\n" + "=" * 60)
    print("TESTING RELEVANCE JUDGE AGENT")
    print("=" * 60)
    
    agent = RelevanceJudge()
    
    test_cases = [
        {
            "question": "What is machine learning?",
            "ai_response": "Machine learning is a subset of artificial intelligence that enables systems to learn from data."
        },
        {
            "question": "What is the capital of France?",
            "ai_response": "I like pizza and pasta."
        },
        {
            "question": "Explain quantum computing.",
            "ai_response": "Quantum computing uses qubits instead of classical bits."
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}:")
        print(f"   Question: {test['question']}")
        print(f"   Response: {test['ai_response'][:50]}...")
        
        result = agent.evaluate(test['question'], test['ai_response'])
        
        print(f"   ✅ Relevance Score: {result['relevance_score']}")
        print(f"   📝 Reasoning: {result['reasoning']}")
        print(f"   📊 Term Coverage: {result['term_coverage']}")
        print(f"   📌 Key Points Covered: {result['key_points_covered'][:2]}")

def test_accuracy_agent():
    """Test Accuracy Judge Agent"""
    print("\n" + "=" * 60)
    print("TESTING ACCURACY JUDGE AGENT")
    print("=" * 60)
    
    agent = AccuracyJudge()
    
    test_cases = [
        {
            "question": "What is the capital of France?",
            "ai_response": "Paris is the capital of France.",
            "reference_answer": "The capital of France is Paris."
        },
        {
            "question": "What is 2+2?",
            "ai_response": "2+2 equals 5.",
            "reference_answer": "2+2 equals 4."
        },
        {
            "question": "What is the tallest mountain?",
            "ai_response": "Mount Everest is the tallest mountain.",
            "reference_answer": "Mount Everest is the tallest mountain on Earth."
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}:")
        print(f"   Question: {test['question']}")
        print(f"   Response: {test['ai_response'][:50]}...")
        
        result = agent.evaluate(
            test['question'], 
            test['ai_response'],
            reference_answer=test.get('reference_answer')
        )
        
        print(f"   ✅ Accuracy Score: {result['accuracy_score']}")
        print(f"   📝 Evidence: {result['evidence']}")
        print(f"   ✅ Correct Claims: {len(result['correct_claims'])}")
        print(f"   ❌ Incorrect Claims: {len(result['incorrect_claims'])}")

def test_hallucination_agent():
    """Test Hallucination Detection Agent"""
    print("\n" + "=" * 60)
    print("TESTING HALLUCINATION DETECTION AGENT")
    print("=" * 60)
    
    agent = HallucinationDetector()
    
    test_cases = [
        {
            "question": "What is the capital of France?",
            "ai_response": "Paris is the capital of France. It has a population of 12 million people.",
            "source_context": "Paris is the capital of France with a population of 2.1 million."
        },
        {
            "question": "What is machine learning?",
            "ai_response": "Machine learning is a subset of AI.",
            "source_context": "Machine learning is a field of artificial intelligence that uses algorithms to learn from data."
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}:")
        print(f"   Question: {test['question']}")
        print(f"   Response: {test['ai_response'][:50]}...")
        
        result = agent.evaluate(
            test['question'],
            test['ai_response'],
            test['source_context']
        )
        
        print(f"   🚨 Hallucination Detected: {result['hallucination_detected']}")
        print(f"   📊 Hallucination Score: {result['hallucination_score']}")
        print(f"   📌 Hallucinated Statements: {len(result['hallucinated_statements'])}")
        print(f"   ✅ Supported Statements: {len(result['supported_statements'])}")
        print(f"   📝 Summary: {result['summary']}")

def test_validation_agent():
    """Test Validation Agent"""
    print("\n" + "=" * 60)
    print("TESTING VALIDATION AGENT")
    print("=" * 60)
    
    agent = ValidationAgent()
    
    test_dataset = [
        {
            "question": "What is the capital of France?",
            "ai_response": "Paris is the capital of France.",
            "reference_answer": "The capital of France is Paris.",
            "source_context": "Paris is the capital of France."
        },
        {
            "question": "What is 2+2?",
            "ai_response": "2+2 equals 4.",
            "reference_answer": "2+2 equals 4.",
            "source_context": "2+2 equals 4."
        },
        {
            "question": "What is machine learning?",
            "ai_response": "ML is a subset of AI.",
            "reference_answer": "Machine learning is a field of AI.",
            "source_context": "Machine learning is a subset of artificial intelligence."
        },
        {
            "question": "What is the tallest mountain?",
            "ai_response": "Mount Everest is the tallest.",
            "reference_answer": "Mount Everest is the tallest mountain.",
            "source_context": "Mount Everest is the tallest mountain on Earth."
        }
    ]
    
    print(f"\n📊 Test Dataset Size: {len(test_dataset)}")
    
    result = agent.evaluate(test_dataset)
    
    print("\n📊 Validation Summary:")
    summary = result.get("validation_summary", {})
    
    if summary:
        relevance = summary.get("relevance_agent", {})
        accuracy = summary.get("accuracy_agent", {})
        hallucination = summary.get("hallucination_agent", {})
        
        print(f"\n   🔵 Relevance Agent:")
        print(f"      - Avg Score: {relevance.get('avg_score', 0)}")
        print(f"      - Consistency: {relevance.get('consistency', 0)}")
        print(f"      - Pass Rate: {relevance.get('pass_rate', 0)}")
        
        print(f"\n   🟢 Accuracy Agent:")
        print(f"      - Avg Score: {accuracy.get('avg_score', 0)}")
        print(f"      - Consistency: {accuracy.get('consistency', 0)}")
        print(f"      - Pass Rate: {accuracy.get('pass_rate', 0)}")
        
        print(f"\n   🟠 Hallucination Agent:")
        print(f"      - Detection Rate: {hallucination.get('detection_rate', 0)}")
        
        print(f"\n   📊 Overall Pass Rate: {summary.get('overall_pass_rate', 0)}")
    
    print(f"\n📋 Total Tested: {result.get('total_tested', 0)}")

def test_with_rag():
    """Test agents with RAG context"""
    print("\n" + "=" * 60)
    print("TESTING AGENTS WITH RAG CONTEXT")
    print("=" * 60)
    
    # Initialize RAG
    retriever = RAGRetriever()
    
    if not retriever.is_ready():
        print("❌ RAG not ready. Run build_knowledge_base.py first.")
        return
    
    print("✅ RAG is ready!")
    
    # Test query
    question = "What is the capital of France?"
    ai_response = "Paris is the capital of France. It has a population of 12 million."
    
    print(f"\n📝 Question: {question}")
    print(f"📝 Response: {ai_response}")
    
    # Get context from RAG
    context = retriever.retrieve_context(question, k=3)
    print(f"\n📚 Retrieved Context: {context[:200]}...")
    
    # Run agents with RAG context
    relevance = RelevanceJudge()
    accuracy = AccuracyJudge()
    hallucination = HallucinationDetector()
    
    relevance_result = relevance.evaluate(question, ai_response)
    accuracy_result = accuracy.evaluate(question, ai_response, source_context=context)
    hallucination_result = hallucination.evaluate(question, ai_response, context)
    
    print(f"\n📊 Results with RAG Context:")
    print(f"   🔵 Relevance Score: {relevance_result['relevance_score']}")
    print(f"   🟢 Accuracy Score: {accuracy_result['accuracy_score']}")
    print(f"   🚨 Hallucination Score: {hallucination_result['hallucination_score']}")
    print(f"   🚨 Hallucination Detected: {hallucination_result['hallucination_detected']}")

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🏆 MILESTONE 2 - AGENT TESTS")
    print("=" * 60)
    
    try:
        # Run all tests
        test_relevance_agent()
        test_accuracy_agent()
        test_hallucination_agent()
        test_validation_agent()
        test_with_rag()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")

if __name__ == "__main__":
    main()