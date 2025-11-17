FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Use gunicorn for production, fallback to flask run for development
# Railway will set PORT environment variable, but we default to 5000
CMD if [ "$FLASK_ENV" = "production" ]; then \
      gunicorn --bind [::]:${PORT:-5000} --workers 2 --threads 2 --timeout 120 --access-logfile - --error-logfile - --log-level info wsgi:app; \
    else \
      python run.py; \
    fi

