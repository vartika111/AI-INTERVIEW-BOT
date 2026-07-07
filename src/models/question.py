from typing import List

class Question:
    """Represents a structured interview question with technical criteria."""

    def __init__(self, id: str, topic: str, difficulty: str, question_text: str, expected_concepts: List[str]) -> None:
        self._id: str = id
        self._topic: str = topic
        self._difficulty: str = difficulty
        self._question_text: str = question_text
        self._expected_concepts: List[str] = expected_concepts

    # Getters for encapsulation
    @property
    def id(self) -> str:
        return self._id

    @property
    def topic(self) -> str:
        return self._topic

    @property
    def difficulty(self) -> str:
        return self._difficulty

    @property
    def question_text(self) -> str:
        return self._question_text

    @property
    def questionText(self) -> str:
        """CamelCase alias for question_text compatibility."""
        return self._question_text

    @property
    def expected_concepts(self) -> List[str]:
        return self._expected_concepts

    @property
    def expectedConcepts(self) -> List[str]:
        """CamelCase alias for expected_concepts compatibility."""
        return self._expected_concepts

    # Core Methods
    def display_question(self) -> str:
        """Returns a formatted user-friendly display string of the question."""
        border = "=" * 40
        return (
            f"{border}\n"
            f"Question ID: {self._id}\n"
            f"Topic: {self._topic} | Difficulty: {self._difficulty}\n"
            f"{border}\n"
            f"{self._question_text}\n"
            f"{border}"
        )

    def displayQuestion(self) -> str:
        """CamelCase alias for display_question."""
        return self.display_question()

    def __repr__(self) -> str:
        return f"Question(id={self._id!r}, topic={self._topic!r}, difficulty={self._difficulty!r})"
