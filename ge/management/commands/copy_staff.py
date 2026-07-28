from django.core.management.base import BaseCommand
from ge.models import GeStaff
from qdb.models import Staff


def populate_staff(self):
    source_records = Staff.objects.all()

    target_instances = [
        GeStaff(
            name=record.name,
            email=record.email
        )
        for record in source_records
    ]

    GeStaff.objects.bulk_create(target_instances)


class Command(BaseCommand):

    help = "Copies staff records from the QDB database to the GE database."

    def handle(self, *args, **options):
        populate_staff(self)

