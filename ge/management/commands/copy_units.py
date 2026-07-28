from django.core.management.base import BaseCommand
from ge.models import GeUnit
from qdb.models import Unit


def populate_units(self):
    source_records = Unit.objects.all()

    target_instances = [
        GeUnit(
            name=record.name
        )
        for record in source_records
    ]

    GeUnit.objects.bulk_create(target_instances)


class Command(BaseCommand):

    help = "Copies unit records from the QDB database to the GE database."

    def handle(self, *args, **options):
        populate_units(self)

