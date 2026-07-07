import unittest
from src.models.candidate import Candidate
from src.models.question import Question
from src.models.interview import Interview
from src.models.result import Result

class TestModels(unittest.TestCase):
    def test_candidate_creation_and_methods(self):
        # 1. Test creation and getters
        candidate = Candidate(id="C1", name="Alice", email="alice@example.com")
        self.assertEqual(candidate.id, "C1")
        self.assertEqual(candidate.name, "Alice")
        self.assertEqual(candidate.email, "alice@example.com")
        self.assertEqual(len(candidate.selected_skills), 0)
        self.assertEqual(len(candidate.interview_history), 0)

        # 2. Test profile updating
        candidate.update_profile(name="Alice Bob", email="alice.bob@example.com")
        self.assertEqual(candidate.name, "Alice Bob")
        self.assertEqual(candidate.email, "alice.bob@example.com")

        # 3. Test validation errors
        with self.assertRaises(ValueError):
            candidate.name = "   "
        
        with self.assertRaises(ValueError):
            candidate.email = "invalid_email_no_at_sign"

        # 4. Test skill management
        candidate.add_skill("Python")
        candidate.add_skill("Java")
        # Duplicate skills should not be added
        candidate.add_skill("Python")
        self.assertEqual(candidate.selected_skills, ["Python", "Java"])
        self.assertEqual(candidate.selectedSkills, ["Python", "Java"])  # camelCase alias

        with self.assertRaises(ValueError):
            candidate.add_skill("")

    def test_question_creation_and_display(self):
        question = Question(
            id="Q1",
            topic="Python",
            difficulty="Easy",
            question_text="What is a decorator?",
            expected_concepts=["functions as first-class citizens", "closure", "@ syntax"]
        )
        
        self.assertEqual(question.id, "Q1")
        self.assertEqual(question.topic, "Python")
        self.assertEqual(question.difficulty, "Easy")
        self.assertEqual(question.question_text, "What is a decorator?")
        self.assertEqual(question.questionText, "What is a decorator?")
        self.assertEqual(len(question.expected_concepts), 3)
        self.assertEqual(len(question.expectedConcepts), 3)

        display = question.display_question()
        self.assertIn("Question ID: Q1", display)
        self.assertIn("Topic: Python", display)
        self.assertIn("What is a decorator?", display)

    def test_interview_lifecycle(self):
        candidate = Candidate(id="C2", name="Bob", email="bob@example.com")
        q1 = Question("Q1", "OOP", "Easy", "Explain inheritance", ["reusability"])
        q2 = Question("Q2", "OOP", "Medium", "Explain polymorphism", ["overriding", "overloading"])

        interview = Interview(interview_id="I1", candidate=candidate)
        self.assertEqual(interview.interview_id, "I1")
        self.assertEqual(interview.interviewId, "I1")
        self.assertEqual(interview.candidate, candidate)
        self.assertEqual(len(interview.questions), 0)
        self.assertEqual(interview.status, "CREATED")

        # Add questions
        interview.add_question(q1)
        interview.add_question(q2)
        self.assertEqual(len(interview.questions), 2)

        # Cannot get next question before starting
        with self.assertRaises(ValueError):
            interview.next_question()

        # Start interview
        interview.start_interview()
        self.assertEqual(interview.status, "IN_PROGRESS")
        self.assertEqual(interview.current_question_index, 0)
        # Candidate history should link the interview
        self.assertIn(interview, candidate.interview_history)
        self.assertEqual(len(candidate.interviewHistory), 1)

        # Cannot add questions once started
        with self.assertRaises(ValueError):
            interview.add_question(q1)

        # Question sequence progression
        first_q = interview.next_question()
        self.assertEqual(first_q, q1)
        self.assertEqual(interview.current_question_index, 1)

        second_q = interview.next_question()
        self.assertEqual(second_q, q2)
        self.assertEqual(interview.current_question_index, 2)

        third_q = interview.next_question()
        self.assertIsNone(third_q)

        # Complete interview
        interview.complete_interview()
        self.assertEqual(interview.status, "COMPLETED")

        # Cannot complete again or modify status arbitrarily
        with self.assertRaises(ValueError):
            interview.complete_interview()

    def test_result_creation_and_summary(self):
        result = Result(
            score=9.5,
            feedback="Excellent conceptual clarity.",
            strengths=["Clear definitions", "Good code structure examples"],
            weaknesses=["None noted"]
        )

        self.assertEqual(result.score, 9.5)
        self.assertEqual(result.feedback, "Excellent conceptual clarity.")
        self.assertEqual(len(result.strengths), 2)
        self.assertEqual(len(result.weaknesses), 1)

        # Test score validation
        with self.assertRaises(ValueError):
            result.score = 11.0

        with self.assertRaises(ValueError):
            result.score = -1.5

        summary = result.generate_summary()
        self.assertIn("Overall Score: 9.5 / 10.0", summary)
        self.assertIn("Excellent conceptual clarity.", summary)
        self.assertIn("- Clear definitions", summary)
        self.assertIn("- None noted", summary)

if __name__ == "__main__":
    unittest.main()
