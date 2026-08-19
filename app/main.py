from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import uuid

from app.database import engine, get_db
from app import models, schemas
from app.rag_retriever import RAGRetriever

# ==============================================================================
# AGENT IMPORTS
# ==============================================================================

# Set this to False to use rule-based agents instead of LLM
USE_LLM = True

if USE_LLM:
    from app.agents.relevance_agent import RelevanceJudge
    from app.agents.accuracy_agent import AccuracyJudge
    from app.agents.hallucination_agent import HallucinationDetector
    from app.agents.completeness_agent import CompletenessJudge
    from app.agents.verdict_agent import VerdictAgent
    from app.agents.validation_agent import ValidationAgent
    AGENT_TYPE = "LLM-Powered"
else:
    from app.agents.relevance_agent import RelevanceJudge
    from app.agents.accuracy_agent import AccuracyJudge
    from app.agents.hallucination_agent import HallucinationDetector
    from app.agents.completeness_agent import CompletenessJudge
    from app.agents.verdict_agent import VerdictAgent
    from app.agents.validation_agent import ValidationAgent
    AGENT_TYPE = "Rule-Based"

# ==============================================================================
# SETUP
# ==============================================================================

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="VeriScore AI - Response Quality Evaluator",
    description=f"AI-powered response evaluation with {AGENT_TYPE} agents. Modules 1, 2, and 3 complete.",
    version="0.1.0-alpha"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG retriever
rag_retriever = RAGRetriever()

# Initialize All 6 Agents
relevance_judge = RelevanceJudge()
accuracy_judge = AccuracyJudge()
hallucination_detector = HallucinationDetector()
completeness_judge = CompletenessJudge()
verdict_agent = VerdictAgent()
validation_agent = ValidationAgent()

logger.info(f"✅ System initialized with {AGENT_TYPE} agents")
logger.info("✅ Agents: Relevance, Accuracy, Hallucination, Completeness, Verdict, Validation")


# ==============================================================================
# INFRASTRUCTURE ENDPOINTS
# ==============================================================================

@app.get("/health", tags=["Infrastructure"])
async def health_check():
    return {
        "status": "healthy",
        "module": "VeriScore AI - Modules 1, 2, 3",
        "rag_ready": rag_retriever.is_ready(),
        "agent_type": AGENT_TYPE,
        "agents": ["Relevance", "Accuracy", "Hallucination", "Completeness", "Verdict", "Validation"]
    }


# ==============================================================================
# MODULE 1: EVALUATION INPUT ENDPOINTS
# ==============================================================================

@app.post(
    "/api/evaluations/single", 
    response_model=schemas.SubmissionAcknowledgement, 
    status_code=status.HTTP_201_CREATED,
    tags=["Submissions"]
)
async def submit_single_evaluation(
    payload: schemas.SingleSubmissionCreate, 
    db: Session = Depends(get_db)
) -> schemas.SubmissionAcknowledgement:
    
    new_submission = models.EvaluationSubmission(
        question=payload.question,
        ai_response=payload.ai_response,
        reference_answer=payload.reference_answer,
        source_document=payload.source_document,
        source_document_name=payload.source_document_name,
        mode="single"
    )
    
    try:
        db.add(new_submission)
        db.commit()
        db.refresh(new_submission)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database insertion failed: {str(e)}"
        )
    
    return schemas.SubmissionAcknowledgement(
        submission_id=new_submission.id,
        status=new_submission.status,
        message="Evaluation request successfully logged and queued for evaluation."
    )


@app.get(
    "/api/evaluations/{submission_id}", 
    response_model=schemas.SubmissionDetailsResponse,
    tags=["Submissions"]
)
async def get_evaluation_status(
    submission_id: str, 
    db: Session = Depends(get_db)
) -> schemas.SubmissionDetailsResponse:
    
    record = db.query(models.EvaluationSubmission).filter(models.EvaluationSubmission.id == submission_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation submission with ID '{submission_id}' not found."
        )
    
    return record


@app.post("/api/v1/evaluate")
async def submit_for_evaluation(payload: schemas.EvaluationRequest):
    return {
        "status": "received",
        "message": "Evaluation data ingestion successful",
        "data": {
            "question": payload.question,
            "ai_response": payload.ai_response,
            "has_reference": payload.reference_answer is not None
        }
    }


