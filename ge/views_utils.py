import logging
import zipfile
import pandas as pd
import pytds

from calendar import monthrange
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


def get_as_of_date(ledger_year_month: str) -> str:
    """Get the as-of label for use in column headers,
    defined as the last day of the ledger_year_month selected
    when a user runs the report.
    """
    # Convert given YYYYMM to a date (start of month)
    report_date = datetime.strptime(ledger_year_month, "%Y%m")
    # calendar.monthrange returns weekday of month start (unneeded here)
    # and number of days in month, and is leap-year aware.
    _, days_in_month = monthrange(report_date.year, report_date.month)
    # Set day in report_date to the final day of the month.
    as_of_date = report_date.replace(day=days_in_month)
    # return as-of date in MM/DD/YY format, with text.
    return f"as of {datetime.strftime(as_of_date, "%m/%d/%y")}"


def get_month_name(ledger_year_month: str) -> str:
    """Returns the full name of the month (only), given ledger_year_month
    in yyyymm format."""
    return datetime.strptime(ledger_year_month, "%Y%m").strftime("%B")


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
    """Returns Pandas DataFrames with the set(s) of data needed for a given report.
    This combines local and QDB data.
    """
    all_data = list()
    # Get local fund data first.
    local_data = get_local_data(report_type)
    # Add current QDB data associated with the local funds.
    for fund in local_data:
        qdb_data = get_qdb_data(
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
    """Returns data from the local `GeFund` table, based on `report_type`."""
    # Start with all active funds.
    funds = GeFund.objects.filter(active=True)
    if report_type == "master":
        # Master report gets all active funds, no additional filtering.
        pass
    elif report_type in ["aul_benedetti", "aul_gomez"]:
        # AUL reports require fuzzy matching against multiple fields.
        # Strip off the prefix and search for the last name anywhere in
        # the GeUnit.name or the GeFund.home_unit_dept fields.
        report_unit = report_type.replace("aul_", "")
        funds = funds.filter(
            Q(unit__name__icontains=report_unit)
            | Q(home_unit_dept__icontains=report_unit)
        )
    else:
        # report_type values are derived from GeUnit.name, so find exact matches.
        funds = funds.filter(unit__name=report_type)

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
            "fund_type",
        )
    )

    return fund_data


