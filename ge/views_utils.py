import logging
import zipfile
import pandas as pd
import pytds

from django.db.models import Q
from datetime import datetime
from django.http import HttpResponse
from functools import reduce
from openpyxl import load_workbook
from openpyxl.styles.borders import Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from os import path
from tempfile import NamedTemporaryFile
from ge.forms import ReportForm
from ge.models import BFSImport, CDWImport, GeFund, LibraryData, MTFImport
from lbs.settings import BASE_DIR
from qdb.scripts.settings import DB_SERVER, DB_DATABASE, DB_USER, DB_PASSWORD

logger = logging.getLogger(__name__)


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
                # Seems like this will always be just bfs.available,
                # since ld.total_fund_value is set to 0 by qryAAA_0Clear,
                # and this set doesn't intersect qryAAA_3FoundTotVal...
                # so ld.total_fund_value was not updated by bfs.market_value.
                # Per LBS, total_fund_value is not really used...
                # but we'll replicate legacy logic for consistency.
                ld.total_fund_value = ld.total_fund_value + bfs.available
                ld.save()
                cnt += 1
    logger.info(f"qryAAA_3FoundTotVal_2: {cnt} updated")

    # Original Access query qryAAA_3FoundTotVal_3:
    # This currently matches no rows.
    # Per LBS, total_fund_value is not really used...
    # but we'll replicate legacy logic for consistency.
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


def get_librarydata_results(search_type: str, search_term: str) -> list[LibraryData]:
    """Search LibraryData fields for a search_term, based on search_type.

    Parameters:
    search_type -- The type of search (fund or keyword)
    search_term -- The term to search for

    Returns a list of LibraryData objects matching the search.
    """
    if search_type == "fund":
        fields_to_search = ["fau_fund", "fau_fund_no", "ucop_fdn_no"]
    elif search_type == "keyword":
        fields_to_search = [
            "fund_manager",
            "fund_purpose",
            "fund_restriction",
            "fund_summary",
            "fund_title",
            "lbs_notes",
            "notes",
        ]
    elif search_type == "unit":
        fields_to_search = ["unit"]
    elif search_type == "new_funds":
        fields_to_search = ["fund_manager", "unit"]
    else:
        raise ValueError(f"Unsupported search type: {search_type}")

    # Search logic is different for new funds
    if search_type == "new_funds":
        # Look for empty fields, overriding search_term if supplied.
        search_term = ""
        q_list = [Q(**{field + "__exact": search_term}) for field in fields_to_search]
        # AND them all together.
        q_filter = reduce(lambda a, b: a & b, q_list)
    else:
        # Get a list of individual Q() statements looking for search_term in each field.
        # Example result: [<Q: (AND: ('field_a', 'term'))>, <Q: (AND: ('field_b', 'term'))>]
        q_list = [
            Q(**{field + "__icontains": search_term}) for field in fields_to_search
        ]
        # OR them all together.
        q_filter = reduce(lambda a, b: a | b, q_list)

    # Apply the filter to find results.
    results = LibraryData.objects.filter(q_filter).order_by("id")

    # Return results as a list of objects, rather than a queryset.
    return [item for item in results]


def sum_col(ws: Worksheet, col: str, col_top: int = 5) -> None:
    """Add a total row to an Excel spreadsheet column."""
    last_row = get_last_row(ws, col)
    ws[f"{col}{last_row + 1}"] = f"=SUM({col}{col_top}:{col}{last_row})"


def get_last_row(ws: Worksheet, col: str) -> int:
    """Get the index of the last non-empty row in an Excel spreadsheet column."""
    last_row = len(ws[col])
    # make sure we get the first non-empty row from the bottom
    last_row -= next(i for i, x in enumerate(reversed(ws[col])) if x.value is not None)
    return last_row


def get_last_col(ws: Worksheet, row: int) -> int:
    """Get the index of the last non-empty column in an Excel spreadsheet row."""
    last_col = len(ws[row])
    # make sure we get the first non-empty column from the right
    last_col -= next(i for i, x in enumerate(reversed(ws[row])) if x.value is not None)
    return last_col


