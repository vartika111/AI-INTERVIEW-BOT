import sys
import os
from src.services.llm_client import MockLLMClient, OpenAIClient
from src.services.question_generator import QuestionGenerator
from src.services.evaluator import Evaluator
from src.services.interview_manager import InterviewManager
from src.services.follow_up_question_generator import FollowUpQuestionGenerator
from src.database import InMemoryStorage, InterviewRepository

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def print_separator(char: str = "=", length: int = 60) -> None:
    print(char * length)

def select_from_menu(title: str, options: list) -> str:
    print(f"\nSelect {title}:")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    
    while True:
        try:
            choice = input(f"Enter option number (1-{len(options)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            else:
                print(f"Invalid option. Please enter a number between 1 and {len(options)}.")
        except ValueError:
            print("Please enter a valid number.")

def main() -> None:
    print_separator("*")
    print("           WELCOME TO THE AI INTERVIEW BOT CLI")
    print_separator("*")
    
    # 1. Gather Candidate Information
    print("\n--- Step 1: Candidate Registration ---")
    name = input("Enter your full name: ").strip()
    while not name:
        name = input("Name cannot be empty. Please enter your name: ").strip()

    email = input("Enter your email address: ").strip()
    while "@" not in email:
        email = input("Invalid email. Please enter a valid email address: ").strip()

    skills_input = input("Enter your current skills (comma-separated): ").strip()
    skills = [s.strip() for s in skills_input.split(",") if s.strip()]

    # 2. Select Topic and Difficulty
    topics = ["Java", "Python", "DSA", "OOP", "SQL"]
    topic = select_from_menu("Technical Topic", topics)

    difficulties = ["Easy", "Medium", "Hard"]
    difficulty = select_from_menu("Interview Difficulty", difficulties)

    # 3. Select Question Count
    while True:
        try:
            count_input = input("\nEnter number of questions to generate (default 3): ").strip()
            if not count_input:
                count = 3
                break
            count = int(count_input)
            if count > 0:
                break
            else:
                print("Count must be greater than zero.")
        except ValueError:
            print("Please enter a valid integer.")

    print("\nInitializing interview session...")
    
    # 4. Initialize dependencies dynamically
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            print("\n[INFO] OPENAI_API_KEY detected. Initializing OpenAIClient...")
            llm_client = OpenAIClient(api_key=openai_key)
        except Exception as e:
            print(f"\n[WARNING] Failed to load OpenAIClient: {e}. Falling back to MockLLMClient...")
            llm_client = MockLLMClient()
    else:
        print("\n[INFO] No OPENAI_API_KEY detected in environment. Using MockLLMClient...")
        llm_client = MockLLMClient()

    generator = QuestionGenerator(llm_client)
    evaluator = Evaluator(llm_client)
    
    # Use SQLite database storage by default
    try:
        print("\n[INFO] Initializing SQLite database storage (interview_bot.db)...")
        storage = InterviewRepository(db_path="interview_bot.db")
    except Exception as e:
        print(f"\n[WARNING] Failed to initialize SQLite storage: {e}. Falling back to InMemoryStorage...")
        storage = InMemoryStorage()

    follow_up_generator = FollowUpQuestionGenerator(llm_client)
    manager = InterviewManager(generator, evaluator, storage, follow_up_generator)

    # 5. Create and Start Interview
    try:
        interview = manager.create_interview(
            name=name,
            email=email,
            topic=topic,
            difficulty=difficulty,
            count=count
        )
    except Exception as e:
        print(f"\n[ERROR] Failed to start interview: {e}")
        sys.exit(1)

    # Populate candidate skills if provided
    for s in skills:
        interview.candidate.add_skill(s)

    print_separator()
    print(f" Interview Started! (Session ID: {interview.interview_id})")
    print(f" Candidate: {interview.candidate.name} ({interview.candidate.email})")
    print(f" Domain: {topic} | Difficulty: {difficulty} | Questions: {len(interview.questions)}")
    print_separator()

    # 6. Conduct Interview Loop
    index = 0
    while True:
        question = manager.get_next_question(interview.interview_id)
        if not question:
            break

        # Fetch the updated interview state to dynamically handle inserted follow-ups
        current_interview = manager.get_interview(interview.interview_id)
        question_count = len(current_interview.questions)

        print(f"\nQuestion {index + 1} of {question_count}:")
        print(question.display_question())
        
        answer = input("\nYour Answer: ").strip()
        while not answer:
            print("Answer cannot be empty. If you do not know, type 'I do not know'.")
            answer = input("\nYour Answer: ").strip()

        # Submit answer to manager
        manager.submit_answer(interview.interview_id, question.id, answer)
        print("Response recorded successfully.")
        index += 1

    # 7. Complete Interview and Print Report
    print("\nConcluding interview. Evaluating your answers...")
    result = manager.complete_interview(interview.interview_id)
    
    print("\nEvaluation completed!")
    print(result.generate_summary())
    print("\nThank you for participating! Your results have been stored.")
    print_separator("*")

if __name__ == "__main__":
    main()