def get_columns_for_report(report_type: str, tab_type: str = "master") -> list[str]:
    """Returns a list of columns for filtering a Pandas dataframe created from queries.
    This allows customization of the consistent data returned by the queries.
    These were more varied originally; now *almost* all fields are used in all reports...
    but not quite consistent.
    """
    # Column order matters, but from Python 3.7 dict key order is preserved;
    # using a dict here allows removing unwanted columns by name instead of by position.
    # These are: column_name : [tab_type, ...]
    report_columns = {
        "unit__name": ["endowments", "gifts", "master"],  # local
        "home_unit_dept": ["endowments", "gifts", "master"],  # local
        "title": ["endowments", "gifts", "master"],  # local
        "fund_type": ["master"],  # derived from QDB data, only used in master report
        "manager": ["endowments", "gifts", "master"],  # local
        "ucop_fdn_no": ["endowments", "gifts", "master"],  # QDB
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
    else:
        # Ordinary reports, with fewer fields, and tab_type matters.
        return [
            column_name
            for column_name, tab_types in report_columns.items()
            if tab_type in tab_types
        ]


def create_excel_output(
    report_type: str, ledger_year_month: str, data: tuple[pd.DataFrame, pd.DataFrame]
) -> Workbook:
    """Create Excel output for a report.

    Returns a Workbook, for direct download or archiving as needed.
    """
    # Master report has extra columns, so use a different template.
    if report_type in ("master"):
        template_file = path.join(BASE_DIR, "ge/ge_template_ul.xlsx")
    else:
        template_file = path.join(BASE_DIR, "ge/ge_template.xlsx")
    wb = load_workbook(template_file)

    # Tweaks based on the date of the report, via ledger_year_month.
    month_name = get_month_name(ledger_year_month)
    report_title = (
        f"University Library and Associated Departments: Gift and Endowment Summary, "
        f"and YTD Financial Results through the Month Ending: {month_name}"
    )
    as_of_date = get_as_of_date(ledger_year_month)

    if report_type == "master":
        # only one sheet in master report, so remove the other and rename
        gifts = wb["Gifts"]
        wb.remove(gifts)
        ws = wb["Endowments"]
        ws.title = "G&E"

        # Only one sheet in master report, so only one set of data.
        endowments_df = data[0]
        master_cols = get_columns_for_report(report_type)
        df = endowments_df[master_cols]
        ws = df_to_excel(df, ws)

        # add correct cell formatting
        for col in ("J", "K", "L", "M", "O"):
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

        # add as-of dates to J-M balance cols and projected annual income (O)
        ws["J3"] = as_of_date
        ws["O3"] = as_of_date

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
                # remove column from Excel template - col P for UL and unit reports
                wb["Endowments"].delete_cols(16)

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
                # remove column from Excel template - col O for UL and unit reports
                wb["Gifts"].delete_cols(15)

        # put data into Excel worksheets
        gifts_ws = wb["Gifts"]
        endowments_ws = wb["Endowments"]
        gifts_ws = df_to_excel(gifts_df, gifts_ws)
        endowments_ws = df_to_excel(endowments_df, endowments_ws)

        # add totals and formatting for money columns
        gifts_money_cols = ["I", "J", "K", "L"]
        endowments_money_cols = ["I", "J", "K", "L", "N"]

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
        # I3 is always the start of the 4 common financial cols
        endowments_ws["I3"] = as_of_date
        gifts_ws["I3"] = as_of_date
        # Projected Annual Income col is N on endowments reports
        endowments_ws["N3"] = as_of_date

        add_border_formatting(endowments_ws)
        add_border_formatting(gifts_ws)

    # Make some general column width adjustments per LBS preference.
    # These columns are consistent on all worksheets & workbooks.
    # Unfortunately, ColumnDimension.bestFit appears to be ignored by Excel;
    # I found widths had to be set manually.
    for worksheet in wb.worksheets:
        # Unit (column A): size to fit data.
        set_max_width(worksheet, column_letter="A")
        # Home Unit / Dept (column B): LBS wants it "smaller"; 15 seems right.
        worksheet.column_dimensions["B"].width = 15
        # Fund Title (column C); LBS wants it "smaller"; 40 seems right.
        worksheet.column_dimensions["C"].width = 40

        # Set report title
        worksheet["A1"] = report_title

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
    workbook = create_excel_output(report_type, ledger_year_month, data)

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
        workbook = create_excel_output(report_type, ledger_year_month, data)
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


def get_qdb_ge_query(fye: bool = False) -> str:
    """Get the QDB query string for GE reports,
    with or without fiscal year end (fye) filter.
    The fye filter is used only for the June report, which requires
    using "preliminary" funds values.

    :param is_fye: Whether to include the fiscal year end (fye) filter
    :return: The complete QDB GE query string
    """
    QDB_GE_SELECT_CLAUSE = """
SELECT
    fun.fund_title
,	fun.foundatn_fund_num AS ucop_fdn_no
,	glb.account_number as account
,	glb.cost_center_code as cost_center
,	glb.fund_number as fund
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
"""

    QDB_GE_FYE_FILTER = """
-- For fiscal year end, also limit to "preliminary" closeout
AND glb.fye_proc_ind = 'P'
"""

    QDB_GE_GROUP_ORDER_CLAUSE = """
GROUP BY
    fun.fund_title
,	fun.foundatn_fund_num
,	glb.account_number
,	glb.cost_center_code
,	glb.fund_number
ORDER BY glb.account_number, glb.cost_center_code, glb.fund_number
;
"""
    # Assemble the query, including the FYE filter if needed.
    query = QDB_GE_SELECT_CLAUSE
    if fye:
        query += QDB_GE_FYE_FILTER
    return query + QDB_GE_GROUP_ORDER_CLAUSE


def get_qdb_data(
    account: str,
    cost_center: str,
    fund: str,
    ledger_year_month: str,
) -> list[dict]:
    """Retrieves data from QDB, using the query from `get_qdb_query()`
    and the parameters passed to this method.
    """
    conn = pytds.connect(DB_SERVER, DB_DATABASE, DB_USER, DB_PASSWORD)
    # Connection and cursor are closed automatically via 'with'
    with conn:
        conn.as_dict = True
        cursor = conn.cursor()
        # June reports need to use "preliminary" amounts, as the FYE
        # (fiscal year end) process is not yet completed.
        fye = is_fye(ledger_year_month)
        qdb_query = get_qdb_ge_query(fye)
        # Run query with the real parameters.
        cursor.execute(qdb_query % (account, cost_center, fund, ledger_year_month))
        # This query should only return one row at most, but return all rows
        # and let the caller decide what to do.
        rows = cursor.fetchall()
        return rows


def add_qdb_to_local_data(fund: dict, qdb_data: list) -> dict:
    """Merges `qdb_data` into `local_data`.  The result
    represents one complete row of data, for use in a report.
    """
    # `qdb_data` should have just one row, but make sure.
    if len(qdb_data) == 1:
        # Add fields from the one row of qdb data to local fund data.
        fund.update(qdb_data[0])
        return fund
    else:
        raise ValueError("qdb_data did not contain 1 row.")


def is_fye(ledger_year_month: str) -> bool:
    """Returns True if the given month represents the end of the fiscal year
    (June), False otherwise.
    """
    return ledger_year_month.endswith("06")


def set_max_width(ws: Worksheet, column_letter: "str") -> None:
    """Given a worksheet and a column letter reference (e.g., "A", "Q"),
    return the worksheet (by reference) with that column set to the maximum width of data
    in that column, plus padding apparently needed by Excel.
    """
    cells = ws[column_letter]
    max_width = max({len(cell.value) for cell in cells if cell.value})
    # 4 characters of extra padding seems right. This should be constant, not dynamic.
    padding = 4
    max_width += padding
    ws.column_dimensions[column_letter].width = max_width
