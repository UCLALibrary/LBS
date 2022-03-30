#!/bin/bash

# LBS Django project may have multiple applications, though only 1 at present
APP_DIR=lbs

# Pick up any local changes to requirements.txt, which do *not* automatically get re-installed when starting the container.
# Do this only in dev environment!
if [ "$DJANGO_RUN_ENV" = "dev" ]; then
  pip install --no-cache-dir -r "$APP_DIR"/requirements.txt --user --no-warn-script-location
fi

# Check when database is ready for connections
echo "Checking database connectivity..."
until python -c 'import os, psycopg2 ; conn = psycopg2.connect(host=os.environ.get("DJANGO_DB_HOST"),user=os.environ.get("DJANGO_DB_USER"),password=os.environ.get("DJANGO_DB_PASSWORD"),dbname=os.environ.get("DJANGO_DB_NAME"))' ; do
  echo "Database connection not ready - waiting"
  sleep 5
done

# Run database migrations
python "$APP_DIR"/manage.py migrate

if [ "$DJANGO_RUN_ENV" = "dev" ]; then
  # Create default superuser for dev environment, using django env vars.
  # Logs will show error if this exists, which is OK.
  python "$APP_DIR"/manage.py createsuperuser --no-input
fi

if [ "$DJANGO_RUN_ENV" = "dev" ]; then
  python "$APP_DIR"/manage.py runserver 0.0.0.0:8000
else
  # Build static files directory, starting fresh each time - do we really need this?
  python "$APP_DIR"/manage.py collectstatic --no-input

  # Start the Gunicorn web server
  # Gunicorn cmd line flags:
  # -w number of gunicorn worker processes
  # -b IPADDR:PORT binding
  # --access-logfile where to send HTTP access logs (- is stdout)
  export GUNICORN_CMD_ARGS="-w 3 -b 0.0.0.0:8000 --access-logfile -"
  cd "$APP_DIR"
  gunicorn lbs.wsgi:application
fi
