# Generated by Django 4.2.5 on 2023-11-03 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ge', '0003_librarydata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='librarydata',
            name='commitments',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='fau_account',
            field=models.CharField(blank=True, default='', max_length=8),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='fau_cost_center',
            field=models.CharField(blank=True, default='', max_length=2),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='fau_fund',
            field=models.CharField(blank=True, default='', max_length=6),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='fau_fund_no',
            field=models.CharField(blank=True, default='', max_length=6),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='fund_manager',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='fund_purpose',
            field=models.CharField(blank=True, default='', max_length=2000),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='fund_restriction',
            field=models.CharField(blank=True, default='', max_length=1000),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='fund_summary',
            field=models.CharField(blank=True, default='', max_length=1000),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='fund_title',
            field=models.CharField(blank=True, default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='fund_type',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='home_dept',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='home_unit_dept',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='lbs_notes',
            field=models.CharField(blank=True, default='', max_length=1000),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='max_mtf_trf_amt',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='mtf_authority',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='new_fund',
            field=models.CharField(blank=True, default='', max_length=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='notes',
            field=models.CharField(blank=True, default='', max_length=1000),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='operating_balance',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='original_id',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='projected_annual_income',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='reg_fdn',
            field=models.CharField(blank=True, default='', max_length=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='total_balance',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='total_fund_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='ucop_fdn_no',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='unit',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='unit_grande',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='ytd_appropriation',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='librarydata',
            name='ytd_expenditure',
            field=models.FloatField(blank=True, null=True),
        ),
    ]