# Use a more specific Python runtime as a parent image
FROM python:3.11-slim-buster as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIPENV_VENV_IN_PROJECT=1

# Set work directory
WORKDIR /app

# Install system dependencies and clean up cache to reduce layer size
RUN apt-get update && \
    apt-get install -y netcat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --upgrade pip && \
    pip install pipenv

# Copy Pipfile and Pipfile.lock to ensure both are copied
COPY Pipfile Pipfile.lock /app/

# Install project dependencies
RUN pipenv install --deploy

# Create a non-root user and switch to it
RUN useradd -m app
USER app

# Copy project
COPY --chown=app:app . /app

# Final stage: Create the final execution image
FROM python:3.11-slim-buster
COPY --from=builder /app /app
WORKDIR /app
USER app

# Run the application
CMD ["python3", "uvicorn server:app"]
