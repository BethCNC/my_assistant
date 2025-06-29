FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Run the application directly with uvicorn on port 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"] 