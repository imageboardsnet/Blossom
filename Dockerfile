# syntax=docker/dockerfile:1
FROM python:3.12-alpine
WORKDIR /code
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Install necessary build tools and dependencies
RUN apk add --no-cache gcc musl-dev linux-headers

# Copy and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy application code and other files
COPY . .
COPY static /code
COPY templates /code
COPY obj /code
COPY utils /code

# Create necessary directories
RUN mkdir -p /code/data /code/endpoints /code/var

# Command to run the application
CMD ["gunicorn", "-b", "0.0.0.0:7000", "app:create_app()"]