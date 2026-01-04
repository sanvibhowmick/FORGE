# Use a slim version of Python to keep the build fast and light
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system-level dependencies for Docker and general utilities
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Set the command to run your orchestrator
CMD ["python", "main.py"]