from django.core.management.base import BaseCommand
from qdb.scripts.orchestrator import Orchestrator
from qdb.scripts.settings import REPORTS_DIR, DEFAULT_RECIPIENTS, UL_NAME


class Command(BaseCommand):
    help = "Run the legacy QDB reporting tool"

    def add_arguments(self, parser):
        parser.add_argument("-l", "--list_units", action="store_true",
                            help="List all the units")
        parser.add_argument("-y", "--year", type=int,
                            help="Year of the report")
        parser.add_argument("-m", "--month", type=int,
                            help="Month number of the report")
        parser.add_argument("-u", "--units", nargs='+',
                            help="Unit ID number; if omitted all units will receive reports")
        parser.add_argument("-e", "--email", action="store_true",
                            help="Email the report to the recipients")
        parser.add_argument("-r", "--list_recipients", action="store_true",
                            help="Display the list of people to email for each report")
        parser.add_argument("-o", "--override_recipients", action="store_const", const=None,
                            help="List of dev(s) to email for each report")

    def handle(self, *args, **options):
        list_units = options["list_units"]
        year = options["year"]
        month = options["month"]
        units = options["units"]
        email = options["email"]
        list_recipients = options["list_recipients"]
        override_recipients = options["override_recipients"]

        # using code from __main__ of orchestrator
        try:
            orchestrator = Orchestrator(REPORTS_DIR, DEFAULT_RECIPIENTS)
            if list_units is True:
                print(orchestrator.list_units())
            yyyymm = orchestrator.validate_date(year, month, yyyymm=True)
            units = orchestrator.validate_units(units)
            orchestrator.run(yyyymm, units, send_email=email,
                             list_recipients=list_recipients, override_recipients=override_recipients)
            return
        except ValueError as e:
            exit(e)
