from django.core.management.base import BaseCommand
from ge.models import GeFund, GeStaff, LibraryData


def populate_funds(self):
    acct_records = LibraryData.objects.all()

    fund_instances = [
        GeFund(
            account=record.fau_account,
            cost_center=record.fau_cost_center,
            fund=record.fau_fund,
            title=record.fund_title,
            manager=get_manager(record.fund_manager),
            mtf_authority=get_mtf_auth(record.mtf_authority),
            fund_purpose=record.fund_purpose,
            fund_summary=record.fund_summary,
            fund_restriction=record.fund_restriction,
            general_notes=record.notes,
            lbs_notes=record.lbs_notes,
        )
        for record in acct_records
    ]

    GeFund.objects.bulk_create(fund_instances)


def get_manager(mgr_name):
    return GeStaff.objects.filter(name=mgr_name).first()


def get_mtf_auth(mtf_auth_name):
    return GeStaff.objects.filter(name=mtf_auth_name).first()


class Command(BaseCommand):

    help = "Copies fund records from the QDB database to the GE database."

    def handle(self, *args, **options):
        populate_funds(self)
