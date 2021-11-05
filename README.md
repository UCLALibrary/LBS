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

[localhost:8000/admin/](localhost:8000/admin/)

6. Open your editor and create/edit relevant files

/path/to/your/projects/LBS/lbs/qdb/
    admin.py
    models.py
    tests.py
    views.py
    etc ...

## Docker
...

## Developer Tips

1. Work with the underlying SQLite database in the project directory
     - install an independent db browser such as **[DB Browser for SQLite](https://sqlitebrowser.org/{panel})**

2. The imported data is from CSV files dumped from the existing reporting system

3. The fixture file for testing was created with the following:
```
python3 manage.py dumpdata --indent 4 --output qdb/fixtures/sample_data.json
```

If "contenttype" errors appear while testing, the contenttype may be left out during file creation:
```
python3 manage.py dumpdata --indent 4 --exclude contenttypes --output qdb/fixtures/sample_data.json
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
