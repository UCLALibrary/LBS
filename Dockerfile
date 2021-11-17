FROM python:3.8-slim-bullseye

RUN apt-get update

RUN useradd -c "django app user" -d /home/django -s /bin/bash -m django
USER django

WORKDIR /home/django/LBS

COPY --chown=django:django . .
RUN pip install --no-cache-dir -r lbs/requirements.txt --user --no-warn-script-location

EXPOSE 8000

CMD [ "sh", "python lbs/manage.py runserver" ]
