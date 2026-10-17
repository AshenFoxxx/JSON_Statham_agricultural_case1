FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5001

# Set Python to unbuffered mode
ENV PYTHONUNBUFFERED=1

# Run the docs server
CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "5001"]
