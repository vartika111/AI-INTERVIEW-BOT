from typing import List
from ..models.question import Question
from .llm_client import LLMClient

class QuestionGenerator:
    """Service responsible for generating domain-specific technical questions."""

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client: LLMClient = llm_client

    def generate_questions(self, domain: str, count: int = 5) -> List[Question]:
        """
        Generates a list of questions for a specific technical domain.
        Currently returns placeholders to be integrated with prompt engineering.
        """
        # Placeholder questions mapping
        questions: List[Question] = []
        for i in range(1, count + 1):
            q_id = f"Q-{domain.upper()}-{i:02d}"
            text = f"Describe a core concept or solve a problem in {domain} (Sample Question {i})."
            questions.append(Question(
                question_id=q_id,
                text=text,
                domain=domain,
                difficulty="Medium",
                rubric=f"Criteria for evaluated concept in {domain}"
            ))
        return questions