def get_as_of_date(date: datetime = datetime.now()) -> str:
    """Get the as-of label for use in column headers,
    defined as the last day of the previous quarter.
    """
    current_month = date.month
    # Jan - Mar
    if current_month <= 3:
        end_date = "12/31"
        year = date.year - 1
    # Apr - Jun
    elif current_month <= 6:
        end_date = "3/31"
        year = date.year
    # Jul - Sep
    elif current_month <= 9:
        end_date = "6/30"
        year = date.year
    # Oct - Dec
    else:
        end_date = "9/30"
        year = date.year
    # return as-of date in MM/DD/YY format
    return f"as of {end_date}/{year % 100}"


def df_to_excel(df: pd.DataFrame, ws: Worksheet) -> Worksheet:
    """Puts dataframe into Excel worksheet, with data starting at row 5."""
    # convert to rows for use in spreadsheet
    rows = dataframe_to_rows(df, index=False, header=False)
    # add rows to spreadsheet, starting at row 5
    for r_col_id, row in enumerate(rows, 1):
        for c_col_id, value in enumerate(row, 1):
            ws.cell(row=r_col_id + 4, column=c_col_id, value=value)
    return ws


def get_data_for_report(
    report_type: str, ledger_year_month: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_data = list()
    # Get local fund data first.
    local_data = get_local_data(report_type)
    # Add current QDB data associated with the local funds.
    for fund in local_data:
        qdb_data = get_qdb_data(
            report_type,
            fund.get("account", ""),
            fund.get("cost_center", ""),
            fund.get("fund", ""),
            ledger_year_month,
        )
        # Should have 1 row; might get 0; should not have more than 1.
        # TODO: Decide what to do / log if other than 1 row.
        if len(qdb_data) == 1:
            fund_with_qdb = add_qdb_to_local_data(fund, qdb_data)
            all_data.append(fund_with_qdb)

    # Reports have different data structures;
    # split into Gifts and Endowments as needed.
    if report_type == "master":
        # Master report has only one set of data, combining gifts and endowments.
        # For consistency, return two dataframes, one with all data and one empty.
        return (pd.DataFrame(all_data), pd.DataFrame())
    else:
        # Split by fund type.
        endowments = [
            record for record in all_data if record.get("fund_type", "") == "Endowment"
        ]
        gifts = [record for record in all_data if record.get("fund_type", "") == "Gift"]
        return (pd.DataFrame(endowments), pd.DataFrame(gifts))


def get_local_data(report_type: str) -> list[dict]:
    # Get associated units, needed for some queries.
    report_units = get_units_for_report(report_type)
    # Start with all active funds.
    funds = GeFund.objects.filter(active=True)
    if report_type == "master":
        # Master report gets all active funds, no additional filtering.
        pass
    elif report_type in ["aul_benedetti", "aul_gomez", "aul_grappone"]:
        # Only one report_unit is relevant for the AUL reports,
        # but it needs fuzzy matching.
        report_unit = report_units[0]
        funds = funds.filter(
            Q(unit__name__icontains=report_unit)
            | Q(home_unit_dept__icontains=report_unit)
        )
    else:
        # There can be multiple units associated with a fund.
        funds = funds.filter(unit__name__in=report_units)

    # Sort the remaining funds by unit and FAU components.
    funds = funds.order_by("unit__name", "account", "cost_center", "fund")
    # Convert queryset to list of dicts, for data manipulation with no further database backing.
    # Keep only fields needed for reporting.
    fund_data = list(
        funds.values(
            "account",
            "cost_center",
            "fund",
            "title",
            "manager",
            "mtf_authority",
            "unit__name",
            "home_unit_dept",
            "projected_annual_income",
            "fund_purpose",
            "fund_summary",
            "fund_restriction",
            "general_notes",
            "lbs_notes",
        )
    )
    # Add a fund_type field, calculated from relevant data. This will be needed for reports.
    # This is not in the database, and not on the model as a property can't be used for queries.
    for record in fund_data:
        record["fund_type"] = get_fund_type(record.get("fund", ""))

        # TODO: For now, preserve unwanted to-be-removed columns with placeholders.
        placeholders = {
            # "fund_type": "REMOVE",
            "reg_fdn": "REMOVE",
            "fau_fund_no": "REMOVE",
            "max_mtf_trf_amt": "UNKNOWN",
            "total_balance": "UNKNOWN",
        }
        record.update(placeholders)

    return fund_data


def get_columns_for_report(report_type: str, tab_type: str = "master") -> list[str]:
    # Most columns are used in all reports, but not all.
    # Column order matters, but from Python 3.7 dict key order is preserved;
    # using a dict here allows removing unwanted columns by name instead of by position.
    # These are: column_name : [tab_type, ...]
    report_columns = {
        "unit__name": ["endowments", "gifts", "master"],  # local
        "home_unit_dept": ["endowments", "gifts", "master"],  # local
        "title": ["endowments", "gifts", "master"],  # local
        "fund_type": ["endowments", "gifts", "master"],  # REMOVE
        "reg_fdn": ["endowments", "gifts", "master"],  # REMOVE
        "manager": ["endowments", "gifts", "master"],  # local
        "ucop_fdn_no": ["endowments", "gifts", "master"],  # QDB
        "fau_fund_no": ["endowments", "gifts", "master"],  # REMOVE
        "account": ["endowments", "gifts", "master"],  # local
        "cost_center": ["endowments", "gifts", "master"],  # local
        "fund": ["endowments", "gifts", "master"],  # local
        "ytd_appropriation": ["endowments", "gifts", "master"],  # QDB
        "ytd_expenditure": ["endowments", "gifts", "master"],  # QDB
        "commitments": ["endowments", "gifts", "master"],  # QDB
        "operating_balance": ["endowments", "gifts", "master"],  # QDB
        "max_mtf_trf_amt": ["master"],  # UNKNOWN
        "total_balance": ["master"],  # UNKNOWN
        "mtf_authority": ["endowments", "gifts", "master"],  # local
        "projected_annual_income": ["endowments", "master"],  # local
        "fund_purpose": ["endowments", "gifts", "master"],  # local
        "fund_restriction": ["endowments", "gifts", "master"],  # local
        "general_notes": ["endowments", "gifts", "master"],  # local
        "lbs_notes": ["endowments", "gifts", "master"],  # local
    }

    if report_type == "master":
        # All columns are used in master report; tab_type is not relevant.
        return [column_name for column_name in report_columns.keys()]
    elif report_type == "ul":
        # UL report also gets some columns only master report does
        # (max_mtf_trf_amt and total_balance), but also needs the
        # endowments vs. gifts distinctions of tab_type.
        return [
            column_name
            for column_name, tab_types in report_columns.items()
            if "master" in tab_types and tab_type in tab_types
        ]
    else:
        # Ordinary reports, with fewer fields, and tab_type matters.
        return [
            column_name
            for column_name, tab_types in report_columns.items()
            if tab_type in tab_types
        ]


def get_units_for_report(report_type: str) -> list[str]:
    # map each report type to list of strings needed for query
    report_units = {
        "archives": ["Archives"],
        "arts": ["Arts"],
        "biomed": ["Biomed"],
        "digilib": ["DigiLib", "Digital Library"],
        "eal": ["EAL"],
        "ftva": ["FTVA"],
        "hsc": ["History & SC Sciences"],
        "hssd": ["HSSD", "SSHD"],
        "ias": ["Int'l Studies"],
        "lhr": ["LHR"],
        "lsc": ["LSC"],
        "management": ["Management"],
        "music": ["Music"],
        "oh": ["Oral History"],
        "pa": ["Performing Arts"],
        "powell": ["Powell"],
        "preservation": ["Preservation"],
        "sel": ["SEL"],
        "ul": ["UL"],
        "aul_benedetti": ["Benedetti"],
        "aul_gomez": ["Gomez"],
        "aul_grappone": ["Grappone"],
    }
    return report_units.get(report_type, [])


def create_excel_output(
    report_type: str, data: tuple[pd.DataFrame, pd.DataFrame]
) -> Workbook:
    """Create Excel output for a report.

    Returns a Workbook, for direct download or archiving as needed.
    """
    # UL and Master reports have extra columns, so use a different template
    if report_type in ("master", "ul"):
        template_file = path.join(BASE_DIR, "ge/ge_template_ul.xlsx")
    else:
        template_file = path.join(BASE_DIR, "ge/ge_template.xlsx")
    wb = load_workbook(template_file)

    if report_type == "master":
        # only one sheet in master report, so remove the other and rename
        gifts = wb["Gifts"]
        wb.remove(gifts)
        ws = wb["Endowments"]
        ws.title = "G&E"
        # clear label in template
        ws["A1"] = ""

        # TODO: Consider passing columns and report type to one method?
        # Only one sheet in master report, so only one set of data.
        endowments_df = data[0]
        master_cols = get_columns_for_report(report_type)
        df = endowments_df[master_cols]
        ws = df_to_excel(df, ws)

        # add correct cell formatting
        for col in ("L", "M", "N", "O", "P", "Q", "S"):
            for row in range(5, len(ws[col]) + 1):
                # Excel "format code" for Accounting, 2 decimal places, $, comma separator
                ws[f"{col}{row}"].number_format = (
                    """_($* #,##0.00_);_($* (#,##0.00);_($* " - "??_);_(@_)"""
                )
        # add filters on all cols
        filters = ws.auto_filter
        last_col = get_column_letter(get_last_col(ws, 5))
        last_row = get_last_row(ws, "A")
        filters.ref = f"A4:{last_col}{last_row}"

        # add as-of dates to L-O balance cols, max MTF col, and projected annual income
        as_of = get_as_of_date()
        ws["L3"] = as_of
        ws["P3"] = as_of
        ws["S3"] = as_of

    else:
        # Unpack tuple of dataframes into separate dataframes.
        endowments_df, gifts_df = data

        # basic cols for endowments reports
        endowments_cols = get_columns_for_report(report_type, tab_type="endowments")

        if not endowments_df.empty:
            endowments_df = endowments_df[endowments_cols]

            # if there are no fund restrictions, remove that column
            if all(endowments_df["fund_restriction"].isin([""])):
                endowments_df.drop(columns=["fund_restriction"], inplace=True)
                # remove column from Excel template - col U for UL, S for others
                if report_type == "ul":
                    wb["Endowments"].delete_cols(21)
                else:
                    wb["Endowments"].delete_cols(19)

        # basic cols for gifts reports
        gifts_cols = get_columns_for_report(report_type, tab_type="gifts")

        if not gifts_df.empty:
            gifts_df = gifts_df[gifts_cols]

            # if there are no fund restrictions, remove that column
            if all(gifts_df["fund_restriction"].isin([""])):
                gifts_df.drop(columns=["fund_restriction"], inplace=True)
                # remove column from Excel template - col T for UL, R for others
                if report_type == "ul":
                    wb["Gifts"].delete_cols(20)
                else:
                    wb["Gifts"].delete_cols(18)

        # put data into Excel worksheets
        gifts_ws = wb["Gifts"]
        endowments_ws = wb["Endowments"]
        gifts_ws = df_to_excel(gifts_df, gifts_ws)
        endowments_ws = df_to_excel(endowments_df, endowments_ws)

        # add totals and formatting for money columns
        gifts_money_cols = ["L", "M", "N", "O"]
        endowments_money_cols = ["L", "M", "N", "O", "Q"]
        if report_type == "ul":
            gifts_money_cols.extend(["P", "Q"])
            endowments_money_cols.extend(["P", "S"])

        for col in gifts_money_cols:
            sum_col(gifts_ws, col)
            for row in range(5, len(gifts_ws[col]) + 1):
                # Excel "format code" for Accounting, 2 decimal places, $, comma separator
                gifts_ws[f"{col}{row}"].number_format = (
                    """_($* #,##0.00_);_($* (#,##0.00);_($* " - "??_);_(@_)"""
                )

        for col in endowments_money_cols:
            sum_col(endowments_ws, col)
            for row in range(5, len(endowments_ws[col]) + 1):
                # Excel "format code" for Accounting, 2 decimal places, $, comma separator
                endowments_ws[f"{col}{row}"].number_format = (
                    """_($* #,##0.00_);_($* (#,##0.00);_($* " - "??_);_(@_)"""
                )

        # set filters on all columns with data
        endowments_filters = endowments_ws.auto_filter
        last_endowment_col = get_column_letter(get_last_col(endowments_ws, 5))
        last_endowment_row = get_last_row(endowments_ws, "A")
        endowments_filters.ref = f"A4:{last_endowment_col}{last_endowment_row}"

        gifts_filters = gifts_ws.auto_filter
        last_gifts_col = get_column_letter(get_last_col(gifts_ws, 5))
        last_gifts_row = get_last_row(gifts_ws, "A")
        gifts_filters.ref = f"A4:{last_gifts_col}{last_gifts_row}"

        # add as-of dates
        as_of = get_as_of_date()
        # L3 is always the start of the 4 common financial cols
        endowments_ws["L3"] = as_of
        gifts_ws["L3"] = as_of
        if report_type == "ul":
            # UL has extra MTF col on both sheets (P), and one other extra col
            # that pushes the Projected Annual Income col to S
            gifts_ws["P3"] = as_of
            endowments_ws["P3"] = as_of
            endowments_ws["S3"] = as_of
        else:
            # Projected Annual Income col is Q on non-UL endowments reports
            endowments_ws["Q3"] = as_of

        add_border_formatting(endowments_ws)
        add_border_formatting(gifts_ws)

    return wb


def get_bytes_from_workbook(workbook: Workbook) -> bytes:
    """Convert openpyxl workbook into bytes for serving via HTTP."""
    with NamedTemporaryFile() as tmp:
        workbook.save(tmp.name)
        tmp.seek(0)
        stream = tmp.read()
    return stream


def download_excel_file(report_type: str, ledger_year_month: str) -> HttpResponse:
    """Get Excel file via HTTP response."""
    data = get_data_for_report(report_type, ledger_year_month)
    workbook = create_excel_output(report_type, data)

    stream = get_bytes_from_workbook(workbook)

    response = HttpResponse(
        content=stream,
        content_type="application/ms-excel",
    )
    response["Content-Disposition"] = (
        f'attachment; filename={report_type}-Report-{datetime.now().strftime("%Y%m%d%H%M")}.xlsx'
    )

    return response


def download_zip_file(ledger_year_month: str) -> HttpResponse:
    """Get zip file containing all Excel reports, via HTTP response."""

    # Use the same timestamp for all reports and for zip file.
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    response = HttpResponse(content_type="application/zip")
    zip_filename = f"ge_reports-{timestamp}.zip"
    # This works, because Django's HttpResponse is a file-like object.
    zip_file = zipfile.ZipFile(response, mode="w")  # type: ignore

    # Get list of reports from ReportForm.
    report_types = [choice[0] for choice in ReportForm().fields["report_type"].choices]
    # Get Excel workbook for each, convert to bytes, and add to zip file.
    for report_type in report_types:
        data = get_data_for_report(report_type, ledger_year_month)
        workbook = create_excel_output(report_type, data)
        excel_filename = f"{report_type}-Report-{timestamp}.xlsx"
        stream = get_bytes_from_workbook(workbook)
        zip_file.writestr(excel_filename, stream)

    # Attach it to the response and return it.
    response["Content-Disposition"] = f"attachment; filename={zip_filename}"
    return response


def add_border_formatting(ws: Worksheet) -> None:
    """Fix formatting for borders on Excel sheet header cells."""
    # row 2 contains top of column headers, and is sometimes merged with 3
    # so we count row 2, but apply the border to row 3
    last_border_col = get_last_col(ws, 2)
    # last col (LBS Notes) is excluded from border formatting, and Excel cols are 1-indexed
    # so we use range(1, last_border_col) to get all but the last col
    for header_cell_index in range(1, last_border_col):
        current_cell = ws[f"{get_column_letter(header_cell_index)}3"]
        current_cell.border = Border(
            bottom=Side(border_style="medium"),
            left=Side(border_style="thin"),
            right=Side(border_style="thin"),
        )
    # Last col before LBS notes needs medium border on right and bottom
    ws[f"{get_column_letter(last_border_col - 1)}3"].border = Border(
        right=Side(border_style="medium"), bottom=Side(border_style="medium")
    )


def get_qdb_query(report_type: str) -> str:
    # TODO: Splice this into create_excel_output() or similar, when local data is finalized.
    QDB_GE_QUERY = """
SELECT
    fun.fund_title
,	fun.foundatn_fund_num AS ucop_fdn_no
,	glb.account_number
,	glb.cost_center_code
,	glb.fund_number
,	fun.fund_purpose_code
,	fun.fund_restr_code
,	sum(-glb.ytd_appropriation) AS ytd_appropriation
,	sum(glb.ytd_financial) AS ytd_expenditure
,	sum(glb.encumbrance) AS commitments
,	sum(-glb.bal_operating) AS operating_balance
FROM qdb.dbo.gl_balances glb
INNER JOIN qdb.dbo.account acc
    ON glb.location_code = acc.location_code
    AND glb.account_number = acc.account_number
    AND glb.cost_center_code = acc.cost_center_code
INNER JOIN qdb.dbo.fund fun
    ON glb.location_code = fun.location_code
    AND glb.fund_number = fun.fund_number
-- Hard-coded filters first
WHERE glb.location_code = '4'
AND (glb.dept_code_account LIKE '54%%' OR glb.dept_code_account = '0461')
AND fun.fund_closed_flag <> 'Y'
-- Variable filters provided by caller
-- TODO: Figure out why quoting these is needed when IT SHOULD NOT BE!
AND glb.account_number = '%s'
AND glb.cost_center_code = '%s'
AND glb.fund_number = '%s'
AND glb.ledger_year_month = '%s'
GROUP BY
    fun.fund_title
,	fun.foundatn_fund_num
,	glb.account_number
,	glb.cost_center_code
,	glb.fund_number
,	fun.fund_purpose_code
,	fun.fund_restr_code
ORDER BY glb.account_number, glb.cost_center_code, glb.fund_number
;
"""
    return QDB_GE_QUERY


def get_qdb_data(
    report_type,
    account_number: str,
    cost_center_code: str,
    fund_number: str,
    ledger_year_month: str,
) -> list[dict]:
    conn = pytds.connect(DB_SERVER, DB_DATABASE, DB_USER, DB_PASSWORD)
    # Connection and cursor are closed automatically via 'with'
    with conn:
        conn.as_dict = True
        cursor = conn.cursor()
        # TODO: Query will be built based on parameters passed to this method.
        # For now, just use static query.
        qdb_query = get_qdb_query(report_type)
        # Run query with the other, real, parameters
        cursor.execute(
            qdb_query
            % (account_number, cost_center_code, fund_number, ledger_year_month)
        )
        # This query should only return one row at most, but return all rows
        # and let the caller decide what to do.
        rows = cursor.fetchall()
        return rows


def add_qdb_to_local_data(fund: dict, qdb_data: list) -> dict:
    # `qdb_data` should have just one row, but make sure.
    if len(qdb_data) == 1:
        # Add fields from the one row of qdb data to local fund data.
        fund.update(qdb_data[0])
        return fund
    else:
        raise ValueError("qdb_data did not contain 1 row.")


def get_fund_type(fund: str) -> str:
    # Ideally this would be on the GeFund model,
    # but can't use a model property or method in a query.
    match fund:
        case f if "10000" <= f <= "19999":
            return "Endowment"
        case f if "34100" <= f <= "39799":
            return "Endowment"
        case f if "39800" <= f <= "56999":
            return "Gift"
        case f if "93014" <= f <= "95215":
            return "Endowment"
        case _:
            return "Unknown"
