import unittest
import os
from src.database.sqlite_repository import InterviewRepository
from src.models.candidate import Candidate
from src.models.question import Question
from src.models.interview import Interview
from src.models.result import Result

class TestSQLiteRepository(unittest.TestCase):
    def setUp(self) -> None:
        # Initialize an in-memory database for testing
        self.repo = InterviewRepository(db_path=":memory:")
        
        self.candidate = Candidate(
            id="CAN-1234",
            name="Diana Prince",
            email="diana@amazon.com"
        )
        
        self.q1 = Question(
            id="Q1",
            topic="SQL",
            difficulty="Easy",
            question_text="Explain SELECT.",
            expected_concepts=["projection"]
        )
        self.q2 = Question(
            id="Q2",
            topic="SQL",
            difficulty="Medium",
            question_text="Explain window functions.",
            expected_concepts=["partition", "order by"]
        )

    def test_save_and_retrieve_interview(self) -> None:
        # Create and populate interview session
        interview = Interview(
            interview_id="INT-999",
            candidate=self.candidate,
            questions=[self.q1, self.q2]
        )
        interview.start_interview() # moves index to 0, status to IN_PROGRESS
        interview.add_answer("Q1", "SELECT is used to query columns.")
        
        # Save to database
        self.repo.save_interview(interview)
        
        # Retrieve and assert
        retrieved = self.repo.get_interview("INT-999")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.interview_id, "INT-999")
        self.assertEqual(retrieved.status, "IN_PROGRESS")
        self.assertEqual(retrieved.current_question_index, 0)
        self.assertEqual(len(retrieved.questions), 2)
        
        # Verify candidate reconstruction
        self.assertEqual(retrieved.candidate.id, "CAN-1234")
        self.assertEqual(retrieved.candidate.name, "Diana Prince")
        self.assertEqual(retrieved.candidate.email, "diana@amazon.com")
        
        # Verify question sorting order
        self.assertEqual(retrieved.questions[0].id, "Q1")
        self.assertEqual(retrieved.questions[1].id, "Q2")
        
        # Verify answers are populated
        self.assertEqual(retrieved.answers.get("Q1"), "SELECT is used to query columns.")
        self.assertNotIn("Q2", retrieved.answers)
        
        # No result yet
        self.assertIsNone(retrieved.result)

    def test_update_interview_state(self) -> None:
        interview = Interview(
            interview_id="INT-888",
            candidate=self.candidate,
            questions=[self.q1]
        )
        interview.start_interview()
        self.repo.save_interview(interview)
        
        # Update answer and status
        interview.add_answer("Q1", "Updated Answer")
        interview.complete_interview() # moves status to COMPLETED
        
        # Attach a result
        result = Result(
            score=8.5,
            feedback="Great window calculations.",
            strengths=["Window usage"],
            weaknesses=["Needs optimization"],
            interview_id="INT-888"
        )
        interview.result = result
        
        # Resave (updates state)
        self.repo.save_interview(interview)
        
        # Retrieve and assert changes
        retrieved = self.repo.get_interview("INT-888")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.status, "COMPLETED")
        self.assertEqual(retrieved.answers["Q1"], "Updated Answer")
        
        # Verify result fields reconstruction
        self.assertIsNotNone(retrieved.result)
        self.assertEqual(retrieved.result.score, 8.5)
        self.assertEqual(retrieved.result.feedback, "Great window calculations.")
        self.assertEqual(retrieved.result.strengths, ["Window usage"])
        self.assertEqual(retrieved.result.weaknesses, ["Needs optimization"])

    def test_get_interview_history(self) -> None:
        # Create two interviews for candidate
        int1 = Interview(interview_id="INT-H1", candidate=self.candidate, questions=[self.q1])
        int2 = Interview(interview_id="INT-H2", candidate=self.candidate, questions=[self.q2])
        
        self.repo.save_interview(int1)
        # Artificially delay a tiny bit or let it save
        self.repo.save_interview(int2)
        
        history = self.repo.get_interview_history("CAN-1234")
        self.assertEqual(len(history), 2)
        # Ordered by date DESC, so the second one saved comes first
        self.assertEqual(history[0].interview_id, "INT-H2")
        self.assertEqual(history[1].interview_id, "INT-H1")
        
        # Verify candidate history reference is populated
        self.assertEqual(len(history[0].candidate.interview_history), 2)

    def test_get_non_existent_interview(self) -> None:
        retrieved = self.repo.get_interview("INT-MISSING")
        self.assertIsNone(retrieved)

    def test_camel_case_compatibility(self) -> None:
        interview = Interview(
            interview_id="INT-CC",
            candidate=self.candidate,
            questions=[self.q1]
        )
        # Test saveInterview
        self.repo.saveInterview(interview)
        
        # Test getInterview
        retrieved = self.repo.getInterview("INT-CC")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.interview_id, "INT-CC")
        
        # Test getInterviewHistory
        history = self.repo.getInterviewHistory("CAN-1234")
        self.assertTrue(any(i.interview_id == "INT-CC" for i in history))

if __name__ == "__main__":
    unittest.main()
