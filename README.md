# Automated LBS reporting

This project provides tools to automate as much work as possible in report creation and delivery by UCLA's Library Business Services (LBS).

It contains two Django applications: QDB (Query Database, for general financial reports) and GE (Gifts and Expenditures).

QDB:
 - Harvests raw data from campus financial system each month
 - Processes the raw data to generate a report for each fund
 - Distribute each report to the appropriate fund managers via email

 GE:
 - Imports data from multiple Excel files
 - Processes data to generate a report for each library unit / manager

## Developer Setup on Docker

This is the preferred way to run the project for development.

* Code is automatically mounted in the django container, so local changes are reflected in the running system.
* Data is stored in a local postgres container and persisted to a local volume.

#### (Re)build using docker compose
```
cd /path/to/your/projects/LBS
# If you just want to rebuild:
docker compose build
# Normally, build and run application
# Leave off the -d to see real-time output in console.
docker compose up --build -d
# If rebuilding is not needed:
docker compose up -d
``` 

#### Connect to the application

[http://localhost:8000/admin/](http://localhost:8000/admin/)

#### Run commands in the django container as needed
```
# General-purpose shell
docker compose exec django bash
# Django management commands
docker compose exec django python manage.py
# The first time, to initialize the local database with data from fixtures, run:
docker compose exec django python manage.py load_initial_data qdb/fixtures/staff.csv qdb/fixtures/unit.csv qdb/fixtures/accounts.csv
# Note: This local data is out of date, but should be OK for development & testing.
```

#### Stop the application; shuts down and removes containers, but not volumes with data
```
docker compose down
```

#### Clean up untagged images, which can be left after repeated builds
```
docker rmi $(docker images -q --filter "dangling=true")
```

## Status messages displayed to the user

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

## Developer Tips

  - `QDB_DB_PASSWORD` is defined in `.docker compose_secrets.env` - ask a team member for this file.  This file is used only in development.
  - Do not commit this file (file names containing "secret" are excluded via the .gitignore file)
  - Browse to the Report Form on your local machine:
[http://localhost:8000/qdb/report/](http://http://localhost:8000/qdb/report/)

**Work with the underlying PostgreSQL database in its own docker container**
```
docker compose exec db psql qdb -U qdb_user

# help
\?

# list databases, tables and data
\l
\dt
select * from qdb_staff;
```

**The imported data is from CSV files dumped from the existing QDB reporting system**

The fixture file:
  - verified current 20220304
  - file was created with the following:
```
docker compose exec django python manage.py dumpdata --indent 4 --output qdb/fixtures/sample_data.json
```

If "contenttype" errors appear while testing, the contenttype may be left out during file creation:
```
docker compose exec django python manage.py dumpdata --indent 4 --exclude contenttypes --output qdb/fixtures/sample_data.json
```

**Test display on Windows Dark Mode to ensure readability**

## Reports and Email

To test email functionality as a developer:
- There are placeholders in `.docker compose_django.env`.  This file is under version control; do not edit to set local values.
- Instead, create/edit `.docker compose_secrets.env` and assign values there.  This file is loaded after other env files, so variables set here override all others:
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

**Run manually to generate reports at the command line using Docker**

- Configure QDB to run in a Docker environment as described above
- Use `docker compose up` to start the container
- open another terminal in which to run the script (or run via `docker compose up -d`)
- run the VPN if you are outside of the UCLA ip space
- run the script with different flags to test
- use the --email flag to send an email with the attached report(s) to the recipients

docker compose exec django python manage.py run_qdb_reporter -l
docker compose exec django python manage.py run_qdb_reporter -y 2017 -m 5 -u 6 -r

-l --list_units - List all the units
-y --year - Year of the report
-m --month - Month number of the report
-u --units - Unit ID number; if omitted all units will receive reports
-e --email - Email the report to the recipients
-r --list_recipients - Display the list of people to email for each report
-o --override_recipients - Override the list of email recipients
```

## Testing

```
# Run all tests
docker compose exec django python manage.py test
# Or just those for the qdb (or ge) application
docker compose exec django python manage.py test qdb
docker compose exec django python manage.py test ge
```

## Using pgAdmin

To use [pgAdmin](https://www.pgadmin.org/) during development, start the local application like this:

```
# Start in background using a non-default configuration file
docker compose -f docker compose_PGADMIN.yml up -d
# Shut it down in the same way, to ensure all resources are closed
docker compose -f docker compose_PGADMIN.yml down
```

You can then access `pgAdmin` via browser at http://localhost:5050/ .

Log in using the arbitrary local credentials from `docker compose_PGADMIN.yml`:
* User: `systems@library.ucla.edu`
* Password: `admin`

After first login, register the local database server.
* `Object -> Register -> Server`
* Name: whatever you want
* On the Connection tab, use local-only info from `.docker compose_db.env`
  * Host name/address: `db`
  * Port: `5432`
  * Username: `qdb_user`
  * Password: `dev_qdb_pass`
  * Save password? Yes
  * Click `Save`, without changing any other settings

See [pgAdmin documentation](https://www.pgadmin.org/docs/) for more information.

## Viewing the log

Local development environment: `view logs/application.log`.

In deployed container:
* `/logs/`: see latest 200 lines of the log
* `/logs/nnn`: see latest `nnn` lines of the log

## Scheduling QDB reports

The QDB reports can be scheduled to run monthly (or at other intervals), via the `/qdb/cron/` URL (available via the QDB header as "QDB Scheduling").
This uses a basic `CronJob` Django model, which stores the standard `cron` schedule fields (minutes, hours, days of month, months, days of week),
the command to run, and an `enabled` field to turn the job on or off.

`CronJob` records are formatted as needed and output to the `django` user's `crontab` via the `update_crontab` Django management command.
This command is called when `CronJob` records are updated via the `crontab` Django view.

This currently is a very basic implementation:
* Only one `CronJob` is allowed (enforced via an overridden `CronJob.save()`).
* No validation of cron format is done, since the scheduling fields allow ranges and intervals (e.g., `5-10`, `*/5`, `5,10,20,39`, etc.).
* However, the underlying Linux `crontab` program does some validation, and will reject invalid data.

If there is a future need for multiple `crontab` entries, or for user-friendly schedule entry, more programming will be needed or a
more complex 3rd-party solution may be a better choice.
