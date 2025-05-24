<<<<<<< HEAD
# Use an official Python runtime as a parent image
FROM python:3.11-slim
=======
# Use official Python image
FROM python:3.11-slim
>>>>>>> 9b8ec3688264f617e473e5b6dc7bd4987fd12a02

<<<<<<< HEAD
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
=======
# Set work directory
>>>>>>> 9b8ec3688264f617e473e5b6dc7bd4987fd12a02
WORKDIR /app

<<<<<<< HEAD
# Install dependencies
=======
# Copy application and install dependencies
>>>>>>> 9b8ec3688264f617e473e5b6dc7bd4987fd12a02
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

<<<<<<< HEAD
# Copy the application code
COPY . .
=======
COPY app.py .
>>>>>>> 9b8ec3688264f617e473e5b6dc7bd4987fd12a02

<<<<<<< HEAD
# Expose the port
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

=======
# Expose port and run the app
EXPOSE 8080
CMD ["python", "app.py"]

>>>>>>> 9b8ec3688264f617e473e5b6dc7bd4987fd12a02