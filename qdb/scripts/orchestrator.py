from itertools import groupby
import arrow
import logging
import os
from qdb.models import Account, Recipient, Unit
from qdb.scripts.settings import UL_NAME
from qdb.scripts import fetcher, formatter, sender
from qdb.scripts.parser import Parser

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self, reports_dir, recipients):
        self.reports_dir = reports_dir
        self.recipients = recipients

    def validate_date(self, year=None, month=None, yyyymm=False):
        today = arrow.now()
        if year is None and month is None:
            report_date = today.shift(months=-1)
            month = report_date.month
            year = report_date.year
        elif not (year and month):
            raise ValueError("ERROR: You must supply both year and month or neither")
        elif month < 1 or month > 12:
            raise ValueError("ERROR: month must be a number from 1 to 12")
        # arrow.now() defaults to local timezone; arrow.get() defaults to UTC...
        # Must tell arrow.get() to use same timezone as today.
        elif arrow.get(year=year, month=month, day=1, tzinfo=today.tzinfo) > today:
            raise ValueError("ERROR: cannot request a future report")
        if yyyymm is True:
            return f"{year}{month:02}"
        return year, month

    def get_all_units(self):
        # Caller expects a list
        units = Unit.objects.all().order_by("name")
        return [unit for unit in units]

    def get_units(self, unit_id: int | None = None) -> list:
        # Caller didn't ask for a specific unit: return all
        if unit_id is None:
            return self.get_all_units()
        unit = Unit.objects.get(id=unit_id)
        # Caller asked for the "All units" "unit"
        if unit.name == "All units":
            return self.get_all_units()
        else:
            # Caller needs a list
            return [unit]

    def list_units(self) -> str:
        units = self.get_all_units()
        name_length = max([len(unit.name) for unit in units])
        header = "\nID | Name"
        bar = "---|" + "-" * (name_length + 1)
        msg = [header, bar]
        for unit in units:
            msg.append(f"{unit.id:>2} | {unit.name}")
        return "\n".join(msg)

    def get_accounts_for_unit(self, unit_id: int) -> list[tuple[str, list[str]]]:
        """Gets account and cost center information for a unit.
        Returns a list of tuples, with each tuple consisting of 2 elements:
        1: account
        2: list of cost centers
        Example response (partial):
        [('606000', ['AD', 'LB']), ('606000', ['LM'])]
        """

        # Data can be obtained by a union of 2 queries which each use the
        # postgresql-specific string_agg() function, but that's complex and not
        # database-agnostic.  Instead, use 2 simple ORM queries and basic python.

        # Separate Library Materials (LM) from other cost centers, as requested.
        lm_data = (
            Account.objects.filter(unit_id=unit_id, cost_center="LM")
            .values_list("account", "cost_center")
            .order_by("account", "cost_center")
        )
        # Legacy query explicitly excluded accounts with no cost center.
        non_lm_data = (
            Account.objects.filter(unit_id=unit_id)
            .exclude(cost_center__in=["LM", ""])
            .values_list("account", "cost_center")
            .order_by("account", "cost_center")
        )

        accounts = []
        for data in [lm_data, non_lm_data]:
            # Each "data" is a Django QuerySet containing a list of tuples
            # (account, cost center), and many accounts have multiple cost centers.
            # Example input: [("606000", "AD"), ("606000", "LB")]
            # Convert each data list into a tuple (account, [list of cost centers]).
            # Example output: [("606000", ["AD", "LB"])]
            structured_accounts = [
                (k, [v for _, v in g]) for k, g in groupby(list(data), lambda x: x[0])
            ]
            accounts.extend(structured_accounts)

        # Make sure integrated list of accounts is sorted.
        return sorted(accounts)

    def cleanup_reports_dir(self):
        for f in os.listdir(self.reports_dir):
            if f == ".gitignore":
                continue
            try:
                os.remove(os.path.join(self.reports_dir, f))
            except FileNotFoundError:
                logger.error(f"Could not delete from reports directory: {f}")

    def get_recipients(self, unit_id: int, unit_name: str) -> set:
        """Gets the recipients (email addresses) to which a unit's report
        should be sent.
        """

        # This is set on class instantiation based on DEFAULT_RECIPIENTS,
        # either to developers (dev mode) or to LBS (prod mode).
        recipients = set(self.recipients)

        # Legacy code alert: Apparently, if unit_name parameter is "LBS", only the
        # unit head should get the report, instead of all unit-designated recipients.
        # Normally, everyone in LBS_RECIPIENTS (which is used for DEFAULT_RECIPIENTS
        # in production) will get a copy of every report.
        if unit_name == "LBS":
            roles = ["head"]
        else:
            roles = ["aul", "head", "assoc"]

        unit_recipients = Recipient.objects.filter(
            unit_id=unit_id, role__in=roles
        ).values_list("recipient__email", flat=True)

        recipients.update(unit_recipients)
        return recipients

    def generate_filename(self, unit_name, yyyymm):
        name = f"{unit_name.replace(' ','_')}_{yyyymm[:4]}_{yyyymm[4:]}.xlsx"
        return os.path.join(self.reports_dir, name)

    def run(
        self,
        yyyymm,
        units,
        send_email=False,
        override_recipients=None,
        list_recipients=False,
    ):
        for unit in units:
            unit_id = unit.id
            unit_name = unit.name
            if override_recipients is not None:
                recipients = override_recipients
            else:
                recipients = self.get_recipients(unit_id, unit_name)

            if list_recipients is True:
                # print statements in this block are for command-line, not logged.
                print(f"\n{unit_name} recipients:")
                for r in sorted(recipients):
                    print(f"-- {r}")
                    continue
            print("See logs for other output.")
            parser = Parser(yyyymm, unit_name)
            for account, cc_list in self.get_accounts_for_unit(unit_id):
                logger.info(
                    f"Running {yyyymm} report of {account}{cc_list} for unit {unit_name}"
                )
                rows = fetcher.get_qdb_data(yyyymm, account, cc_list)
                if len(rows) == 0:  # pragma: no cover
                    logger.warning(f"No data from QDB for {account}{cc_list}")
                    continue
                result = parser.add_account(unit_id, account, cc_list, rows)
                if result is False:  # pragma: no cover
                    logger.warning(f"Account {account} is empty. Exclude from report")
            if len(parser.data["accounts"]) == 0:  # pragma: no cover
                logger.warning(f"All accounts empty. No report generated for {unit}")
                continue
            filename = self.generate_filename(unit_name, yyyymm)
            formatter.generate_report(parser.data, filename)

            if send_email is True:
                sender.send_report(parser.data, filename, recipients)
                os.remove(filename)
                logger.info(f"Sent report {filename} to {recipients}")
            else:
                logger.info(f"Generated report at {filename}")
