from django.core.management.base import BaseCommand
from ge.models import GeUnit, LibraryData


def populate_units(self):
    unit_records = LibraryData.objects.all().values_list("unit", flat=True).distinct()

    unit_instances = [GeUnit(name=record) for record in unit_records]

    GeUnit.objects.bulk_create(unit_instances)


class Command(BaseCommand):

    help = "Copies unit records from the LibraryData table to the GeUnit table."

    def handle(self, *args, **options):
        populate_units(self)
