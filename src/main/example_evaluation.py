import sys
from src.models.question import Question
from src.services.llm_client import MockLLMClient, LLMClient
from src.services.evaluator import Evaluator

class StringLLMClient(LLMClient):
    """A dummy client that returns static raw strings for demonstration."""
    def __init__(self, response: str) -> None:
        self.response = response

    def generate_response(self, prompt: str) -> str:
        return self.response

    def evaluate_answer(self, question: Question, answer: str) -> str:
        return self.response

    def generate_follow_up(self, question: Question, answer: str) -> str:
        return "Follow up"

def run_examples() -> None:
    print("==================================================")
    print("         EVALUATOR SERVICE DEMONSTRATION          ")
    print("==================================================")

    # Define a test question
    question = Question(
        id="Q-OOP-01",
        topic="OOP",
        difficulty="Easy",
        question_text="Explain encapsulation in Object-Oriented Programming.",
        expected_concepts=["data hiding", "private modifiers", "getters/setters"]
    )

    # 1. Demonstration using MockLLMClient
    print("\n--- Example 1: MockLLMClient Evaluation ---")
    mock_client = MockLLMClient()
    evaluator_mock = Evaluator(mock_client)
    
    answer_1 = "Encapsulation is hiding the internal state and requiring all interaction to be performed through public methods."
    print(f"Candidate Answer: \"{answer_1}\"")
    
    result_1 = evaluator_mock.evaluate(question, answer_1)
    print("\nParsed Result Object:")
    print(f"  Score:  {result_1.score} / 10.0")
    print(f"  Feedback:\n{result_1.feedback}")
    print(f"  Strengths: {result_1.strengths}")
    print(f"  Improvements: {result_1.weaknesses}")

    # 2. Demonstration using structured JSON Markdown wrap
    print("\n--- Example 2: Markdown-Wrapped JSON response from LLM ---")
    markdown_json = (
        "```json\n"
        "{\n"
        "  \"score\": 9.5,\n"
        "  \"correctness\": \"Highly accurate explanation\",\n"
        "  \"explanation\": \"Candidate correctly identified data hiding and access control standard practices.\",\n"
        "  \"strengths\": [\"Clear distinction of access levels\", \"Understands class structures\"],\n"
        "  \"improvements\": [\"Mention potential performance benefits or compile-time optimizations\"]\n"
        "}\n"
        "```"
    )
    json_client = StringLLMClient(markdown_json)
    evaluator_json = Evaluator(json_client)
    
    result_2 = evaluator_json.evaluate(question, answer_1)
    print("\nParsed Result Object:")
    print(f"  Score:  {result_2.score} / 10.0")
    print(f"  Feedback:\n{result_2.feedback}")
    print(f"  Strengths: {result_2.strengths}")
    print(f"  Improvements: {result_2.weaknesses}")

    # 3. Demonstration of robust fallback parsing
    print("\n--- Example 3: Unstructured text response fallback ---")
    unstructured_text = (
        "Evaluation summary:\n"
        "The candidate has a decent attempt here. The candidate score is 6.5 out of 10.\n"
        "Strengths:\n"
        "- Good definition of wrapping logic\n"
        "- Mentions private properties\n"
        "Weaknesses / Improvements:\n"
        "- Did not list getters or setters specifically\n"
        "- Could provide an example\n"
    )
    fallback_client = StringLLMClient(unstructured_text)
    evaluator_fallback = Evaluator(fallback_client)
    
    result_3 = evaluator_fallback.evaluate(question, "Encapsulation means wrapping data.")
    print("\nParsed Result Object:")
    print(f"  Score:  {result_3.score} / 10.0")
    print(f"  Feedback:\n{result_3.feedback}")
    print(f"  Strengths: {result_3.strengths}")
    print(f"  Improvements: {result_3.weaknesses}")

if __name__ == "__main__":
    run_examples()
