# Database Setup - BOT-COMProject

## Overview

BOT-COMProject uses PostgreSQL as its database system with SQLAlchemy 2.0 as the ORM and Alembic for migrations.

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the `.env.example` file to `.env` and update the values:

```bash
cp .env.example .env
```

Update `DATABASE_URL` with your PostgreSQL connection string:

```
DATABASE_URL=postgresql://username:password@host:port/database_name
```

### 3. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE botcomproject;

# Exit
\q
```

### 4. Run Migrations

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Run migrations
alembic upgrade head
```

### 5. Create Tables (Alternative)

If you prefer to create tables directly without Alembic:

```python
from app.infrastructure.database.connection import db_config

# Create all tables
db_config.create_all_tables()
```

## Database Schema

### Tables

| Table | Description |
|-------|-------------|
| `uploads` | File uploads from Aranda |
| `cases` | Cases from Aranda |
| `processings` | Processing executions |
| `processing_rejections` | Rejected cases |
| `estimations` | Time estimations |
| `ai_results` | AI-generated descriptions and times |
| `catalogo_tiempos` | Time catalog (Excel `test_data/catalogo_tiempos.xlsx`) loaded into PostgreSQL |

### Relationships

```
Upload 1 ──── N Case
Upload 1 ──── N Processing
Processing 1 ──── N ProcessingRejection
Processing 1 ──── N Estimation
Processing 1 ──── N AIResult
Case 1 ──── N ProcessingRejection
Case 1 ──── N Estimation
Case 1 ──── N AIResult
```

### `ai_results` fields

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `processing_id` | UUID | Reference to `processings` |
| `case_id` | UUID | Reference to `cases` |
| `case_code` | String(50) | Codigo Caso (Aranda) |
| `case_type` | String(50) | `Incidente` / `Requerimiento` |
| `status` | String(100) | Estado del caso |
| `final_category` | String(200) | Categoría final del caso |
| `estimated_minutes` | Integer | Tiempo recomendado (minutos, del catálogo) |
| `generated_description` | Text | Descripción profesional generada (inicia con "Se realizó") |
| `model_name` | String(100) | Modelo de Ollama usado |
| `tokens_used` | Integer | Tokens de la inferencia |
| `latency_ms` | Float | Latencia de la respuesta (ms) |
| `created_at` | DateTime(timezone) | Fecha de creación (UTC) |

Migrations are applied with Alembic from `backend/alembic/versions/` (currently up to revision `005`).

## Common Commands

### Run Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Check current version
alembic current

# View migration history
alembic history
```

### Generate New Migration

```bash
# Auto-generate migration
alembic revision --autogenerate -m "description"

# Create empty migration
alembic revision -m "description"
```

### Reset Database

```bash
# Drop all tables
alembic downgrade base

# Run all migrations
alembic upgrade head
```

## Testing

For testing, you can use an in-memory SQLite database:

```python
from app.infrastructure.database.connection import DatabaseConfig

# Use SQLite for tests
test_config = DatabaseConfig("sqlite:///:memory:")
test_config.create_all_tables()
```

## Troubleshooting

### Connection Issues

1. Verify PostgreSQL is running
2. Check `DATABASE_URL` in `.env`
3. Ensure database exists
4. Check user permissions

### Migration Issues

1. Check migration files in `alembic/versions/`
2. Verify no conflicting migrations
3. Check database state with `alembic current`
