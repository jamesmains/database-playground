# Python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies for psycopg2 and Docker
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app's code
COPY . .

# Expose the port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]