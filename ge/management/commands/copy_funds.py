from django.core.management.base import BaseCommand
from ge.models import GeFund, GeStaff
from qdb.models import  Account, Recipient


def populate_funds(self):
    acct_records = Account.objects.all()
    
    fund_instances = [
        GeFund(
            account=record.account,
            cost_center=record.cost_center,
            #fund=?,
            title=record.title[:100],
            manager=get_manager(record.unit),
            mtf_authority=get_mtf_auth(record.unit)
        )
        for record in acct_records
    ]

    GeFund.objects.bulk_create(fund_instances)


def get_manager(mgr_unit):
    return Recipient.objects.filter(unit=mgr_unit).filter(role="Head")


def get_mtf_auth(mtf_auth_unit):
    return Recipient.objects.filter(unit=mtf_auth_unit).filter(role="AUL")


class Command(BaseCommand):

    help = "Copies fund records from the QDB database to the GE database."

    def handle(self, *args, **options):
        populate_funds(self)

