from django.core.management.base import BaseCommand
from ge.models import LibraryData
import csv


def export_library_data():
    library_data_records = (
        LibraryData.objects.all()
        .order_by("unit")
        .values_list(
            "unit",
            "home_unit_dept",
            "fund_title",
            "fund_type",
            "reg_fdn",
            "fund_manager",
            "ucop_fdn_no",
            "fau_fund_no",
            "fau_account",
            "fau_cost_center",
            "fau_fund",
            "ytd_appropriation",
            "ytd_expenditure",
            "commitments",
            "operating_balance",
            "max_mtf_trf_amt",
            "total_balance",
            "mtf_authority",
            "total_fund_value",
            "projected_annual_income",
            "fund_summary",
            "fund_purpose",
            "notes",
            "home_dept",
            "fund_restriction",
            "new_fund",
            "lbs_notes",
        )
    )

    with open("library_data_export.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "unit",
                "home_unit_dept",
                "fund_title",
                "fund_type",
                "reg_fdn",
                "fund_manager",
                "ucop_fdn_no",
                "fau_fund_no",
                "fau_account",
                "fau_cost_center",
                "fau_fund",
                "ytd_appropriation",
                "ytd_expenditure",
                "commitments",
                "operating_balance",
                "max_mtf_trf_amt",
                "total_balance",
                "mtf_authority",
                "total_fund_value",
                "projected_annual_income",
                "fund_summary",
                "fund_purpose",
                "notes",
                "home_dept",
                "fund_restriction",
                "new_fund",
                "lbs_notes",
            ]
        )
        for record in library_data_records:
            writer.writerow(record)


class Command(BaseCommand):
    help = "Exports librarydata records to a CSV file."

    def handle(self, *args, **options):
        export_library_data()
