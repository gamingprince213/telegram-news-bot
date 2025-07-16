FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m botuser && \
    chown botuser:botuser /app

# Copy requirements first
COPY --chown=botuser:botuser requirements.txt .

# Install Python packages
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create data directory
RUN mkdir -p /data && \
    chown botuser:botuser /data

# Copy application code
COPY --chown=botuser:botuser render_bot.py .

# Switch to non-root user
USER botuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "render_bot:app"]
