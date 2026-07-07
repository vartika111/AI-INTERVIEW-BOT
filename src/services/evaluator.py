from typing import List, Dict, Any
from ..models.interview import Interview
from ..models.result import Result
from .llm_client import LLMClient

class Evaluator:
    """Service responsible for evaluating candidate answers and generating interview results."""

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client: LLMClient = llm_client

    def evaluate_interview(self, interview: Interview) -> Result:
        """
        Evaluates candidate answers in the interview.
        Returns a structured Result model with overall score and feedback.
        """
        detailed_evaluations: List[Dict[str, Any]] = []
        total_score = 0.0

        for question in interview.questions:
            answer = interview.answers.get(question.id, "No answer provided.")
            
            # Placeholder LLM evaluation prompt/parsing
            prompt = f"Evaluate this answer: {answer} for question: {question.question_text}"
            llm_response = self.llm_client.generate(prompt)

            # Assigning mock scores for now
            mock_score = 8.0 if answer != "No answer provided." else 0.0
            total_score += mock_score

            detailed_evaluations.append({
                "question_id": question.id,
                "score": mock_score,
                "feedback": f"LLM Feedback details: {llm_response}"
            })

        num_questions = len(interview.questions)
        average_score = (total_score / num_questions) if num_questions > 0 else 0.0

        return Result(
            score=average_score,
            feedback="Good performance across technical areas.",
            strengths=["Strong understanding of syntax", "Correct usage of standard concepts"],
            weaknesses=["Could detail system design considerations further"],
            interview_id=interview.interview_id,
            detailed_evaluations=detailed_evaluations
        )
