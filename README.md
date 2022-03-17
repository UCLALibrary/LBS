# Automated QDB reporting

LBS needs several monthly financial reports. Currently, a report is manually created and delivered via email to each FAU manager using legacy software and Jasper.

This project is to automate as much work as possible in report creation and delivery by:

 - Harvesting raw data from campus financial system each month
 - Processing the raw data to generate a report for each FAU (mimicking the current Excel template)
 - Distribute each report to the appropriate FAU managers via email

The new system is to be built using the Django framework.

---
## Developer Setup on local machine
---
### Local

#### Install Python 3.8
```
https://docs.python-guide.org/`
```

#### Clone this repository
```
cd /path/to/your/projects
git clone git@github.com:UCLALibrary/LBS.git
```
#### Create virtual environment
```
cd /path/to/your/projects/LBS
python3 -m venv ENV
# This needs to be activated every time you work with the application
source ENV/bin/activate
```
#### Update pip and install the project's packages
```
cd /path/to/your/projects/LBS/lbs
pip install --upgrade pip
pip install -r requirements.txt
```

#### Setup the Django environment
```
cd /path/to/your/projects/LBS/lbs
python manage.py migrate
python manage.py load_initial_data qdb/fixtures/staff.csv qdb/fixtures/unit.csv qdb/fixtures/accounts.csv
python manage.py createsuperuser
```

#### Run the Django project
```
cd /path/to/your/projects/LBS/lbs
python manage.py runserver
```

#### Open the Django project in the browser

[http://localhost:8000/admin/](http://localhost:8000/admin/)

#### Open your editor and create/edit relevant files
```
/path/to/your/projects/LBS/lbs/qdb/
```

- admin.py
- models.py
- tests.py
- views.py
- etc ...

#### Deactivate the virtual environment when done working
```
deactivate
```
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
# Leave off the -d to see output in console.
docker-compose up --build -d
# If rebuilding is not needed:
docker-compose up -d
# If the secrets file is being used, put it in place before building
``` 

#### Connect to the application

