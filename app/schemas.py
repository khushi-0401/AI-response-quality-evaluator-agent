from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import SubmissionStatus

# ==============================================================================
# MODULE 1: EVALUATION INPUT SCHEMAS
# ==============================================================================

# What the client sends when submitting a single question/response pair
class SingleSubmissionCreate(BaseModel):
    question: str = Field(..., min_length=1, description="The question asked to the AI")
    ai_response: str = Field(..., min_length=1, description="The AI's response to evaluate")
    reference_answer: Optional[str] = Field(None, description="Optional reference/ground truth answer")
    source_document: Optional[str] = Field(None, description="Optional source document for grounding")
    source_document_name: Optional[str] = Field(None, description="Name of the source document")

# What the API returns immediately upon submission
class SubmissionAcknowledgement(BaseModel):
    submission_id: str = Field(..., description="Unique tracking ID for the submission")
    status: SubmissionStatus = Field(..., description="Current status of the submission")
    message: str = Field(..., description="Human-readable status message")

# What the API returns when checking a submission's status or details
class SubmissionDetailsResponse(BaseModel):
    id: str = Field(..., description="Unique tracking ID")
    question: str = Field(..., description="The question asked to the AI")
    ai_response: str = Field(..., description="The AI's response")
    reference_answer: Optional[str] = Field(None, description="Reference/ground truth answer")
    source_document: Optional[str] = Field(None, description="Source document used for grounding")
    source_document_name: Optional[str] = Field(None, description="Name of the source document")
    mode: str = Field(..., description="Evaluation mode: single, batch, or grounded")
    batch_id: Optional[str] = Field(None, description="Batch ID if part of a batch")
    status: SubmissionStatus = Field(..., description="Current status of the submission")
    created_at: datetime = Field(..., description="Timestamp when the submission was created")
    evaluation_score: Optional[float] = Field(None, description="Evaluation score (if completed)")
    evaluation_feedback: Optional[str] = Field(None, description="Evaluation feedback (if completed)")

    # Pydantic v2 configuration to allow parsing from ORM objects (SQLAlchemy models)
    model_config = ConfigDict(from_attributes=True)

# Simple evaluation request (used by /api/v1/evaluate endpoint)
class EvaluationRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The question asked to the AI")
    ai_response: str = Field(..., min_length=1, description="The AI's response to evaluate")
    reference_answer: Optional[str] = Field(None, description="Optional reference/ground truth answer")
    source_document: Optional[str] = Field(None, description="Optional source document")


# ==============================================================================
# MODULE 2: AGENT EVALUATION SCHEMAS
# ==============================================================================

# Request schema for evaluating with all agents
class AgentEvaluationRequest(BaseModel):
    """Request schema for evaluating with all agents"""
    question: str = Field(..., min_length=1, description="The question asked to the AI")
    ai_response: str = Field(..., min_length=1, description="The AI's response to evaluate")
    reference_answer: Optional[str] = Field(None, description="Optional reference/ground truth answer")
    source_context: Optional[str] = Field(None, description="Optional source context from RAG")
    use_rag: bool = Field(True, description="Whether to use RAG retrieval for context")


# Response from Relevance Judge Agent
class RelevanceResponse(BaseModel):
    """Response from Relevance Judge Agent"""
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score between 0 and 1")
    reasoning: str = Field(..., description="Human-readable reasoning for the score")
    key_points_covered: List[str] = Field(default_factory=list, description="Key points covered in response")
    missing_points: List[str] = Field(default_factory=list, description="Key points missing from response")
    term_coverage: float = Field(..., ge=0.0, le=1.0, description="Percentage of key terms covered")


# Response from Accuracy Judge Agent
class AccuracyResponse(BaseModel):
    """Response from Accuracy Judge Agent"""
    accuracy_score: float = Field(..., ge=0.0, le=1.0, description="Accuracy score between 0 and 1")
    evidence: str = Field(..., description="Supporting evidence for the score")
    correct_claims: List[str] = Field(default_factory=list, description="Verified correct claims")
    incorrect_claims: List[str] = Field(default_factory=list, description="Incorrect or unverified claims")
    partially_correct_claims: List[str] = Field(default_factory=list, description="Partially correct claims")
    total_claims: int = Field(..., description="Total number of claims extracted")
    verified_claims: int = Field(..., description="Number of verified claims")


# Response from Hallucination Detection Agent
class HallucinationResponse(BaseModel):
    """Response from Hallucination Detection Agent"""
    hallucination_detected: bool = Field(..., description="Whether hallucination was detected")
    hallucination_score: float = Field(..., ge=0.0, le=1.0, description="Hallucination severity score")
    hallucinated_statements: List[Dict[str, Any]] = Field(default_factory=list, description="List of hallucinated statements with details")
    supported_statements: List[Dict[str, Any]] = Field(default_factory=list, description="List of supported statements")
    total_claims: int = Field(..., description="Total number of claims analyzed")
    hallucinated_count: int = Field(..., description="Number of hallucinated claims")
    supported_count: int = Field(..., description="Number of supported claims")
    summary: str = Field(..., description="Human-readable summary")


# Combined response from all agents
class AgentEvaluationResponse(BaseModel):
    """Combined response from all agents"""
    submission_id: str = Field(..., description="Unique submission ID")
    question: str = Field(..., description="The original question")
    ai_response: str = Field(..., description="The AI response evaluated")
    relevance: RelevanceResponse = Field(..., description="Relevance evaluation results")
    accuracy: AccuracyResponse = Field(..., description="Accuracy evaluation results")
    hallucination: HallucinationResponse = Field(..., description="Hallucination detection results")
    status: str = Field(..., description="Overall evaluation status")


# Validation Request Schema
class ValidationRequest(BaseModel):
    """Request schema for validating agents"""
    test_dataset: List[Dict[str, Any]] = Field(
        ..., 
        min_length=1, 
        description="List of test cases with question, ai_response, reference_answer, source_context"
    )


# Validation Summary Schema
class AgentValidationSummary(BaseModel):
    """Summary of agent validation results"""
    total_tested: int = Field(..., description="Total number of test cases")
    relevance_agent: Dict[str, float] = Field(..., description="Relevance agent performance metrics")
    accuracy_agent: Dict[str, float] = Field(..., description="Accuracy agent performance metrics")
    hallucination_agent: Dict[str, float] = Field(..., description="Hallucination agent performance metrics")
    overall_pass_rate: float = Field(..., description="Overall pass rate across all agents")


# Validation Response Schema
class ValidationResponse(BaseModel):
    """Complete validation response"""
    validation_summary: Dict[str, Any] = Field(..., description="Validation summary statistics")
    detailed_results: List[Dict[str, Any]] = Field(default_factory=list, description="Detailed results per test case")
    total_tested: int = Field(..., description="Total number of test cases")