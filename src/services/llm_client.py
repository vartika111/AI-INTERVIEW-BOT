from abc import ABC, abstractmethod

class LLMClient(ABC):
    """Abstract base class representing an LLM API client wrapper."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Sends a prompt to the LLM and returns the text response."""
        pass


class MockLLMClient(LLMClient):
    """A mock implementation of the LLM client for local testing and validation."""

    def generate(self, prompt: str) -> str:
        """Returns standard mockup responses based on the request type."""
        # Simple placeholder generation logic
        if "question" in prompt.lower():
            return "Placeholder LLM Question Text"
        elif "evaluate" in prompt.lower() or "score" in prompt.lower():
            return "Score: 8/10\nFeedback: Great placeholder answer."
        return "Mock LLM response placeholder"
