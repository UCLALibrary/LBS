
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from qdb.models import Staff, Unit, Account, Subcode, Recipient

import csv


def populate_persons(self, staff_file):
    """
    Does initial creation of Staff
    """
    self.stdout.write(f"Parsing {staff_file}")
    with open(staff_file, encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile, dialect="excel")

        for row in reader:
            # Get relevant data from CSV
            staff_id = row["id"]
            name = row["name"]
            email = row["email"]

            self.stdout.write(f"\tProcessing {name}...")

            # Staff
            person = _create_person(staff_id, name, email)


def populate_units(self, unit_file):
    """
    Does initial creation of Units
    """
    self.stdout.write(f"Parsing {unit_file}")
    with open(unit_file, encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile, dialect="excel")

        for row in reader:
            # Get relevant data from CSV
            name = row["name"]
            head = row["head"]
            aul = row["aul"]

            self.stdout.write(f"\tProcessing {name}...")

            # Library Units
            unit = _create_unit(name, head, aul)


def populate_accounts(self, accounts_file):
    """
    Does initial creation of Account
    """
    self.stdout.write(f"Parsing {accounts_file}")
    with open(accounts_file, encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile, dialect="excel")

        for row in reader:
            # Get relevant data from CSV
            account_num = row["account"]
            cost_center = row["cost_center"]
            title = row["title"]
            unit_id = row["unit"]

            self.stdout.write(f"\tProcessing {title}...")

            # Account
            account = _create_account(account_num, cost_center, title, unit_id)


def populate_subcodes(self):
    """Does initial subcode creation"""
    self.stdout.write(f"Adding subcodes")
    # just hardcoding it for now
    subcode_dict = {
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
    for subcode in subcode_dict:
        sc, created = Subcode.objects.get_or_create(code=subcode,
                                                    titles=subcode_dict[subcode]['title'],
                                                    notes=subcode_dict[subcode]['notes'])
        sc.save()


def _create_person(staff_id, name, email):
    # Staff (persons) might already exist, via small initial load
    staff, created = Staff.objects.get_or_create(staff_id=staff_id, name=name,
                                                 email=email)
    staff.save()
    return staff


def _create_unit(name, head, aul):
    # units might already exist
    unit, created = Unit.objects.get_or_create(name=name)
    if head:
        member = Staff.objects.get(staff_id=head)
        unit.members.add(member)
        unit.save()
        # add roles to recipient table at this step
        recip = Recipient.objects.get(recipient=member, unit=unit)
        recip.role = "head"
        recip.save()
    if aul:
        member = Staff.objects.get(staff_id=aul)
        unit.members.add(member)
        unit.save()
        # add roles to recipient table at this step
        recip = Recipient.objects.get(recipient=member, unit=unit)
        recip.role = "aul"
        recip.save()

    unit.save()
    return unit


def _create_account(acct, cost_center, title, unit_id):
    # get foreign key first
    acct_unit = Unit.objects.get(id=unit_id)
    row, created = Account.objects.get_or_create(account=acct,
                                                 cost_center=cost_center,
                                                 title=title,
                                                 unit=acct_unit)
    row.save()
    return row


class Command(BaseCommand):
    help = "Load QDB data from CSV into database"

    def add_arguments(self, parser):
        parser.add_argument("staff_file")
        parser.add_argument("unit_file")
        parser.add_argument("accounts_file")

    def handle(self, *args, **options):
        staff = options["staff_file"]
        unit = options["unit_file"]
        accounts = options["accounts_file"]
        populate_persons(self, staff)
        populate_units(self, unit)
        populate_accounts(self, accounts)
        populate_subcodes(self)
