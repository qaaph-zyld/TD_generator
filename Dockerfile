# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY td_generator/ td_generator/

# Set environment variables
ENV PYTHONPATH=/app
ENV ANTHROPIC_API_KEY=""

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "td_generator"]
