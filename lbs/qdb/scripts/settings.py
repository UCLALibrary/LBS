import os

# Environment
# Can be 'dev', 'test' or 'prod' - default to 'dev'
ENV = os.environ.get('DJANGO_RUN_ENV', 'dev')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Email server
SMTP_SERVER = os.environ['DJANGO_EMAIL_SMTP_SERVER']
PORT = os.environ['DJANGO_EMAIL_SMTP_PORT']
FROM_ADDRESS = os.environ['DJANGO_EMAIL_FROM_ADDRESS']
PASSWORD = os.environ['DJANGO_EMAIL_PASSWORD']
# This is used by SMTP call in sender.py
APP_IP = os.environ['DJANGO_APP_IP'] # The IP of the machine running this app

# QDB server
DB_SERVER = os.environ['QDB_DB_SERVER']
DB_DATABASE = os.environ['QDB_DB_DATABASE']
DB_USER = os.environ['QDB_DB_USER']
DB_PASSWORD = os.environ.get('QDB_DB_PASSWORD', '') # not relevant for CI builds

# Folder for reports
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

# University Librarian
UL_NAME = 'Ginny Steel'

# Staff contacts
LBS_CONTACT = "Doris Wang"
LBS_CONTACT_TITLE = "Director, Library Business Services"
LBS_CONTACT_EMAIL = "doris@library.ucla.edu"
SDLS_CONTACT = "Joshua Gomez"
SDLS_CONTACT_TITLE = "Head, Software Development & Library Systems"
SLDS_CONTACT_EMAIL = "joshuagomez@library.ucla.edu"

# Report Recipients
# Used only when running tests
TEST_RECIPIENT = os.environ.get('QDB_TEST_RECIPIENT', FROM_ADDRESS)

DEV_RECIPIENTS = [
    'joshuagomez@library.ucla.edu',  # Joshua Gomez
    'akohler@library.ucla.edu'  # Andy Kohler
]

LBS_RECIPIENTS = [
    'doris@library.ucla.edu',  # Doris Wang
    'jian@library.ucla.edu'  # Sandy Ma
]

# akohler 20220414: test env will be treated like prod until rancher rebuild
if ENV == 'dev':  # pragma: no cover
    DEFAULT_RECIPIENTS = DEV_RECIPIENTS
else:
    DEFAULT_RECIPIENTS = LBS_RECIPIENTS

# Message strings
MESSAGE_CLOSER = f'''

If you have any questions about the content of the report please contact:
{LBS_CONTACT}
{LBS_CONTACT_TITLE}
{LBS_CONTACT_EMAIL}

This report and email were auto-generated.
If you have technical questions about the message or the report, please contact:
{SDLS_CONTACT}
{SDLS_CONTACT_TITLE}
{SLDS_CONTACT_EMAIL}'''


# Subcodes
SUBCODES = {
    '00': {
        'title': 'Salaries - Academic',
        'notes': 'LBS will balance sub 00 fund 19900 at year end'},
    '01': {
        'title': 'Salaries - Staff',
        'notes': 'LBS will balance sub 01 fund 19900 at year end'},
    '02': {
        'title': 'General Assistance',
        'notes': 'Please use other (sub 02 only) LBS monthly report to track the allocations and expenditures'},
    '03': {
        'title': 'Supplies and Expense',
        'notes': 'Includes travel'},
    '04': {
        'title': 'Equipment and Facilities',
        'notes': ''},
    '05': {
        'title': 'Books/Collections',
        'notes': ''},
    '06': {
        'title': 'Employee Benefits',
        'notes': '19900 benefits will be funded from the Library Reserve account at year end'},
    '07': {
        'title': 'Special Items',
        'notes': ''},
    '08': {
        'title': 'Unallocated Funds',
        'notes': ''},
    '09': {
        'title': 'Recharges and Departments',
        'notes': ''},
    '9H': {
        'title': 'Overhead (F&A)',
        'notes': 'Apply to Contracts and Grants'}
}
