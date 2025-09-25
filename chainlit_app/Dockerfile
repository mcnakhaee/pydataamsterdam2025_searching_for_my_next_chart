FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
# The following directories must exist in your repository.
# If they don't, create them (even if empty) and commit the change.
COPY .chainlit/ ./.chainlit/
COPY public/ ./public/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Use Heroku's PORT environment variable.
# The shell form is used here to allow $PORT to be substituted.
CMD chainlit run src/chainlit_app.py --host 0.0.0.0 --port $PORT --headless