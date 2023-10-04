from django.db import models


# Data imported from UCLA Business and Finance Solutions
class BFSImport(models.Model):
    source = models.CharField(max_length=1, null=True)
    organization = models.CharField(max_length=50, null=True)
    fau_org = models.CharField(max_length=4, null=True)
    department = models.CharField(max_length=50, null=True)
    fau_dept = models.CharField(max_length=4, null=True)
    fund_type = models.CharField(max_length=50, null=True)
    # Normally 5 chars but some data has 6...
    fau_fund = models.CharField(max_length=6, null=True)
    # No values in sample file, not sure what this is
    fund_old = models.CharField(max_length=50, null=True)
    purpose = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=200, null=True)
    beginning_balance = models.FloatField(null=True)
    contributions = models.FloatField(null=True)
    investment_income = models.FloatField(null=True)
    gift_fee_payments = models.FloatField(null=True)
    real_gl = models.FloatField(null=True)
    unreal_gl = models.FloatField(null=True)
    foundation_transfers = models.FloatField(null=True)
    transfers_to_univ = models.FloatField(null=True)
    expenditures = models.FloatField(null=True)
    transfers_adj = models.FloatField(null=True)
    ending_balance = models.FloatField(null=True)
    available = models.FloatField(null=True)
    unavailable = models.FloatField(null=True)
    principal = models.FloatField(null=True)
    market_value = models.FloatField(null=True)
    projected_income = models.FloatField(null=True)
    sort_account = models.CharField(max_length=7, null=True)
    fund_summary = models.CharField(max_length=2000, null=True)
    # No values in sample file, not sure what this is
    fund_memo = models.CharField(max_length=50, null=True)
    period_start = models.DateField(null=True)
    period_end = models.DateField(null=True)


# Data imported from UCLA Campus Data Warehouse
class CDWImport(models.Model):
    # YYYYMM, but no need to treat as date(?)
    ledger_year_month = models.CharField(max_length=6, null=True)
    # No values in sample file, not sure what this is
    fye_proc_indicator = models.CharField(max_length=50, null=True)
    fau_org = models.CharField(max_length=4, null=True)
    fund_group = models.CharField(max_length=10, null=True)
    fau_dept = models.CharField(max_length=4, null=True)
    fau_location = models.CharField(max_length=1, null=True)
    fau_account = models.CharField(max_length=8, null=True)
    fau_cost_center = models.CharField(max_length=2, null=True)
    # Normally 5 chars but some data (in BFSImport) has 6...
    fau_fund = models.CharField(max_length=6, null=True)
    fau_fund_title = models.CharField(max_length=50, null=True)
    inception_to_date_appropriation = models.FloatField(null=True)
    inception_to_date_financial = models.FloatField(null=True)
    encum_ml = models.FloatField(null=True)
    operating_balance = models.FloatField(null=True)


# Data imported from UCLA Monetary Transfer Form system
class MTFImport(models.Model):
    fau_org = models.CharField(max_length=4, null=True)
    organization = models.CharField(max_length=50, null=True)
    division_code = models.CharField(max_length=4, null=True)
    division_title = models.CharField(max_length=50, null=True)
    sub_division_code = models.CharField(max_length=4, null=True)
    sub_division_title = models.CharField(max_length=50, null=True)
    # Excel file treats this as number; may need to add leading 0 on import
    fau_dept = models.CharField(max_length=4, null=True)
    department = models.CharField(max_length=50, null=True)
    # This seems to be different from FAU fund
    fund_id = models.CharField(max_length=5, null=True)
    # This seems to be fund_id with a letter appended...
    fund_nbr = models.CharField(max_length=6, null=True)
    fund_description = models.CharField(max_length=100, null=True)
    # Many values have 0 instead of year
    fiscal_year = models.CharField(max_length=4, null=True)
    # Many values have 0 instead of numerical month
    last_fiscal_month_closed = models.PositiveSmallIntegerField(null=True)
    fdn_dept = models.CharField(max_length=3, null=True)
    fdn_dept_description = models.CharField(max_length=50, null=True)
    # Seems to be same as fau_dept
    univ_dept = models.CharField(max_length=4, null=True)
    # Seems to be the same as department
    univ_dept_description = models.CharField(max_length=50, null=True)
    # Seems to be FAU fund, so using 6 chars to match BFSImport...
    fau_fund = models.CharField(max_length=6, null=True)
    fau_fund_title = models.CharField(max_length=50, null=True)
    use_code = models.CharField(max_length=2, null=True)
    use_description = models.CharField(max_length=50, null=True)
    available_balance = models.FloatField(null=True)
    unavailable_balance = models.FloatField(null=True)
    pending_transfer_balance = models.FloatField(null=True)
    max_transfer_balance = models.FloatField(null=True)
    fund_purpose = models.CharField(max_length=2000, null=True)
    # No values in sample file, not sure what this is
    fund_restriction = models.CharField(max_length=50, null=True)
    # No values in sample file, not sure what this is
    signature_ind = models.CharField(max_length=50, null=True)
    # No values in sample file, not sure what this is
    preparer_phone_number = models.CharField(max_length=50, null=True)
