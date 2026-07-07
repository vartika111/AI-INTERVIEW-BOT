import unittest
from src.services.llm_client import MockLLMClient
from src.services.question_generator import QuestionGenerator
from src.services.evaluator import Evaluator
from src.services.interview_manager import InterviewManager
from src.database.storage import InMemoryStorage

class TestInterviewManager(unittest.TestCase):
    def setUp(self) -> None:
        self.llm_client = MockLLMClient()
        self.question_generator = QuestionGenerator(self.llm_client)
        self.evaluator = Evaluator(self.llm_client)
        self.storage = InMemoryStorage()
        self.manager = InterviewManager(
            question_generator=self.question_generator,
            evaluator=self.evaluator,
            storage=self.storage
        )

    def test_create_interview(self):
        """Tests successful creation and initialization of an interview session."""
        interview = self.manager.create_interview(
            name="Bob",
            email="bob@example.com",
            topic="Java",
            difficulty="Easy",
            count=2
        )

        self.assertIsNotNone(interview)
        self.assertEqual(interview.candidate.name, "Bob")
        self.assertEqual(interview.candidate.email, "bob@example.com")
        self.assertIn("Java", interview.candidate.selected_skills)
        self.assertEqual(len(interview.questions), 2)
        self.assertEqual(interview.status, "IN_PROGRESS")
        self.assertEqual(interview.current_question_index, 0)
        
        # Verify saved in storage
        stored = self.storage.get_interview(interview.interview_id)
        self.assertEqual(stored.interview_id, interview.interview_id)

    def test_flow_progression_and_submissions(self):
        """Tests sequential question retrieval and answer submissions."""
        interview = self.manager.create_interview(
            name="Charlie",
            email="charlie@example.com",
            topic="Python",
            difficulty="Easy",
            count=2
        )

        q1 = self.manager.get_next_question(interview.interview_id)
        self.assertIsNotNone(q1)
        self.assertEqual(q1.id, interview.questions[0].id)
        self.assertEqual(interview.current_question_index, 1)

        self.manager.submit_answer(interview.interview_id, q1.id, "Alice's answer to Q1")
        self.assertEqual(interview.answers[q1.id], "Alice's answer to Q1")

        q2 = self.manager.get_next_question(interview.interview_id)
        self.assertIsNotNone(q2)
        self.assertEqual(q2.id, interview.questions[1].id)
        self.assertEqual(interview.current_question_index, 2)

        self.manager.submit_answer(interview.interview_id, q2.id, "Alice's answer to Q2")

        # Verify no more questions left
        q_none = self.manager.get_next_question(interview.interview_id)
        self.assertIsNone(q_none)

        # Complete and verify result score
        result = self.manager.complete_interview(interview.interview_id)
        self.assertEqual(interview.status, "COMPLETED")
        self.assertEqual(result.score, 8.0)  # Mock score is 8 for non-empty answers
        self.assertEqual(len(result.strengths), 2)
        self.assertEqual(len(interview.candidate.interview_history), 1)

    def test_invalid_operations(self):
        """Tests that incorrect references trigger appropriate ValueErrors."""
        # Non-existent interview
        with self.assertRaises(ValueError):
            self.manager.get_next_question("NON-EXISTENT-ID")

        with self.assertRaises(ValueError):
            self.manager.submit_answer("NON-EXISTENT-ID", "Q1", "Answer")

        with self.assertRaises(ValueError):
            self.manager.complete_interview("NON-EXISTENT-ID")

        # Submit answer to a question not in the interview
        interview = self.manager.create_interview("Dave", "dave@example.com", "OOP", "Easy", 1)
        with self.assertRaises(ValueError):
            self.manager.submit_answer(interview.interview_id, "Q-INVALID-ID", "Some answer")

if __name__ == "__main__":
    unittest.main()
