"""Integration tests for anomalies endpoints using requests."""
import pytest
import requests
import os


class TestAnomaliesEndpointsIntegration:
    """Integration tests for anomalies endpoints against running backend."""
    
    def test_should_list_anomalies_when_authenticated(
        self, authenticated_session, api_base_url
    ):
        # Arrange - using authenticated session
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/anomalies',
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'anomalies' in data
        assert 'total' in data
        assert isinstance(data['anomalies'], list)
        assert isinstance(data['total'], int)
        # Verify anomaly structure if anomalies exist
        if data['anomalies']:
            anomaly = data['anomalies'][0]
            assert 'entry_id' in anomaly
            assert 'log_entry' in anomaly
            assert 'anomaly_type' in anomaly
            assert 'reason' in anomaly
            assert 'confidence' in anomaly
    
    def test_should_list_anomalies_with_pagination_when_params_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange
        params = {
            'page': 1,
            'limit': 20
        }
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/anomalies',
            params=params,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data['anomalies']) <= 20
    
    def test_should_filter_anomalies_by_type_when_anomaly_type_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange
        params = {
            'anomaly_type': 'malicious_domain',
            'limit': 10
        }
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/anomalies',
            params=params,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        # Verify all returned anomalies match filter (if any anomalies exist)
        if data['anomalies']:
            for anomaly in data['anomalies']:
                assert anomaly.get('anomaly_type') == 'malicious_domain'
    
    def test_should_filter_anomalies_by_min_confidence_when_confidence_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange
        params = {
            'min_confidence': 0.7,
            'limit': 10
        }
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/anomalies',
            params=params,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        # Verify all returned anomalies meet confidence threshold (if any anomalies exist)
        if data['anomalies']:
            for anomaly in data['anomalies']:
                assert anomaly.get('confidence', 0) >= 0.7
    
    def test_should_filter_anomalies_by_log_file_when_file_id_provided(
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
        params = {
            'log_file_id': file_id,
            'limit': 10
        }
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/anomalies',
            params=params,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        # Verify all returned anomalies belong to the log file (if any anomalies exist)
        if data['anomalies']:
            for anomaly in data['anomalies']:
                log_entry = anomaly.get('log_entry', {})
                assert log_entry.get('log_file_id') == file_id
    
    def test_should_get_anomaly_timeline_when_authenticated(
        self, authenticated_session, api_base_url
    ):
        # Arrange - using authenticated session
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/anomalies/timeline',
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
            assert 'count' in bucket
            assert 'by_type' in bucket
            assert isinstance(bucket['by_type'], dict)
    
    def test_should_get_anomaly_timeline_with_custom_bucket_when_bucket_minutes_provided(
        self, authenticated_session, api_base_url
    ):
        # Arrange
        params = {
            'bucket_minutes': 60
        }
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/anomalies/timeline',
            params=params,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'buckets' in data
    
    def test_should_get_anomaly_timeline_with_log_file_filter_when_file_id_provided(
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
        params = {
            'log_file_id': file_id
        }
        
        # Act
        response = authenticated_session.get(
            f'{api_base_url}/api/anomalies/timeline',
            params=params,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'buckets' in data
    
    def test_should_reject_all_endpoints_when_not_authenticated(
        self, api_session, api_base_url
    ):
        # Arrange - no authentication
        
        endpoints = [
            '/api/anomalies',
            '/api/anomalies/timeline',
        ]
        
        for endpoint in endpoints:
            # Act
            response = api_session.get(f'{api_base_url}{endpoint}', timeout=5)
            
            # Assert
            assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"

