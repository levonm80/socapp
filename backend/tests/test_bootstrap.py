"""Tests for database bootstrap script."""
import pytest
from models import User
from extensions import db
from scripts.bootstrap import bootstrap_test_user


class TestBootstrapTestUser:
    """Tests for bootstrap_test_user function."""
    
    def test_should_create_test_user_when_user_does_not_exist(self, app):
        # Arrange
        with app.app_context():
            # Ensure user doesn't exist
            existing_user = User.query.filter_by(email='test@example.com').first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()
            
            # Act
            result = bootstrap_test_user()
            
            # Assert
            assert result is True
            user = User.query.filter_by(email='test@example.com').first()
            assert user is not None
            assert user.email == 'test@example.com'
            assert user.check_password('testpassword123')
    
    def test_should_not_create_duplicate_user_when_user_already_exists(self, app):
        # Arrange
        with app.app_context():
            # Create user first
            existing_user = User(email='test@example.com', password='testpassword123')
            db.session.add(existing_user)
            db.session.commit()
            user_id = existing_user.id
            
            # Act
            result = bootstrap_test_user()
            
            # Assert
            assert result is False
            # Verify user still exists and wasn't recreated
            user = User.query.filter_by(email='test@example.com').first()
            assert user is not None
            assert user.id == user_id  # Same user, not a new one
    
    def test_should_handle_database_error_gracefully(self, app, mocker):
        # Arrange
        with app.app_context():
            # Mock db.session.commit to raise an exception
            mocker.patch('extensions.db.session.commit', side_effect=Exception('Database error'))
            
            # Act & Assert
            with pytest.raises(Exception):
                bootstrap_test_user()

