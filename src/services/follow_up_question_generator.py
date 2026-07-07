from ..models.question import Question
from ..models.result import Result
from .llm_client import LLMClient

class FollowUpQuestionGenerator:
    """Service responsible for generating adaptive follow-up questions based on candidate performance."""

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client: LLMClient = llm_client

    def generate_follow_up(self, result: Result, previous_question: Question) -> str:
        """
        Generates an adaptive follow-up question based on the evaluation result score:
        - score >= 8: Ask a deeper conceptual question.
        - score between 5 and 7 (inclusive 5.0 <= score < 8.0): Ask a clarification question.
        - score < 5: Ask an easier question.
        """
        score = result.score
        
        if score >= 8.0:
            prompt_instruction = "The candidate answered the previous question correctly (Score: {score:.1f}/10). Ask a DEEPER CONCEPTUAL follow-up question to probe their advanced knowledge of the topic."
        elif 5.0 <= score < 8.0:
            prompt_instruction = "The candidate's answer was partially correct (Score: {score:.1f}/10). Ask a CLARIFICATION follow-up question to help them clarify or elaborate on the gaps in their answer."
        else:
            prompt_instruction = "The candidate struggled with the previous question (Score: {score:.1f}/10). Ask a simpler, EASIER follow-up question on the same topic to test foundational knowledge."

        prompt = (
            f"You are a technical interviewer conducting a live conversation.\n"
            f"Technical Topic: {previous_question.topic}\n"
            f"Previous Question Asked: {previous_question.question_text}\n"
            f"Candidate's Answer evaluation:\n"
            f"- Score: {score:.1f}/10\n"
            f"- Feedback: {result.feedback}\n\n"
            f"Instruction: {prompt_instruction.format(score=score)}\n\n"
            f"Generate a single, natural conversational follow-up question based on the instruction above. "
            f"Do not write greetings, prefaces, or conversational filler. Output only the question text."
        )

        return self.llm_client.generate_response(prompt)

    def generateFollowUp(self, result: Result, previousQuestion: Question) -> str:
        """CamelCase alias for generate_follow_up compatibility."""
        return self.generate_follow_up(result, previousQuestion)
