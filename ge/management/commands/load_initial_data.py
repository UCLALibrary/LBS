
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from ge.models import GeStaff, GeUnit, GeFund

import csv


def populate_staff(self, staff_file):
    """
    Does initial creation of GeStaff
    """
    self.stdout.write(f"Parsing {staff_file}")
    with open(staff_file, encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile, dialect="excel")

        for row in reader:
            # Get relevant data from CSV
            name = row["name"]
            email = row["email"]

            self.stdout.write(f"\tProcessing {name}...")

            # Staff
            stadd = _create_staff(name, email)


def populate_units(self, unit_file):
    """
    Does initial creation of GeUnit
    """
    self.stdout.write(f"Parsing {unit_file}")
    with open(unit_file, encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile, dialect="excel")

        for row in reader:
            # Get relevant data from CSV
            name = row["name"]

            self.stdout.write(f"\tProcessing {name}...")

            # Library Units
            unit = _create_unit(name)


def populate_funds(self, funds_file):
    """
    Does initial creation of GeFund
    """
    self.stdout.write(f"Parsing {funds_file}")
    with open(funds_file, encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile, dialect="excel")

        for row in reader:
            # Get relevant data from CSV
            account = row["account"]
            cost_center = row["cost_center"]
            fund = row["fund"]
            title = row["title"]
            manager = row["manager"]
            mtf_authority = row["mtf_authority"]
            fund_purpose = row["fund_purpose"]
            fund_summary = row["fund_summary"]
            fund_restriction = row["fund_restriction"]
            general_notes = row["general_notes"]
            lbs_notes = row["lbs_notes"]
            
            self.stdout.write(f"\tProcessing {title}...")

            # Fund
            fund = _create_fund(
                account,
                cost_center,
                fund,
                title,
                manager,
                mtf_authority,
                fund_purpose,
                fund_summary,
                fund_restriction,
                general_notes,
                lbs_notes,
            )


def _create_staff(name, email):
    # Staff (persons) might already exist, via small initial load
    staff, created = GeStaff.objects.get_or_create(name=name,
                                                 email=email)
    staff.save()
    return staff


def _create_unit(name):
    # units might already exist
    unit, created = GeUnit.objects.get_or_create(name=name)

    unit.save()
    return unit


def _create_fund(acct, cost_center, fund, title, manager, mtf_authority, fund_purpose, fund_summary, fund_restriction, general_notes, lbs_notes):
    # get foreign keys first
    fund_mgr = GeStaff.objects.get(id=manager)
    fund_auth = GeStaff.objects.get(id=mtf_authority)
    row, created = GeFund.objects.get_or_create(
        account=acct,
        cost_center=cost_center,
        fund=fund,
        title=title,
        manager=fund_mgr,
        mtf_authority=fund_auth,
        fund_purpose=fund_purpose,
        fund_summary=fund_summary,
        fund_restriction=fund_restriction,
        general_notes=general_notes,
        lbs_notes=lbs_notes,
    )

    row.save()
    return row


class Command(BaseCommand):
    help = "Load QDB data from CSV into database"

    def add_arguments(self, parser):
        parser.add_argument("staff_file")
        parser.add_argument("unit_file")
        parser.add_argument("funds_file")

    def handle(self, *args, **options):
        staff = options["staff_file"]
        unit = options["unit_file"]
        accounts = options["funds_file"]
        populate_staff(self, staff)
        populate_units(self, unit)
        populate_funds(self, accounts)
