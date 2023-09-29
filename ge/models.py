from django.db import models


# Data imported from UCLA Business and Finance Solutions
class BFSImport(models.Model):
    source = models.CharField(max_length=1)
    organization = models.CharField(max_length=50)
    fau_org = models.CharField(max_length=4)
    department = models.CharField(max_length=50)
    fau_dept = models.CharField(max_length=4)
    fund_type = models.CharField(max_length=50)
    # Normally 5 chars but some data has 6...
    fau_fund = models.CharField(max_length=6)
    # No values in sample file, not sure what this is
    fund_old = models.CharField(max_length=50)
    purpose = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    beginning_balance = models.FloatField()
    contributions = models.FloatField()
    investment_income = models.FloatField()
    gift_fee_payments = models.FloatField()
    real_gl = models.FloatField()
    unreal_gl = models.FloatField()
    foundation_transfers = models.FloatField()
    transfers_to_univ = models.FloatField()
    expenditures = models.FloatField()
    transfers_adj = models.FloatField()
    ending_balance = models.FloatField()
    available = models.FloatField()
    unavailable = models.FloatField()
    principal = models.FloatField()
    market_value = models.FloatField()
    projected_income = models.FloatField()
    sort_account = models.CharField(max_length=7)
    fund_summary = models.CharField(max_length=2000)
    # No values in sample file, not sure what this is
    fund_memo = models.CharField(max_length=50)
    period_start = models.DateField()
    period_end = models.DateField()


# Data imported from UCLA Campus Data Warehouse
class CDWImport(models.Model):
    # YYYYMM, but no need to treat as date(?)
    ledger_year_month = models.CharField(max_length=6)
    # No values in sample file, not sure what this is
    fye_proc_indicator = models.CharField(max_length=50)
    fau_org = models.CharField(max_length=4)
    fund_group = models.CharField(max_length=10)
    fau_dept = models.CharField(max_length=4)
    fau_location = models.CharField(max_length=1)
    fau_account = models.CharField(max_length=8)
    fau_cost_center = models.CharField(max_length=2)
    # Normally 5 chars but some data (in BFSImport) has 6...
    fau_fund = models.CharField(max_length=6)
    fau_fund_title = models.CharField(max_length=50)
    inception_to_date_appropriation = models.FloatField()
    inception_to_date_financial = models.FloatField()
    encum_ml = models.FloatField
    operating_balance = models.FloatField()


# Data imported from UCLA Monetary Transfer Form system
class MTFImport(models.Model):
    fau_org = models.CharField(max_length=4)
    organization = models.CharField(max_length=50)
    division_code = models.CharField(max_length=4)
    division_title = models.CharField(max_length=50)
    sub_division_code = models.CharField(max_length=4)
    sub_division_title = models.CharField(max_length=50)
    # Excel file treats this as number; may need to add leading 0 on import
    fau_dept = models.CharField(max_length=4)
    department = models.CharField(max_length=50)
    # This seems to be different from FAU fund
    fund_id = models.CharField(max_length=5)
    # This seems to be fund_id with a letter appended...
    fund_nbr = models.CharField(max_length=6)
    fund_description = models.CharField(max_length=100)
    # Many values have 0 instead of year
    fiscal_year = models.CharField(max_length=4)
    # Many values have 0 instead of numerical month
    last_fiscal_month_closed = models.PositiveSmallIntegerField()
    fdn_dept = models.CharField(max_length=3)
    fdn_dept_description = models.CharField(max_length=50)
    # Seems to be same as fau_dept
    univ_dept = models.CharField(max_length=4)
    # Seems to be the same as department
    univ_dept_description = models.CharField(max_length=50)
    # Seems to be FAU fund, so using 6 chars to match BFSImport...
    fau_fund = models.CharField(max_length=6)
    fau_fund_title = models.CharField(max_length=50)
    use_code = models.CharField(max_length=2)
    use_description = models.CharField(max_length=50)
    available_balance = models.FloatField()
    unavailable_balance = models.FloatField()
    pending_transfer_balance = models.FloatField()
    max_transfer_balance = models.FloatField()
    fund_purpose = models.CharField(max_length=2000)
    # No values in sample file, not sure what this is
    fund_restriction = models.CharField(max_length=50)
    # No values in sample file, not sure what this is
    signature_ind = models.CharField(max_length=50)
    # No values in sample file, not sure what this is
    preparer_phone_number = models.CharField(max_length=50)