# ==============================================================================
# MODULE 1: RAG ENDPOINTS
# ==============================================================================

@app.post(
    "/api/evaluations/grounded",
    response_model=schemas.SubmissionAcknowledgement,
    status_code=status.HTTP_201_CREATED,
    tags=["RAG Evaluations"]
)
async def evaluate_with_grounding(
    payload: schemas.SingleSubmissionCreate,
    db: Session = Depends(get_db)
) -> schemas.SubmissionAcknowledgement:
    
    if not rag_retriever.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Knowledge base not initialized. Please run build_knowledge_base.py first."
        )
    
    context = rag_retriever.retrieve_context(payload.question, k=3)
    
    new_submission = models.EvaluationSubmission(
        question=payload.question,
        ai_response=payload.ai_response,
        reference_answer=payload.reference_answer,
        source_document=context,
        source_document_name="RAG_Retrieved_Context",
        mode="grounded"
    )
    
    try:
        db.add(new_submission)
        db.commit()
        db.refresh(new_submission)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database insertion failed: {str(e)}"
        )
    
    return schemas.SubmissionAcknowledgement(
        submission_id=new_submission.id,
        status=new_submission.status,
        message=f"Evaluation submission with RAG grounding created. Retrieved {len(context)} characters of context."
    )


@app.get(
    "/api/rag/status",
    tags=["RAG"]
)
async def get_rag_status():
    is_ready = rag_retriever.is_ready()
    return {
        "rag_ready": is_ready,
        "persist_directory": "./chroma_db",
        "message": "Knowledge base is ready" if is_ready else "Please run build_knowledge_base.py"
    }


@app.post(
    "/api/rag/rebuild",
    tags=["RAG"]
)
async def rebuild_knowledge_base():
    import subprocess
    import sys
    
    try:
        result = subprocess.run(
            [sys.executable, "build_knowledge_base.py"],
            capture_output=True,
            text=True,
            cwd="."
        )
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Build failed: {result.stderr}"
            )
        
        global rag_retriever
        rag_retriever = RAGRetriever()
        
        return {
            "status": "success",
            "message": "Knowledge base rebuilt successfully",
            "output": result.stdout
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rebuild knowledge base: {str(e)}"
        )


# ==============================================================================
# MODULE 2: AGENT EVALUATION ENDPOINTS
# ==============================================================================