[http://localhost:8000/admin/](http://localhost:8000/admin/)

#### Run commands in the django container as needed
```
# General-purpose shell
docker-compose exec django bash
# Django management commands
docker-compose exec django python lbs/manage.py
# The first time, moving to postgres, run these 3:
docker-compose exec django python lbs/manage.py migrate
docker-compose exec django python lbs/manage.py createsuperuser
docker-compose exec django python lbs/manage.py load_initial_data lbs/qdb/fixtures/staff.csv lbs/qdb/fixtures/unit.csv lbs/qdb/fixtures/accounts.csv
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
**TEMPORARY - Create secret_qdb_password.txt in the project root directory (/path/to/projects/LBS) contining the QDB password on a single line**
  - Do not commit this file (file names containing "secret" are excluded via the .gitignore file)
  - Browse to the Report Form on your local machine:
[http://http://localhost:8000/qdb/report/](http://http://localhost:8000/qdb/report/)
  - Secret management should be improved for production deployment.
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
python3 manage.py dumpdata --indent 4 --output lbs/qdb/fixtures/sample_data.json
```

If "contenttype" errors appear while testing, the contenttype may be left out during file creation:
```
python3 manage.py dumpdata --indent 4 --exclude contenttypes --output lbs/qdb/fixtures/sample_data.json
```
---
**Drop the leading lbs/ when running outside of docker**
```
python3 manage.py dumpdata --indent 4 --output qdb/fixtures/sample_data.json
```
---
**Test display on Windows Dark Mode to ensure readability**

---
## Reports and Email
---

The reports are generated and/or emailed by a management script which can be either run automatically by the submitting the form in the qdb app or run manually on the command line. In the _prod_ environment (```DJANGO_RUN_ENV=prod```), the reports are emailed to the recipients listed in ```LBS_RECIPIENTS``` **and** they are emailed to staff matches in the _recipients_ table.

Alternatively, in the _dev_ environment (DJANGO_RUN_ENV=dev), the reports are emailed to the recipients listed in ```DEV_RECIPIENTS``` **and** they are emailed to staff matches in the _recipients_ table.
- The recipient email list may be overridden by setting the ```override_recipients``` argument in ``` views.py``` to one or more email addresses:
```
override_recipients=['email1@library.ucla.edu', 'email2@library.ucla.edu', ...]
```

- Note: In _dev_ only, the email is typically sent via your personal smtp (e.g. gmail.com). However, the Google company is discontinuing name/password access to their smtp and an alternative smtp will need to be used in local _dev_ environments after May 2022. _Prod_ already uses UCLA smtp and is not effected by Google's removal of this service. See:  

 [Less secure apps & your Google Account](https://support.google.com/accounts/answer/6010255#zippy=%2Cif-less-secure-app-access-is-on-for-your-account%2Cif-less-secure-app-access-is-off-for-your-account)

```
"To help keep your account secure, starting May 30, 2022, ​​Google will no longer support the use of third-party apps or devices which ask you to sign in to your Google Account using only your username and password."
```
---
**Use the qdb app to send emails with generated reports attached**
- set the environment variables
- specify a smtp server that you have access to

```nano .docker-compose_django.env```

```
DJANGO_RUN_ENV=dev

# QDB database server
QDB_DB_SERVER=obiwan.qdb.ucla.edu
QDB_DB_DATABASE=qdb
QDB_DB_USER=mgrlib
# This one comes from secrets
QDB_DB_PASSWORD_FILE=/run/secrets/qdb_password

# Email server info
QDB_SMTP_SERVER=smtp.gmail.com
QDB_PORT=587
QDB_FROM_ADDRESS=qdb.test.ucla.@gmail.com
QDB_PASSWORD=unknown
```

- set the developer recipient list to your email
- add other comma-delimited developers and/or unit staffmembers as needed for testing

```nano lbs/qdb/scripts/settings.py```

```
DEV_RECIPIENTS = [
    'janebruin@library.ucla.edu',
    'joebruin@library.ucla.edu'
]

```
Configure the ```else``` section around line 68 in ```views.py```
- set ```email=True``` to enable sending of emails
  - if ```email=False``` no emails are sent
  - if ```email=False``` reports are stored in the server file system in lbs/qdb/reports/
- set ```override_recipients``` to receive reports sent via email to your email address
  -  ```override_recipients=['email1@library.ucla.edu', 'email2@library.ucla.edu', ...]```
  - you must configure your own SMTP in ```.docker-compose_django.env```
  - use caution to avoid accidentally blasting reports to unsuspecting recipients
  - set ```email=False``` and read the recipient address in the terminal to check recipient list  before sending emails
  - example config:

```nano lbs/qdb/views.py```
```
        call_command('run_qdb_reporter', list_units=True, year=int(year_from_form),
                     month=int(month_from_form), units=[unit_from_form], email=False, list_recipients=True, override_recipients=['youremail1@library.ucla.edu')]

```
---
**Run manually to generate reports at the command line using Docker**
- Configure QDB to run in a Docker environment as described above
- Use ```docker-compose up``` to start the container
- open another terminal in which to run the script
- 
```
docker-compose exec django python lbs/manage.py run_qdb_reporter -l
docker-compose exec django python lbs/manage.py run_qdb_reporter-y 2017 -m 5 -u 6 -r

```

```
-l --list_units - List all the units
-y --year - Year of the report
-m --month - Month number of the report
-u --units - Unit ID number; if omitted all units will receive reports
-e --email - Email the report to the recipients
-r --list_recipients - Display the list of people to email for each report
-o --override_recipients - Override the list of email recipients
```
---
**Run manually to generate reports at the command line on a local install (no Docker)**
  - set the environment variables

```nano .env/local.env```

```
##### Required, for database access
export QDB_DB_SERVER="obiwan.qdb.ucla.edu"
export QDB_DB_DATABASE="qdb"
export QDB_DB_USER="mgrlib"
export QDB_DB_PASSWORD="<ASK>"

##### Optional, for sending email
##### Note: see above in this document - the gmail smtp may not work after May 2022 when using username/password only
export QDB_SMTP_SERVER="smtp.gmail.com"
export QDB_PORT=587
export QDB_FROM_ADDRESS="qdb.test.ucla.@gmail.com"
export QDB_PASSWORD="<ASK>"

##### Optional (application sets 'dev' by default)
export DJANGO_RUN_ENV=dev
```

  - Source the local.env file

```source .env/local.env```

  - run the VPN if you are outside of the UCLA ip space
  - run the script with different flags to test
  - use the --email flag to send an email with the attached report(s) to the recipients
  - examples:
 
```
python3 manage.py run_qdb_reporter -l
python3 manage.py run_qdb_reporter -y 2017 -m 5 -u 6 -r
```

```
-l --list_units - List all the units
-y --year - Year of the report
-m --month - Month number of the report
-u --units - Unit ID number; if omitted all units will receive reports
-e --email - Email the report to the recipients
-r --list_recipients - Display the list of people to email for each report
```
---
## Testing
---
 Start the container in a terminal  then run tests from a second terminal  

 ```
 #### terminal #1
 docker=-compose up
 
 #### terminal #2
 docker-compose exec django python lbs/manage.py test qdb.tests
 ```
 
 When running locally directly on your machine:
```
cd /path/to/your/projects/LBS/lbs
python3 manage.py test
```
---
## Validate your code
---
```
python3 manage.py check
