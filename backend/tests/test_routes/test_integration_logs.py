"""Integration tests for logs endpoints using requests."""
import pytest
import requests
import os
import uuid
from pathlib import Path


class TestLogsEndpointsIntegration:
    """Integration tests for logs endpoints against running backend."""
    
    @pytest.fixture
    def test_log_file_path(self):
        """Path to test log file."""
        test_data_dir = Path(__file__).parent.parent.parent.parent / 'test-data'
        log_file = test_data_dir / 'zscaler_nss_like.log'
        if not log_file.exists():
            # Try CSV version
            log_file = test_data_dir / 'zscaler_nss_like_logs.csv'
        return log_file
    
    def test_should_upload_log_file_when_valid_file_provided(
        self, authenticated_session, api_base_url, test_log_file_path
    ):
        # Arrange
        if not test_log_file_path.exists():
            pytest.skip(f"Test log file not found at {test_log_file_path}")
        
        # Act
        with open(test_log_file_path, 'rb') as f:
            files = {'file': (test_log_file_path.name, f, 'text/plain')}
            response = authenticated_session.post(
                f'{api_base_url}/api/logs/upload',
                files=files,
                timeout=60  # Upload may take time
            )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'log_file_id' in data
        assert 'status' in data
        # Verify UUID format
        try:
            uuid.UUID(data['log_file_id'])
        except ValueError:
            pytest.fail(f"Invalid UUID format: {data['log_file_id']}")
    
    def test_should_reject_upload_when_no_file_provided(self, authenticated_session, api_base_url):
        # Arrange - no file in request
        
        # Act
        response = authenticated_session.post(
            f'{api_base_url}/api/logs/upload',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
    
    def test_should_reject_upload_when_not_authenticated(self, api_session, api_base_url, test_log_file_path):
        # Arrange
        if not test_log_file_path.exists():
            pytest.skip(f"Test log file not found at {test_log_file_path}")
        
        # Act
        with open(test_log_file_path, 'rb') as f:
            files = {'file': (test_log_file_path.name, f, 'text/plain')}
            response = api_session.post(
                f'{api_base_url}/api/logs/upload',
                files=files,
                timeout=10
            )
        
        # Assert
        assert response.status_code == 401
    
    def test_should_list_log_files_when_authenticated(self, authenticated_session, api_base_url):
        # Arrange - using authenticated session
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/logs/files',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'files' in data
        assert 'total' in data
        assert 'page' in data
        assert 'limit' in data
        assert isinstance(data['files'], list)
        assert isinstance(data['total'], int)
        assert isinstance(data['page'], int)
        assert isinstance(data['limit'], int)
    
    def test_should_list_log_files_with_pagination_when_page_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange
        params = {'page': 1, 'limit': 10}
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/logs/files',
            params=params,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['page'] == 1
        assert data['limit'] == 10
    
    def test_should_get_log_file_details_when_valid_id_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange - first get list of files to get a valid ID
        list_response = authenticated_session.get(
            f'{api_base_url}/api/logs/files',
            timeout=10
        )
        if list_response.status_code != 200:
            pytest.skip("Cannot get list of files")
        
        files = list_response.json().get('files', [])
        if not files:
            pytest.skip("No log files available for testing")
        
        file_id = files[0]['id']
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/logs/files/{file_id}',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'id' in data
        assert 'filename' in data
        assert 'status' in data
        assert data['id'] == file_id
    
    def test_should_reject_get_log_file_when_invalid_id(self, authenticated_session, api_base_url):
        # Arrange
        invalid_id = 'not-a-valid-uuid'
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/logs/files/{invalid_id}',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
    
    def test_should_get_log_file_preview_when_valid_id_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange - get a valid file ID
        list_response = authenticated_session.get(
            f'{api_base_url}/api/logs/files',
            timeout=10
        )
        if list_response.status_code != 200:
            pytest.skip("Cannot get list of files")
        
        files = list_response.json().get('files', [])
        if not files:
            pytest.skip("No log files available for testing")
        
        file_id = files[0]['id']
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/logs/files/{file_id}/preview',
            params={'lines': 10},
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'preview' in data
        assert isinstance(data['preview'], list)
    
    def test_should_list_log_entries_when_authenticated(self, authenticated_session, api_base_url):
        # Arrange - using authenticated session
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/logs/entries',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'entries' in data
        assert 'total' in data
        assert 'page' in data
        assert 'limit' in data
        assert isinstance(data['entries'], list)
    
    def test_should_filter_log_entries_when_filters_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange
        params = {
            'action': 'Blocked',
            'page': 1,
            'limit': 10
        }
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/logs/entries',
            params=params,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'entries' in data
        # Verify all returned entries match filter (if any entries exist)
        if data['entries']:
            for entry in data['entries']:
                assert entry.get('action') == 'Blocked'
    
    def test_should_get_log_entry_when_valid_id_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange - get a valid entry ID
        list_response = authenticated_session.get(
            f'{api_base_url}/api/logs/entries',
            params={'limit': 1},
            timeout=10
        )
        if list_response.status_code != 200:
            pytest.skip("Cannot get list of entries")
        
        entries = list_response.json().get('entries', [])
        if not entries:
            pytest.skip("No log entries available for testing")
        
        entry_id = entries[0]['id']
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/logs/entries/{entry_id}',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'id' in data
        assert 'timestamp' in data
        assert 'url' in data
        assert data['id'] == entry_id
    
    def test_should_reject_get_log_entry_when_invalid_id(
        self, authenticated_session, api_base_url
    ):
        # Arrange
        invalid_id = 'not-a-valid-uuid'
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/logs/entries/{invalid_id}',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
    
    def test_should_reject_all_endpoints_when_not_authenticated(self, api_session, api_base_url):
        # Arrange - no authentication
        
        endpoints = [
            ('GET', '/api/logs/files'),
            ('GET', '/api/logs/files/invalid-id'),
            ('GET', '/api/logs/entries'),
            ('GET', '/api/logs/entries/invalid-id'),
        ]
        
        for method, endpoint in endpoints:
            # Act
            if method == 'GET':
                response = api_session.get(f'{api_base_url}{endpoint}', timeout=5)
            else:
                response = api_session.post(f'{api_base_url}{endpoint}', timeout=5)
            
            # Assert
            assert response.status_code == 401, f"Endpoint {method} {endpoint} should require authentication"

