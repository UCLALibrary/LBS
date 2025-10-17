import pytds
from .settings import DB_SERVER, DB_DATABASE, DB_USER, DB_PASSWORD


QDB_QUERY_SELECT_CLAUSE = """
SELECT
    glb.account_number + ' ' + glb.cost_center_code + ' ' + glb.fund_number + ' '
    + acc.account_title + ' ' + fun.fund_title AS fau
,	glb.sub_code
,	glb.account_number
,	glb.cost_center_code
,	glb.fund_number
,	acc.account_title
,	fun.fund_title
,	sum (-glb.ytd_appropriation) AS ytd_approp
,	sum (glb.ytd_financial) AS ytd_expense
,	sum (glb.encumbrance) AS encumbrance
,	sum (glb.memo_lien) AS memo_lien
,	sum (-glb.bal_operating) AS operating_bal_am
FROM qdb.dbo.gl_balances glb
INNER JOIN qdb.dbo.account acc
    ON glb.location_code = acc.location_code
    AND glb.account_number = acc.account_number
    AND glb.cost_center_code = acc.cost_center_code
INNER JOIN qdb.dbo.fund fun
    ON glb.location_code = fun.location_code
    AND glb.fund_number = fun.fund_number
"""

QDB_QUERY_WHERE_CLAUSE = """
-- Hard-coded filters first
WHERE glb.location_code = '4'
AND (glb.dept_code_account LIKE '54%%' OR glb.dept_code_account = '0461')
AND fun.fund_closed_flag <> 'Y'
-- Variable filters provided by caller
AND glb.ledger_year_month = %s
AND glb.account_number = %s
-- No nulls in glb, but '' is a legal value and must be requested
-- Caller must replace CC_PLACEHOLDERS
AND glb.cost_center_code IN (CC_PLACEHOLDERS)
"""

QDB_QUERY_FYE_FILTER = """
-- For fiscal year end, also limit to "preliminary" closeout
AND glb.fye_proc_ind = 'P'
"""

QDB_QUERY_GROUP_ORDER_CLAUSE = """
GROUP BY
    glb.account_number
,	glb.cost_center_code
,	glb.fund_number
,	glb.sub_code
,	acc.account_title
,	fun.fund_title
ORDER BY fau, glb.sub_code
;
"""


def get_qdb_query(is_fye: bool = False) -> str:
    """Get the QDB query string, with or without fiscal year end (fye) filter.

    :param is_fye: Whether to include the fiscal year end (fye) filter
    :return: The complete QDB query string
    """
    query = QDB_QUERY_SELECT_CLAUSE + QDB_QUERY_WHERE_CLAUSE
    if is_fye:
        query += QDB_QUERY_FYE_FILTER
    return query + QDB_QUERY_GROUP_ORDER_CLAUSE


def get_qdb_data(yyyymm: str, account_number: str, cc_codes: list[str]) -> list:
    """Get the QDB data for a given account and cost center codes.

    :param yyyymm: The year and month in YYYYMM format
    :param account_number: The account number
    :param cc_codes: The list of cost center codes
    :return: A list representing rows of QDB data
    """
    # determine if this is a Fiscal Year End (June) report
    is_fye = yyyymm.endswith("06")

    conn = pytds.connect(DB_SERVER, DB_DATABASE, DB_USER, DB_PASSWORD)
    # Connection and cursor are closed automatically via 'with'
    with conn:
        conn.as_dict = True
        cursor = conn.cursor()
        # Build the variable-length placeholders for cc_codes
        # Then update QDB_QUERY to use this value.
        # cc_placeholders = ', '.join(['%s'] * len(cc_codes))

        # Convert list to single-quoted string suitable for SQL
        cc_values = str(cc_codes)[1:-1]

        # In-place replace does not work... have to use a local variable
        qdb_query = get_qdb_query(is_fye)
        qdb_final_query = qdb_query.replace("CC_PLACEHOLDERS", cc_values)
        # Run query with the other, real, parameters
        cursor.execute(qdb_final_query % (yyyymm, account_number))
        rows = cursor.fetchall()
        return rows
