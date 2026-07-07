import uuid

def generate_id(prefix: str = "ID") -> str:
    """Generates a unique string identifier with a given prefix."""
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"
