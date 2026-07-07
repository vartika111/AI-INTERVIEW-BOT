from typing import List, Dict, Optional
from .candidate import Candidate
from .question import Question
from .result import Result

class Interview:
    """Represents a stateful interview session."""

    def __init__(self, interview_id: str, candidate: Candidate, questions: List[Question]) -> None:
        self.interview_id: str = interview_id
        self.candidate: Candidate = candidate
        self.questions: List[Question] = questions
        self.answers: Dict[str, str] = {}  # Maps question_id to candidate's response
        self.status: str = "IN_PROGRESS"  # e.g., 'IN_PROGRESS', 'COMPLETED'
        self.result: Optional[Result] = None

    def add_answer(self, question_id: str, answer: str) -> None:
        """Adds a candidate answer for a specific question."""
        self.answers[question_id] = answer

    def is_complete(self) -> bool:
        """Checks if all questions in the interview have been answered."""
        return len(self.answers) >= len(self.questions)

    def __repr__(self) -> str:
        return f"Interview(id={self.interview_id!r}, candidate={self.candidate.name!r}, status={self.status!r})"
