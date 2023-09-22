# Automated QDB reporting

LBS needs several monthly financial reports. Currently, a report is manually created and delivered via email to each FAU manager using legacy software and Jasper.

This project is to automate as much work as possible in report creation and delivery by:

 - Harvesting raw data from campus financial system each month
 - Processing the raw data to generate a report for each FAU (mimicking the current Excel template)
 - Distribute each report to the appropriate FAU managers via email

The new system uses the Django framework.

---
## Developer Setup on Docker
---

This is the preferred way to run the project for development.

* Code is automatically mounted in the django container, so local changes are reflected in the running system.
* Data is stored in postgres and persisted to a local volume.

#### (Re)build using docker-compose
```
cd /path/to/your/projects/LBS
# If you just want to rebuild:
docker-compose build
# Normally, build and run application
# Leave off the -d to see real-time output in console.
docker-compose up --build -d
# If rebuilding is not needed:
docker-compose up -d
``` 

#### Connect to the application

[http://localhost:8000/admin/](http://localhost:8000/admin/)

#### Run commands in the django container as needed
```
# General-purpose shell
docker-compose exec django bash
# Django management commands
docker-compose exec django python manage.py
# The first time, moving to postgres, run these 3:
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py createsuperuser
docker-compose exec django python manage.py load_initial_data qdb/fixtures/staff.csv qdb/fixtures/unit.csv qdb/fixtures/accounts.csv
```

#### Stop the application; shuts down and removes containers, but not volumes with data
```
docker-compose down
```

#### Clean up untagged images, which can be left after repeated builds
```
docker rmi $(docker images -q --filter "dangling=true")
```

---
## Status messages displayed to the user
---
1. "Spinner"
    - Indicates report generation is in progress

2. Estimated report generation time when user selects _All units_
    - Please allow up to 5 minutes

3. QDB report successfully generated

4. Remote database not available
    - User is advised to wait and try again

5. Network problem
    - VPN information is provided

6. General failure
    - Link to the _UCLA Library Service Portal_ is provided

7. Form error
    - Please check your selections

8. General AJAX error
    - Link to the _UCLA Library Service Portal_ is provided

---
## Developer Tips
---
  - `QDB_DB_PASSWORD` is defined in `.docker-compose_secrets.env` - ask a team member for this file.  This file is used only in development.
  - Do not commit this file (file names containing "secret" are excluded via the .gitignore file)
  - Browse to the Report Form on your local machine:
[http://localhost:8000/qdb/report/](http://http://localhost:8000/qdb/report/)
---
**Work with the underlying PostgreSQL database in its own docker container**
```
docker-compose exec db bash
psql qdb -U qdb_user

# help
\?

# list databases, tables and data
\l
\dt
select * from qdb_staff;
```
---
**The imported data is from CSV files dumped from the existing QDB reporting system**

The fixture file:
  - verified current 20220304
  - file was created with the following:
```
docker-compose exec django python manage.py dumpdata --indent 4 --output qdb/fixtures/sample_data.json
```

If "contenttype" errors appear while testing, the contenttype may be left out during file creation:
```
docker-compose exec django python manage.py dumpdata --indent 4 --exclude contenttypes --output qdb/fixtures/sample_data.json
```
---
**Test display on Windows Dark Mode to ensure readability**

---
## Reports and Email
---

To test email functionality as a developer:
- There are placeholders in `.docker-compose_django.env`.  This file is under version control; do not edit to set local values.
- Instead, create/edit `.docker-compose_secrets.env` and assign values there.  This file is loaded after other env files, so variables set here override all others:
```
DJANGO_EMAIL_SMTP_SERVER=your_smtp_server
DJANGO_EMAIL_SMTP_PORT=your_smtp_port
DJANGO_EMAIL_FROM_ADDRESS=your_email
DJANGO_EMAIL_PASSWORD=your_email_password
```

The reports are generated and/or emailed by a management script which can be either run automatically by the submitting the form in the qdb app or run manually on the command line. In the _prod_ environment (```DJANGO_RUN_ENV=prod```), the reports are emailed to the recipients listed in ```LBS_RECIPIENTS``` **and** they are emailed to staff matches in the _recipients_ table.

Alternatively, in the _dev_ environment (DJANGO_RUN_ENV=dev), the reports are emailed to the recipients listed in ```DEV_RECIPIENTS``` **and** they are emailed to staff matches in the _recipients_ table.
- The recipient email list may be overridden by setting the ```override_recipients``` (command-line) or by entering one
or more email addresses, separate by spaces, in the `Override recipients` text box in the UI.
- When testing functionality from the command line, override recipients via the `-o` switch:
```
# Example, testing current report
# -u 5: Unit 5 (LHR)
# -r: List recipients for this report, after overrides are applied
# -o your@email.address: The override address; multiple addresses: -o address1 address2 etc.
# -e: Send the report by email.  Only use when testing with -o override.
python manage.py run_qdb_reporter -u 5 -r -o your@email.address -e
```

```
---
**Run manually to generate reports at the command line using Docker**

- Configure QDB to run in a Docker environment as described above
- Use `docker-compose up` to start the container
- open another terminal in which to run the script (or run via `docker-compose up -d`)
- run the VPN if you are outside of the UCLA ip space
- run the script with different flags to test
- use the --email flag to send an email with the attached report(s) to the recipients

docker-compose exec django python manage.py run_qdb_reporter -l
docker-compose exec django python manage.py run_qdb_reporter -y 2017 -m 5 -u 6 -r

-l --list_units - List all the units
-y --year - Year of the report
-m --month - Month number of the report
-u --units - Unit ID number; if omitted all units will receive reports
-e --email - Email the report to the recipients
-r --list_recipients - Display the list of people to email for each report
-o --override_recipients - Override the list of email recipients
```

---
## Testing
---
 Start the container in a terminal then run tests from a second terminal  

```
#### terminal #1
docker-compose up

#### terminal #2
docker-compose exec django python manage.py test qdb.tests
```
 
---
## Inspect the Django project for common problems
---
```
docker-compose exec django python manage.py check
```