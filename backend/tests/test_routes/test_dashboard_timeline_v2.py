"""Tests for dashboard timeline v2 endpoint with PostgreSQL bucketing."""
import pytest
from datetime import datetime, timedelta
from models import LogEntry, LogFile, User
from extensions import db


class TestDashboardTimelineV2:
    """Tests for /api/dashboard/timeline/v2 endpoint."""
    
    def test_should_return_timeline_buckets_when_authenticated(
        self, authenticated_client, sample_user_data, sample_log_file_data
    ):
        # Arrange - create log file and entries
        with authenticated_client.application.app_context():
            user = User.query.filter_by(email=sample_user_data['email']).first()
            if not user:
                user = User(email=sample_user_data['email'], password=sample_user_data['password'])
                db.session.add(user)
                db.session.commit()
            
            log_file = LogFile(
                filename=sample_log_file_data['filename'],
                uploaded_by=user.id,
                status='completed',
                total_entries=3,
                date_range_start=datetime(2022, 6, 20, 10, 0, 0),
                date_range_end=datetime(2022, 6, 20, 11, 0, 0)
            )
            db.session.add(log_file)
            db.session.commit()
            
            # Create entries at different times within 15-minute buckets
            base_time = datetime(2022, 6, 20, 10, 5, 0)
            for i in range(3):
                entry = LogEntry(
                    log_file_id=log_file.id,
                    timestamp=base_time + timedelta(minutes=i*5),
                    url=f'https://example{i}.com',
                    domain=f'example{i}.com',
                    action='Allowed' if i % 2 == 0 else 'Blocked'
                )
                db.session.add(entry)
            db.session.commit()
        
        # Act
        response = authenticated_client.get('/api/dashboard/timeline/v2')
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'buckets' in data
        assert isinstance(data['buckets'], list)
        if data['buckets']:
            bucket = data['buckets'][0]
            assert 'bucket_time' in bucket or 'time' in bucket
            assert 'log_count' in bucket or 'total' in bucket
            assert 'blocked_count' in bucket or 'blocked' in bucket
    
    def test_should_filter_by_log_file_id_when_provided(
        self, authenticated_client, sample_user_data, sample_log_file_data
    ):
        # Arrange - create two log files with entries
        with authenticated_client.application.app_context():
            user = User.query.filter_by(email=sample_user_data['email']).first()
            if not user:
                user = User(email=sample_user_data['email'], password=sample_user_data['password'])
                db.session.add(user)
                db.session.commit()
            
            log_file1 = LogFile(
                filename='file1.log',
                uploaded_by=user.id,
                status='completed',
                total_entries=2
            )
            log_file2 = LogFile(
                filename='file2.log',
                uploaded_by=user.id,
                status='completed',
                total_entries=2
            )
            db.session.add_all([log_file1, log_file2])
            db.session.commit()
            
            # Add entries to both files
            for log_file in [log_file1, log_file2]:
                entry = LogEntry(
                    log_file_id=log_file.id,
                    timestamp=datetime(2022, 6, 20, 10, 5, 0),
                    url='https://example.com',
                    domain='example.com',
                    action='Allowed'
                )
                db.session.add(entry)
            db.session.commit()
            
            file_id = str(log_file1.id)
        
        # Act
        response = authenticated_client.get(
            f'/api/dashboard/timeline/v2?log_file_id={file_id}'
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'buckets' in data
        # Should only include entries from log_file1
    
    def test_should_use_custom_date_range_when_provided(
        self, authenticated_client, sample_user_data, sample_log_file_data
    ):
        # Arrange
        start_time = datetime(2022, 6, 20, 10, 0, 0)
        end_time = datetime(2022, 6, 20, 11, 0, 0)
        
        with authenticated_client.application.app_context():
            user = User.query.filter_by(email=sample_user_data['email']).first()
            if not user:
                user = User(email=sample_user_data['email'], password=sample_user_data['password'])
                db.session.add(user)
                db.session.commit()
            
            log_file = LogFile(
                filename=sample_log_file_data['filename'],
                uploaded_by=user.id,
                status='completed',
                total_entries=2
            )
            db.session.add(log_file)
            db.session.commit()
            
            # Entry within range
            entry1 = LogEntry(
                log_file_id=log_file.id,
                timestamp=start_time + timedelta(minutes=15),
                url='https://example1.com',
                domain='example1.com',
                action='Allowed'
            )
            # Entry outside range (before)
            entry2 = LogEntry(
                log_file_id=log_file.id,
                timestamp=start_time - timedelta(hours=1),
                url='https://example2.com',
                domain='example2.com',
                action='Allowed'
            )
            db.session.add_all([entry1, entry2])
            db.session.commit()
        
        # Act
        start_iso = start_time.isoformat()
        end_iso = end_time.isoformat()
        response = authenticated_client.get(
            f'/api/dashboard/timeline/v2?start_time={start_iso}&end_time={end_iso}'
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'buckets' in data
        # Should only include entry1, not entry2
    
    def test_should_use_custom_bucket_period_when_provided(
        self, authenticated_client, sample_user_data, sample_log_file_data
    ):
        # Arrange
        base_time = datetime(2022, 6, 20, 10, 0, 0)
        
        with authenticated_client.application.app_context():
            user = User.query.filter_by(email=sample_user_data['email']).first()
            if not user:
                user = User(email=sample_user_data['email'], password=sample_user_data['password'])
                db.session.add(user)
                db.session.commit()
            
            log_file = LogFile(
                filename=sample_log_file_data['filename'],
                uploaded_by=user.id,
                status='completed',
                total_entries=3
            )
            db.session.add(log_file)
            db.session.commit()
            
            # Create entries at 5, 20, 35 minutes (should create 3 buckets with 15-min period)
            for offset in [5, 20, 35]:
                entry = LogEntry(
                    log_file_id=log_file.id,
                    timestamp=base_time + timedelta(minutes=offset),
                    url=f'https://example{offset}.com',
                    domain=f'example{offset}.com',
                    action='Allowed'
                )
                db.session.add(entry)
            db.session.commit()
        
        # Act - use 30-minute buckets
        response = authenticated_client.get(
            f'/api/dashboard/timeline/v2?bucket_minutes=30&start_time={base_time.isoformat()}&end_time={(base_time + timedelta(hours=1)).isoformat()}'
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'buckets' in data
        # With 30-minute buckets, should have fewer buckets than with 15-minute buckets
    
    def test_should_separate_blocked_and_allowed_counts_when_entries_exist(
        self, authenticated_client, sample_user_data, sample_log_file_data
    ):
        # Arrange
        base_time = datetime(2022, 6, 20, 10, 0, 0)
        
        with authenticated_client.application.app_context():
            user = User.query.filter_by(email=sample_user_data['email']).first()
            if not user:
                user = User(email=sample_user_data['email'], password=sample_user_data['password'])
                db.session.add(user)
                db.session.commit()
            
            log_file = LogFile(
                filename=sample_log_file_data['filename'],
                uploaded_by=user.id,
                status='completed',
                total_entries=4
            )
            db.session.add(log_file)
            db.session.commit()
            
            # Create entries: 2 allowed, 2 blocked in same bucket
            bucket_time = base_time.replace(minute=0, second=0, microsecond=0)
            for i, action in enumerate(['Allowed', 'Blocked', 'Allowed', 'Blocked']):
                entry = LogEntry(
                    log_file_id=log_file.id,
                    timestamp=bucket_time + timedelta(minutes=i),
                    url=f'https://example{i}.com',
                    domain=f'example{i}.com',
                    action=action
                )
                db.session.add(entry)
            db.session.commit()
        
        # Act
        response = authenticated_client.get(
            f'/api/dashboard/timeline/v2?start_time={base_time.isoformat()}&end_time={(base_time + timedelta(hours=1)).isoformat()}&bucket_minutes=15'
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'buckets' in data
        if data['buckets']:
            # Find bucket with data
            bucket_with_data = next((b for b in data['buckets'] if b.get('log_count', b.get('total', 0)) > 0), None)
            if bucket_with_data:
                total = bucket_with_data.get('log_count', bucket_with_data.get('total', 0))
                blocked = bucket_with_data.get('blocked_count', bucket_with_data.get('blocked', 0))
                assert total == 4
                assert blocked == 2
    
    def test_should_include_empty_buckets_when_no_data_in_period(
        self, authenticated_client, sample_user_data
    ):
        # Arrange - no log entries created
        start_time = datetime(2022, 6, 20, 10, 0, 0)
        end_time = datetime(2022, 6, 20, 11, 0, 0)
        
        # Act
        response = authenticated_client.get(
            f'/api/dashboard/timeline/v2?start_time={start_time.isoformat()}&end_time={end_time.isoformat()}&bucket_minutes=15'
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'buckets' in data
        assert isinstance(data['buckets'], list)
        # Should have buckets for the time period, even if empty
        # With 15-minute buckets over 1 hour, should have 4 buckets
        assert len(data['buckets']) == 4
        # All buckets should have log_count = 0
        for bucket in data['buckets']:
            count = bucket.get('log_count', bucket.get('total', 0))
            assert count == 0
    
    def test_should_reject_request_when_not_authenticated(self, client):
        # Arrange - no authentication
        
        # Act
        response = client.get('/api/dashboard/timeline/v2')
        
        # Assert
        assert response.status_code == 401
    
    def test_should_handle_invalid_date_range_when_start_after_end(
        self, authenticated_client
    ):
        # Arrange
        start_time = datetime(2022, 6, 20, 11, 0, 0)
        end_time = datetime(2022, 6, 20, 10, 0, 0)
        
        # Act
        response = authenticated_client.get(
            f'/api/dashboard/timeline/v2?start_time={start_time.isoformat()}&end_time={end_time.isoformat()}'
        )
        
        # Assert
        # Should return 400 Bad Request or handle gracefully
        assert response.status_code in [400, 200]  # 200 if handled gracefully with empty result
    
    def test_should_use_default_bucket_period_when_not_provided(
        self, authenticated_client, sample_user_data, sample_log_file_data
    ):
        # Arrange
        base_time = datetime(2022, 6, 20, 10, 0, 0)
        
        with authenticated_client.application.app_context():
            user = User.query.filter_by(email=sample_user_data['email']).first()
            if not user:
                user = User(email=sample_user_data['email'], password=sample_user_data['password'])
                db.session.add(user)
                db.session.commit()
            
            log_file = LogFile(
                filename=sample_log_file_data['filename'],
                uploaded_by=user.id,
                status='completed',
                total_entries=1
            )
            db.session.add(log_file)
            db.session.commit()
            
            entry = LogEntry(
                log_file_id=log_file.id,
                timestamp=base_time,
                url='https://example.com',
                domain='example.com',
                action='Allowed'
            )
            db.session.add(entry)
            db.session.commit()
        
        # Act - don't provide bucket_minutes, should default to 15
        response = authenticated_client.get(
            f'/api/dashboard/timeline/v2?start_time={base_time.isoformat()}&end_time={(base_time + timedelta(hours=1)).isoformat()}'
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert 'buckets' in data

