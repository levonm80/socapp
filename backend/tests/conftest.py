"""Pytest fixtures for SOC application tests."""
import pytest
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import sys
import tempfile
import uuid
import requests

# Add backend directory to Python path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app
from extensions import db


@pytest.fixture
def app():
    """Create application for testing."""
    # Use in-memory SQLite for tests
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app(test_config={
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key',
        'OPENAI_API_KEY': 'test-openai-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def authenticated_client(app, sample_user_data):
    """Create test client with X-User-Id header simulating Kong authentication."""
    from models import User
    
    with app.app_context():
        # Create a test user
        user = User(email=sample_user_data['email'], password=sample_user_data['password'])
        db.session.add(user)
        db.session.commit()
        user_id = str(user.id)
    
    # Create client with X-User-Id header
    client = app.test_client()
    client.environ_base['HTTP_X_USER_ID'] = user_id
    return client


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        'email': 'test@example.com',
        'password': 'testpassword123'
    }


@pytest.fixture
def sample_log_file_data():
    """Sample log file data for testing."""
    return {
        'filename': 'test_log.log',
        'status': 'completed',
        'total_entries': 1000,
        'date_range_start': datetime(2022, 6, 20, 0, 0, 0),
        'date_range_end': datetime(2022, 6, 20, 23, 59, 59)
    }


@pytest.fixture
def sample_log_entry_data():
    """Sample log entry data for testing."""
    return {
        'timestamp': datetime(2022, 6, 20, 12, 0, 0),
        'location': 'ny-gre',
        'protocol': 'HTTPS',
        'url': 'https://example.com/path',
        'domain': 'example.com',
        'action': 'Allowed',
        'app_name': 'Example',
        'app_class': 'Business Apps',
        'throttle_req_size': 1000,
        'throttle_resp_size': 5000,
        'req_size': 500,
        'resp_size': 2000,
        'url_class': 'Business Use',
        'url_supercat': 'Business and Economy',
        'url_cat': 'Business',
        'dlp_dict': 'None',
        'dlp_eng': 'None',
        'dlp_hits': 0,
        'file_class': 'None',
        'file_type': 'None',
        'location2': 'ny-gre',
        'department': 'Engineering',
        'client_ip': '172.17.3.49',
        'server_ip': '66.211.175.229',
        'http_method': 'GET',
        'http_status': 200,
        'user_agent': 'Mozilla/5.0',
        'threat_category': 'None',
        'fw_filter': 'FwFilter',
        'fw_rule': 'Firewall_1',
        'policy_type': 'Other',
        'reason': 'None',
        'is_anomalous': False
    }


# ============================================================================
# Integration Test Fixtures (for testing against running backend)
# ============================================================================

@pytest.fixture(scope='session')
def api_base_url():
    """Get base URL for API from environment variable or default."""
    base_url = os.getenv('API_BASE_URL', 'http://localhost:5000')
    # Remove trailing slash if present
    return base_url.rstrip('/')


@pytest.fixture(scope='session')
def api_session(api_base_url):
    """Create a requests session with base URL configured."""
    session = requests.Session()
    session.base_url = api_base_url
    return session


@pytest.fixture(scope='function')
def authenticated_session(api_session, api_base_url):
    """Create an authenticated session with JWT token."""
    # Try to login with default test credentials
    # These should be created in the test database
    login_data = {
        'email': os.getenv('TEST_USER_EMAIL', 'test@example.com'),
        'password': os.getenv('TEST_USER_PASSWORD', 'testpassword123')
    }
    
    try:
        response = api_session.post(
            f'{api_base_url}/api/auth/login',
            json=login_data,
            timeout=5
        )
        if response.status_code == 200:
            token = response.json()['token']
            api_session.headers.update({'Authorization': f'Bearer {token}'})
            return api_session
        else:
            pytest.skip(f"Cannot authenticate: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        pytest.skip(f"Cannot connect to backend at {api_base_url}. Is the backend running?")
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Request failed: {str(e)}")

