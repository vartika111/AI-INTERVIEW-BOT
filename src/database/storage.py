from abc import ABC, abstractmethod
from typing import Dict, Optional
from ..models.interview import Interview
from ..models.candidate import Candidate

class Storage(ABC):
    """Abstract interface representing the interview persistence layer."""

    @abstractmethod
    def save_interview(self, interview: Interview) -> None:
        """Saves or updates an interview session."""
        pass

    @abstractmethod
    def get_interview(self, interview_id: str) -> Optional[Interview]:
        """Retrieves an interview session by its unique ID."""
        pass

    @abstractmethod
    def save_candidate(self, candidate: Candidate) -> None:
        """Saves or updates a candidate profile."""
        pass

    @abstractmethod
    def get_candidate(self, candidate_id: str) -> Optional[Candidate]:
        """Retrieves a candidate by their unique ID."""
        pass


class InMemoryStorage(Storage):
    """Simple in-memory dictionary-based storage for testing."""

    def __init__(self) -> None:
        self._interviews: Dict[str, Interview] = {}
        self._candidates: Dict[str, Candidate] = {}

    def save_interview(self, interview: Interview) -> None:
        self._interviews[interview.interview_id] = interview

    def get_interview(self, interview_id: str) -> Optional[Interview]:
        return self._interviews.get(interview_id)

    def save_candidate(self, candidate: Candidate) -> None:
        self._candidates[candidate.id] = candidate

    def get_candidate(self, candidate_id: str) -> Optional[Candidate]:
        return self._candidates.get(candidate_id)

