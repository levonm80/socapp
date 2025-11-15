"""Security utilities."""
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """Hash a password."""
    return generate_password_hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """Verify a password against its hash."""
    return check_password_hash(password_hash, password)

