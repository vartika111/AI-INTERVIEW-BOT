from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any

class CandidateCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Full name of the candidate")
    email: EmailStr = Field(..., description="Email address of the candidate")
    skills: Optional[List[str]] = Field(default_factory=list, description="Initial list of skills")

class CandidateResponse(BaseModel):
    id: str
    name: str
    email: str
    skills: List[str]

    class Config:
        from_attributes = True

class InterviewStartRequest(BaseModel):
    topic: str = Field(..., description="Technical topic (e.g. Java, Python, DSA, OOP, SQL)")
    difficulty: str = Field(..., description="Interview difficulty (Easy, Medium, Hard)")
    count: Optional[int] = Field(default=3, ge=1, description="Number of questions to generate")
    candidate_id: Optional[str] = Field(default=None, description="Optional existing candidate ID")
    name: Optional[str] = Field(default=None, description="Candidate name (required if candidate_id is not provided)")
    email: Optional[str] = Field(default=None, description="Candidate email (required if candidate_id is not provided)")

class InterviewStartResponse(BaseModel):
    interview_id: str
    candidate_id: str
    status: str
    topic: str
    difficulty: str
    question_count: int

class AnswerSubmitRequest(BaseModel):
    interview_id: str = Field(..., description="Active interview session ID")
    question_id: Optional[str] = Field(default=None, description="ID of the question being answered. Defaults to current active question.")
    answer: str = Field(..., min_length=1, description="Candidate response text")

class AnswerSubmitResponse(BaseModel):
    status: str
    message: str
    question_id: str
    answered_count: int
    total_count: int

class InterviewNextRequest(BaseModel):
    interview_id: str = Field(..., description="Active interview session ID")

class QuestionSchema(BaseModel):
    id: str
    topic: str
    difficulty: str
    question_text: str
    expected_concepts: List[str]

class InterviewNextResponse(BaseModel):
    question: Optional[QuestionSchema] = None
    status: str
    is_finished: bool

class DetailedEvaluation(BaseModel):
    question_id: str
    score: float
    feedback: str
    strengths: List[str]
    weaknesses: List[str]

class InterviewResultResponse(BaseModel):
    interview_id: str
    candidate_id: str
    score: Optional[float] = None
    feedback: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    status: str
    detailed_evaluations: List[DetailedEvaluation] = Field(default_factory=list)

class HistoricalInterviewSchema(BaseModel):
    interview_id: str
    topic: str
    difficulty: str
    status: str
    score: Optional[float] = None
    date: str

class CandidateHistoryResponse(BaseModel):
    candidate_id: str
    name: str
    email: str
    interviews: List[HistoricalInterviewSchema]
