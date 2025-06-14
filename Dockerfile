FROM python:3.13-slim-bookworm

RUN apt-get update

# Set correct timezone
RUN ln -sf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime

# Install dependencies needed to build psycopg python module.
RUN apt-get install -y gcc python3-dev libpq-dev

# For this application, also install cron and sudo,
# and allow django to start cron.
RUN apt-get install -y cron sudo \
    && echo "django ALL=(ALL:ALL) NOPASSWD:/usr/sbin/service cron start" > /etc/sudoers.d/django_cron

# Create django user and switch context to that user.
# For this application, give django user sudo access.
RUN useradd -c "django app user" -d /home/django -s /bin/bash -m django -G sudo
USER django

# Switch to application directory
WORKDIR /home/django/LBS

# Copy application files to image, and ensure django user owns everything
COPY --chown=django:django . .

# Include local python bin into django user's path, mostly for pip
ENV PATH=/home/django/.local/bin:${PATH}

# Make sure pip is up to date, and don't complain if it isn't yet
RUN pip install --upgrade pip --disable-pip-version-check

# Install requirements for this application
RUN pip install --no-cache-dir -r requirements.txt --user --no-warn-script-location

# Expose the typical Django port
EXPOSE 8000

# When container starts, run script for environment-specific actions
CMD [ "sh", "docker_scripts/entrypoint.sh" ]
