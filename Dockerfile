# Use official slim Python runtime as base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DB_PATH=/app/data/interview_bot.db

# Set work directory
WORKDIR /app

# Install system dependencies (SQLite development headers if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    sqlite3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install python packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY src /app/src
COPY main.py /app/

# Create database data folder
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run FastAPI using Uvicorn
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
