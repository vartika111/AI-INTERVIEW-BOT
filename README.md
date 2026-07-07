# AI Interview Bot

An intelligent, Object-Oriented system designed to conduct automated technical interviews across multiple domains (Java, Python, DSA, OOP, SQL) using Large Language Models (LLMs).

## Project Purpose
The AI Interview Bot aims to streamline and standardise the initial screening phases of technical recruitment. By using generative AI, the bot simulates a real technical interviewer: asking target domain-specific questions, collecting response answers, dynamically evaluating candidates, and saving candidate history. This provides recruiters with consistent, data-driven feedback on a candidate's readiness before standard human interviews.

## Features
- **Technical Domain Selection**: Support for Java, Python, Data Structures & Algorithms (DSA), Object-Oriented Programming (OOP), and SQL.
- **Dynamic Question Generation**: Leverages LLMs to generate contextual technical questions of varying difficulty levels.
- **Candidate Evaluation**: Automatically grades answers using an LLM evaluator against rubrics and assigns a scoring system.
- **Interview Session Tracking**: Models stateful interviews allowing step-by-step progress.
- **Interview History & Reports**: Structures results to save detailed, persistent logs of candidate performance.

## Architecture
The project follows standard **Object-Oriented Programming (OOP)** and clean-architecture separation of concerns:

- `src/models/`: Encapsulates pure domain models and core states (e.g., `Candidate`, `Question`, `Interview`, `Result`).
- `src/services/`: Core logic layer (e.g., `QuestionGenerator` for prompting and model mapping, `Evaluator` for scoring, `LLMClient` to abstract the underlying LLM provider).
- `src/database/`: Persistence layer interfaces for storing and loading interview sessions.
- `src/utils/`: Generic helper functions and configuration utilities.
- `src/main/`: Core execution/cli entry points.

## Future Improvements
- **Interactive Web Interface**: A modern React or Vue frontend for candidates to take interviews.
- **Audio/Voice Response Analysis**: Allowing candidates to speak their answers, using Speech-to-Text and analyzing voice tone/confidence.
- **Code Execution Sandbox**: Executing candidate code (especially for Python/DSA/SQL) to verify correctness automatically alongside LLM conceptual feedback.
- **Advanced Dynamic Prompts**: Adapting difficulty on-the-fly based on candidate response quality (adaptive interview pathing).
- **Recruiter Dashboard**: An interface to search, filter, and review completed interview reports.
