import pandas as pd
from django.core.management.base import BaseCommand
from ge.models import GeFund, GeRecipient, GeStaff, GeUnit


def import_excel_data(excel_file: str) -> None:
    """Import data from an Excel file into the specified Django model."""
    data = get_data_from_excel(excel_file)
    for row in data:
        aul = row["UL/AUL"]
        head = row["Unit Head"]
        unit_name = row["Unit"]
        add_recipient(aul, unit_name, "AUL")
        add_recipient(head, unit_name, "Head")
        if fund_exists(row["Account"], row["CC"], row["Fund"]):
            update_fund(row)
        else:
            create_fund(row)


def update_fund(row: dict) -> None:
    """Update an existing GeFund record with the given data."""
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
    fund.projected_annual_income = row[" Projected Annual Income As of March 2026 "]
    if row["Last FY Activity"] != "FY26":
        fund.lbs_notes += f" {row['Last FY Activity']}"
    fund.active = True
    fund.save()


def create_fund(row: dict) -> None:
    """Create a new GeFund record with the given data."""
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
        projected_annual_income=row[" Projected Annual Income As of March 2026 "],
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


def add_recipient(name: str, unit_name: str, role: str) -> GeRecipient:
    """Create a new GeRecipient record with the given name and role, and return it."""
    staff = GeStaff.objects.filter(name=name).first()
    if not staff:
        staff = add_staff(name)
    unit = GeUnit.objects.filter(name=unit_name).first()
    if not unit:
        unit = add_unit(unit_name)
    recipient = GeRecipient(staff=staff, unit=unit, role=role)
    recipient.save()
    return recipient


def get_fund_mapping() -> dict:
    """Return a mapping of Excel column names to model field names
    for the various imports of data.
    """
    GeFund = {
        "Fiscal Year": "ignore",
        "Quarterly": "ignore",
        "Ledger Month": "ignore",
        "UL/AUL": "gerecipient",
        "Fund Type": "ignore",
        "Unit Head": "gerecipient",
        "Unit": "unit",
        "Home Unit/Dept": "home_unit_dept",
        "Fund Title": "title",
        "Fund Type": "ignore",
        "Regental/ Foundation": "ignore",
        "Fund Manager": "manager",
        "UCOP/ Foundation No.": "ignore",
        "Account": "account",
        "CC": "cost_center",
        "Fund": "fund",
        "YTD Appropriation": "ignore",
        "YTD Expenditure": "ignore",
        "Commitments": "ignore",
        "Operating Balance": "ignore",
        "MTF_Authority": "mtf_authority",
        " Projected Annual Income As of March 2026 ": "projected_annual_income",
        "Fund Purpose": "fund_purpose",
        "Fund Restriction": "fund_restriction",
        "Last FY Activity": "maybeappendtolbsnotes",
    }
    return GeFund


class Command(BaseCommand):

    help = "Loads new GE data from Excel file to GeFund."

    def handle(self, *args, **options):
        # TODO: Implement the logic to load new data from an Excel file into the GeFund model.
        """
        This command should read data from a specified Excel file and create new GeFund instances
        Read Excel file into dictionary, canabilize get_data_from_excel()
        for each row in the dictionary:
            If the incoming Account + CC + Fund values exactly match an existing record in GeFund,
                update the relevant other columns in the matched record from the Excel data.
            If the incoming data does not exactly match an existing record, create a new GeFund
                record with the incoming data.
            Ignore columns A-C, E, J, K, M, Q-T
            Several columns of incoming data will need special handling:
                D (UL/AUL) and F (Unit Head): Create (or look up and use) a GeStaff record to
                    create a GeRecipient record with the appropriate role.
                G (Unit): Create (or look up and use) a GeUnit record.
                H (Home Unit/Dept): Import into new field GeFund.home_unit_dept.
                L (Fund Manager) and U (MTF_Authority): Import into the corresponding
                    redefined fields.
                V (Projected Annual Income): Import into the new GeFund.projected_annual_income.
                Y (Last FY Activity): LBS asked for an Active vs Inactive flag.  However, they also
                    said their Excel data represents “current active list of funds”.  So:
                        For every GeFund record added/updated via import, set GeFund.active = True.
                        If column Y contains a value other than “FY26”, append the value to the
                            record's lbs_notes value.
        """
        pass
