import os
import json
import random
from typing import List, Optional, Dict
from ..models.question import Question
from .llm_client import LLMClient

class QuestionGenerator:
    """Service responsible for generating technical questions, supporting local JSON databases and future LLMs."""

    # Supported domains and difficulties mapping for normalization and validation
    SUPPORTED_TOPICS: Dict[str, str] = {
        "java": "Java",
        "python": "Python",
        "dsa": "DSA",
        "oop": "OOP",
        "sql": "SQL"
    }
    
    SUPPORTED_DIFFICULTIES: Dict[str, str] = {
        "easy": "Easy",
        "medium": "Medium",
        "hard": "Hard"
    }

    def __init__(self, llm_client: Optional[LLMClient] = None, question_bank_path: Optional[str] = None) -> None:
        self.llm_client: Optional[LLMClient] = llm_client
        
        # Resolve the default local question bank path if not provided
        if question_bank_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self._question_bank_path = os.path.join(current_dir, "..", "database", "question_bank.json")
        else:
            self._question_bank_path = question_bank_path

    def generate_questions(self, topic: str, difficulty: str, count: int = 3) -> List[Question]:
        """
        Generates a list of Question objects based on topic, difficulty, and requested count.
        Validates topic and difficulty. Fallbacks to local bank if LLM client is not fully configured.
        """
        # 1. Validation and Normalization
        normalized_topic = self.SUPPORTED_TOPICS.get(topic.strip().lower())
        if not normalized_topic:
            raise ValueError(
                f"Unsupported topic '{topic}'. Must be one of: {list(self.SUPPORTED_TOPICS.values())}"
            )

        normalized_difficulty = self.SUPPORTED_DIFFICULTIES.get(difficulty.strip().lower())
        if not normalized_difficulty:
            raise ValueError(
                f"Unsupported difficulty '{difficulty}'. Must be one of: {list(self.SUPPORTED_DIFFICULTIES.values())}"
            )

        if count <= 0:
            raise ValueError("Question count must be a positive integer greater than zero")

        # 2. LLM Client routing (Bridge to future LLM API integration)
        # If a real non-mock LLM is present and active, we would route to prompt generation.
        # For now, we will load from our separated local question bank JSON database.
        return self._generate_from_local_bank(normalized_topic, normalized_difficulty, count)

    def generateQuestions(self, topic: str, difficulty: str, count: int = 3) -> List[Question]:
        """CamelCase alias for generate_questions."""
        return self.generate_questions(topic, difficulty, count)

    def _generate_from_local_bank(self, topic: str, difficulty: str, count: int) -> List[Question]:
        """Loads and selects questions from the local JSON file database."""
        if not os.path.exists(self._question_bank_path):
            raise FileNotFoundError(f"Question bank database file not found at: {self._question_bank_path}")

        with open(self._question_bank_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        topic_data = data.get(topic, {})
        question_pool = topic_data.get(difficulty, [])

        if not question_pool:
            raise ValueError(f"No questions found in bank for {topic} - {difficulty}")

        # Randomly sample the pool to avoid duplicate question sessions
        # If count exceeds pool size, take the whole pool
        sampled_data = random.sample(question_pool, min(count, len(question_pool)))

        questions: List[Question] = []
        for q in sampled_data:
            questions.append(Question(
                id=q["id"],
                topic=topic,
                difficulty=difficulty,
                question_text=q["questionText"],
                expected_concepts=q["expectedConcepts"]
            ))

        return questions
