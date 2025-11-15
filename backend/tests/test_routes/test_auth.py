"""Tests for authentication routes."""
import pytest
from flask import json
from models import User
from extensions import db


class TestAuthRoutes:
    """Tests for authentication endpoints."""
    
    def test_should_login_when_valid_credentials(self, app, client, sample_user_data):
        # Arrange
        with app.app_context():
            user = User(email=sample_user_data['email'], password=sample_user_data['password'])
            db.session.add(user)
            db.session.commit()
        
        # Act
        response = client.post('/api/auth/login', json={
            'email': sample_user_data['email'],
            'password': sample_user_data['password']
        })
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
        assert 'user' in data
        assert data['user']['email'] == sample_user_data['email']
        assert 'id' in data['user']
    
    def test_should_reject_login_when_invalid_password(self, app, client, sample_user_data):
        # Arrange
        with app.app_context():
            user = User(email=sample_user_data['email'], password=sample_user_data['password'])
            db.session.add(user)
            db.session.commit()
        
        # Act
        response = client.post('/api/auth/login', json={
            'email': sample_user_data['email'],
            'password': 'wrongpassword'
        })
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data or 'message' in data
    
    def test_should_reject_login_when_user_not_found(self, app, client):
        # Arrange - no user created
        
        # Act
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'password'
        })
        
        # Assert
        assert response.status_code == 401
    
    def test_should_return_current_user_when_authenticated(self, app, client, sample_user_data):
        # Arrange
        from flask_jwt_extended import create_access_token
        
        with app.app_context():
            user = User(email=sample_user_data['email'], password=sample_user_data['password'])
            db.session.add(user)
            db.session.commit()
            user_id = str(user.id)
            token = create_access_token(identity=user_id)
        
        # Act - simulate Kong passing through the JWT token
        response = client.get('/api/auth/me', headers={
            'Authorization': f'Bearer {token}'
        })
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'user' in data
        assert data['user']['email'] == sample_user_data['email']
        assert data['user']['id'] == user_id
    
    def test_should_reject_me_when_not_authenticated(self, app, client):
        # Act
        response = client.get('/api/auth/me')
        
        # Assert
        assert response.status_code == 401
    
    def test_should_logout_when_authenticated(self, app, client, sample_user_data):
        # Arrange
        from flask_jwt_extended import create_access_token
        
        with app.app_context():
            user = User(email=sample_user_data['email'], password=sample_user_data['password'])
            db.session.add(user)
            db.session.commit()
            user_id = str(user.id)
            token = create_access_token(identity=user_id)
        
        # Act - simulate Kong passing through the JWT token
        response = client.post('/api/auth/logout', headers={
            'Authorization': f'Bearer {token}'
        })
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data

