import logging
import zipfile
import pandas as pd
import pytds

from django.db.models import Q
from datetime import datetime
from django.http import HttpResponse
from openpyxl import load_workbook
from openpyxl.styles.borders import Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from os import path
from tempfile import NamedTemporaryFile
from ge.forms import ReportForm
from ge.models import GeFund
from lbs.settings import BASE_DIR
from qdb.scripts.settings import DB_SERVER, DB_DATABASE, DB_USER, DB_PASSWORD

logger = logging.getLogger(__name__)


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
    elif report_type in ["aul_benedetti", "aul_gomez"]:
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
        # UL report needs the endowments vs. gifts distinctions of tab_type,
        # with the same columns overall as master report.
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
        for col in ("L", "M", "N", "O", "Q"):
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

        # add as-of dates to L-O balance cols and projected annual income (Q)
        as_of = get_as_of_date()
        ws["L3"] = as_of
        ws["Q3"] = as_of

    else:
        # Unpack tuple of dataframes into separate dataframes.
        endowments_df, gifts_df = data

        # basic cols for endowments reports
        endowments_cols = get_columns_for_report(report_type, tab_type="endowments")

        if not endowments_df.empty:
            endowments_df = endowments_df[endowments_cols]

            # if there are no fund restrictions, remove that column
            if all(endowments_df["fund_restriction"].isnull()) or all(
                endowments_df["fund_restriction"].isin(["N/A"])
            ):
                # Work around SettingWithCopyWarning by using df.copy() instead of inplace=True
                endowments_df = endowments_df.drop(columns=["fund_restriction"]).copy()
                # remove column from Excel template - col S for UL and unit reports
                wb["Endowments"].delete_cols(19)

        # basic cols for gifts reports
        gifts_cols = get_columns_for_report(report_type, tab_type="gifts")

        if not gifts_df.empty:
            gifts_df = gifts_df[gifts_cols]

            # if there are no fund restrictions, remove that column
            if all(gifts_df["fund_restriction"].isnull()) or all(
                gifts_df["fund_restriction"].isin(["N/A"])
            ):
                # Work around SettingWithCopyWarning by using df.copy() instead of inplace=True
                gifts_df = gifts_df.drop(columns=["fund_restriction"]).copy()
                # remove column from Excel template - col R for UL and unit reports
                wb["Gifts"].delete_cols(18)

        # put data into Excel worksheets
        gifts_ws = wb["Gifts"]
        endowments_ws = wb["Endowments"]
        gifts_ws = df_to_excel(gifts_df, gifts_ws)
        endowments_ws = df_to_excel(endowments_df, endowments_ws)

        # add totals and formatting for money columns
        gifts_money_cols = ["L", "M", "N", "O"]
        endowments_money_cols = ["L", "M", "N", "O", "Q"]

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
        # Projected Annual Income col is Q on endowments reports
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
