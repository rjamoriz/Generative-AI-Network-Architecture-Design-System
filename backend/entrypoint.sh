#!/bin/bash
set -e

echo "Starting Network Design System Backend..."

# Wait for Postgres to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Wait for MongoDB to be ready
echo "Waiting for MongoDB..."
while ! mongosh --host $MONGODB_URI --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
  sleep 1
done
echo "MongoDB is ready!"

# Run Alembic migrations
echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
