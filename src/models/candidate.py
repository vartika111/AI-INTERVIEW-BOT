class Candidate:
    """Represents a candidate taking a technical interview."""
    
    def __init__(self, candidate_id: str, name: str, email: str, target_domain: str) -> None:
        self.candidate_id: str = candidate_id
        self.name: str = name
        self.email: str = email
        self.target_domain: str = target_domain  # e.g., 'Java', 'Python', 'DSA', 'OOP', 'SQL'

    def __repr__(self) -> str:
        return f"Candidate(id={self.candidate_id!r}, name={self.name!r}, domain={self.target_domain!r})"
