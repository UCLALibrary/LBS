from django.core.management.base import BaseCommand
from ge.models import GeStaff, LibraryData


def populate_staff(self):
    mgr_records = (
        LibraryData.objects.all().values_list("fund_manager", flat=True).distinct()
    )
    mtf_auth_records = (
        LibraryData.objects.all().values_list("mtf_authority", flat=True).distinct()
    )
    deduped_merged_records = set(mgr_records).union(set(mtf_auth_records))

    staff_instances = [
        GeStaff(name=record, email="fake@library.ucla.edu")
        for record in deduped_merged_records
    ]

    GeStaff.objects.bulk_create(staff_instances)


class Command(BaseCommand):

    help = "Copies staff records from the LibraryData table to the GeStaff table."

    def handle(self, *args, **options):
        populate_staff(self)
