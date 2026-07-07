from typing import Optional, List
from ..models.candidate import Candidate
from ..models.question import Question
from ..models.interview import Interview
from ..models.result import Result
from .question_generator import QuestionGenerator
from .evaluator import Evaluator
from ..database.storage import Storage
from ..utils.helpers import generate_id

class InterviewManager:
    """Service orchestrating the life cycle, state transition, and storage of interview sessions."""

    def __init__(self, question_generator: QuestionGenerator, evaluator: Evaluator, storage: Storage) -> None:
        self._question_generator: QuestionGenerator = question_generator
        self._evaluator: Evaluator = evaluator
        self._storage: Storage = storage

    def create_interview(self, name: str, email: str, topic: str, difficulty: str, count: int = 3) -> Interview:
        """
        Initializes a candidate profile, fetches matching questions,
        creates and starts a stateful interview session, and persists it.
        """
        # 1. Create candidate and register skill
        candidate_id = generate_id("CAN")
        candidate = Candidate(id=candidate_id, name=name, email=email)
        candidate.add_skill(topic)

        # 2. Fetch questions from generator
        questions = self._question_generator.generate_questions(topic=topic, difficulty=difficulty, count=count)

        # 3. Instantiate stateful interview session
        interview_id = generate_id("INT")
        interview = Interview(interview_id=interview_id, candidate=candidate, questions=questions)
        interview.start_interview()

        # 4. Persist and return the active session
        self._storage.save_interview(interview)
        return interview

    def createInterview(self, name: str, email: str, topic: str, difficulty: str, count: int = 3) -> Interview:
        """CamelCase alias for create_interview."""
        return self.create_interview(name, email, topic, difficulty, count)

    def get_next_question(self, interview_id: str) -> Optional[Question]:
        """Retrieves and advances the interview's current question."""
        interview = self._get_interview_or_raise(interview_id)
        question = interview.next_question()
        
        # Save updated index state to storage
        self._storage.save_interview(interview)
        return question

    def getNextQuestion(self, interview_id: str) -> Optional[Question]:
        """CamelCase alias for get_next_question."""
        return self.get_next_question(interview_id)

    def submit_answer(self, interview_id: str, question_id: str, answer: str) -> None:
        """Submits and stores the candidate response for a specific question."""
        interview = self._get_interview_or_raise(interview_id)
        
        # Verify the question belongs to this interview
        valid_question_ids = [q.id for q in interview.questions]
        if question_id not in valid_question_ids:
            raise ValueError(f"Question '{question_id}' does not belong to this interview session.")

        interview.add_answer(question_id, answer)
        self._storage.save_interview(interview)

    def submitAnswer(self, interview_id: str, question_id: str, answer: str) -> None:
        """CamelCase alias for submit_answer."""
        self.submit_answer(interview_id, question_id, answer)

    def complete_interview(self, interview_id: str) -> Result:
        """Concludes the interview session, evaluates responses, saves, and returns the result."""
        interview = self._get_interview_or_raise(interview_id)
        
        # Complete the state transition on the model
        interview.complete_interview()

        # Evaluate the candidate answers
        result = self._evaluator.evaluate_interview(interview)
        interview.result = result

        # Save finalized status to storage
        self._storage.save_interview(interview)
        return result

    def completeInterview(self, interview_id: str) -> Result:
        """CamelCase alias for complete_interview."""
        return self.complete_interview(interview_id)

    def _get_interview_or_raise(self, interview_id: str) -> Interview:
        """Helper retrieving a session or raising ValueError if missing."""
        interview = self._storage.get_interview(interview_id)
        if not interview:
            raise ValueError(f"Interview session with ID '{interview_id}' not found.")
        return interview
