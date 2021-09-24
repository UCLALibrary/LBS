
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from qdb.models import Staff, Unit

import csv

def create_staff(self, staff_file):
    """
    Does initial creation of Staff
    """
    self.stdout.write(f"Parsing {staff_file}")
    # Windows-derived CSV has leading BOM, so specify utf-8-sig, not utf-8
    with open(staff_file, encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile, dialect="excel")
        # Field names from CSV, for reference:
        # ['department_code', 'employee_name', 'employee_id', 'ucla_id', 'email', job_code', 'job_code_desc', 'job_class_description', 'supervisor', 'department', 'aul_ul']
        for row in reader:
            # Get relevant data from CSV
            staff_id = row["id"]
            name = row["name"]
            email = row["email"]

            self.stdout.write(f"\tProcessing {name}...")

            # Staff
            staff = _get_staff(staff_id, name, email)

def create_unit(self, unit_file):
    """
    Does initial creation of Units
    """
    self.stdout.write(f"Parsing {unit_file}")
    # Windows-derived CSV has leading BOM, so specify utf-8-sig, not utf-8
    with open(unit_file, encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile, dialect="excel")
        # Field names from CSV, for reference:
        # ['department_code', 'employee_name', 'employee_id', 'ucla_id', 'email', job_code', 'job_code_desc', 'job_class_description', 'supervisor', 'department', 'aul_ul']
        for row in reader:
            # Get relevant data from CSV
            name = row["name"]
            head = row["head"]
            aul = row["aul"]

            self.stdout.write(f"\tProcessing {name}...")

            # Staff
            unit = _get_unit(name, head, aul)

def _get_staff(staff_id, name, email):
    # Users might already exist, via small initial load
    staff, created = Staff.objects.get_or_create(staff_id=staff_id, name=name, email=email)
    staff.save()
    return staff

def _get_unit(name, head, aul):
    # units might already exist, via small initial load
    unit, created = Unit.objects.get_or_create(name=name)
    if head:
        member1 = Staff.objects.get(staff_id=head)
        unit.members.add(member1)
    if aul:
        member2 = Staff.objects.get(staff_id=aul)
        unit.members.add(member2)

    unit.save()
    return unit

class Command(BaseCommand):
    help = "Load QDB data from CSV into database"

    def add_arguments(self, parser):
        parser.add_argument("staff_file")
        parser.add_argument("unit_file")

    def handle(self, *args, **options):
        staff = options["staff_file"]
        unit = options["unit_file"]
        create_staff(self, staff)
        create_unit(self, unit)

