# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required by Poetry and FastAPI
RUN apt-get update \
    && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to the path
ENV PATH="/root/.local/bin:$PATH"

# Copy the pyproject.toml and poetry.lock files into the container
COPY pyproject.toml poetry.lock /app/

# Install dependencies using Poetry
RUN poetry install --no-root --only main

# Copy the application code to the container
COPY . /app/

# Expose the port that FastAPI will run on
EXPOSE 8000

# Start the FastAPI app using Uvicorn
CMD ["poetry", "run", "fastapi", "run", "src/index.py"]
