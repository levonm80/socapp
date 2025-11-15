"""Run the Flask application."""
from app import create_app
from flask_migrate import upgrade
from scripts.bootstrap import bootstrap_test_user
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app(os.environ.get('FLASK_ENV', 'development'))


def init_db():
    """Initialize database: run migrations and bootstrap data."""
    with app.app_context():
        try:
            # Run migrations
            logger.info("Running database migrations...")
            upgrade()
            logger.info("Migrations completed successfully.")
            
            # Bootstrap test user
            logger.info("Bootstrapping test user...")
            created = bootstrap_test_user()
            if created:
                logger.info("Test user created: test@example.com / testpassword123")
            else:
                logger.info("Test user already exists, skipping creation.")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            sys.exit(1)


if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

