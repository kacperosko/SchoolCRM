#!/bin/bash
set -e

# 1. Czekaj na uruchomienie PostgreSQL
until PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c '\q'; do
  echo "Waiting for Postgres..."
  sleep 2
done

# 2. Migracje Django
python manage.py migrate

# 3. Tworzenie procedur i triggerów
psql "host=$DB_HOST dbname=$DB_NAME user=$DB_USER password=$DB_PASSWORD" -f /app/init_db/init.sql

# 4. Generowanie danych testowych
python manage.py generate_test_data

# 5. Uruchom serwer Django
python manage.py runserver 0.0.0.0:8000


cd SchoolCRM

docker compose up --build
