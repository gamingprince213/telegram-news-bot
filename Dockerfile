FROM python:3.9-slim

WORKDIR /app

# Install system dependencies and create user
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    adduser --disabled-password --gecos '' botuser

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies as non-root user
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create data directory and set permissions
RUN mkdir -p /data && \
    chown botuser:botuser /data

# Copy application code
COPY render_bot.py .

# Switch to non-root user
USER botuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "render_bot:app"]
