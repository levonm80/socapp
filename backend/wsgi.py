"""WSGI entry point for production deployment."""
from app import create_app
import os

# Create app instance for WSGI servers (gunicorn, uwsgi, etc.)
app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == '__main__':
    app.run()

