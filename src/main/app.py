import sys
from ..models.candidate import Candidate
from ..models.interview import Interview
from ..services.llm_client import MockLLMClient
from ..services.question_generator import QuestionGenerator
from ..services.evaluator import Evaluator
from ..database.storage import InMemoryStorage
from ..utils.helpers import generate_id

def run_mock_interview() -> None:
    """Executes a simulated interview to verify component integration and API designs."""
    print("=== AI Interview Bot Initialization ===")
    
    # 1. Initialize core service dependencies and storage
    llm_client = MockLLMClient()
    generator = QuestionGenerator(llm_client)
    evaluator = Evaluator(llm_client)
    storage = InMemoryStorage()

    # 2. Define a mock candidate
    candidate = Candidate(
        id=generate_id("CAN"),
        name="Alex Smith",
        email="alex.smith@example.com"
    )
    candidate.add_skill("Python")
    candidate.add_skill("SQL")
    print(f"Created Candidate: {candidate}")
    print(f"Selected Skills: {candidate.selected_skills}")

    # 3. Generate questions
    print("\nGenerating questions for domain: Python...")
    # Using generator to produce list of Question models
    questions = generator.generate_questions(topic="Python", difficulty="Medium", count=3)
    for q in questions:
        print(q.display_question())

    # 4. Instantiate and start the interview session state
    interview = Interview(
        interview_id=generate_id("INT"),
        candidate=candidate,
        questions=questions
    )
    interview.start_interview()
    print(f"\nInitialized Session: {interview}")
    print(f"Interview Status: {interview.status}")

    # 5. Provide simulated candidate answers
    simulated_answers = {
        questions[0].id: "Python is a high-level interpreted programming language known for readability.",
        questions[1].id: "List comprehensions provide a concise way to create lists.",
        questions[2].id: "Decorators modify the behavior of a function or class dynamically."
    }

    print("\nSimulating candidate submissions:")
    for q_id, answer in simulated_answers.items():
        interview.add_answer(q_id, answer)
        print(f"  Submitted answer for {q_id}")

    # 6. Complete and evaluate the interview
    if interview.is_complete():
        interview.complete_interview()
        print(f"Interview Status: {interview.status}")
        
        print(f"\nEvaluating interview session...")
        result = evaluator.evaluate_interview(interview)
        interview.result = result
        
        # Save session to persistent layer
        storage.save_interview(interview)
        print("Saved interview results to storage.")

        # 7. Print final report card using the new generate_summary method
        print("\n" + result.generate_summary())
        print(f"Candidate's Interview History count: {len(candidate.interview_history)}")

if __name__ == "__main__":
    run_mock_interview()
