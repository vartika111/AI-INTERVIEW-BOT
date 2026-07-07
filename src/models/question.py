from typing import Optional

class Question:
    """Represents a technical interview question."""

    def __init__(
        self,
        question_id: str,
        text: str,
        domain: str,
        difficulty: str,
        rubric: Optional[str] = None
    ) -> None:
        self.question_id: str = question_id
        self.text: str = text
        self.domain: str = domain  # e.g., 'Java', 'Python', etc.
        self.difficulty: str = difficulty  # e.g., 'Easy', 'Medium', 'Hard'
        self.rubric: Optional[str] = rubric  # Evaluation standard guidelines for the LLM

    def __repr__(self) -> str:
        return f"Question(id={self.question_id!r}, domain={self.domain!r}, difficulty={self.difficulty!r})"
