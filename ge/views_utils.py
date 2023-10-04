from django.db.models import Model
from pandas import read_excel


def import_excel_data(excel_file: str, model: Model) -> None:
    """Import Excel data into a table.

    Parameters:
    excel_file -- The name of the Excel file.
    model -- The Django model to use.
    """
    data = get_data_from_excel(excel_file)
    # Get the Excel -> model field mapping for this model.
    # model._meta is internal, but apparently well and permanently supported.
    mapping = get_mapping(model._meta.object_name)
    # Clear out old data before importing.
    model.objects.all().delete()
    # Iterate through rows of data, creating and saving an object for each.
    for row in data:
        # Create initial empty object.
        obj = model()
        for excel_name, field_name in mapping.items():
            # Set the value for each field.
            setattr(obj, field_name, row[excel_name])
        obj.save()
    # TODO: Logging
    # print(f"Created: {model.objects.count()} objects")


def get_data_from_excel(excel_file: str) -> list[dict]:
    """Read data from an Excel file (either .xls or .xlsx).
    Only reads data from the first worksheet, which is all we need.

    Returns a list of dictionaries, one for each row of data,
    keyed by the column names in the Excel file's header row.
    """
    # keep_default_na=False: Return empty strings instead of NaN or na.
    # dtype=object: Return the actual data from Excel, not an intepretation of it.
    df = read_excel(excel_file, keep_default_na=False, dtype=object)
    # Uses pandas.DataFrame.to_dict with 'records' parameter:
    # 'records' : list like [{column -> value}, … , {column -> value}]
    return df.to_dict("records")


def get_mapping(model_name: str) -> dict:
    """Return a mapping of Excel column names to model field names
    for the various imports of data.

    Parameter:
    model_name -- The name of the Django model.
    """
    maps = {
        "BFSImport": {
            "Source": "source",
            "Organization": "organization",
            "OrgNumber": "fau_org",
            "Department": "department",
            "DeptNumber": "fau_dept",
            "FundType/Source": "fund_type",
            "Fund": "fau_fund",
            "FundOld": "fund_old",
            "Purpose": "purpose",
            "Description": "description",
            "BeginningBalance": "beginning_balance",
            "Contributions": "contributions",
            "InvestmentIncome": "investment_income",
            "GiftFeePayments": "gift_fee_payments",
            "RealGl": "real_gl",
            "UnrealGL": "unreal_gl",
            "FoundationTransfers": "foundation_transfers",
            "TransfersToUniv": "transfers_to_univ",
            "Expenditures": "expenditures",
            "Transfers/Adj": "transfers_adj",
            "EndingBalance": "ending_balance",
            "Available": "available",
            "Unavailable": "unavailable",
            "Principal": "principal",
            "MarketValue": "market_value",
            "ProjectedIncome": "projected_income",
            "SortAccount": "sort_account",
            "FundSummary": "fund_summary",
            "FundMemo": "fund_memo",
            "PeriodStart": "period_start",
            "PeriodEnd": "period_end",
        },
        "CDWImport": {
            "Ledger Year Month": "ledger_year_month",
            "FYE Proc Indicator": "fye_proc_indicator",
            "Account Org Code": "fau_org",
            "Fund Group": "fund_group",
            "Account Department Code": "fau_dept",
            "Location Code": "fau_location",
            "Account Number": "fau_account",
            "Cost Center Code": "fau_cost_center",
            "Fund Number": "fau_fund",
            "Fund Title": "fau_fund_title",
            "Inception-to-Date Appropriation": "inception_to_date_appropriation",
            "Inception-to-Date Financial": "inception_to_date_financial",
            "Encum&ML": "encum_ml",
            "Operating Balance": "operating_balance",
        },
        "MTFImport": {
            "org_code": "fau_org",
            "org_title": "organization",
            "division_code": "division_code",
            "division_title": "division_title",
            "sub_division_code": "sub_division_code",
            "sub_division_title": "sub_division_title",
            "dept_code": "fau_dept",
            "dept_title": "department",
            "fund_id": "fund_id",
            "fund_nbr": "fund_nbr",
            "fund_desc": "fund_description",
            "fiscal_yr": "fiscal_year",
            "last_fiscal_month_closed": "last_fiscal_month_closed",
            "fdn_dept": "fdn_dept",
            "fdn_dept_desc": "fdn_dept_description",
            "univ_dept": "univ_dept",
            "univ_dept_desc": "univ_dept_description",
            "univ_fund_nbr": "fau_fund",
            "univ_fund_desc": "fau_fund_title",
            "use_code": "use_code",
            "use_desc": "use_description",
            "available_bal": "available_balance",
            "unavailable_bal": "unavailable_balance",
            "pending_transfer_bal": "pending_transfer_balance",
            "max_transfer_bal": "max_transfer_balance",
            "fund_purpose": "fund_purpose",
            "fund_restriction": "fund_restriction",
            "signature_ind": "signature_ind",
            "preparer_phone_num": "preparer_phone_number",
        },
    }
    return maps[model_name]
