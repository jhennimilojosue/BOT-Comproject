#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until pg_isready -h "${POSTGRES_HOST:-db}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-postgres}" > /dev/null 2>&1; do
  sleep 2
done
echo "PostgreSQL is ready."

echo "Waiting for Ollama..."
until curl -fsS "http://${OLLAMA_HOST:-ollama}:11434/api/version" > /dev/null 2>&1; do
  sleep 3
done
echo "Ollama is ready."

echo "Running Alembic migrations..."
cd /app && alembic upgrade head

echo "Pulling Ollama model if missing..."
curl -fsS -X POST "http://${OLLAMA_HOST:-ollama}:11434/api/pull" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"${OLLAMA_MODEL:-qwen2.5-coder:3b}\"}" || true

echo "Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000