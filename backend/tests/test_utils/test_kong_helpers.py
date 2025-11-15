"""Tests for Kong helper utilities."""
import uuid
import pytest
from flask import Flask
from werkzeug.exceptions import Unauthorized
from flask_jwt_extended import create_access_token, JWTManager


def test_should_extract_user_id_when_valid_token():
    """Test that get_user_id_from_kong extracts user ID from JWT token."""
    # Arrange
    from utils.kong_helpers import get_user_id_from_kong
    
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    jwt = JWTManager(app)
    test_user_id = str(uuid.uuid4())
    
    with app.app_context():
        token = create_access_token(identity=test_user_id)
        
        with app.test_request_context(headers={'Authorization': f'Bearer {token}'}):
            # Act
            result = get_user_id_from_kong()
            
            # Assert
            assert result == uuid.UUID(test_user_id)
            assert isinstance(result, uuid.UUID)


def test_should_raise_401_when_header_missing():
    """Test that get_user_id_from_kong raises 401 when Authorization header is missing."""
    # Arrange
    from utils.kong_helpers import get_user_id_from_kong
    
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    
    with app.test_request_context():
        # Act & Assert
        with pytest.raises(Unauthorized) as exc_info:
            get_user_id_from_kong()
        
        assert exc_info.value.code == 401
        assert 'Missing or invalid Authorization' in str(exc_info.value.description)


def test_should_raise_401_when_token_invalid():
    """Test that get_user_id_from_kong raises 401 when token is invalid."""
    # Arrange
    from utils.kong_helpers import get_user_id_from_kong
    
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    jwt = JWTManager(app)
    
    with app.app_context():
        with app.test_request_context(headers={'Authorization': 'Bearer invalid-token'}):
            # Act & Assert
            with pytest.raises(Unauthorized) as exc_info:
                get_user_id_from_kong()
            
            assert exc_info.value.code == 401


def test_should_raise_401_when_bearer_missing():
    """Test that get_user_id_from_kong raises 401 when Bearer prefix is missing."""
    # Arrange
    from utils.kong_helpers import get_user_id_from_kong
    
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    
    with app.test_request_context(headers={'Authorization': 'some-token'}):
        # Act & Assert
        with pytest.raises(Unauthorized) as exc_info:
            get_user_id_from_kong()
        
        assert exc_info.value.code == 401
        assert 'Missing or invalid Authorization' in str(exc_info.value.description)

