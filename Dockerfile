# Use official Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (replace 5000 with your application's port if different)
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]