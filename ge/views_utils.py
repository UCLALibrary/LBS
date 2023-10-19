import logging
from django.db.models import Model
from pandas import read_excel
from ge.models import BFSImport, CDWImport, LibraryData, MTFImport

logger = logging.getLogger(__name__)


def import_excel_data(excel_file: str, model: Model) -> None:
    """Import Excel data into a table.

    Parameters:
    excel_file -- The name of the Excel file.
    model -- The Django model to use.
    """
    data = get_data_from_excel(excel_file)
    # Get the Excel -> model field mapping for this model.
    # model._meta is internal, but apparently well and permanently supported.
    model_name = model._meta.object_name
    mapping = get_mapping(model_name)
    # Clear out old data before importing.
    model.objects.all().delete()
    try:
        # Iterate through rows of data, creating and saving an object for each.
        for row in data:
            # Create initial empty object.
            obj = model()
            for excel_name, field_name in mapping.items():
                # Set the value for each field.
                setattr(obj, field_name, row[excel_name])
            obj.save()
    except KeyError as ex:
        # Add useful info and re-raise up to caller
        error_message = f"Unexpected column {str(ex)} in {excel_file} for {model_name}"
        raise KeyError(error_message) from None


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
        "LibraryData": {
            "ID": "original_id",
            "UnitGrande": "unit_grande",
            "Unit": "unit",
            "Home Unit/Dept": "home_unit_dept",
            "Fund Title": "fund_title",
            "Fund Type": "fund_type",
            "Reg/Fdn": "reg_fdn",
            "Fund Manager": "fund_manager",
            "UCOP/ FDN No": "ucop_fdn_no",
            "Fund No": "fau_fund_no",
            "Account": "fau_account",
            "CC": "fau_cost_center",
            "Fund": "fau_fund",
            "YTD Appropriation": "ytd_appropriation",
            "YTD Expenditure": "ytd_expenditure",
            "Commitments": "commitments",
            "Operating Balance": "operating_balance",
            "Max MTF Trf Amt": "max_mtf_trf_amt",
            "Total Balance": "total_balance",
            "MTF_Authority": "mtf_authority",
            "Total Fund Value": "total_fund_value",
            "Projected Annual Income": "projected_annual_income",
            "Fund Summary": "fund_summary",
            "Fund Purpose": "fund_purpose",
            "Notes": "notes",
            "Home Dept": "home_dept",
            "FundRestriction": "fund_restriction",
            "NewFund": "new_fund",
            "LBS Notes": "lbs_notes",
        },
    }
    return maps[model_name]


def add_funds() -> None:
    """Add funds from campus data not already in LibraryData
    for use in reports.
    """

    # Original Access query qryAddNew_2:
    # Add rows to LibraryData from CDWImport where
    # (fau_account, fau_cost_center, fau_fund) doesn't already exist.
    incoming_funds = CDWImport.objects.all().values(
        "fau_account", "fau_cost_center", "fau_fund"
    )
    current_funds = LibraryData.objects.all().values(
        "fau_account", "fau_cost_center", "fau_fund"
    )
    for f in incoming_funds:
        if f not in current_funds:
            new_fund = LibraryData(
                fau_account=f["fau_account"],
                fau_cost_center=f["fau_cost_center"],
                fau_fund=f["fau_fund"],
                new_fund="Y",
            )

            # Original Access query qryAddNew_3:
            # Match on BFSImport data to set other values in the new fund.
            # Match is only on fau_fund, which often can find multiple rows,
            # but the relevant fields appear to be the same for any given fund.
            # Take the "first" match - if any, since match is not guaranteed.
            bfs_funds = BFSImport.objects.filter(fau_fund=new_fund.fau_fund)
            if bfs_funds.exists():
                bfs_fund = bfs_funds[0]
                new_fund.fund_title = bfs_fund.description
                new_fund.fund_type = bfs_fund.fund_type
                new_fund.fund_summary = bfs_fund.fund_summary
                new_fund.fund_purpose = bfs_fund.purpose

                # Original Access query qryAddNew_4 - queryAddNew_7:
                # Normalize reg_fdn and fund_type values.
                # These are converted from Access and assume all data... matches assumptions.
                # These are dependent on a matching BFSImport row being found above.
                if "FOUNDATION" in new_fund.fund_type.upper():
                    new_fund.reg_fdn = "F"
                if "REGENTAL" in new_fund.fund_type.upper():
                    new_fund.reg_fdn = "R"
                if "ENDOWMENT" in new_fund.fund_type.upper():
                    new_fund.fund_type = "Endowment"
                if "EXPENDITURE" in new_fund.fund_type.upper():
                    new_fund.fund_type = "Current Expenditure"

            else:
                # No matching BFSImport row found, so log a message.
                logger.warning(
                    f"No matching BFS (consolidated) data found for {new_fund.fau_fund=}"
                )

            # Original Access query qryAddNew_8:
            # Clear the "new_fund" flag.
            new_fund.new_fund = "N"

            # Finally, save the new LibraryData record.
            logger.info(f"Added fund: {new_fund}")
            new_fund.save()


