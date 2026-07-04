# ==============================================================================
# DEVELOPER NOTE: This is the Core Schema Design for AI-Evaluator Core
# Tracking tracking metrics for prompt queries vs AI-generated text outputs.
# TODO: Future iterations might require a separate table for batch metadata.
# ==============================================================================
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class SubmissionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class EvaluationSubmission(Base):
    __tablename__ = "evaluation_submissions"

    # Automatically generates a unique tracking ID string for every entry
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    reference_answer = Column(Text, nullable=True)
    source_document = Column(Text, nullable=True)
    source_document_name = Column(String(255), nullable=True)
    mode = Column(String(50), default="single")  # single or batch
    batch_id = Column(String(36), nullable=True)
    status = Column(SQLEnum(SubmissionStatus), default=SubmissionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.now)