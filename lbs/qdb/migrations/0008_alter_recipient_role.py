# Generated by Django 3.2.6 on 2022-01-27 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qdb', '0007_alter_recipient_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipient',
            name='role',
            field=models.CharField(choices=[('aul', 'AUL'), ('head', 'Head')], max_length=100),
        ),
    ]
