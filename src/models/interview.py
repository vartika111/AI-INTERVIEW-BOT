from typing import List, Optional, Dict
from .candidate import Candidate
from .question import Question
from .result import Result

class Interview:
    """Coordinates the life cycle and status of a technical interview session."""

    def __init__(self, interview_id: str, candidate: Candidate, questions: Optional[List[Question]] = None) -> None:
        self._interview_id: str = interview_id
        self._candidate: Candidate = candidate
        self._questions: List[Question] = questions if questions is not None else []
        self._current_question_index: int = -1  # Starts at -1 before interview starts
        self._status: str = "CREATED"  # e.g., 'CREATED', 'IN_PROGRESS', 'COMPLETED'
        
        # Legacy attributes from Step 1 to keep app.py working
        self.answers: Dict[str, str] = {}
        self.evaluations: Dict[str, Result] = {}
        self.result: Optional[Result] = None

    # Getters and Setters for encapsulation
    @property
    def interview_id(self) -> str:
        return self._interview_id

    @property
    def interviewId(self) -> str:
        """CamelCase alias for interview_id compatibility."""
        return self._interview_id

    @property
    def candidate(self) -> Candidate:
        return self._candidate

    @property
    def questions(self) -> List[Question]:
        return self._questions

    @property
    def current_question_index(self) -> int:
        return self._current_question_index

    @property
    def currentQuestionIndex(self) -> int:
        """CamelCase alias for current_question_index compatibility."""
        return self._current_question_index

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        valid_statuses = {"CREATED", "IN_PROGRESS", "COMPLETED"}
        if value not in valid_statuses:
            raise ValueError(f"Invalid status: {value}. Must be one of {valid_statuses}")
        self._status = value

    # Core Methods
    def start_interview(self) -> None:
        """Starts the interview session, setting status to IN_PROGRESS and connecting to candidate history."""
        if self._status != "CREATED":
            raise ValueError("Interview has already been started or completed")
        self._status = "IN_PROGRESS"
        self._current_question_index = 0
        
        # Link this interview session back to candidate's history log
        if self not in self._candidate.interview_history:
            self._candidate.interview_history.append(self)

    def startInterview(self) -> None:
        """CamelCase alias for start_interview."""
        self.start_interview()

    def add_question(self, question: Question) -> None:
        """Adds a new question to the interview session."""
        if self._status != "CREATED":
            raise ValueError("Cannot add questions once the interview has started")
        self._questions.append(question)

    def addQuestion(self, question: Question) -> None:
        """CamelCase alias for add_question."""
        self.add_question(question)

    def insert_question(self, index: int, question: Question) -> None:
        """Inserts a question at a specific index in the interview session."""
        if self._status not in ("CREATED", "IN_PROGRESS"):
            raise ValueError("Cannot insert questions once the interview has completed")
        self._questions.insert(index, question)

    def insertQuestion(self, index: int, question: Question) -> None:
        """CamelCase alias for insert_question."""
        self.insert_question(index, question)

    def next_question(self) -> Optional[Question]:
        """
        Retrieves the next question in the interview process.
        Advances the current question index by 1.
        Returns None if there are no more questions left.
        """
        if self._status != "IN_PROGRESS":
            raise ValueError("Interview is not currently in progress")

        if 0 <= self._current_question_index < len(self._questions):
            question = self._questions[self._current_question_index]
            self._current_question_index += 1
            return question
        
        return None

    def nextQuestion(self) -> Optional[Question]:
        """CamelCase alias for next_question."""
        return self.next_question()

    def complete_interview(self) -> None:
        """Concludes the interview, updating the status to COMPLETED."""
        if self._status != "IN_PROGRESS":
            raise ValueError("Can only complete an interview that is currently in progress")
        self._status = "COMPLETED"

    def completeInterview(self) -> None:
        """CamelCase alias for complete_interview."""
        self.complete_interview()

    # Legacy helper from Step 1 to keep app.py compiling/functioning
    def add_answer(self, question_id: str, answer: str) -> None:
        """Stores candidate's answer for evaluation."""
        self.answers[question_id] = answer

    def is_complete(self) -> bool:
        """Legacy helper indicating if all questions are answered."""
        return len(self.answers) >= len(self._questions)

    def __repr__(self) -> str:
        return f"Interview(id={self._interview_id!r}, candidate={self._candidate.name!r}, status={self._status!r})"
