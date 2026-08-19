from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import SubmissionStatus

# ==============================================================================
# MODULE 1: EVALUATION INPUT SCHEMAS
# ==============================================================================

class SingleSubmissionCreate(BaseModel):
    question: str = Field(..., min_length=1, description="The question asked to the AI")
    ai_response: str = Field(..., min_length=1, description="The AI's response to evaluate")
    reference_answer: Optional[str] = Field(None, description="Optional reference/ground truth answer")
    source_document: Optional[str] = Field(None, description="Optional source document for grounding")
    source_document_name: Optional[str] = Field(None, description="Name of the source document")

class SubmissionAcknowledgement(BaseModel):
    submission_id: str = Field(..., description="Unique tracking ID for the submission")
    status: SubmissionStatus = Field(..., description="Current status of the submission")
    message: str = Field(..., description="Human-readable status message")

class SubmissionDetailsResponse(BaseModel):
    id: str
    question: str
    ai_response: str
    reference_answer: Optional[str] = None
    source_document: Optional[str] = None
    source_document_name: Optional[str] = None
    mode: str
    batch_id: Optional[str] = None
    status: SubmissionStatus
    created_at: datetime
    evaluation_score: Optional[float] = None
    evaluation_feedback: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class EvaluationRequest(BaseModel):
    question: str = Field(..., min_length=1)
    ai_response: str = Field(..., min_length=1)
    reference_answer: Optional[str] = None
    source_document: Optional[str] = None

# ==============================================================================
# MODULE 2: AGENT EVALUATION SCHEMAS
# ==============================================================================

class AgentEvaluationRequest(BaseModel):
    question: str = Field(..., min_length=1)
    ai_response: str = Field(..., min_length=1)
    reference_answer: Optional[str] = None
    source_context: Optional[str] = None
    use_rag: bool = True

class RelevanceResponse(BaseModel):
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    key_points_covered: List[str] = []
    missing_points: List[str] = []
    term_coverage: float = Field(..., ge=0.0, le=1.0)

class AccuracyResponse(BaseModel):
    accuracy_score: float = Field(..., ge=0.0, le=1.0)
    evidence: str
    correct_claims: List[str] = []
    incorrect_claims: List[str] = []
    partially_correct_claims: List[str] = []
    total_claims: int
    verified_claims: int

class HallucinationResponse(BaseModel):
    hallucination_detected: bool
    hallucination_score: float = Field(..., ge=0.0, le=1.0)
    hallucinated_statements: List[Dict[str, Any]] = []
    supported_statements: List[Dict[str, Any]] = []
    total_claims: int
    hallucinated_count: int
    supported_count: int
    summary: str

# ==============================================================================
# MODULE 3: COMPLETENESS & VERDICT SCHEMAS (NEW)
# ==============================================================================

class CompletenessResponse(BaseModel):
    completeness_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    covered_aspects: List[str] = []
    missing_aspects: List[str] = []

class VerdictResponse(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=1.0)
    verdict: str
    verdict_emoji: str
    dimension_breakdown: Dict[str, Dict[str, Any]]
    consolidated_reasoning: str

class AgentEvaluationResponse(BaseModel):
    submission_id: str
    question: str
    ai_response: str
    relevance: RelevanceResponse
    accuracy: AccuracyResponse
    completeness: CompletenessResponse
    hallucination: HallucinationResponse
    verdict: VerdictResponse
    status: str

class ValidationRequest(BaseModel):
    test_dataset: List[Dict[str, Any]] = Field(..., min_length=1)

class ValidationResponse(BaseModel):
    validation_summary: Dict[str, Any]
    detailed_results: List[Dict[str, Any]] = []
    total_tested: int