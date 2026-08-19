# ==============================================================================
# END-TO-END TESTING - VeriScore AI
# Development of AI Response Validation System
# with Hallucination Detection Assistance
# ==============================================================================

import requests
import time
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
PASS = 0
FAIL = 0
TOTAL = 0

def print_header(text):
    print("\n" + "=" * 70)
    print(f"   {text}")
    print("=" * 70)

def print_test(name, status, message=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if status:
        PASS += 1
        print(f"   ✅ {name}: PASSED {message}")
    else:
        FAIL += 1
        print(f"   ❌ {name}: FAILED {message}")
    return status

def print_subtest(name, status, message=""):
    if status:
        print(f"      ✅ {name}: {message}")
    else:
        print(f"      ❌ {name}: {message}")
    return status

# ==============================================================================
# TEST 1: INFRASTRUCTURE
# ==============================================================================

def test_health():
    print("\n🔵 TEST 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test("Health Check", True, f"Status: {data.get('status')}")
            return True
        return print_test("Health Check", False, f"Status {response.status_code}")
    except Exception as e:
        return print_test("Health Check", False, str(e))

def test_agent_status():
    print("\n🔵 TEST 2: Agent Status")
    try:
        response = requests.get(f"{BASE_URL}/api/agents/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("agents_ready") == True:
                print_test("Agent Status", True, "All 6 agents ready")
                return True
        return print_test("Agent Status", False, f"Status {response.status_code}")
    except Exception as e:
        return print_test("Agent Status", False, str(e))

def test_rag_status():
    print("\n🔵 TEST 3: RAG Status")
    try:
        response = requests.get(f"{BASE_URL}/api/rag/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("rag_ready") == True:
                print_test("RAG Status", True, f"Ready, {data.get('persist_directory')}")
                return True
            return print_test("RAG Status", False, "RAG not ready")
        return print_test("RAG Status", False, f"Status {response.status_code}")
    except Exception as e:
        return print_test("RAG Status", False, str(e))

# ==============================================================================
# TEST 2: MODULE 1 - INPUT
# ==============================================================================

def test_single_evaluation():
    print("\n🔵 TEST 4: Single Evaluation (Module 1)")
    try:
        payload = {
            "question": "What is the capital of France?",
            "ai_response": "Paris is the capital of France.",
            "reference_answer": "The capital of France is Paris."
        }
        response = requests.post(f"{BASE_URL}/api/evaluations/single", json=payload, timeout=10)
        if response.status_code == 201:
            data = response.json()
            if "submission_id" in data:
                print_test("Single Evaluation", True, f"ID: {data['submission_id'][:8]}...")
                return True
        return print_test("Single Evaluation", False, f"Status {response.status_code}")
    except Exception as e:
        return print_test("Single Evaluation", False, str(e))

def test_invalid_input():
    print("\n🔵 TEST 5: Invalid Input Handling")
    try:
        payload = {"question": "", "ai_response": ""}
        response = requests.post(f"{BASE_URL}/api/evaluations/single", json=payload, timeout=10)
        if response.status_code == 422:
            print_test("Invalid Input", True, "422 Validation Error")
            return True
        return print_test("Invalid Input", False, f"Expected 422, got {response.status_code}")
    except Exception as e:
        return print_test("Invalid Input", False, str(e))

# ==============================================================================
# TEST 3: MODULE 2 - AGENTS
# ==============================================================================

def test_relevance_agent():
    print("\n🔵 TEST 6: Relevance Agent")
    try:
        payload = {
            "question": "What is the capital of France?",
            "ai_response": "Paris is the capital of France."
        }
        response = requests.post(f"{BASE_URL}/api/agents/relevance", json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            score = data.get("relevance_score", 0)
            if score >= 0.8:
                print_test("Relevance Agent", True, f"Score: {score:.2f}")
                return True
            return print_test("Relevance Agent", False, f"Score too low: {score:.2f}")
        return print_test("Relevance Agent", False, f"Status {response.status_code}")
    except Exception as e:
        return print_test("Relevance Agent", False, str(e))

def test_accuracy_agent():
    print("\n🔵 TEST 7: Accuracy Agent")
    try:
        payload = {
            "question": "What is the capital of France?",
            "ai_response": "Paris is the capital of France.",
            "reference_answer": "The capital of France is Paris."
        }
        response = requests.post(f"{BASE_URL}/api/agents/accuracy", json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            score = data.get("accuracy_score", 0)
            if score >= 0.8:
                print_test("Accuracy Agent", True, f"Score: {score:.2f}")
                return True
            return print_test("Accuracy Agent", False, f"Score too low: {score:.2f}")
        return print_test("Accuracy Agent", False, f"Status {response.status_code}")
    except Exception as e:
        return print_test("Accuracy Agent", False, str(e))

def test_hallucination_agent():
    print("\n🔵 TEST 8: Hallucination Agent")
    try:
        payload = {
            "question": "What is the capital of France?",
            "ai_response": "Paris is the capital of France. It has a population of 12 million.",
            "source_context": "Paris is the capital of France with a population of 2.1 million."
        }
        response = requests.post(f"{BASE_URL}/api/agents/hallucination", json=payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            if data.get("hallucination_detected") == True:
                print_test("Hallucination Agent", True, "Hallucination correctly detected")
                return True
            return print_test("Hallucination Agent", False, "Hallucination not detected")
        return print_test("Hallucination Agent", False, f"Status {response.status_code}")
    except Exception as e:
        return print_test("Hallucination Agent", False, str(e))

# ==============================================================================
# TEST 4: MODULE 3 - COMPLETENESS + VERDICT
# ==============================================================================

def test_completeness_agent():
    print("\n🔵 TEST 9: Completeness Agent")
    try:
        payload = {
            "question": "What is machine learning and how does it work?",
            "ai_response": "Machine learning is a subset of artificial intelligence."
        }
        response = requests.post(f"{BASE_URL}/api/agents/completeness", json=payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            score = data.get("completeness_score", 0)
            missing = data.get("missing_aspects", [])
            if score < 0.6 and len(missing) > 0:
                print_test("Completeness Agent", True, f"Score: {score:.2f}, Missing: {len(missing)}")
                return True
            return print_test("Completeness Agent", False, f"Score: {score:.2f}, Missing: {len(missing)}")
        return print_test("Completeness Agent", False, f"Status {response.status_code}")
    except Exception as e:
        return print_test("Completeness Agent", False, str(e))

def test_verdict_agent():
    print("\n🔵 TEST 10: Verdict Agent")
    try:
        payload = {
            "question": "What is the capital of France?",
            "ai_response": "Paris is the capital of France.",
            "reference_answer": "The capital of France is Paris.",
            "source_context": "Paris is the capital of France."
        }
        response = requests.post(f"{BASE_URL}/api/agents/verdict", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("verdict") == "PASS":
                print_test("Verdict Agent", True, f"Verdict: PASS, Score: {data.get('overall_score')}")
                return True
            return print_test("Verdict Agent", False, f"Verdict: {data.get('verdict')}")
        return print_test("Verdict Agent", False, f"Status {response.status_code}")
    except Exception as e:
        return print_test("Verdict Agent", False, str(e))

# ==============================================================================
# TEST 5: EVALUATE-ALL
# ==============================================================================

def test_evaluate_all():
    print("\n🔵 TEST 11: Evaluate-All (Complete Pipeline)")
    try:
        payload = {
            "question": "What is the capital of France?",
            "ai_response": "Paris is the capital of France. It has a population of 12 million.",
            "reference_answer": "The capital of France is Paris.",
            "source_context": "Paris is the capital of France with a population of 2.1 million."
        }
        response = requests.post(f"{BASE_URL}/api/agents/evaluate-all", json=payload, timeout=45)
        if response.status_code == 200:
            data = response.json()
            checks = [
                ("relevance" in data, "Relevance present"),
                ("accuracy" in data, "Accuracy present"),
                ("completeness" in data, "Completeness present"),
                ("hallucination" in data, "Hallucination present"),
                ("verdict" in data, "Verdict present"),
                ("submission_id" in data, "Submission ID present")
            ]
            all_passed = True
            for check, msg in checks:
                if not print_subtest(msg, check, "OK" if check else "Missing"):
                    all_passed = False
            
            if all_passed:
                print_test("Evaluate-All", True, f"Verdict: {data['verdict']['verdict']}")
                return True
            return print_test("Evaluate-All", False, "Missing required fields")
        return print_test("Evaluate-All", False, f"Status {response.status_code}")
    except Exception as e:
        return print_test("Evaluate-All", False, str(e))

# ==============================================================================
# TEST 6: FRONTEND API
# ==============================================================================

def test_frontend_health():
    print("\n🔵 TEST 12: Frontend (HTML page accessible)")
    try:
        response = requests.get("http://localhost:3000/", timeout=5)
        if response.status_code == 200:
            if "VeriScore" in response.text or "AI" in response.text:
                print_test("Frontend Page", True, "HTML page loaded")
                return True
            return print_test("Frontend Page", False, "Page loaded but content missing")
        return print_test("Frontend Page", False, f"Status {response.status_code}")
    except Exception as e:
        return print_test("Frontend Page", False, f"Frontend not running: {str(e)}")

def test_dashboard_page():
    print("\n🔵 TEST 13: Dashboard Page")
    try:
        response = requests.get("http://localhost:3000/dashboard.html", timeout=5)
        if response.status_code == 200:
            if "Dashboard" in response.text or "chart" in response.text.lower():
                print_test("Dashboard Page", True, "Dashboard loaded")
                return True
            return print_test("Dashboard Page", False, "Page loaded but content missing")
        return print_test("Dashboard Page", False, f"Status {response.status_code}")
    except Exception as e:
        return print_test("Dashboard Page", False, f"Not accessible: {str(e)}")

# ==============================================================================
# TEST 7: CONSISTENCY VALIDATION
# ==============================================================================

def test_scoring_consistency():
    print("\n🔵 TEST 14: Scoring Consistency (3 runs)")
    try:
        payload = {
            "question": "What is the capital of France?",
            "ai_response": "Paris is the capital of France.",
            "reference_answer": "The capital of France is Paris.",
            "source_context": "Paris is the capital of France."
        }
        
        scores = []
        for i in range(3):
            response = requests.post(f"{BASE_URL}/api/agents/verdict", json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                scores.append(data.get("overall_score", 0))
            else:
                print_test("Scoring Consistency", False, f"Run {i+1} failed")
                return False
            
            time.sleep(1)  # Small delay between runs
        
        # Check consistency
        avg_score = sum(scores) / len(scores)
        max_diff = max(scores) - min(scores)
        
        if max_diff <= 0.1:
            print_test("Scoring Consistency", True, f"Scores: {scores}, Avg: {avg_score:.2f}, Diff: {max_diff:.3f}")
            return True
        else:
            print_test("Scoring Consistency", False, f"Scores: {scores}, Diff too large: {max_diff:.3f}")
            return False
            
    except Exception as e:
        return print_test("Scoring Consistency", False, str(e))

# ==============================================================================
# RUN ALL TESTS
# ==============================================================================

def run_all_tests():
    global PASS, FAIL, TOTAL
    
    print_header("🧪 VERISCORE AI - END-TO-END TESTING")
    print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Backend URL: {BASE_URL}")
    print(f"   Frontend URL: http://localhost:3000")
    print("   Make sure both servers are running!")
    print("=" * 70)
    
    time.sleep(2)
    
    # Run all tests
    test_health()
    test_agent_status()
    test_rag_status()
    
    test_single_evaluation()
    test_invalid_input()
    
    test_relevance_agent()
    test_accuracy_agent()
    test_hallucination_agent()
    
    test_completeness_agent()
    test_verdict_agent()
    test_evaluate_all()
    
    test_frontend_health()
    test_dashboard_page()
    
    test_scoring_consistency()
    
    # =============================================
    # SUMMARY
    # =============================================
    print_header("📊 TEST SUMMARY")
    print(f"   Total Tests : {TOTAL}")
    print(f"   ✅ Passed   : {PASS}")
    print(f"   ❌ Failed   : {FAIL}")
    print(f"   Pass Rate   : {(PASS/TOTAL*100):.1f}%" if TOTAL > 0 else "No tests run")
    print("=" * 70)
    
    if FAIL == 0:
        print("🎉 ALL TESTS PASSED! System is ready for deployment.")
    else:
        print(f"⚠️ {FAIL} test(s) failed. Please review the errors above.")
    
    print("=" * 70)

if __name__ == "__main__":
    run_all_tests()