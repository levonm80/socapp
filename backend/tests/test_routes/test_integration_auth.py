"""Integration tests for authentication endpoints using requests."""
import pytest
import requests
import os


class TestAuthEndpointsIntegration:
    """Integration tests for authentication endpoints against running backend."""
    
    def test_should_login_when_valid_credentials_provided(self, api_session, api_base_url):
        # Arrange
        email = os.getenv('TEST_USER_EMAIL', 'test@example.com')
        password = os.getenv('TEST_USER_PASSWORD', 'testpassword123')
        login_data = {
            'email': email,
            'password': password
        }
        
        # Act
        response = api_session.post(
            f'{api_base_url}/api/auth/login',
            json=login_data,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'token' in data
        assert 'user' in data
        assert data['user']['email'] == email
        assert 'id' in data['user']
        assert isinstance(data['token'], str)
        assert len(data['token']) > 0
    
    def test_should_reject_login_when_email_missing(self, api_session, api_base_url):
        # Arrange
        login_data = {
            'password': 'testpassword123'
        }
        
        # Act
        response = api_session.post(
            f'{api_base_url}/api/auth/login',
            json=login_data,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
    
    def test_should_reject_login_when_password_missing(self, api_session, api_base_url):
        # Arrange
        login_data = {
            'email': 'test@example.com'
        }
        
        # Act
        response = api_session.post(
            f'{api_base_url}/api/auth/login',
            json=login_data,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
    
    def test_should_reject_login_when_invalid_credentials(self, api_session, api_base_url):
        # Arrange
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        # Act
        response = api_session.post(
            f'{api_base_url}/api/auth/login',
            json=login_data,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 401
        data = response.json()
        assert 'error' in data
    
    def test_should_get_current_user_when_authenticated(self, authenticated_session, api_base_url):
        # Arrange - using authenticated session from fixture
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/auth/me',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'user' in data
        assert 'id' in data['user']
        assert 'email' in data['user']
        assert 'created_at' in data['user']
    
    def test_should_reject_me_when_not_authenticated(self, api_session, api_base_url):
        # Arrange - no auth token
        
        # Act
        response = api_session.get(
            f'{api_base_url}/api/auth/me',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 401
    
    def test_should_reject_me_when_invalid_token(self, api_session, api_base_url):
        # Arrange
        headers = {'Authorization': 'Bearer invalid_token_here'}
        
        # Act
        response = api_session.get(
            f'{api_base_url}/api/auth/me',
            headers=headers,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 422  # JWT decode error
    
    def test_should_logout_when_authenticated(self, authenticated_session, api_base_url):
        # Arrange - using authenticated session
        
        # Act
        response = authenticated_session.post(
            f'{api_base_url}/api/auth/logout',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
    
    def test_should_reject_logout_when_not_authenticated(self, api_session, api_base_url):
        # Arrange - no auth token
        
        # Act
        response = api_session.post(
            f'{api_base_url}/api/auth/logout',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 401

