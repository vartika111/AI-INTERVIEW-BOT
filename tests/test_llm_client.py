import os
import unittest
from src.services.llm_client import MockLLMClient, OpenAIClient
from src.models.question import Question

class TestLLMClient(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_client = MockLLMClient()
        self.question = Question(
            id="Q1",
            topic="Python",
            difficulty="Easy",
            question_text="What are lists?",
            expected_concepts=["mutable", "sequence"]
        )

    def test_mock_client_generate_response(self):
        """Tests that the mock client returns matching strings for different prompt keywords."""
        resp1 = self.mock_client.generate_response("Evaluate the candidate's answer")
        self.assertIn("Score:", resp1)

        resp2 = self.mock_client.generate_response("Generate follow-up question")
        self.assertIn("Mock Follow-up:", resp2)

        resp3 = self.mock_client.generate_response("Some random prompt text")
        self.assertEqual(resp3, "Mock LLM text completion response.")

    def test_mock_client_methods(self):
        """Tests structured evaluate and follow up methods on MockLLMClient."""
        evaluation = self.mock_client.evaluate_answer(self.question, "A list is mutable.")
        self.assertIn("Score: 8/10", evaluation)
        self.assertIn("Candidate answered 'A list is mutable.'", evaluation)

        follow_up = self.mock_client.generate_follow_up(self.question, "A list is mutable.")
        self.assertIn("mutable, sequence", follow_up)

    def test_openai_client_key_validation(self):
        """Tests that OpenAIClient raises ValueError if initialized with no API key."""
        # Temporarily clear environment variable if set to isolate test execution
        old_env_key = os.environ.get("OPENAI_API_KEY")
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

        try:
            with self.assertRaises(ValueError) as ctx:
                OpenAIClient()
            self.assertIn("OpenAI API Key is missing", str(ctx.exception))
        finally:
            # Restore environment variable
            if old_env_key is not None:
                os.environ["OPENAI_API_KEY"] = old_env_key

if __name__ == "__main__":
    unittest.main()
