import os
import json
from abc import ABC, abstractmethod
from typing import Optional
from ..models.question import Question

class LLMClient(ABC):
    """Abstract interface defining required LLM services for the AI Interview Bot."""

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Sends a raw text prompt to the LLM and returns the text response."""
        pass

    def generateResponse(self, prompt: str) -> str:
        """CamelCase alias for generate_response."""
        return self.generate_response(prompt)

    @abstractmethod
    def evaluate_answer(self, question: Question, answer: str) -> str:
        """Evaluates a candidate's answer against the given question text and expected concepts."""
        pass

    def evaluateAnswer(self, question: Question, answer: str) -> str:
        """CamelCase alias for evaluate_answer."""
        return self.evaluate_answer(question, answer)

    @abstractmethod
    def generate_follow_up(self, question: Question, answer: str) -> str:
        """Generates a contextual follow-up question based on the candidate's response."""
        pass

    def generateFollowUp(self, question: Question, answer: str) -> str:
        """CamelCase alias for generate_follow_up."""
        return self.generate_follow_up(question, answer)

    # Legacy method from Step 1 to maintain backwards compatibility in Evaluator
    def generate(self, prompt: str) -> str:
        """Backwards compatible routing for Step 1 evaluator calls."""
        return self.generate_response(prompt)


class MockLLMClient(LLMClient):
    """Mock implementation returning pre-defined simulated responses for test execution."""

    def generate_response(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "evaluate" in prompt_lower or "rubric" in prompt_lower:
            return "Score: 8/10. Feedback: Correct explanation of concepts."
        if "follow-up" in prompt_lower or "probe" in prompt_lower:
            return "Mock Follow-up: Can you elaborate on how garbage collection manages memory cycles?"
        return "Mock LLM text completion response."

    def evaluate_answer(self, question: Question, answer: str) -> str:
        data = {
            "score": 8.0,
            "correctness": "Correct concept explanation. (Score: 8/10)",
            "explanation": f"Candidate answered '{answer}' which covers '{question.topic}'.",
            "strengths": ["Strong understanding of syntax", "Correct usage of standard concepts"],
            "improvements": ["Could detail system design considerations further"]
        }
        return json.dumps(data)

    def generate_follow_up(self, question: Question, answer: str) -> str:
        return f"Interesting answer on '{question.topic}'. Can you elaborate on the expected concepts: {', '.join(question.expected_concepts)}?"


class OpenAIClient(LLMClient):
    """Concrete implementation integrating with OpenAI API using the official Python SDK."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o") -> None:
        self.model = model
        
        # Load API key from environment if not explicitly provided
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API Key is missing. Please set the OPENAI_API_KEY environment variable "
                "or pass it directly to the constructor."
            )
            
        # Lazy import of openai to prevent crashes if the package is not installed/loaded in a minimal setup
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError as e:
            raise ImportError(
                "The 'openai' library is required to use OpenAIClient. "
                "Please run: pip install openai"
            ) from e

    def generate_response(self, prompt: str) -> str:
        """Queries OpenAI Chat Completions endpoint with exception handling wrappers."""
        try:
            import openai
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional, helpful technical interviewer assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("Received empty response from OpenAI Completion endpoint")
            return content.strip()
        except openai.OpenAIError as e:
            # Handle rate limits, auth errors, network disconnects
            print(f"[LLM ERROR] OpenAI API request failed: {e}")
            raise RuntimeError(f"OpenAI service error: {e}") from e
        except Exception as e:
            print(f"[LLM ERROR] Unexpected failure in LLM invocation: {e}")
            raise RuntimeError(f"Failed to query LLM service: {e}") from e

    def evaluate_answer(self, question: Question, answer: str) -> str:
        """Asks the LLM to grade and summarize candidate performance."""
        prompt = (
            f"Evaluate the candidate's answer for the following question:\n"
            f"Question: {question.question_text}\n"
            f"Topic: {question.topic} | Difficulty: {question.difficulty}\n"
            f"Expected Concepts: {', '.join(question.expected_concepts)}\n\n"
            f"Candidate's Answer:\n\"{answer}\"\n\n"
            f"You MUST return a JSON object with the following schema:\n"
            f"{{\n"
            f"  \"score\": <float value between 0.0 and 10.0>,\n"
            f"  \"correctness\": \"<brief evaluation of correctness>\",\n"
            f"  \"explanation\": \"<detailed explanation of what was correct or missing>\",\n"
            f"  \"strengths\": [\"<strength 1>\", \"<strength 2>\"],\n"
            f"  \"improvements\": [\"<improvement 1>\", \"<improvement 2>\"]\n"
            f"}}\n"
            f"Respond ONLY with the raw JSON block. Do not include any additional markdown, formatting, wrapper or conversational text."
        )
        return self.generate_response(prompt)

    def generate_follow_up(self, question: Question, answer: str) -> str:
        """Asks the LLM to generate a natural conversational follow-up question."""
        prompt = (
            f"You are a technical interviewer conducting a live conversation.\n"
            f"Question asked: {question.question_text}\n"
            f"Candidate's Answer:\n\"{answer}\"\n\n"
            f"Generate a single follow-up question to probe deeper or clarify their response. "
            f"Do not write greetings or prefaces, output only the question text."
        )
        return self.generate_response(prompt)
