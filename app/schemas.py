from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models import SubmissionStatus

# What the client sends when submitting a single question/response pair
class SingleSubmissionCreate(BaseModel):
    question: str
    ai_response: str
    reference_answer: Optional[str] = None
    source_document: Optional[str] = None
    source_document_name: Optional[str] = None

# What the API returns immediately upon submission
class SubmissionAcknowledgement(BaseModel):
    submission_id: str
    status: SubmissionStatus
    message: str

# What the API returns when checking a submission's status or details
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

    # Pydantic v2 configuration to allow parsing from ORM objects (SQLAlchemy models)
    model_config = ConfigDict(from_attributes=True)