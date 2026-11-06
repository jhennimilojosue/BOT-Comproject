#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until python -c "
import sys, time
try:
    import psycopg2
except Exception as e:
    print('psycopg2 missing')
    sys.exit(1)
from urllib.parse import urlparse
import os
url = os.environ.get('DATABASE_URL','postgresql://postgres:postgres@db:5432/bot_comproject')
parsed = urlparse(url)
host = os.environ.get('POSTGRES_HOST') or parsed.hostname or 'db'
port = os.environ.get('POSTGRES_PORT') or parsed.port or 5432
user = os.environ.get('POSTGRES_USER') or parsed.username or 'postgres'
pw  = os.environ.get('POSTGRES_PASSWORD') or parsed.password or 'postgres'
db  = parsed.path.lstrip('/') if parsed.path else 'bot_comproject'
try:
    conn = psycopg2.connect(host=host,port=port,user=user,password=pw,database=db,connect_timeout=2)
    conn.close()
    sys.exit(0)
except Exception as ex:
    pass
sys.exit(1)
" 2>/dev/null; do
  sleep 2
done
echo "PostgreSQL is ready."

echo "Checking Ollama availability..."
until curl -fsS "http://${OLLAMA_HOST:-host.docker.internal}:11434/api/version" > /dev/null 2>&1; do
  echo "Waiting for Ollama at ${OLLAMA_HOST:-host.docker.internal}:11434..."
  sleep 3
done
echo "Ollama is ready."

echo "Running Alembic migrations..."
cd /app && alembic upgrade head

echo "Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000