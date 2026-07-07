import unittest
from src.services.question_generator import QuestionGenerator
from src.models.question import Question

class TestQuestionGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = QuestionGenerator()

    def test_java_medium_interview_generation(self):
        """Tests that a Java Medium interview requests questions correctly with expected types."""
        questions = self.generator.generate_questions(topic="Java", difficulty="Medium", count=2)
        
        self.assertEqual(len(questions), 2)
        for q in questions:
            self.assertIsInstance(q, Question)
            self.assertEqual(q.topic, "Java")
            self.assertEqual(q.difficulty, "Medium")
            self.assertTrue(q.id.startswith("Q-JAVA-"))
            self.assertTrue(len(q.question_text) > 0)
            self.assertTrue(len(q.expected_concepts) > 0)

    def test_dsa_easy_interview_generation(self):
        """Tests that a DSA Easy interview requests questions correctly with expected types."""
        questions = self.generator.generate_questions(topic="DSA", difficulty="Easy", count=2)
        
        self.assertEqual(len(questions), 2)
        for q in questions:
            self.assertIsInstance(q, Question)
            self.assertEqual(q.topic, "DSA")
            self.assertEqual(q.difficulty, "Easy")
            self.assertTrue(q.id.startswith("Q-DSA-"))
            self.assertTrue(len(q.question_text) > 0)
            self.assertTrue(len(q.expected_concepts) > 0)

    def test_input_validation(self):
        """Tests that invalid topics, difficulties, or counts raise ValueErrors."""
        # Invalid topic
        with self.assertRaises(ValueError) as ctx:
            self.generator.generate_questions(topic="HTML", difficulty="Easy", count=1)
        self.assertIn("Unsupported topic", str(ctx.exception))

        # Invalid difficulty
        with self.assertRaises(ValueError) as ctx:
            self.generator.generate_questions(topic="Python", difficulty="Beginner", count=1)
        self.assertIn("Unsupported difficulty", str(ctx.exception))

        # Invalid count (zero or negative)
        with self.assertRaises(ValueError) as ctx:
            self.generator.generate_questions(topic="Python", difficulty="Easy", count=0)
        self.assertIn("Question count must be a positive integer", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.generator.generate_questions(topic="Python", difficulty="Easy", count=-5)

    def test_case_insensitivity_and_whitespace(self):
        """Tests that validation is case-insensitive and trims trailing whitespace."""
        questions = self.generator.generate_questions(topic="  pYtHoN  ", difficulty="  mEdIuM  ", count=1)
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].topic, "Python")
        self.assertEqual(questions[0].difficulty, "Medium")

    def test_count_exceeds_pool(self):
        """Tests that requesting more questions than available returns all available questions without crash."""
        # Java Hard has only 1 question in bank. Requesting 5 should return 1.
        questions = self.generator.generate_questions(topic="Java", difficulty="Hard", count=5)
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].id, "Q-JAVA-05")

if __name__ == "__main__":
    unittest.main()
