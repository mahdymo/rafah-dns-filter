# DNS Filter Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY dependencies.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r dependencies.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p /app/blocklists /app/logs

# Set permissions
RUN chmod +x setup_ubuntu.sh

# Expose ports
EXPOSE 5000 5353/udp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/stats || exit 1

# Run the application
CMD ["python3", "main.py"]