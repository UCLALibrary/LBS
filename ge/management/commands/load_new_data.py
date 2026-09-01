import pandas as pd
from django.core.management.base import BaseCommand
from ge.models import GeFund, GeRecipient, GeStaff, GeUnit


def import_excel_data(self, funds_file):
    """Import data from an Excel file into the specified Django model."""
    data = get_data_from_excel(funds_file)
    for row in data:
        aul = row["UL/AUL"]
        head = row["Unit Head"]
        unit_name = row["Unit"]
        if not recipient_exists(aul, unit_name, "AUL"):
            add_recipient(aul, unit_name, "AUL")
        if not recipient_exists(head, unit_name, "Head"):
            add_recipient(head, unit_name, "Head")
        if fund_exists(row["Account"], row["CC"], row["Fund"]):
            update_fund(self, row)
        else:
            create_fund(self, row)


def update_fund(self, row: dict) -> None:
    """Update an existing GeFund record with the given data."""
    self.stdout.write(f"Updating fund: {row['Account']} - {row['CC']} - {row['Fund']}")
    fund = GeFund.objects.get(
        account=row["Account"], cost_center=row["CC"], fund=row["Fund"]
    )
    fund.title = row["Fund Title"]
    fund.manager = row["Fund Manager"]
    fund.mtf_authority = row["MTF_Authority"]
    fund.fund_purpose = row["Fund Purpose"]
    fund.fund_restriction = row["Fund Restriction"]
    fund.unit = get_unit(row["Unit"])
    fund.home_unit_dept = row["Home Unit/Dept"]
    fund.projected_annual_income = row["Projected Annual Income\nAs of March 2026"]
    if row["Last FY Activity"] != "FY26":
        fund.lbs_notes += f" {row['Last FY Activity']}"
    fund.active = True
    fund.save()


def create_fund(self, row: dict) -> None:
    """Create a new GeFund record with the given data."""
    self.stdout.write(f"Creating fund: {row['Account']} - {row['CC']} - {row['Fund']}")
    fund = GeFund(
        account=row["Account"],
        cost_center=row["CC"],
        fund=row["Fund"],
        title=row["Fund Title"],
        manager=row["Fund Manager"],
        mtf_authority=row["MTF_Authority"],
        fund_purpose=row["Fund Purpose"],
        fund_restriction=row["Fund Restriction"],
        unit=get_unit(row["Unit"]),
        home_unit_dept=row["Home Unit/Dept"],
        projected_annual_income=row["Projected Annual Income\nAs of March 2026"],
        lbs_notes="" if row["Last FY Activity"] == "FY26" else row["Last FY Activity"],
        active=True,
    )
    fund.save()


def get_data_from_excel(excel_file: str) -> list[dict]:
    """Read data from an Excel file (either .xls or .xlsx).
    Only reads data from the first worksheet, which is all we need.

    Returns a list of dictionaries, one for each row of data,
    keyed by the column names in the Excel file's header row.
    """
    # keep_default_na=False: Return empty strings instead of NaN or na.
    # dtype=object: Return the actual data from Excel, not an intepretation of it.
    df = pd.read_excel(excel_file, keep_default_na=False, dtype=object)
    # Uses pandas.DataFrame.to_dict with 'records' parameter:
    # 'records' : list like [{column -> value}, … , {column -> value}]
    return df.to_dict("records")


def get_or_create_staff(name: str) -> GeStaff:
    """Get or create a GeStaff record with the given name."""
    staff, created = GeStaff.objects.get_or_create(
        name=name, defaults={"email": "fake@library.ucla.edu"}
    )
    return staff


def recipient_exists(staff_name: str, unit_name: str, staff_role: str) -> bool:
    """Check if a GeRecipient record exists with the given staff name, unit name, and role."""
    recipient_staff = get_or_create_staff(staff_name)
    recipient_unit = get_unit(unit_name)
    return GeRecipient.objects.filter(
        recipient=recipient_staff, unit=recipient_unit, role=staff_role
    ).exists()


def fund_exists(account: str, cost_center: str, fund: str) -> bool:
    """Check if a GeFund record exists with the given account, cost_center, and fund values."""
    return GeFund.objects.filter(
        account=account, cost_center=cost_center, fund=fund
    ).exists()


def add_staff(name: str) -> GeStaff:
    """Create a new GeStaff record with the given name and return it."""
    staff = GeStaff(name=name, email="fake@library.ucla.edu")
    staff.save()
    return staff


def add_unit(name: str) -> GeUnit:
    """Create a new GeUnit record with the given name and return it."""
    unit = GeUnit(name=name)
    unit.save()
    return unit


def get_unit(name: str) -> GeUnit | None:
    """Return the GeUnit record with the given name, or None if it doesn't exist."""
    return GeUnit.objects.filter(name=name).first()


def add_recipient(staff_name: str, unit_name: str, staff_role: str):
    """Create a new GeRecipient record with the given name and role, and return it."""
    recipient_staff = get_or_create_staff(staff_name)
    recipient_unit = get_unit(unit_name)
    if not recipient_unit:
        recipient_unit = add_unit(unit_name)
    recipient = GeRecipient(
        recipient=recipient_staff, unit=recipient_unit, role=staff_role
    )
    recipient.save()


class Command(BaseCommand):

    help = "Loads new GE data from Excel file to GeFund."

    def add_arguments(self, parser):
        parser.add_argument("funds_file")

    def handle(self, *args, **options):
        funds_file = options["funds_file"]
        import_excel_data(self, funds_file)
