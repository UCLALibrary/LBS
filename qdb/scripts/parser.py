import arrow
from decimal import Decimal
from .settings import SUBCODES

LOCALE = arrow.locales.EnglishLocale()


class Parser:
    def __init__(self, yyyymm, unit_name):
        self.data = {
            "unit": unit_name,
            "year": int(yyyymm[:4]),
            "month": int(yyyymm[4:]),
            "month_name": LOCALE.month_name(int(yyyymm[4:])),
            "accounts": [],
            "sub02s": [],
        }

    def calculate_percent_left(self, approp, amount):
        if approp > 0:
            return Decimal(max(0.00, amount / approp))
        return Decimal(0.00)

    def calculate_totals(self, subs):
        return {
            "Appropriation": sum([s["Appropriation"] for s in subs.values()]),
            "Expense": sum([s["Expense"] for s in subs.values()]),
            "Encumbrance": sum([s["Encumbrance"] for s in subs.values()]),
            "Memo Lien": sum([s["Memo Lien"] for s in subs.values()]),
            "Amount": sum([s["Amount"] for s in subs.values()]),
        }

    def exclude(self, row):
        for field in [
            "ytd_approp",
            "ytd_expense",
            "encumbrance",
            "memo_lien",
            "operating_bal_am",
        ]:
            if row[field] != Decimal(0):
                return False
        return True

    def exclude_ftva_aul_row(self, unit_id, row):
        # Handle FTVA AUL fund reporting differently, per SYS-1659.

        # Should only get called for relevant units, but check anyhow.
        # Unit 27: FTVA; unit 35: HaDuong - AUL Discretionary Funds
        if unit_id not in [27, 35]:
            # Not a relevant unit, tell caller not to exclude it.
            return False

        account_number = row["account_number"]
        cost_center = row["cost_center_code"]
        fund_number = row["fund_number"]
        # Look at 432975-AD funds only
        if (account_number, cost_center) != ("432975", "AD"):
            # Not a relevant fund, tell caller not to exclude it.
            return False

        # If unit is FTVA (27), exclude 432975-AD-19933;
        if unit_id == 27:
            return fund_number == "19933"
        # if unit is HaDuong - AUL Discretionary Funds (35), exclude all except 432975-AD-19933.
        if unit_id == 35:
            return fund_number != "19933"

    def add_account(self, unit_id, account, cc_list, rows):
        acct_dict = {
            "title": rows[0]["account_title"].strip(),
            "account": account,
            "cc_list": cc_list,
            "faus": {},
        }
        for row in rows:
            if self.exclude(row):
                continue
            # Handle FTVA AUL fund reporting differently, per SYS-1659
            # Unit 27: FTVA; unit 35: HaDuong - AUL Discretionary Funds
            if unit_id in [27, 35]:
                if self.exclude_ftva_aul_row(unit_id, row):
                    continue

            fau = f"{row['account_number']}-{row['cost_center_code']}-{row['fund_number']}"
            if fau not in acct_dict["faus"].keys():
                acct_dict["faus"][fau] = {"fund_title": row["fund_title"], "subs": {}}
            row_dict = {
                "name": SUBCODES[row["sub_code"]]["title"],
                "Appropriation": row["ytd_approp"],
                "Expense": row["ytd_expense"],
                "Encumbrance": row["encumbrance"],
                "Memo Lien": row["memo_lien"],
                "Amount": row["operating_bal_am"],
                "Percent": self.calculate_percent_left(
                    row["ytd_approp"], row["operating_bal_am"]
                ),
            }
            acct_dict["faus"][fau]["subs"][row["sub_code"]] = row_dict
            if row["fund_number"] == "19900" and row["sub_code"] == "02":
                self.data["sub02s"].append(
                    {"fau": fau, "fund_title": row["fund_title"], "row_dict": row_dict}
                )
        if len(acct_dict["faus"]) > 0:
            for key, fau in acct_dict["faus"].items():
                fau["totals"] = self.calculate_totals(fau["subs"])
            self.data["accounts"].append(acct_dict)
            return True
        return False
