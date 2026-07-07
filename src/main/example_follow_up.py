from src.models.question import Question
from src.models.result import Result
from src.services.llm_client import LLMClient
from src.services.follow_up_question_generator import FollowUpQuestionGenerator

class PrintPromptLLMClient(LLMClient):
    """LLMClient implementation that prints the instruction it received and returns a simulated question."""
    def generate_response(self, prompt: str) -> str:
        # Find and display the instruction line from the prompt
        instruction_line = ""
        for line in prompt.split("\n"):
            if "Instruction:" in line:
                instruction_line = line
                break
        
        print(f"  [LLM received instruction]: {instruction_line}")
        
        if "DEEPER CONCEPTUAL" in prompt:
            return "Adaptive Follow-up (Deeper): Can you explain how you would design a highly concurrent transactional database index using B-Trees?"
        elif "CLARIFICATION" in prompt:
            return "Adaptive Follow-up (Clarification): You mentioned indexing speeds up read queries. Can you clarify how it affects write operations?"
        else:
            return "Adaptive Follow-up (Easier): What is a primary key, and how does it relate to index lookups?"

    def evaluate_answer(self, question: Question, answer: str) -> str:
        return ""

    def generate_follow_up(self, question: Question, answer: str) -> str:
        return ""

def run_follow_up_demonstration() -> None:
    print("==================================================")
    print("      ADAPTIVE FOLLOW-UP DEMONSTRATION            ")
    print("==================================================")

    # Define a test question
    previous_question = Question(
        id="Q-SQL-04",
        topic="SQL",
        difficulty="Medium",
        question_text="What are database indexes and how do they speed up lookups at the expense of write overhead?",
        expected_concepts=["B-Tree indexing keys", "index scanning execution path", "INSERT/UPDATE indexing rebuild logs"]
    )

    llm = PrintPromptLLMClient()
    generator = FollowUpQuestionGenerator(llm)

    # 1. High score scenario (score >= 8.0)
    print("\n--- Scenario 1: High Score (Score = 9.0) ---")
    result_high = Result(
        score=9.0,
        feedback="Excellent explanation of B-Trees and execution path details."
    )
    question_high = generator.generate_follow_up(result_high, previous_question)
    print(f"  Generated Question: {question_high}")

    # 2. Mid score scenario (5.0 <= score < 8.0)
    print("\n--- Scenario 2: Mid Score (Score = 6.5) ---")
    result_mid = Result(
        score=6.5,
        feedback="Good, but failed to address how write operations are affected."
    )
    question_mid = generator.generate_follow_up(result_mid, previous_question)
    print(f"  Generated Question: {question_mid}")

    # 3. Low score scenario (score < 5.0)
    print("\n--- Scenario 3: Low Score (Score = 3.0) ---")
    result_low = Result(
        score=3.0,
        feedback="Answer was very vague and did not detail indexes or write overhead."
    )
    question_low = generator.generate_follow_up(result_low, previous_question)
    print(f"  Generated Question: {question_low}")

if __name__ == "__main__":
    run_follow_up_demonstration()
