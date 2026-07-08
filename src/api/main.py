import os
import logging
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware

from ..models.candidate import Candidate
from ..models.interview import Interview
from ..models.result import Result
from ..models.question import Question

from ..database.sqlite_repository import InterviewRepository
from ..database.storage import InMemoryStorage

from ..services.llm_client import OpenAIClient, MockLLMClient
from ..services.question_generator import QuestionGenerator
from ..services.evaluator import Evaluator
from ..services.follow_up_question_generator import FollowUpQuestionGenerator
from ..services.interview_manager import InterviewManager

from ..utils.helpers import generate_id
from .schemas import (
    CandidateCreate,
    CandidateResponse,
    InterviewStartRequest,
    InterviewStartResponse,
    AnswerSubmitRequest,
    AnswerSubmitResponse,
    InterviewNextRequest,
    InterviewNextResponse,
    InterviewResultResponse,
    DetailedEvaluation,
    HistoricalInterviewSchema,
    CandidateHistoryResponse,
    QuestionSchema
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(
    title="AI Interview Bot API",
    description="Backend API for stateful, adaptive technical interview sessions powered by AI.",
    version="1.0.0"
)

# Enable CORS for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Storage & Dependency Services
db_path = os.getenv("DB_PATH", "interview_bot.db")
openai_key = os.getenv("OPENAI_API_KEY")

logger.info(f"Initializing Storage with path: {db_path}")
if db_path == ":memory:":
    # Hold single in-memory database reference across requests
    storage = InterviewRepository(db_path=":memory:")
else:
    storage = InterviewRepository(db_path=db_path)

if openai_key:
    logger.info("OPENAI_API_KEY detected. Initializing OpenAIClient...")
    llm_client = OpenAIClient(api_key=openai_key)
else:
    logger.info("No OPENAI_API_KEY detected. Falling back to MockLLMClient...")
    llm_client = MockLLMClient()

question_generator = QuestionGenerator(llm_client=llm_client)
evaluator = Evaluator(llm_client=llm_client)
follow_up_generator = FollowUpQuestionGenerator(llm_client=llm_client)

interview_manager = InterviewManager(
    question_generator=question_generator,
    evaluator=evaluator,
    storage=storage,
    follow_up_generator=follow_up_generator
)

@app.get("/health", tags=["System"])
def health_check():
    """Returns database and application operational health status."""
    return {"status": "healthy", "database": "connected"}

@app.post("/candidate", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED, tags=["Candidates"])
def create_candidate(req: CandidateCreate):
    """Registers a new candidate profile along with their initial skill sets."""
    try:
        candidate_id = generate_id("CAN")
        candidate = Candidate(id=candidate_id, name=req.name, email=str(req.email))
        for skill in req.skills:
            candidate.add_skill(skill)
        
        storage.save_candidate(candidate)
        logger.info(f"Successfully registered candidate: {candidate_id}")
        return CandidateResponse(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            skills=candidate.selected_skills
        )
    except ValueError as e:
        logger.error(f"Validation failure during candidate registration: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating candidate: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create candidate profile.")

@app.get("/candidate/{id}", response_model=CandidateResponse, tags=["Candidates"])
def get_candidate(id: str):
    """Retrieves metadata of a registered candidate by their ID."""
    candidate = storage.get_candidate(id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Candidate with ID '{id}' not found.")
    
    return CandidateResponse(
        id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        skills=candidate.selected_skills
    )

@app.post("/interview/start", response_model=InterviewStartResponse, status_code=status.HTTP_201_CREATED, tags=["Interviews"])
def start_interview(req: InterviewStartRequest):
    """Initializes a stateful interview session, generating questions and linking to a candidate."""
    try:
        candidate_id = req.candidate_id
        name = req.name or ""
        email = req.email or ""

        if candidate_id:
            # Re-use existing candidate profile
            candidate = storage.get_candidate(candidate_id)
            if not candidate:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Candidate ID '{candidate_id}' not found.")
            name = candidate.name
            email = candidate.email
        else:
            # Require profile info for anonymous/new candidates
            if not name or not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Name and email are required when candidate_id is not provided."
                )

        interview = interview_manager.create_interview(
            name=name,
            email=email,
            topic=req.topic,
            difficulty=req.difficulty,
            count=req.count,
            candidate_id=candidate_id
        )

        logger.info(f"Started interview session: {interview.interview_id} for candidate: {interview.candidate.id}")
        return InterviewStartResponse(
            interview_id=interview.interview_id,
            candidate_id=interview.candidate.id,
            status=interview.status,
            topic=req.topic,
            difficulty=req.difficulty,
            question_count=len(interview.questions)
        )
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Value validation error starting interview: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start interview: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to initialize interview: {str(e)}")

@app.post("/interview/next", response_model=InterviewNextResponse, tags=["Interviews"])
def get_next_question(req: InterviewNextRequest):
    """Advances and returns the next question. Triggers completion/evaluation if no questions remain."""
    try:
        interview = storage.get_interview(req.interview_id)
        if not interview:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Interview session '{req.interview_id}' not found.")

        if interview.status == "COMPLETED":
            return InterviewNextResponse(status="COMPLETED", is_finished=True)

        question = interview_manager.get_next_question(req.interview_id)
        
        if question:
            return InterviewNextResponse(
                question=QuestionSchema(
                    id=question.id,
                    topic=question.topic,
                    difficulty=question.difficulty,
                    question_text=question.question_text,
                    expected_concepts=question.expected_concepts
                ),
                status="IN_PROGRESS",
                is_finished=False
            )
        else:
            # Out of questions - complete and evaluate the session
            logger.info(f"No questions remaining. Finalizing interview {req.interview_id}...")
            interview_manager.complete_interview(req.interview_id)
            return InterviewNextResponse(status="COMPLETED", is_finished=True)
            
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching next question: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/interview/answer", response_model=AnswerSubmitResponse, tags=["Interviews"])
def submit_answer(req: AnswerSubmitRequest):
    """Saves answer for a specific question, executing real-time evaluation and adaptive follow-up generation."""
    try:
        interview = storage.get_interview(req.interview_id)
        if not interview:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Interview session '{req.interview_id}' not found.")

        if interview.status != "IN_PROGRESS":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Answers can only be submitted for active interviews.")

        question_id = req.question_id
        if not question_id:
            # Default to the most recently retrieved question
            idx = interview.current_question_index - 1
            if 0 <= idx < len(interview.questions):
                question_id = interview.questions[idx].id
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active question available to answer.")

        # Verify question belongs to interview
        valid_question_ids = [q.id for q in interview.questions]
        if question_id not in valid_question_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Question ID '{question_id}' does not belong to this interview session."
            )

        interview_manager.submit_answer(req.interview_id, question_id, req.answer)
        
        # Re-fetch state to reflect any inserted dynamic follow-up questions
        updated_interview = storage.get_interview(req.interview_id)
        
        return AnswerSubmitResponse(
            status="SUCCESS",
            message="Answer recorded successfully.",
            question_id=question_id,
            answered_count=len(updated_interview.answers),
            total_count=len(updated_interview.questions)
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/interview/result/{id}", response_model=InterviewResultResponse, tags=["Interviews"])
def get_result(id: str):
    """Retrieves evaluation metrics, strengths, improvements, and question details of an interview."""
    try:
        interview = storage.get_interview(id)
        if not interview:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Interview session '{id}' not found.")

        # Automatically finalize the interview if it wasn't completed yet
        if interview.status != "COMPLETED":
            logger.info(f"Interview '{id}' results queried while in state '{interview.status}'. Auto-completing session...")
            try:
                interview_manager.complete_interview(id)
                interview = storage.get_interview(id)
            except Exception as e:
                logger.error(f"Failed to auto-complete interview: {e}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot evaluate incomplete session: {e}")

        result = interview.result
        if not result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Evaluation results could not be generated.")

        detailed_evals = []
        # Populate detailed evaluations lists if present
        evals_source = result.detailed_evaluations if hasattr(result, "detailed_evaluations") else []
        for item in evals_source:
            detailed_evals.append(DetailedEvaluation(
                question_id=item.get("question_id", ""),
                score=item.get("score", 0.0),
                feedback=item.get("feedback", ""),
                strengths=item.get("strengths", []),
                weaknesses=item.get("weaknesses", [])
            ))

        # Fallback if detailed evaluations were not cached in Result model directly
        if not detailed_evals and hasattr(interview, "evaluations"):
            for q_id, q_res in interview.evaluations.items():
                detailed_evals.append(DetailedEvaluation(
                    question_id=q_id,
                    score=q_res.score,
                    feedback=q_res.feedback,
                    strengths=q_res.strengths,
                    weaknesses=q_res.weaknesses
                ))

        return InterviewResultResponse(
            interview_id=interview.interview_id,
            candidate_id=interview.candidate.id,
            score=result.score,
            feedback=result.feedback,
            strengths=result.strengths,
            weaknesses=result.weaknesses,
            status=interview.status,
            detailed_evaluations=detailed_evals
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching result: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/history/{candidate_id}", response_model=CandidateHistoryResponse, tags=["Candidates"])
def get_candidate_history(candidate_id: str):
    """Retrieves all past interviews completed or started by a specific candidate."""
    candidate = storage.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Candidate with ID '{candidate_id}' not found.")

    interviews = storage.get_interview_history(candidate_id)
    history_list = []
    for item in interviews:
        # Reconstruct topic from first question topic or default to SQL/Unknown
        topic = item.questions[0].topic if item.questions else "Unknown"
        history_list.append(HistoricalInterviewSchema(
            interview_id=item.interview_id,
            topic=topic,
            difficulty=item.questions[0].difficulty if item.questions else "Medium",
            status=item.status,
            score=item.result.score if item.result else None,
            date=getattr(item, "_date", "Unknown") # Fetch private date attribute if it is set in sqlite db
        ))

    return CandidateHistoryResponse(
        candidate_id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        interviews=history_list
    )
