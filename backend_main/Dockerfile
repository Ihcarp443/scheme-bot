FROM python:3.11-slim

WORKDIR /app

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Change this based on your FastAPI entry point
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]