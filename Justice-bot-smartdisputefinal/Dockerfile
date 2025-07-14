# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir .

# Copy your current working application files
COPY . .

# Remove unnecessary files to reduce size
RUN find . -name "*.pyc" -delete
RUN find . -name "__pycache__" -type d -exec rm -rf {} +
RUN rm -rf attached_assets/ backup_* temp_* export_pkg/ data/
RUN rm -f *_test.py *_debug.py check_*.py fix_*.py create_*.py cleanup_*.py
RUN rm -f *_8080.py *_port8080.py app_*.py main_*.py deploy_*.py run_*.py
RUN rm -f *.sh *.pid *.log *.md *.txt *.zip

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port 8080
EXPOSE 8080

# Use your existing gunicorn config but on port 8080
CMD exec gunicorn --config gunicorn.conf.py main:app