FROM python:3.12-slim

WORKDIR /app

# Install system deps (bcrypt needs libssl)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for SQLite
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
