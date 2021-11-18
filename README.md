# Automated QDB reporting

LBS needs several monthly financial reports. Currently, a report is manually created and delivered via email to each FAU manager using legacy software and Jasper.

This project is to automate as much work as possible in report creation and delivery by:

 - Harvesting raw data from campus financial system each month
 - Processing the raw data to generate a report for each FAU (mimicking the current Excel template)
 - Distribute each report to the appropriate FAU managers via email

The new system is to be built using the Django framework.

## Developer Setup

### Local

1. Install Python 3.8
	- https://docs.python-guide.org/

2. Clone this repository

```
cd /path/to/your/projects
git clone git@github.com:UCLALibrary/LBS.git
```

3. Setup the Django environment

```
cd /path/to/your/projects/LBS/lbs
python3 manage.py migrate
python3 manage.py load_initial_data qdb/fixtures/staff.csv qdb/fixtures/unit.csv qdb/fixtures/accounts.csv
python3 manage.py createsuperuser
```

4. Run the Django project

```
python3 manage.py runserver
```

5. Open the Django project in the browser

[http://localhost:8000/admin/](http://localhost:8000/admin/)

6. Open your editor and create/edit relevant files
```
/path/to/your/projects/LBS/lbs/qdb/
```

- admin.py
- models.py
- tests.py
- views.py
- etc ...

## Docker
...

## Developer Tips

1. Work with the underlying SQLite database in the project directory
     - install an independent db browser such as **[DB Browser for SQLite](https://sqlitebrowser.org)**

2. The imported data is from CSV files dumped from the existing reporting system

3. The fixture file for testing was created with the following:
```
python3 manage.py dumpdata --indent 4 --output qdb/fixtures/sample_data.json
```

If "contenttype" errors appear while testing, the contenttype may be left out during file creation:
```
python3 manage.py dumpdata --indent 4 --exclude contenttypes --output qdb/fixtures/sample_data.json
```

4. The reports are generate by a management script which can be run manually for development and testing.
    - set the environment variables

```nano .env/local.env```

```
##### Required, for database access
export QDB_DB_SERVER="obiwan.qdb.ucla.edu"
export QDB_DB_DATABASE="qdb"
export QDB_DB_USER="mgrlib"
export QDB_DB_PASSWORD="<ASK>"

##### Optional, for sending email
export QDB_SMTP_SERVER="smtp.gmail.com"
export QDB_PORT=587
export QDB_FROM_ADDRESS="qdb.test.ucla.@gmail.com"
export QDB_PASSWORD="<ASK>"

#####Optional (application sets 'dev' by default)
export QDB_ENV=dev
```

  - Source the local.env file

```source .env/local.env```

  - run the VPN if you are outside of the UCLA ip space
  - run the script with different flags to test:
 
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

## Testing
1. Run tests from the command line
```
cd /path/to/your/projects/LBS/lbs
python3 manage.py test
```

2. Validate your code
```
python3 manage.py check
```

3. Run the tests
```
python3 manage.py test
```
