"""Tests for health check route."""
import pytest
from flask import json


class TestHealthRoute:
    """Tests for health check endpoint."""
    
    def test_should_return_healthy_status_when_service_is_running(self, app, client):
        # Arrange - no setup needed, health check should always work
        
        # Act
        response = client.get('/api/health')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert 'service' in data
    
    def test_should_not_require_authentication(self, app, client):
        # Arrange - no authentication headers
        
        # Act
        response = client.get('/api/health')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_should_respond_to_get_method(self, app, client):
        # Arrange
        
        # Act
        response = client.get('/api/health')
        
        # Assert
        assert response.status_code == 200
    
    def test_should_return_json_content_type(self, app, client):
        # Arrange
        
        # Act
        response = client.get('/api/health')
        
        # Assert
        assert response.status_code == 200
        assert response.content_type == 'application/json'

