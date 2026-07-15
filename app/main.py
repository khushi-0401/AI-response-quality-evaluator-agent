from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import uuid

from app.database import engine, get_db
from app import models, schemas
from app.rag_retriever import RAGRetriever
from app.agents import RelevanceJudge, AccuracyJudge, HallucinationDetector, ValidationAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This line creates the actual database file and its tables inside your computer on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DELL-Sandbox :AI Response Quality Evaluator Agent",
    description="My custom module for capturing, validating, and auditing AI-generated text data. Built on FastAPI",
    version="0.1.0-alpha"
)

# Initialize RAG retriever
rag_retriever = RAGRetriever()

# Initialize Agents
relevance_judge = RelevanceJudge()
accuracy_judge = AccuracyJudge()
hallucination_detector = HallucinationDetector()
validation_agent = ValidationAgent()


# ==============================================================================
# INFRASTRUCTURE ENDPOINTS
# ==============================================================================

@app.get("/health", tags=["Infrastructure"])
async def health_check():
    return {
        "status": "healthy",
        "module": "Evaluation Input Module",
        "rag_ready": rag_retriever.is_ready()
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
    
    # Create the database object map from the clean incoming request data
    new_submission = models.EvaluationSubmission(
        question=payload.question,
        ai_response=payload.ai_response,
        reference_answer=payload.reference_answer,
        source_document=payload.source_document,
        source_document_name=payload.source_document_name,
        mode="single"
    )
    
    # Insert the entry into your local SQLite ledger file
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
    
    # Return acknowledgment containing the automatic tracking unique ID token
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
    
    # Lookup the record using its unique string ID
    record = db.query(models.EvaluationSubmission).filter(models.EvaluationSubmission.id == submission_id).first()
    
    # Return an error error message if the ID doesn't match anything in our records
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
    """
    Evaluate AI response with RAG grounding using the knowledge base
    """
    # Check if RAG is ready
    if not rag_retriever.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Knowledge base not initialized. Please run build_knowledge_base.py first."
        )
    
    # Retrieve relevant context from knowledge base
    context = rag_retriever.retrieve_context(payload.question, k=3)
    
    # Create submission with grounding context
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
    """Check the status of the RAG knowledge base"""
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
    """Rebuild the knowledge base from scratch (for development)"""
    import subprocess
    import sys
    
    try:
        # Run the build script
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
        
        # Re-initialize the retriever
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
    """
    Evaluate relevance of AI response to the question.
    Returns relevance score with reasoning.
    """
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
            term_coverage=result["term_coverage"]
        )
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
    """
    Evaluate accuracy of AI response against reference or RAG context.
    Returns accuracy score with evidence.
    """
    try:
        # If source_context not provided and use_rag is True, retrieve from RAG
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
    """
    Detect hallucinations in AI response by cross-referencing with RAG context.
    Returns hallucinated statements with severity levels.
    """
    try:
        # If source_context not provided and use_rag is True, retrieve from RAG
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
    """
    Run all three agents (Relevance, Accuracy, Hallucination) and store results.
    """
    try:
        # Get RAG context if needed
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
        
        hallucination_result = hallucination_detector.evaluate(
            question=payload.question,
            ai_response=payload.ai_response,
            source_context=source_context or ""
        )
        
        # Store submission with agent results
        new_submission = models.EvaluationSubmission(
            question=payload.question,
            ai_response=payload.ai_response,
            reference_answer=payload.reference_answer,
            source_document=source_context,
            source_document_name="RAG_Context_for_Agents",
            mode="agent_evaluation",
            evaluation_score=accuracy_result.get("accuracy_score", 0),
            evaluation_feedback=relevance_result.get("reasoning", "") + " | " + hallucination_result.get("summary", "")
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
                term_coverage=relevance_result["term_coverage"]
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
            status="completed"
        )
    except Exception as e:
        logger.error(f"Error in evaluate-all: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )


@app.post(
    "/api/agents/validate",
    tags=["Agents"]
)
async def validate_agents(
    payload: schemas.ValidationRequest
):
    """
    Validate all agents using a test dataset.
    Returns validation summary and detailed results.
    """
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
# HEALTH CHECK ENDPOINTS
# ==============================================================================

@app.get(
    "/api/agents/status",
    tags=["Agents"]
)
async def get_agents_status():
    """Check the status of all agents"""
    return {
        "agents_ready": True,
        "relevance_agent": "ready",
        "accuracy_agent": "ready",
        "hallucination_agent": "ready",
        "validation_agent": "ready",
        "rag_available": rag_retriever.is_ready()
    }