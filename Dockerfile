FROM python:3.9-slim AS base

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py /app/
COPY config.yaml /app/

# Install system dependencies, including Nginx and Supervisor
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor && \
    rm -rf /var/lib/apt/lists/*

# Copy frontend files for Nginx
COPY frontend_app/ /usr/share/nginx/html/

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy Supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports for both Flask and Nginx
EXPOSE 3000 80

# Start Supervisor to manage Nginx and Flask
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]