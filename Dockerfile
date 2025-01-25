# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Copy the .env file into the container (if needed)
COPY .env .

# Command to run the application
CMD ["python", "Phase3_LLM_RAG/QueryConversion.py"]