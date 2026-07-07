import os
from src.database.sqlite_repository import InterviewRepository
from src.models.candidate import Candidate
from src.models.question import Question
from src.models.interview import Interview
from src.models.result import Result

def run_storage_demonstration() -> None:
    db_file = "demo_storage.db"
    
    # Ensure starting with a fresh database file
    if os.path.exists(db_file):
        os.remove(db_file)
        
    print("==================================================")
    print("      INTERVIEW REPOSITORY DB DEMONSTRATION       ")
    print("==================================================")

    # 1. Initialize repository
    print(f"Initializing InterviewRepository with database file: {db_file}...")
    repo = InterviewRepository(db_path=db_file)

    # 2. Define candidate and questions
    candidate = Candidate(
        id="CAN-DEMO",
        name="Peter Parker",
        email="peter.parker@dailybugle.com"
    )
    q1 = Question("Q1", "OOP", "Easy", "What is polymorphism?", ["overriding", "interfaces"])
    q2 = Question("Q2", "OOP", "Medium", "Explain abstraction.", ["data hiding", "interfaces"])

    # 3. Create and Save Interview session
    print("\nStep 1: Creating and saving a new interview...")
    interview = Interview(
        interview_id="INT-DEMO-1",
        candidate=candidate,
        questions=[q1, q2]
    )
    interview.start_interview()
    
    repo.save_interview(interview)
    print("  Interview saved to database.")

    # 4. Load from DB, modify, and save
    print("\nStep 2: Retrieving interview from DB and adding answer...")
    retrieved = repo.get_interview("INT-DEMO-1")
    print(f"  Retrieved interview status: {retrieved.status}")
    print(f"  Retrieved interview current question index: {retrieved.current_question_index}")
    
    retrieved.add_answer("Q1", "Polymorphism means taking many forms, e.g. method overriding.")
    repo.save_interview(retrieved)
    print("  Interview updated with answer in DB.")

    # 5. Complete and evaluate interview, then save
    print("\nStep 3: Completing interview and saving evaluation results...")
    retrieved_again = repo.get_interview("INT-DEMO-1")
    retrieved_again.complete_interview()
    
    # Attach a result
    result = Result(
        score=9.0,
        feedback="Very good conceptual clarity on OOP principles.",
        strengths=["Clear polymorphism definition", "Correct terminology"],
        weaknesses=["None noted"],
        interview_id="INT-DEMO-1"
    )
    retrieved_again.result = result
    
    repo.save_interview(retrieved_again)
    print("  Completed interview results saved in DB.")

    # 6. Save a second interview to demonstrate candidate history
    print("\nStep 4: Creating a second interview for the same candidate...")
    interview_2 = Interview(
        interview_id="INT-DEMO-2",
        candidate=candidate,
        questions=[q1]
    )
    repo.save_interview(interview_2)
    print("  Second interview saved in DB.")

    # 7. Query Candidate History
    print("\nStep 5: Retrieving candidate interview history...")
    history = repo.get_interview_history("CAN-DEMO")
    print(f"  Total interviews found: {len(history)}")
    for idx, h in enumerate(history, 1):
        print(f"  {idx}. Interview ID: {h.interview_id} | Status: {h.status} | Score: {h.result.score if h.result else 'N/A'}")

    # 8. Clean up
    print(f"\nCleaning up database file {db_file}...")
    if os.path.exists(db_file):
        os.remove(db_file)
    print("Demonstration successfully completed!")

if __name__ == "__main__":
    run_storage_demonstration()
