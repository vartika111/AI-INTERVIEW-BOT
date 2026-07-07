from typing import List, Dict, Any

class Result:
    """Represents the evaluation result of a completed technical interview."""

    def __init__(
        self,
        interview_id: str,
        score: float,
        overall_feedback: str,
        detailed_evaluations: List[Dict[str, Any]]
    ) -> None:
        self.interview_id: str = interview_id
        self.score: float = score  # e.g., numeric scale like 0-10 or percentage
        self.overall_feedback: str = overall_feedback
        self.detailed_evaluations: List[Dict[str, Any]] = detailed_evaluations  # List containing breakdown per question

    def __repr__(self) -> str:
        return f"Result(interview_id={self.interview_id!r}, score={self.score})"