def update_data() -> None:
    """Update LibraryData rows to final state before report generation."""

    # Original Access query qryAAA_0Clear:
    # Set several financial values to 0 for all rows.
    cnt = LibraryData.objects.all().update(
        ytd_appropriation=0,
        ytd_expenditure=0,
        commitments=0,
        operating_balance=0,
        max_mtf_trf_amt=0,
        projected_annual_income=0,
        total_fund_value=0,
    )
    logger.info(f"qryAAA_0Clear: {cnt} updated")

    # Original Access query qryAAA_1UpdateMTF (and duplicate qryAAA_1UpdateMTF1):
    # Update relevant LibraryData rows from MTF data (first matching row only, if any).
    cnt = 0
    for ld in LibraryData.objects.all():
        if ld.ucop_fdn_no:
            mtf_rows = MTFImport.objects.filter(fund_nbr=ld.ucop_fdn_no)
            if mtf_rows.exists():
                mtf = mtf_rows[0]
                ld.fund_restriction = mtf.fund_restriction
                ld.max_mtf_trf_amt = mtf.max_transfer_balance
                ld.save()
                cnt += 1
    logger.info(f"qryAAA_1UpdateMTF: {cnt} updated")

    # Original Access query qryAAA_2ProjIncomFound:
    # Update projected annual income from BFS data (Foundation funds).
    cnt = 0
    for ld in LibraryData.objects.all():
        if ld.ucop_fdn_no:
            bfs_rows = BFSImport.objects.filter(fau_fund=ld.ucop_fdn_no, source="F")
            if bfs_rows.exists():
                bfs = bfs_rows[0]
                ld.projected_annual_income = bfs.projected_income
                ld.save()
                cnt += 1
    logger.info(f"qryAAA_2ProjIncomFound: {cnt} updated")

    # Original Access query qryAAA_2ProjIncomReg:
    # Update projected annual income from BFS data (Regental funds).
    cnt = 0
    for ld in LibraryData.objects.all():
        if ld.fau_fund:
            bfs_rows = BFSImport.objects.filter(fau_fund=ld.fau_fund, source="R")
            if bfs_rows.exists():
                bfs = bfs_rows[0]
                ld.projected_annual_income = bfs.projected_income
                ld.save()
                cnt += 1
    logger.info(f"qryAAA_2ProjIncomReg: {cnt} updated")

    # Original Access query qryAAA_3FoundTotVal:
    cnt = 0
    for ld in LibraryData.objects.filter(reg_fdn="F"):
        if ld.ucop_fdn_no:
            bfs_rows = BFSImport.objects.filter(
                fau_fund=ld.ucop_fdn_no,
                fund_type__in=("ENDOWMENT REGENTAL INCOME", "ENDOWMENT FOUNDATION"),
            )
            if bfs_rows.exists():
                bfs = bfs_rows[0]
                ld.total_fund_value = bfs.market_value
                ld.save()
                cnt += 1
    logger.info(f"qryAAA_3FoundTotVal: {cnt} updated")

    # Original Access query qryAAA_3FoundTotVal_2:
    cnt = 0
    for ld in LibraryData.objects.filter(reg_fdn="F"):
        if ld.fau_fund:
            bfs_rows = BFSImport.objects.filter(
                fau_fund=ld.fau_fund,
                fund_type__in=("ENDOWMENT REGENTAL INCOME", "ENDOWMENT FOUNDATION"),
            )
            if bfs_rows.exists():
                bfs = bfs_rows[0]
                ld.total_fund_value = ld.total_fund_value + bfs.available
                ld.save()
                cnt += 1
    logger.info(f"qryAAA_3FoundTotVal_2: {cnt} updated")

    # Original Access query qryAAA_3FoundTotVal_3:
    # This currently matches no rows; asking LBS if this is correct.
    cnt = 0
    for ld in LibraryData.objects.filter(reg_fdn="F"):
        if ld.fau_fund:
            bfs_rows = BFSImport.objects.filter(
                fau_fund=ld.fau_fund,
                source="R",
                fund_type="ENDOWMENT FOUNDATION",
            )
            if bfs_rows.exists():
                bfs = bfs_rows[0]
                ld.total_fund_value = ld.total_fund_value - bfs.unavailable
                ld.save()
                cnt += 1
    logger.info(f"qryAAA_3FoundTotVal_3: {cnt} updated")

    # Original Access query qryAAA_3RegTotVal:
    # Regental fund math is different from Foundation math above...
    cnt = 0
    for ld in LibraryData.objects.filter(reg_fdn="R"):
        if ld.fau_fund:
            bfs_rows = BFSImport.objects.filter(
                fau_fund=ld.fau_fund,
                source="U",
            )
            if bfs_rows.exists():
                bfs = bfs_rows[0]
                ld.total_fund_value = bfs.available
                ld.save()
                cnt += 1
    logger.info(f"qryAAA_3RegTotVal: {cnt} updated")

    # Original Access query qryAAA_3RegTotVal_2:
    # Regental fund math is different from Foundation math above...
    cnt = 0
    for ld in LibraryData.objects.filter(reg_fdn="R"):
        if ld.fau_fund:
            bfs_rows = BFSImport.objects.filter(
                fau_fund=ld.fau_fund,
                source="R",
            )
            if bfs_rows.exists():
                bfs = bfs_rows[0]
                ld.total_fund_value = ld.total_fund_value - bfs.unavailable
                ld.save()
                cnt += 1
    logger.info(f"qryAAA_3RegTotVal_2: {cnt} updated")

    # Original Access query qryAAA_3RegTotVal_3:
    # Regental fund math is different from Foundation math above...
    cnt = 0
    for ld in LibraryData.objects.filter(reg_fdn="R"):
        if ld.ucop_fdn_no:
            bfs_rows = BFSImport.objects.filter(
                fau_fund=ld.ucop_fdn_no,
                source="R",
            )
            if bfs_rows.exists():
                bfs = bfs_rows[0]
                ld.total_fund_value = ld.total_fund_value + bfs.market_value
                ld.save()
                cnt += 1
    logger.info(f"qryAAA_3RegTotVal_3: {cnt} updated")

    # Original Access query qryAAA_3RegTotVal_4:
    # Regental fund math is different from Foundation math above...
    cnt = 0
    for ld in LibraryData.objects.filter(reg_fdn="R"):
        if ld.fau_fund_no:
            bfs_rows = BFSImport.objects.filter(
                fau_fund=ld.fau_fund_no,
                fau_fund__gt="40000",
                source="U",
            )
            if bfs_rows.exists():
                bfs = bfs_rows[0]
                ld.total_fund_value = bfs.available
                ld.save()
                cnt += 1
    logger.info(f"qryAAA_3RegTotVal_4: {cnt} updated")

    # Original Access query qryAAA_5_5400:
    # Update LibraryData amounts from CDW data.
    cnt = 0
    for ld in LibraryData.objects.all():
        if ld.fau_fund and ld.fau_cost_center and ld.fau_account:
            cdw_rows = CDWImport.objects.filter(
                fau_fund=ld.fau_fund,
                fau_cost_center=ld.fau_cost_center,
                fau_account=ld.fau_account,
            )
            if cdw_rows.exists():
                cdw = cdw_rows[0]
                ld.ytd_appropriation = cdw.inception_to_date_appropriation
                ld.ytd_expenditure = cdw.inception_to_date_financial
                ld.commitments = cdw.encum_ml
                ld.operating_balance = cdw.operating_balance
                ld.save()
                cnt += 1
    logger.info(f"qryAAA_5_5400: {cnt} updated")

    # Original Access query qryAAA_6TotalBalance:
    # Finally, update LibraryData total balance for all rows.
    cnt = 0
    for ld in LibraryData.objects.all():
        ld.total_balance = ld.operating_balance + ld.max_mtf_trf_amt
        ld.save()
        cnt += 1
    logger.info(f"qryAAA_6TotalBalance: {cnt} updated")
