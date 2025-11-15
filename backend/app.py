"""Flask application factory."""
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from sqlalchemy.exc import OperationalError, IntegrityError, DatabaseError
from config import config
from extensions import db, jwt

migrate = Migrate()


def create_app(config_name=None, test_config=None):
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    if test_config:
        # Test configuration passed as dict
        app.config.update(test_config)
    else:
        config_name = config_name or 'default'
        app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # Configure CORS
    # In development, allow all localhost origins
    # In production, this should be restricted to specific domains
    if app.config.get('DEBUG', False):
        CORS(app, resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                    "http://localhost:3001",
                    "http://127.0.0.1:3001"
                ],
                "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "expose_headers": ["Content-Type"],
                "supports_credentials": True,
                "max_age": 3600
            }
        })
    else:
        # Production CORS - more restrictive
        CORS(app, resources={
            r"/api/*": {
                "origins": app.config.get('CORS_ORIGINS', []),
                "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "expose_headers": ["Content-Type"],
                "supports_credentials": True,
                "max_age": 3600
            }
        })
    
    # Register error handlers
    @app.errorhandler(OperationalError)
    def handle_operational_error(error):
        """Handle database operational errors."""
        db.session.rollback()
        return jsonify({
            'error': 'Database connection error',
            'message': str(error.orig) if hasattr(error, 'orig') else str(error),
            'error_code': 'DB_CONNECTION_ERROR'
        }), 503
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        """Handle database integrity errors."""
        db.session.rollback()
        return jsonify({
            'error': 'Database integrity error',
            'message': str(error.orig) if hasattr(error, 'orig') else str(error),
            'error_code': 'DB_INTEGRITY_ERROR'
        }), 400
    
    @app.errorhandler(DatabaseError)
    def handle_database_error(error):
        """Handle general database errors."""
        db.session.rollback()
        return jsonify({
            'error': 'Database error',
            'message': str(error.orig) if hasattr(error, 'orig') else str(error),
            'error_code': 'DB_ERROR'
        }), 500
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.logs import logs_bp
    from routes.anomalies import anomalies_bp
    from routes.dashboard import dashboard_bp
    from routes.ai import ai_bp
    from routes.health import health_bp
    
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(logs_bp, url_prefix='/api/logs')
    app.register_blueprint(anomalies_bp, url_prefix='/api/anomalies')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    
    return app

