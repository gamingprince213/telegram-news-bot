# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory for persistent storage
RUN mkdir -p /data

# Copy application code
COPY render_bot.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "render_bot:app"]
