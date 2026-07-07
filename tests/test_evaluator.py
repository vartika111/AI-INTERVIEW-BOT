import unittest
from src.services.llm_client import LLMClient
from src.services.evaluator import Evaluator
from src.models.question import Question
from src.models.result import Result

class DummyLLMClient(LLMClient):
    def __init__(self, response_to_return: str):
        self.response_to_return = response_to_return
        self.calls = 0

    def generate_response(self, prompt: str) -> str:
        self.calls += 1
        return self.response_to_return

    def evaluate_answer(self, question: Question, answer: str) -> str:
        self.calls += 1
        return self.response_to_return

    def generate_follow_up(self, question: Question, answer: str) -> str:
        return ""

class ErrorLLMClient(LLMClient):
    def generate_response(self, prompt: str) -> str:
        raise RuntimeError("LLM error")

    def evaluate_answer(self, question: Question, answer: str) -> str:
        raise RuntimeError("LLM error")

    def generate_follow_up(self, question: Question, answer: str) -> str:
        return ""

class TestEvaluator(unittest.TestCase):
    def setUp(self) -> None:
        self.question = Question(
            id="Q1",
            topic="Python",
            difficulty="Easy",
            question_text="Explain lists vs tuples.",
            expected_concepts=["mutable", "immutable"]
        )

    def test_evaluate_clean_json(self):
        json_output = '{"score": 9.2, "correctness": "Excellent", "explanation": "Answers matched criteria.", "strengths": ["Clear mutability explanation"], "improvements": ["None"]}'
        llm = DummyLLMClient(json_output)
        evaluator = Evaluator(llm)
        result = evaluator.evaluate(self.question, "Lists are mutable, tuples are immutable.")
        
        self.assertEqual(result.score, 9.2)
        self.assertIn("Excellent", result.feedback)
        self.assertIn("Answers matched criteria.", result.feedback)
        self.assertEqual(result.strengths, ["Clear mutability explanation"])
        self.assertEqual(result.weaknesses, ["None"])

    def test_evaluate_markdown_wrapped_json(self):
        json_output = '```json\n{"score": 7.0, "correctness": "Average", "explanation": "Good detail.", "strengths": ["syntax"], "improvements": ["performance"]}\n```'
        llm = DummyLLMClient(json_output)
        evaluator = Evaluator(llm)
        result = evaluator.evaluate(self.question, "Lists are mutable.")
        
        self.assertEqual(result.score, 7.0)
        self.assertEqual(result.strengths, ["syntax"])
        self.assertEqual(result.weaknesses, ["performance"])

    def test_evaluate_unstructured_fallback(self):
        unstructured_output = "The score for this answer is 8.5. Strengths: - Knows Python syntax. Improvements: - Explain memory layout."
        llm = DummyLLMClient(unstructured_output)
        evaluator = Evaluator(llm)
        result = evaluator.evaluate(self.question, "Some answer")
        
        self.assertEqual(result.score, 8.5)
        self.assertEqual(result.strengths, ["Knows Python syntax."])
        self.assertEqual(result.weaknesses, ["Explain memory layout."])

    def test_evaluate_empty_answer(self):
        llm = DummyLLMClient("")
        evaluator = Evaluator(llm)
        result = evaluator.evaluate(self.question, "   ")
        
        self.assertEqual(result.score, 0.0)
        self.assertIn("No answer provided", result.feedback)
        self.assertEqual(len(result.strengths), 0)
        self.assertEqual(result.weaknesses, ["Candidate did not answer the question."])

    def test_evaluate_client_error(self):
        llm = ErrorLLMClient()
        evaluator = Evaluator(llm)
        result = evaluator.evaluate(self.question, "Lists are mutable.")
        
        self.assertEqual(result.score, 0.0)
        self.assertIn("Failed to query LLM Client", result.feedback)
        self.assertEqual(result.weaknesses, ["N/A due to LLM client error"])

if __name__ == "__main__":
    unittest.main()
