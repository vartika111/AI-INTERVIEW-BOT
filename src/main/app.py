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
        candidate_id=generate_id("CAN"),
        name="Alex Smith",
        email="alex.smith@example.com",
        target_domain="Python"
    )
    print(f"Created Candidate: {candidate}")

    # 3. Generate questions
    print("\nGenerating questions for domain: Python...")
    questions = generator.generate_questions(domain=candidate.target_domain, count=3)
    for q in questions:
        print(f"  [{q.question_id}] {q.text}")

    # 4. Instantiate the interview session state
    interview = Interview(
        interview_id=generate_id("INT"),
        candidate=candidate,
        questions=questions
    )
    print(f"\nInitialized Session: {interview}")

    # 5. Provide simulated candidate answers
    simulated_answers = {
        questions[0].question_id: "Python is a high-level interpreted programming language known for readability.",
        questions[1].question_id: "List comprehensions provide a concise way to create lists.",
        questions[2].question_id: "Decorators modify the behavior of a function or class dynamically."
    }

    print("\nSimulating candidate submissions:")
    for q_id, answer in simulated_answers.items():
        interview.add_answer(q_id, answer)
        print(f"  Submitted answer for {q_id}")

    # 6. Complete and evaluate the interview
    if interview.is_complete():
        interview.status = "COMPLETED"
        print(f"\nEvaluating interview session...")
        result = evaluator.evaluate_interview(interview)
        interview.result = result
        
        # Save session to persistent layer
        storage.save_interview(interview)
        print("Saved interview results to storage.")

        # 7. Print final report card
        print("\n=== Final Evaluation Report ===")
        print(f"Interview ID: {result.interview_id}")
        print(f"Candidate: {candidate.name}")
        print(f"Overall Score: {result.score:.2f} / 10")
        print(f"Overall Feedback: {result.overall_feedback}")
        print("Question-by-Question Details:")
        for detail in result.detailed_evaluations:
            print(f"  - {detail['question_id']}: Score: {detail['score']}, Feedback: {detail['feedback']}")

if __name__ == "__main__":
    run_mock_interview()
