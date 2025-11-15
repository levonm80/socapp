"""Database bootstrap script."""
from models import User
from extensions import db


def bootstrap_test_user():
    """Create test user if it doesn't exist.
    
    Returns:
        bool: True if user was created, False if user already exists.
    """
    # Check if user already exists
    existing_user = User.query.filter_by(email='test@example.com').first()
    if existing_user:
        return False
    
    # Create test user
    user = User(email='test@example.com', password='testpassword123')
    db.session.add(user)
    db.session.commit()
    return True

