# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy application and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Expose port and run the app
EXPOSE 8080
CMD ["python", "app.py"]
