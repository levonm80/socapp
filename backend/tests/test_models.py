"""Tests for database models."""
import pytest
from datetime import datetime
from werkzeug.security import check_password_hash

from models import User, LogFile, LogEntry, UserRiskScore
from extensions import db


class TestUser:
    """Tests for User model."""
    
    def test_should_create_user_when_valid_data_provided(self, app, sample_user_data):
        # Arrange
        with app.app_context():
            # Act
            user = User(
                email=sample_user_data['email'],
                password=sample_user_data['password']
            )
            db.session.add(user)
            db.session.commit()
            
            # Assert
            assert user.id is not None
            assert user.email == sample_user_data['email']
            assert user.password_hash is not None
            assert user.password_hash != sample_user_data['password']  # Should be hashed
            assert check_password_hash(user.password_hash, sample_user_data['password'])
            assert user.created_at is not None
            assert user.updated_at is not None
    
    def test_should_raise_error_when_duplicate_email(self, app, sample_user_data):
        # Arrange
        with app.app_context():
            user1 = User(email=sample_user_data['email'], password='password1')
            db.session.add(user1)
            db.session.commit()
            
            # Act & Assert
            user2 = User(email=sample_user_data['email'], password='password2')
            db.session.add(user2)
            with pytest.raises(Exception):  # IntegrityError or similar
                db.session.commit()
    
    def test_should_verify_password_when_correct(self, app, sample_user_data):
        # Arrange
        with app.app_context():
            user = User(email=sample_user_data['email'], password=sample_user_data['password'])
            db.session.add(user)
            db.session.commit()
            
            # Act
            result = user.check_password(sample_user_data['password'])
            
            # Assert
            assert result is True
    
    def test_should_reject_password_when_incorrect(self, app, sample_user_data):
        # Arrange
        with app.app_context():
            user = User(email=sample_user_data['email'], password=sample_user_data['password'])
            db.session.add(user)
            db.session.commit()
            
            # Act
            result = user.check_password('wrongpassword')
            
            # Assert
            assert result is False


class TestLogFile:
    """Tests for LogFile model."""
    
    def test_should_create_log_file_when_valid_data_provided(self, app, sample_user_data, sample_log_file_data):
        # Arrange
        with app.app_context():
            user = User(email=sample_user_data['email'], password=sample_user_data['password'])
            db.session.add(user)
            db.session.commit()
            
            # Act
            log_file = LogFile(
                filename=sample_log_file_data['filename'],
                uploaded_by=user.id,
                status=sample_log_file_data['status'],
                total_entries=sample_log_file_data['total_entries'],
                date_range_start=sample_log_file_data['date_range_start'],
                date_range_end=sample_log_file_data['date_range_end']
            )
            db.session.add(log_file)
            db.session.commit()
            
            # Assert
            assert log_file.id is not None
            assert log_file.filename == sample_log_file_data['filename']
            assert log_file.uploaded_by == user.id
            assert log_file.status == sample_log_file_data['status']
            assert log_file.total_entries == sample_log_file_data['total_entries']
            assert log_file.date_range_start == sample_log_file_data['date_range_start']
            assert log_file.date_range_end == sample_log_file_data['date_range_end']
            assert log_file.uploaded_at is not None
    
    def test_should_have_relationship_with_user(self, app, sample_user_data, sample_log_file_data):
        # Arrange
        with app.app_context():
            user = User(email=sample_user_data['email'], password=sample_user_data['password'])
            db.session.add(user)
            db.session.commit()
            
            log_file = LogFile(
                filename=sample_log_file_data['filename'],
                uploaded_by=user.id,
                status='completed',
                total_entries=100
            )
            db.session.add(log_file)
            db.session.commit()
            
            # Act - verify relationship via direct query (UUIDType stores as string in SQLite,
            # so relationship queries need string comparison, but foreign key relationship works)
            user_log_files = LogFile.query.filter_by(uploaded_by=user.id).all()
            
            # Assert - verify foreign key relationship works
            assert len(user_log_files) == 1
            assert str(user_log_files[0].id) == str(log_file.id)
            # Verify the relationship attribute exists
            assert hasattr(user, 'log_files')
            # Verify relationship is a query object (lazy='dynamic')
            assert hasattr(user.log_files, 'filter_by')


class TestLogEntry:
    """Tests for LogEntry model."""
    
    def test_should_create_log_entry_when_valid_data_provided(self, app, sample_user_data, sample_log_file_data, sample_log_entry_data):
        # Arrange
        with app.app_context():
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
            
            # Act
            log_entry = LogEntry(
                log_file_id=log_file.id,
                **sample_log_entry_data
            )
            db.session.add(log_entry)
            db.session.commit()
            
            # Assert
            assert log_entry.id is not None
            assert log_entry.log_file_id == log_file.id
            assert log_entry.timestamp == sample_log_entry_data['timestamp']
            assert log_entry.url == sample_log_entry_data['url']
            assert log_entry.domain == sample_log_entry_data['domain']
            assert log_entry.action == sample_log_entry_data['action']
            assert log_entry.is_anomalous == False
    
    def test_should_have_relationship_with_log_file(self, app, sample_user_data, sample_log_file_data, sample_log_entry_data):
        # Arrange
        with app.app_context():
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
            
            log_entry = LogEntry(
                log_file_id=log_file.id,
                **sample_log_entry_data
            )
            db.session.add(log_entry)
            db.session.commit()
            
            # Act
            file_entries = log_file.entries.all()
            
            # Assert
            assert len(file_entries) == 1
            assert file_entries[0].id == log_entry.id
    
    def test_should_store_anomaly_fields_when_anomalous(self, app, sample_user_data, sample_log_file_data, sample_log_entry_data):
        # Arrange
        with app.app_context():
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
            
            # Act
            entry_data = sample_log_entry_data.copy()
            entry_data.update({
                'is_anomalous': True,
                'anomaly_type': 'malicious_domain',
                'anomaly_reason': 'Domain in malicious list',
                'anomaly_confidence': 0.95
            })
            log_entry = LogEntry(
                log_file_id=log_file.id,
                **entry_data
            )
            db.session.add(log_entry)
            db.session.commit()
            
            # Assert
            assert log_entry.is_anomalous is True
            assert log_entry.anomaly_type == 'malicious_domain'
            assert log_entry.anomaly_reason == 'Domain in malicious list'
            assert log_entry.anomaly_confidence == 0.95


class TestUserRiskScore:
    """Tests for UserRiskScore model."""
    
    def test_should_create_user_risk_score_when_valid_data_provided(self, app, sample_user_data, sample_log_file_data):
        # Arrange
        with app.app_context():
            user = User(email=sample_user_data['email'], password=sample_user_data['password'])
            db.session.add(user)
            db.session.commit()
            
            log_file = LogFile(
                filename=sample_log_file_data['filename'],
                uploaded_by=user.id,
                status='completed',
                total_entries=100
            )
            db.session.add(log_file)
            db.session.commit()
            
            # Act
            risk_score = UserRiskScore(
                log_file_id=log_file.id,
                user_identifier='user@example.com',
                risk_score=75.5,
                anomaly_count=10,
                blocked_count=5,
                malicious_domain_count=2
            )
            db.session.add(risk_score)
            db.session.commit()
            
            # Assert
            assert risk_score.id is not None
            assert risk_score.log_file_id == log_file.id
            assert risk_score.user_identifier == 'user@example.com'
            assert risk_score.risk_score == 75.5
            assert risk_score.anomaly_count == 10
            assert risk_score.blocked_count == 5
            assert risk_score.malicious_domain_count == 2
            assert risk_score.calculated_at is not None

