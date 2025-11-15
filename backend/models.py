"""Database models."""
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET, JSON
from sqlalchemy import TypeDecorator, Text
import json
from sqlalchemy import Column, String, Integer, Boolean, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from extensions import db


class JSONType(TypeDecorator):
    """JSON type that works with both PostgreSQL and SQLite."""
    impl = Text
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(Text())
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return json.dumps(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return json.loads(value)


class UUIDType(TypeDecorator):
    """UUID type that works with both PostgreSQL and SQLite."""
    impl = String(36)
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value  # Already UUID
        return uuid.UUID(value) if value else None


class INETType(TypeDecorator):
    """INET type that works with both PostgreSQL and SQLite."""
    impl = String(45)  # IPv6 max length
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(INET())
        else:
            return dialect.type_descriptor(String(45))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, str):
            return value
        return str(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return str(value) if value else None


class User(db.Model):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    log_files = relationship('LogFile', backref='uploader', lazy='dynamic')
    
    def __init__(self, email, password):
        self.email = email
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': str(self.id),
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class LogFile(db.Model):
    """Log file model."""
    __tablename__ = 'log_files'
    
    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    uploaded_by = Column(UUIDType(), ForeignKey('users.id'), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(50), nullable=False, default='uploading')  # uploading, processing, completed, failed
    total_entries = Column(Integer, default=0)
    date_range_start = Column(DateTime)
    date_range_end = Column(DateTime)
    file_metadata = Column(JSONType)
    
    # Relationships
    entries = relationship('LogEntry', backref='log_file', lazy='dynamic', cascade='all, delete-orphan')
    user_risk_scores = relationship('UserRiskScore', backref='log_file', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert log file to dictionary."""
        return {
            'id': str(self.id),
            'filename': self.filename,
            'uploaded_by': str(self.uploaded_by),
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'status': self.status,
            'total_entries': self.total_entries,
            'date_range_start': self.date_range_start.isoformat() if self.date_range_start else None,
            'date_range_end': self.date_range_end.isoformat() if self.date_range_end else None,
            'metadata': self.file_metadata
        }


class LogEntry(db.Model):
    """Log entry model for Zscaler NSS web proxy logs."""
    __tablename__ = 'log_entries'
    
    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    log_file_id = Column(UUIDType(), ForeignKey('log_files.id'), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    location = Column(String(100))
    protocol = Column(String(10))
    url = Column(Text, nullable=False)
    domain = Column(String(255), index=True)  # Extracted from URL
    action = Column(String(50), index=True)  # Allowed, Blocked
    app_name = Column(String(100))
    app_class = Column(String(100))
    throttle_req_size = Column(Integer)
    throttle_resp_size = Column(Integer)
    req_size = Column(Integer)
    resp_size = Column(Integer)
    url_class = Column(String(100))
    url_supercat = Column(String(100))
    url_cat = Column(String(100), index=True)
    dlp_dict = Column(String(100))
    dlp_eng = Column(String(100))
    dlp_hits = Column(Integer, default=0)
    file_class = Column(String(100))
    file_type = Column(String(100))
    location2 = Column(String(100))
    department = Column(String(100), index=True)
    client_ip = Column(INETType(), index=True)
    server_ip = Column(INETType())
    http_method = Column(String(10))
    http_status = Column(Integer)
    user_agent = Column(Text)
    threat_category = Column(String(100), index=True)  # None, Malware, Phishing, etc.
    fw_filter = Column(String(100))
    fw_rule = Column(String(100))
    policy_type = Column(String(100))
    reason = Column(String(255))
    is_anomalous = Column(Boolean, default=False, index=True)
    anomaly_type = Column(String(50))  # burst_blocked, malicious_domain, risky_category, unusual_ua, large_download
    anomaly_reason = Column(Text)
    anomaly_confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_log_entries_log_file_timestamp', 'log_file_id', 'timestamp'),
    )
    
    def to_dict(self):
        """Convert log entry to dictionary."""
        return {
            'id': str(self.id),
            'log_file_id': str(self.log_file_id),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'location': self.location,
            'protocol': self.protocol,
            'url': self.url,
            'domain': self.domain,
            'action': self.action,
            'app_name': self.app_name,
            'app_class': self.app_class,
            'throttle_req_size': self.throttle_req_size,
            'throttle_resp_size': self.throttle_resp_size,
            'req_size': self.req_size,
            'resp_size': self.resp_size,
            'url_class': self.url_class,
            'url_supercat': self.url_supercat,
            'url_cat': self.url_cat,
            'dlp_dict': self.dlp_dict,
            'dlp_eng': self.dlp_eng,
            'dlp_hits': self.dlp_hits,
            'file_class': self.file_class,
            'file_type': self.file_type,
            'location2': self.location2,
            'department': self.department,
            'client_ip': str(self.client_ip) if self.client_ip else None,
            'server_ip': str(self.server_ip) if self.server_ip else None,
            'http_method': self.http_method,
            'http_status': self.http_status,
            'user_agent': self.user_agent,
            'threat_category': self.threat_category,
            'fw_filter': self.fw_filter,
            'fw_rule': self.fw_rule,
            'policy_type': self.policy_type,
            'reason': self.reason,
            'is_anomalous': self.is_anomalous,
            'anomaly_type': self.anomaly_type,
            'anomaly_reason': self.anomaly_reason,
            'anomaly_confidence': self.anomaly_confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserRiskScore(db.Model):
    """User risk score model."""
    __tablename__ = 'user_risk_scores'
    
    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    log_file_id = Column(UUIDType(), ForeignKey('log_files.id'), nullable=False, index=True)
    user_identifier = Column(String(255), nullable=False, index=True)  # email or IP
    risk_score = Column(Float, nullable=False)  # 0-100
    anomaly_count = Column(Integer, default=0)
    blocked_count = Column(Integer, default=0)
    malicious_domain_count = Column(Integer, default=0)
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    score_metadata = Column(JSONType)  # Breakdown by anomaly type
    
    # Indexes
    __table_args__ = (
        Index('idx_user_risk_scores_user', 'user_identifier'),
        Index('idx_user_risk_scores_log_file', 'log_file_id'),
    )
    
    def to_dict(self):
        """Convert user risk score to dictionary."""
        return {
            'id': str(self.id),
            'log_file_id': str(self.log_file_id),
            'user_identifier': self.user_identifier,
            'risk_score': self.risk_score,
            'anomaly_count': self.anomaly_count,
            'blocked_count': self.blocked_count,
            'malicious_domain_count': self.malicious_domain_count,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
            'metadata': self.score_metadata
        }


class TokenBlacklist(db.Model):
    """Blacklisted JWT tokens (for logout functionality)."""
    __tablename__ = 'token_blacklist'
    
    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    jti = Column(String(36), unique=True, nullable=False, index=True)  # JWT ID
    token_type = Column(String(10), nullable=False)  # 'access' or 'refresh'
    user_id = Column(UUIDType, ForeignKey('users.id'), nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)  # When the token would naturally expire
    
    def to_dict(self):
        """Convert token blacklist entry to dictionary."""
        return {
            'id': str(self.id),
            'jti': self.jti,
            'token_type': self.token_type,
            'user_id': str(self.user_id),
            'revoked_at': self.revoked_at.isoformat() if self.revoked_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

