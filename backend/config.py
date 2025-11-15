"""Application configuration."""
import os
from datetime import timedelta


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    # Kong API Gateway configuration
    TRUST_PROXY_HEADERS = True


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://socapp:socapp_dev@localhost:5432/socapp'
    # CORS settings
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    OPENAI_API_KEY = 'test-openai-key'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

