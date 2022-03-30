FROM python:3.8-slim-bullseye

RUN apt-get update

# Install dependencies needed to build psycopg2 python module
RUN apt-get install -y gcc python3-dev libpq-dev

# Create django user and switch context to that user
RUN useradd -c "django app user" -d /home/django -s /bin/bash -m django
USER django

# Switch to application directory
WORKDIR /home/django/LBS

# Copy application files to image, and ensure django user owns everything
COPY --chown=django:django . .

# Include local python bin into django user's path, mostly for pip
ENV PATH /home/django/.local/bin:${PATH}

# Make sure pip is up to date, and don't complain if it isn't yet
RUN pip install --upgrade pip --disable-pip-version-check

# Install requirements for this application
RUN pip install --no-cache-dir -r lbs/requirements.txt --user --no-warn-script-location

# Expose the typical Django port
EXPOSE 8000

# When container starts, run script for environment-specific actions
CMD [ "sh", "docker_scripts/entrypoint.sh" ]
