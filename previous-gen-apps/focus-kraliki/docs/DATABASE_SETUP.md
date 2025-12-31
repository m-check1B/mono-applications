# Database Setup (PostgreSQL Only)

Focus by Kraliki now requires PostgreSQL everywhere (local development, testing, and production). SQLite is no longer supported because the schema depends on Postgres-only types such as `JSONB`, `ARRAY`, and enum columns.

---

## 1. Provision PostgreSQL

```bash
# Docker (recommended for local dev)
docker run --name focus-kraliki-postgres \
  -e POSTGRES_PASSWORD=focus_kraliki \
  -e POSTGRES_DB=focus_kraliki \
  -p 5432:5432 \
  -d postgres:15
```

The connection string used throughout the project:

```text
postgresql://postgres:focus_kraliki@127.0.0.1:5432/focus_kraliki
```

Add it to `backend/.env`, `frontend/.env` (if needed for SSR utilities), and your `TEST_DATABASE_URL`.

---

## 2. Apply Migrations

```bash
cd applications/focus-kraliki/backend
alembic upgrade head
```

Expected log output mentions the Postgres dialect and the latest revision (`008` at the moment).

---

## 3. Inspecting the Database

### Via `psql`
```bash
psql postgresql://postgres:focus_kraliki@127.0.0.1:5432/focus_kraliki

-- List tables
\dt

-- Describe table
\d+ "user"

-- Query users
SELECT id, email, isPremium, usageCount FROM "user";
```

### Via Python shell
```python
import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect("postgresql://postgres:focus_kraliki@127.0.0.1:5432/focus_kraliki")
cur = conn.cursor(cursor_factory=RealDictCursor)
cur.execute("SELECT email, isPremium, usageCount FROM \"user\";")
print(cur.fetchall())
cur.close()
conn.close()
```

---

## 4. Backups & Restores

```bash
# Backup
pg_dump postgresql://postgres:focus_kraliki@127.0.0.1:5432/focus_kraliki > focus_kraliki_backup_$(date +%Y%m%d).sql

# Restore
psql postgresql://postgres:focus_kraliki@127.0.0.1:5432/focus_kraliki < focus_kraliki_backup_YYYYMMDD.sql
```

---

## 5. Testing Database

- Set `TEST_DATABASE_URL` (used by `backend/tests/conftest.py`) to a dedicated Postgres database such as `postgresql://postgres:focus_kraliki@127.0.0.1:5432/focus_kraliki_test`.
- Ensure the database exists before running `pytest`; tests will automatically create/drop tables per test.

---

## 6. Helpful Commands

```bash
# Create additional database/user
psql -h 127.0.0.1 -U postgres -c "CREATE DATABASE focus_kraliki_dev;"
psql -h 127.0.0.1 -U postgres -c \"CREATE USER focus_dev WITH PASSWORD 'focus_dev';\"
psql -h 127.0.0.1 -U postgres -c \"GRANT ALL PRIVILEGES ON DATABASE focus_kraliki_dev TO focus_dev;\"

# Reset schema
psql postgresql://postgres:focus_kraliki@127.0.0.1:5432/focus_kraliki -c \"DROP SCHEMA public CASCADE; CREATE SCHEMA public;\"
alembic upgrade head
```

Keep Postgres running whenever you work on Focus by Kraliki—without it the backend, tests, and ii-agent tooling will fail fast with a clear error message.
