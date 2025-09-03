FROM python:3.11-slim

# Zainstaluj wymagane pakiety systemowe do psycopg2 i Pillow
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    python3-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Skopiuj requirements i zainstaluj
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj resztę projektu
COPY . /app/
