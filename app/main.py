from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import engine, get_db
from app import models, schemas

# This line creates the actual database file and its tables inside your computer on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DELL-Sandbox :AI Response Quality Evaluator Agent",
    description="My custom module for capturing , validating,and  auditing AI-generated text data. Built on FastAPI",
    version="0.1.0-alpha"
)

@app.get("/health", tags=["Infrastructure"])
async def health_check():
    return {"status": "healthy", "module": "Evaluation Input Module"}


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