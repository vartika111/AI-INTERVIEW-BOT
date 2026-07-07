import json
import re
from typing import List, Dict, Any
from ..models.interview import Interview
from ..models.question import Question
from ..models.result import Result
from .llm_client import LLMClient

class Evaluator:
    """Service responsible for evaluating candidate answers and generating interview results."""

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client: LLMClient = llm_client

    def evaluate(self, question: Question, answer: str) -> Result:
        """
        Evaluates a single question and answer using the LLMClient.
        Parses the JSON response safely and returns a Result object.
        """
        # Ensure answer is not empty
        if not answer.strip():
            return Result(
                score=0.0,
                feedback="No answer provided.",
                strengths=[],
                weaknesses=["Candidate did not answer the question."]
            )

        try:
            raw_response = self.llm_client.evaluate_answer(question, answer)
        except Exception as e:
            # Handle client/API errors gracefully
            return Result(
                score=0.0,
                feedback=f"Failed to query LLM Client for evaluation: {str(e)}",
                strengths=[],
                weaknesses=["N/A due to LLM client error"]
            )

        # Parse JSON response safely
        parsed = self._parse_llm_json(raw_response)
        
        # Extract fields with safe defaults
        score = parsed.get("score")
        try:
            score_val = float(score) if score is not None else 0.0
            # Guard bounds
            score_val = max(0.0, min(10.0, score_val))
        except (ValueError, TypeError):
            score_val = 0.0

        correctness = parsed.get("correctness", "Unable to determine correctness.")
        explanation = parsed.get("explanation", "No explanation provided.")
        feedback = f"Correctness: {correctness}\nExplanation: {explanation}"

        strengths = parsed.get("strengths")
        if not isinstance(strengths, list):
            strengths = [str(strengths)] if strengths is not None else []
        else:
            strengths = [str(s).strip() for s in strengths if str(s).strip()]

        improvements = parsed.get("improvements")
        if not isinstance(improvements, list):
            improvements = [str(improvements)] if improvements is not None else []
        else:
            improvements = [str(imp).strip() for imp in improvements if str(imp).strip()]

        return Result(
            score=score_val,
            feedback=feedback,
            strengths=strengths,
            weaknesses=improvements
        )

    def _parse_llm_json(self, text: str) -> Dict[str, Any]:
        """Safely parses JSON from text, extracting the JSON block if wrapped in markdown or extra text."""
        if not text:
            return {}
        
        trimmed = text.strip()
        # Check if it starts/ends with markdown code blocks
        if trimmed.startswith("```"):
            lines = trimmed.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            trimmed = "\n".join(lines).strip()

        # Try parsing directly
        try:
            return json.loads(trimmed)
        except json.JSONDecodeError:
            pass

        # Try locating the first '{' and last '}'
        start_idx = trimmed.find("{")
        end_idx = trimmed.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = trimmed[start_idx:end_idx+1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # Fallback parsing for unstructured output (e.g. if the LLM output is key-value pairs)
        fallback = {}
        
        # Try extracting score
        score_match = re.search(r'(?:score|Score)\b.*?\b(\d+(?:\.\d+)?)', trimmed)
        if score_match:
            try:
                fallback["score"] = float(score_match.group(1))
            except ValueError:
                pass

        # Try extracting strengths/improvements as lists if they are formatted with list items
        strengths_match = re.search(r'(?:strengths|Strengths)\s*:(.*?)(?:improvements|Improvements|weaknesses|Weaknesses|$)', trimmed, re.DOTALL | re.IGNORECASE)
        if strengths_match:
            items = re.findall(r'[-*•]\s*(.+)', strengths_match.group(1))
            if items:
                fallback["strengths"] = [item.strip() for item in items]
            else:
                fallback["strengths"] = [strengths_match.group(1).strip()]

        improvements_match = re.search(r'(?:improvements|Improvements|weaknesses|Weaknesses)\s*:(.*)', trimmed, re.DOTALL | re.IGNORECASE)
        if improvements_match:
            items = re.findall(r'[-*•]\s*(.+)', improvements_match.group(1))
            if items:
                fallback["improvements"] = [item.strip() for item in items]
            else:
                fallback["improvements"] = [improvements_match.group(1).strip()]

        # For explanation and correctness, fall back to the raw text if parsing failed completely
        if not fallback:
            fallback["explanation"] = trimmed
            fallback["correctness"] = "Parsed from unstructured text."
            
        return fallback

    def evaluate_interview(self, interview: Interview) -> Result:
        """
        Evaluates all candidate answers in the interview.
        Returns a structured Result model with overall score and feedback.
        """
        detailed_evaluations: List[Dict[str, Any]] = []
        total_score = 0.0
        all_strengths = []
        all_weaknesses = []

        for question in interview.questions:
            answer = interview.answers.get(question.id, "")
            
            q_result = self.evaluate(question, answer)
            total_score += q_result.score
            
            detailed_evaluations.append({
                "question_id": question.id,
                "score": q_result.score,
                "feedback": q_result.feedback,
                "strengths": q_result.strengths,
                "weaknesses": q_result.weaknesses
            })
            
            all_strengths.extend(q_result.strengths)
            all_weaknesses.extend(q_result.weaknesses)

        num_questions = len(interview.questions)
        average_score = (total_score / num_questions) if num_questions > 0 else 0.0

        # De-duplicate strengths and weaknesses
        unique_strengths = list(dict.fromkeys(all_strengths))
        unique_weaknesses = list(dict.fromkeys(all_weaknesses))

        # Build comprehensive overall feedback
        if average_score >= 8.0:
            overall_feedback = "Good performance across technical areas."
        elif average_score >= 5.0:
            overall_feedback = "Good performance, but with some areas for improvement."
        else:
            overall_feedback = "Performance was below expectations. Significant review is recommended."

        return Result(
            score=average_score,
            feedback=overall_feedback,
            strengths=unique_strengths if unique_strengths else ["No key strengths identified."],
            weaknesses=unique_weaknesses if unique_weaknesses else ["No key areas for improvement identified."],
            interview_id=interview.interview_id,
            detailed_evaluations=detailed_evaluations
        )
