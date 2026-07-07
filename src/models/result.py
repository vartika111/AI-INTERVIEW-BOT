from typing import List, Dict, Any, Optional

class Result:
    """Encapsulates the final scores, feedback, strengths, and weaknesses of an interview."""

    def __init__(
        self,
        score: float,
        feedback: str,
        strengths: Optional[List[str]] = None,
        weaknesses: Optional[List[str]] = None,
        interview_id: str = "",
        detailed_evaluations: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        self._score: float = score
        self._feedback: str = feedback
        self._strengths: List[str] = strengths if strengths is not None else []
        self._weaknesses: List[str] = weaknesses if weaknesses is not None else []
        
        # Legacy attributes from Step 1 to keep app.py working
        self.interview_id: str = interview_id
        self.detailed_evaluations: List[Dict[str, Any]] = detailed_evaluations if detailed_evaluations is not None else []

    # Getters and Setters for encapsulation
    @property
    def score(self) -> float:
        return self._score

    @score.setter
    def score(self, value: float) -> None:
        if not (0.0 <= value <= 10.0):
            raise ValueError("Score must be between 0.0 and 10.0")
        self._score = value

    @property
    def feedback(self) -> str:
        return self._feedback

    @feedback.setter
    def feedback(self, value: str) -> None:
        self._feedback = value

    @property
    def strengths(self) -> List[str]:
        return self._strengths

    @property
    def weaknesses(self) -> List[str]:
        return self._weaknesses

    # Core Methods
    def generate_summary(self) -> str:
        """Generates a professional text summary of candidate evaluation results."""
        strengths_str = "\n".join([f"  - {s}" for s in self._strengths]) if self._strengths else "  - None noted"
        weaknesses_str = "\n".join([f"  - {w}" for w in self._weaknesses]) if self._weaknesses else "  - None noted"
        
        border = "*" * 50
        return (
            f"{border}\n"
            f"          INTERVIEW PERFORMANCE SUMMARY\n"
            f"{border}\n"
            f"Overall Score: {self._score:.1f} / 10.0\n\n"
            f"Feedback:\n{self._feedback}\n\n"
            f"Key Strengths:\n{strengths_str}\n\n"
            f"Areas for Improvement:\n{weaknesses_str}\n"
            f"{border}"
        )

    def generateSummary(self) -> str:
        """CamelCase alias for generate_summary."""
        return self.generate_summary()

    def __repr__(self) -> str:
        return f"Result(score={self._score}, feedback={self._feedback[:20]!r}...)"
