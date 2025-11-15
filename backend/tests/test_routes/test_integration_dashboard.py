"""Integration tests for dashboard endpoints using requests."""
import pytest
import requests
import os


class TestDashboardEndpointsIntegration:
    """Integration tests for dashboard endpoints against running backend."""
    
    def test_should_get_stats_when_authenticated(self, authenticated_session, api_base_url):
        # Arrange - using authenticated session
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/dashboard/stats',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'total_requests' in data
        assert 'blocked_events' in data
        assert 'malicious_urls' in data
        assert 'high_risk_users' in data
        assert 'data_transfer_bytes' in data
        assert 'trends' in data
        assert isinstance(data['total_requests'], int)
        assert isinstance(data['blocked_events'], int)
        assert isinstance(data['malicious_urls'], int)
        assert isinstance(data['high_risk_users'], int)
        assert isinstance(data['data_transfer_bytes'], (int, type(None)))
    
    def test_should_get_stats_with_log_file_filter_when_file_id_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange - get a valid file ID first
        files_response = authenticated_session.get(
            f'{api_base_url}/api/logs/files',
            timeout=10
        )
        if files_response.status_code != 200:
            pytest.skip("Cannot get list of files")
        
        files = files_response.json().get('files', [])
        if not files:
            pytest.skip("No log files available for testing")
        
        file_id = files[0]['id']
        params = {'log_file_id': file_id}
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/dashboard/stats',
            params=params,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'total_requests' in data
    
    def test_should_get_timeline_when_authenticated(self, authenticated_session, api_base_url):
        # Arrange - using authenticated session
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/dashboard/timeline',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'buckets' in data
        assert isinstance(data['buckets'], list)
        # Verify bucket structure if buckets exist
        if data['buckets']:
            bucket = data['buckets'][0]
            assert 'time' in bucket
            assert 'total' in bucket
            assert 'blocked' in bucket
    
    def test_should_get_timeline_with_custom_params_when_params_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange
        params = {
            'bucket_minutes': 30,
            'hours': 48
        }
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/dashboard/timeline',
            params=params,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'buckets' in data
    
    def test_should_get_timeline_with_data_when_log_file_id_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange - get a valid file ID first
        files_response = authenticated_session.get(
            f'{api_base_url}/api/logs/files',
            timeout=10
        )
        if files_response.status_code != 200:
            pytest.skip("Cannot get list of files")
        
        files = files_response.json().get('files', [])
        if not files:
            pytest.skip("No log files available for testing")
        
        file_id = files[0]['id']
        params = {'log_file_id': file_id}
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/dashboard/timeline',
            params=params,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'buckets' in data
        assert isinstance(data['buckets'], list)
        # If log file has entries, timeline should have buckets
        # (We can't guarantee entries exist, but if they do, buckets should be returned)
        if data['buckets']:
            bucket = data['buckets'][0]
            assert 'time' in bucket
            assert 'total' in bucket
            assert 'blocked' in bucket
            assert bucket['total'] > 0
    
    def test_should_get_timeline_with_all_data_when_no_log_file_id_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange - no log_file_id, should return all available data
        # First check if there are any log files
        files_response = authenticated_session.get(
            f'{api_base_url}/api/logs/files',
            timeout=10
        )
        if files_response.status_code != 200:
            pytest.skip("Cannot get list of files")
        
        files = files_response.json().get('files', [])
        if not files:
            pytest.skip("No log files available for testing")
        
        # Act - get timeline without log_file_id
        response = authenticated_session.get(
            f'{api_base_url}/api/dashboard/timeline',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'buckets' in data
        assert isinstance(data['buckets'], list)
        # If there are log entries in the database, timeline should have buckets
        # (The endpoint should not filter by current time when no log_file_id is provided)
    
    def test_should_get_top_categories_when_authenticated(
        self, authenticated_session, api_base_url
    ):
        # Arrange - using authenticated session
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/dashboard/top-categories',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'categories' in data
        assert isinstance(data['categories'], list)
        # Verify category structure if categories exist
        if data['categories']:
            category = data['categories'][0]
            assert 'name' in category
            assert 'count' in category
            assert 'percentage' in category
    
    def test_should_get_top_categories_with_limit_when_limit_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange
        params = {'limit': 5}
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/dashboard/top-categories',
            params=params,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data['categories']) <= 5
    
    def test_should_get_top_domains_when_authenticated(
        self, authenticated_session, api_base_url
    ):
        # Arrange - using authenticated session
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/dashboard/top-domains',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'domains' in data
        assert isinstance(data['domains'], list)
        # Verify domain structure if domains exist
        if data['domains']:
            domain = data['domains'][0]
            assert 'domain' in domain
            assert 'count' in domain
            assert 'blocked_count' in domain
    
    def test_should_get_top_domains_with_limit_when_limit_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange
        params = {'limit': 20}
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/dashboard/top-domains',
            params=params,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data['domains']) <= 20
    
    def test_should_get_top_users_when_authenticated(
        self, authenticated_session, api_base_url
    ):
        # Arrange - using authenticated session
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/dashboard/top-users',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'users' in data
        assert isinstance(data['users'], list)
        # Verify user structure if users exist
        if data['users']:
            user = data['users'][0]
            assert 'identifier' in user
            assert 'request_count' in user
            assert 'risk_score' in user
    
    def test_should_get_top_users_with_limit_when_limit_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange
        params = {'limit': 15}
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/dashboard/top-users',
            params=params,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data['users']) <= 15
    
    def test_should_get_recent_logs_when_authenticated(
        self, authenticated_session, api_base_url
    ):
        # Arrange - using authenticated session
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/dashboard/recent-logs',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'entries' in data
        assert isinstance(data['entries'], list)
        # Verify entry structure if entries exist
        if data['entries']:
            entry = data['entries'][0]
            assert 'id' in entry
            assert 'timestamp' in entry
            assert 'url' in entry
    
    def test_should_get_recent_logs_with_limit_when_limit_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange
        params = {'limit': 5}
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/dashboard/recent-logs',
            params=params,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data['entries']) <= 5
    
    def test_should_reject_all_endpoints_when_not_authenticated(self, api_session, api_base_url):
        # Arrange - no authentication
        
        endpoints = [
            '/api/dashboard/stats',
            '/api/dashboard/timeline',
            '/api/dashboard/top-categories',
            '/api/dashboard/top-domains',
            '/api/dashboard/top-users',
            '/api/dashboard/recent-logs',
        ]
        
        for endpoint in endpoints:
            # Act
            response = api_session.get(f'{api_base_url}{endpoint}', timeout=5)
            
            # Assert
            assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"

