FROM python:3.8-slim-bullseye

RUN apt-get update

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

# For now, use the built-in Django application server when the container starts
CMD [ "python", "lbs/manage.py", "runserver", "0.0.0.0:8000" ]
