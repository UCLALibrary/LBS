# Generated by Django 4.2.5 on 2023-09-30 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ge', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cdwimport',
            name='encum_ml',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='available',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='beginning_balance',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='contributions',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='department',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='description',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='ending_balance',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='expenditures',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='fau_dept',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='fau_fund',
            field=models.CharField(max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='fau_org',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='foundation_transfers',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='fund_memo',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='fund_old',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='fund_summary',
            field=models.CharField(max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='fund_type',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='gift_fee_payments',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='investment_income',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='market_value',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='organization',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='period_end',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='period_start',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='principal',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='projected_income',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='purpose',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='real_gl',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='sort_account',
            field=models.CharField(max_length=7, null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='source',
            field=models.CharField(max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='transfers_adj',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='transfers_to_univ',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='unavailable',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='bfsimport',
            name='unreal_gl',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='cdwimport',
            name='fau_account',
            field=models.CharField(max_length=8, null=True),
        ),
        migrations.AlterField(
            model_name='cdwimport',
            name='fau_cost_center',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='cdwimport',
            name='fau_dept',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='cdwimport',
            name='fau_fund',
            field=models.CharField(max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='cdwimport',
            name='fau_fund_title',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='cdwimport',
            name='fau_location',
            field=models.CharField(max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='cdwimport',
            name='fau_org',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='cdwimport',
            name='fund_group',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='cdwimport',
            name='fye_proc_indicator',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='cdwimport',
            name='inception_to_date_appropriation',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='cdwimport',
            name='inception_to_date_financial',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='cdwimport',
            name='ledger_year_month',
            field=models.CharField(max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='cdwimport',
            name='operating_balance',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='available_balance',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='department',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='division_code',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='division_title',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='fau_dept',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='fau_fund',
            field=models.CharField(max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='fau_fund_title',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='fau_org',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='fdn_dept',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='fdn_dept_description',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='fiscal_year',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='fund_description',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='fund_id',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='fund_nbr',
            field=models.CharField(max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='fund_purpose',
            field=models.CharField(max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='fund_restriction',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='last_fiscal_month_closed',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='max_transfer_balance',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='organization',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='pending_transfer_balance',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='preparer_phone_number',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='signature_ind',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='sub_division_code',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='sub_division_title',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='unavailable_balance',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='univ_dept',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='univ_dept_description',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='use_code',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='mtfimport',
            name='use_description',
            field=models.CharField(max_length=50, null=True),
        ),
    ]