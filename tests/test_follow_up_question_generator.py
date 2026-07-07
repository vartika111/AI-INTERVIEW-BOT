import unittest
from src.services.llm_client import LLMClient
from src.services.follow_up_question_generator import FollowUpQuestionGenerator
from src.models.question import Question
from src.models.result import Result

class CaptureLLMClient(LLMClient):
    """LLMClient implementation that captures the prompt passed to generate_response."""
    def __init__(self) -> None:
        self.last_prompt = ""

    def generate_response(self, prompt: str) -> str:
        self.last_prompt = prompt
        return f"Mock response for prompt: {prompt[:30]}..."

    def evaluate_answer(self, question: Question, answer: str) -> str:
        return ""

    def generate_follow_up(self, question: Question, answer: str) -> str:
        return ""

class TestFollowUpQuestionGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.llm = CaptureLLMClient()
        self.generator = FollowUpQuestionGenerator(self.llm)
        self.question = Question(
            id="Q1",
            topic="SQL",
            difficulty="Medium",
            question_text="Explain GROUP BY and HAVING.",
            expected_concepts=["grouping", "having filtering"]
        )

    def test_deeper_conceptual_for_high_scores(self):
        # Case score = 8.0
        result = Result(score=8.0, feedback="Great job.")
        self.generator.generate_follow_up(result, self.question)
        self.assertIn("DEEPER CONCEPTUAL", self.llm.last_prompt)
        
        # Case score = 9.5
        result_high = Result(score=9.5, feedback="Flawless.")
        self.generator.generate_follow_up(result_high, self.question)
        self.assertIn("DEEPER CONCEPTUAL", self.llm.last_prompt)

    def test_clarification_for_mid_scores(self):
        # Case score = 5.0
        result_mid1 = Result(score=5.0, feedback="Partially correct.")
        self.generator.generate_follow_up(result_mid1, self.question)
        self.assertIn("CLARIFICATION", self.llm.last_prompt)
        
        # Case score = 7.9
        result_mid2 = Result(score=7.9, feedback="Almost perfect but missed edge case.")
        self.generator.generate_follow_up(result_mid2, self.question)
        self.assertIn("CLARIFICATION", self.llm.last_prompt)

    def test_easier_for_low_scores(self):
        # Case score = 0.0
        result_low1 = Result(score=0.0, feedback="No answer.")
        self.generator.generate_follow_up(result_low1, self.question)
        self.assertIn("EASIER", self.llm.last_prompt)
        
        # Case score = 4.9
        result_low2 = Result(score=4.9, feedback="Got lost in details.")
        self.generator.generate_follow_up(result_low2, self.question)
        self.assertIn("EASIER", self.llm.last_prompt)

    def test_camel_case_compatibility(self):
        result = Result(score=8.5, feedback="Excellent.")
        
        res_snake = self.generator.generate_follow_up(result, self.question)
        prompt_snake = self.llm.last_prompt
        
        res_camel = self.generator.generateFollowUp(result, self.question)
        prompt_camel = self.llm.last_prompt
        
        self.assertEqual(res_snake, res_camel)
        self.assertEqual(prompt_snake, prompt_camel)

if __name__ == "__main__":
    unittest.main()
