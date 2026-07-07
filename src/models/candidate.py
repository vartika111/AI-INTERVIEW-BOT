from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .interview import Interview

class Candidate:
    """Represents a candidate taking a technical interview, managing profile details and history."""

    def __init__(self, id: str, name: str, email: str) -> None:
        self._id: str = id
        self._name: str = name
        self._email: str = email
        self._selected_skills: List[str] = []
        self._interview_history: List['Interview'] = []

    # Getters and Setters (Encapsulation)
    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value.strip():
            raise ValueError("Name cannot be empty")
        self._name = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if "@" not in value:
            raise ValueError("Invalid email format")
        self._email = value

    @property
    def selected_skills(self) -> List[str]:
        return self._selected_skills

    @property
    def selectedSkills(self) -> List[str]:
        """CamelCase alias for selected_skills compatibility."""
        return self._selected_skills

    @property
    def interview_history(self) -> List['Interview']:
        return self._interview_history

    @property
    def interviewHistory(self) -> List['Interview']:
        """CamelCase alias for interview_history compatibility."""
        return self._interview_history

    # Core Methods
    def add_skill(self, skill: str) -> None:
        """Adds a technical skill to the candidate's selected skills if not present."""
        clean_skill = skill.strip()
        if not clean_skill:
            raise ValueError("Skill name cannot be empty")
        if clean_skill not in self._selected_skills:
            self._selected_skills.append(clean_skill)

    def addSkill(self, skill: str) -> None:
        """CamelCase alias for add_skill."""
        self.add_skill(skill)

    def update_profile(self, name: str, email: str) -> None:
        """Updates the candidate's core profile information with validation."""
        self.name = name
        self.email = email

    def updateProfile(self, name: str, email: str) -> None:
        """CamelCase alias for update_profile."""
        self.update_profile(name, email)

    def __repr__(self) -> str:
        return f"Candidate(id={self._id!r}, name={self._name!r}, email={self._email!r})"
