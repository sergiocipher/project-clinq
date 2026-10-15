#!/bin/sh
# WHY THIS FILE EXISTS:
# Runs Alembic migrations before starting Uvicorn. The retry loop handles
# the race condition where Postgres is still booting when the backend container
# starts, and the case where two replicas both try to migrate simultaneously
# (Alembic's migration table serialises concurrent runs safely).
set -e

n=0
until alembic upgrade head; do
  n=$((n + 1))
  [ "$n" -ge 30 ] && echo "migrations failed after 30 tries" && exit 1
  echo "database not ready or migration race, retry $n/30"
  sleep 3
done

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