@app.post(
    "/api/agents/relevance",
    response_model=schemas.RelevanceResponse,
    tags=["Agents"]
)
async def evaluate_relevance(
    payload: schemas.AgentEvaluationRequest
) -> schemas.RelevanceResponse:
    try:
        result = relevance_judge.evaluate(
            question=payload.question,
            ai_response=payload.ai_response
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return schemas.RelevanceResponse(
            relevance_score=result["relevance_score"],
            reasoning=result["reasoning"],
            key_points_covered=result["key_points_covered"],
            missing_points=result["missing_points"],
            term_coverage=result.get("term_coverage", 0.0)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in relevance evaluation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Relevance evaluation failed: {str(e)}"
        )


@app.post(
    "/api/agents/accuracy",
    response_model=schemas.AccuracyResponse,
    tags=["Agents"]
)
async def evaluate_accuracy(
    payload: schemas.AgentEvaluationRequest
) -> schemas.AccuracyResponse:
    try:
        source_context = payload.source_context
        if not source_context and payload.use_rag:
            if rag_retriever.is_ready():
                source_context = rag_retriever.retrieve_context(payload.question, k=3)
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="RAG not available. Please provide source_context or build knowledge base."
                )
        
        result = accuracy_judge.evaluate(
            question=payload.question,
            ai_response=payload.ai_response,
            reference_answer=payload.reference_answer,
            source_context=source_context
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return schemas.AccuracyResponse(
            accuracy_score=result["accuracy_score"],
            evidence=result["evidence"],
            correct_claims=result["correct_claims"],
            incorrect_claims=result["incorrect_claims"],
            partially_correct_claims=result["partially_correct_claims"],
            total_claims=result["total_claims"],
            verified_claims=result["verified_claims"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in accuracy evaluation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Accuracy evaluation failed: {str(e)}"
        )


@app.post(
    "/api/agents/hallucination",
    response_model=schemas.HallucinationResponse,
    tags=["Agents"]
)
async def detect_hallucination(
    payload: schemas.AgentEvaluationRequest
) -> schemas.HallucinationResponse:
    try:
        source_context = payload.source_context
        if not source_context and payload.use_rag:
            if rag_retriever.is_ready():
                source_context = rag_retriever.retrieve_context(payload.question, k=5)
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="RAG not available. Please provide source_context or build knowledge base."
                )
        
        if not source_context:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source context is required for hallucination detection"
            )
        
        result = hallucination_detector.evaluate(
            question=payload.question,
            ai_response=payload.ai_response,
            source_context=source_context
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return schemas.HallucinationResponse(
            hallucination_detected=result["hallucination_detected"],
            hallucination_score=result["hallucination_score"],
            hallucinated_statements=result["hallucinated_statements"],
            supported_statements=result["supported_statements"],
            total_claims=result["total_claims"],
            hallucinated_count=result["hallucinated_count"],
            supported_count=result["supported_count"],
            summary=result["summary"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in hallucination detection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hallucination detection failed: {str(e)}"
        )


# ==============================================================================
# MODULE 3: COMPLETENESS & VERDICT ENDPOINTS
# ==============================================================================

@app.post(
    "/api/agents/completeness",
    response_model=schemas.CompletenessResponse,
    tags=["Agents"]
)
async def evaluate_completeness(
    payload: schemas.AgentEvaluationRequest
) -> schemas.CompletenessResponse:
    try:
        result = completeness_judge.evaluate(
            question=payload.question,
            ai_response=payload.ai_response
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return schemas.CompletenessResponse(
            completeness_score=result["completeness_score"],
            reasoning=result["reasoning"],
            covered_aspects=result["covered_aspects"],
            missing_aspects=result["missing_aspects"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in completeness evaluation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Completeness evaluation failed: {str(e)}"
        )


@app.post(
    "/api/agents/verdict",
    response_model=schemas.VerdictResponse,
    tags=["Agents"]
)
async def get_verdict(
    payload: schemas.AgentEvaluationRequest
) -> schemas.VerdictResponse:
    try:
        # Get source context
        source_context = payload.source_context
        if not source_context and payload.use_rag:
            if rag_retriever.is_ready():
                source_context = rag_retriever.retrieve_context(payload.question, k=3)
        
        # Run all agents to get scores
        relevance_result = relevance_judge.evaluate(
            question=payload.question,
            ai_response=payload.ai_response
        )
        
        accuracy_result = accuracy_judge.evaluate(
            question=payload.question,
            ai_response=payload.ai_response,
            reference_answer=payload.reference_answer,
            source_context=source_context
        )
        
        completeness_result = completeness_judge.evaluate(
            question=payload.question,
            ai_response=payload.ai_response
        )
        
        hallucination_result = hallucination_detector.evaluate(
            question=payload.question,
            ai_response=payload.ai_response,
            source_context=source_context or ""
        )
        
        # Prepare scores and reasonings
        scores = {
            "relevance_score": relevance_result.get("relevance_score", 0),
            "accuracy_score": accuracy_result.get("accuracy_score", 0),
            "completeness_score": completeness_result.get("completeness_score", 0),
            "hallucination_score": hallucination_result.get("hallucination_score", 0)
        }
        
        reasonings = {
            "relevance": relevance_result.get("reasoning", ""),
            "accuracy": accuracy_result.get("evidence", ""),
            "completeness": completeness_result.get("reasoning", ""),
            "hallucination": hallucination_result.get("summary", "")
        }
        
        verdict_result = verdict_agent.evaluate(scores, reasonings)
        
        if "error" in verdict_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=verdict_result["error"]
            )
        
        return schemas.VerdictResponse(
            overall_score=verdict_result["overall_score"],
            verdict=verdict_result["verdict"],
            verdict_emoji=verdict_result["verdict_emoji"],
            dimension_breakdown=verdict_result["dimension_breakdown"],
            consolidated_reasoning=verdict_result["consolidated_reasoning"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in verdict: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verdict failed: {str(e)}"
        )


# ==============================================================================
# MODULE 2 & 3: EVALUATE ALL AGENTS
# ==============================================================================

@app.post(
    "/api/agents/evaluate-all",
    response_model=schemas.AgentEvaluationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Agents"]
)
async def evaluate_all_agents(
    payload: schemas.AgentEvaluationRequest,
    db: Session = Depends(get_db)
) -> schemas.AgentEvaluationResponse:
    try:
        # Get source context
        source_context = payload.source_context
        if not source_context and payload.use_rag:
            if rag_retriever.is_ready():
                source_context = rag_retriever.retrieve_context(payload.question, k=5)
        
        # Run all agents
        relevance_result = relevance_judge.evaluate(
            question=payload.question,
            ai_response=payload.ai_response
        )
        
        accuracy_result = accuracy_judge.evaluate(
            question=payload.question,
            ai_response=payload.ai_response,
            reference_answer=payload.reference_answer,
            source_context=source_context
        )
        
        completeness_result = completeness_judge.evaluate(
            question=payload.question,
            ai_response=payload.ai_response
        )
        
        hallucination_result = hallucination_detector.evaluate(
            question=payload.question,
            ai_response=payload.ai_response,
            source_context=source_context or ""
        )
        
        # Prepare scores and reasonings for verdict
        scores = {
            "relevance_score": relevance_result.get("relevance_score", 0),
            "accuracy_score": accuracy_result.get("accuracy_score", 0),
            "completeness_score": completeness_result.get("completeness_score", 0),
            "hallucination_score": hallucination_result.get("hallucination_score", 0)
        }
        
        reasonings = {
            "relevance": relevance_result.get("reasoning", ""),
            "accuracy": accuracy_result.get("evidence", ""),
            "completeness": completeness_result.get("reasoning", ""),
            "hallucination": hallucination_result.get("summary", "")
        }
        
        verdict_result = verdict_agent.evaluate(scores, reasonings)
        
        # Store in database
        new_submission = models.EvaluationSubmission(
            question=payload.question,
            ai_response=payload.ai_response,
            reference_answer=payload.reference_answer,
            source_document=source_context,
            source_document_name="RAG_Context_for_Agents",
            mode="agent_evaluation",
            evaluation_score=verdict_result.get("overall_score", 0),
            evaluation_feedback=verdict_result.get("consolidated_reasoning", "")
        )
        
        db.add(new_submission)
        db.commit()
        db.refresh(new_submission)
        
        return schemas.AgentEvaluationResponse(
            submission_id=new_submission.id,
            question=payload.question,
            ai_response=payload.ai_response,
            relevance=schemas.RelevanceResponse(
                relevance_score=relevance_result["relevance_score"],
                reasoning=relevance_result["reasoning"],
                key_points_covered=relevance_result["key_points_covered"],
                missing_points=relevance_result["missing_points"],
                term_coverage=relevance_result.get("term_coverage", 0.0)
            ),
            accuracy=schemas.AccuracyResponse(
                accuracy_score=accuracy_result["accuracy_score"],
                evidence=accuracy_result["evidence"],
                correct_claims=accuracy_result["correct_claims"],
                incorrect_claims=accuracy_result["incorrect_claims"],
                partially_correct_claims=accuracy_result["partially_correct_claims"],
                total_claims=accuracy_result["total_claims"],
                verified_claims=accuracy_result["verified_claims"]
            ),
            completeness=schemas.CompletenessResponse(
                completeness_score=completeness_result["completeness_score"],
                reasoning=completeness_result["reasoning"],
                covered_aspects=completeness_result["covered_aspects"],
                missing_aspects=completeness_result["missing_aspects"]
            ),
            hallucination=schemas.HallucinationResponse(
                hallucination_detected=hallucination_result["hallucination_detected"],
                hallucination_score=hallucination_result["hallucination_score"],
                hallucinated_statements=hallucination_result["hallucinated_statements"],
                supported_statements=hallucination_result["supported_statements"],
                total_claims=hallucination_result["total_claims"],
                hallucinated_count=hallucination_result["hallucinated_count"],
                supported_count=hallucination_result["supported_count"],
                summary=hallucination_result["summary"]
            ),
            verdict=schemas.VerdictResponse(
                overall_score=verdict_result["overall_score"],
                verdict=verdict_result["verdict"],
                verdict_emoji=verdict_result["verdict_emoji"],
                dimension_breakdown=verdict_result["dimension_breakdown"],
                consolidated_reasoning=verdict_result["consolidated_reasoning"]
            ),
            status="completed"
        )
    except Exception as e:
        logger.error(f"Error in evaluate-all: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )


# ==============================================================================
# MODULE 2: VALIDATION AGENT
# ==============================================================================

@app.post(
    "/api/agents/validate",
    tags=["Agents"]
)
async def validate_agents(
    payload: schemas.ValidationRequest
):
    try:
        result = validation_agent.evaluate(
            test_dataset=payload.test_dataset
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in validation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


# ==============================================================================
# AGENT STATUS
# ==============================================================================

@app.get(
    "/api/agents/status",
    tags=["Agents"]
)
async def get_agents_status():
    return {
        "agents_ready": True,
        "agent_type": AGENT_TYPE,
        "relevance_agent": "ready",
        "accuracy_agent": "ready",
        "hallucination_agent": "ready",
        "completeness_agent": "ready",
        "verdict_agent": "ready",
        "validation_agent": "ready",
        "rag_available": rag_retriever.is_ready(),
        "llm_available": True
    }


# ==============================================================================
# DASHBOARD STATS ENDPOINT (FOR SIDEBAR)
# ==============================================================================

@app.get("/api/stats", tags=["Dashboard"])
async def get_stats(db: Session = Depends(get_db)):
    """
    Get statistics for the sidebar and dashboard
    """
    try:
        # Total submissions
        total = db.query(models.EvaluationSubmission).count()
        
        # Pass count (COMPLETED with score >= 0.7)
        pass_count = db.query(models.EvaluationSubmission).filter(
            models.EvaluationSubmission.status == models.SubmissionStatus.COMPLETED,
            models.EvaluationSubmission.evaluation_score >= 0.7
        ).count()
        
        # Fail count (COMPLETED with score < 0.5)
        fail_count = db.query(models.EvaluationSubmission).filter(
            models.EvaluationSubmission.status == models.SubmissionStatus.COMPLETED,
            models.EvaluationSubmission.evaluation_score < 0.5
        ).count()
        
        # Needs Improvement (COMPLETED with score between 0.5 and 0.7)
        needs_improvement = db.query(models.EvaluationSubmission).filter(
            models.EvaluationSubmission.status == models.SubmissionStatus.COMPLETED,
            models.EvaluationSubmission.evaluation_score >= 0.5,
            models.EvaluationSubmission.evaluation_score < 0.7
        ).count()
        
        # Average score
        all_scores = db.query(models.EvaluationSubmission.evaluation_score).filter(
            models.EvaluationSubmission.evaluation_score.isnot(None)
        ).all()
        
        avg_score = 0
        if all_scores:
            avg_score = sum(s[0] for s in all_scores) / len(all_scores)
        
        # Recent evaluations (last 5)
        recent = db.query(models.EvaluationSubmission).order_by(
            models.EvaluationSubmission.created_at.desc()
        ).limit(5).all()
        
        recent_evaluations = []
        for r in recent:
            verdict = "PENDING"
            if r.status == models.SubmissionStatus.COMPLETED:
                if r.evaluation_score and r.evaluation_score >= 0.7:
                    verdict = "PASS"
                elif r.evaluation_score and r.evaluation_score >= 0.5:
                    verdict = "NEEDS IMPROVEMENT"
                else:
                    verdict = "FAIL"
            elif r.status == models.SubmissionStatus.FAILED:
                verdict = "FAIL"
            
            recent_evaluations.append({
                "id": r.id,
                "question": r.question[:50] + ("..." if len(r.question) > 50 else ""),
                "score": r.evaluation_score or 0,
                "verdict": verdict,
                "timestamp": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else ""
            })
        
        return {
            "total": total,
            "pass": pass_count,
            "needs_improvement": needs_improvement,
            "fail": fail_count,
            "avg_score": round(avg_score, 2),
            "recent": recent_evaluations
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {
            "total": 0,
            "pass": 0,
            "needs_improvement": 0,
            "fail": 0,
            "avg_score": 0,
            "recent": []
        }