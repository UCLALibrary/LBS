from django.test import TestCase
from qdb.models import Staff, Unit, Account, Subcode, Recipient
from .admin import RecipientAdmin
from unittest import skip
import csv

from django.core.management import call_command


class DataLoadTestCase(TestCase):
    # The use of the dataload test was discussed when it broke after moving to Docker.
    # The problem was narrowed down to the test db continuing indexing from the prod db:
    #   - ie prod Staff table index is 1-34 and Test db Staff table is indexed 35-68
    #   - other tables were similar
    #   - a temporary offsets added to queries permitted the tests to run
    # Because the dataload tests are run only once (during ingest), and are of no use after,
    #   a decision was made to skip the dataload part of the testing
    #
    @skip("The dataload has been verified for the single time it ran after installation of the app.")
    def test_dataload(self):

        call_command('load_initial_data', 'qdb/fixtures/staff.csv',
                     'qdb/fixtures/unit.csv', 'qdb/fixtures/accounts.csv')

        staff_count = Staff.objects.all().count()
        unit_count = Unit.objects.all().count()
        account_count = Account.objects.all().count()
        #print(staff_count, "--->staff_count")

        with open(r"qdb/fixtures/accounts.csv", 'r') as fp:
            csv_accounts_count = len(fp.readlines()) - 1
        with open(r"qdb/fixtures/staff.csv", 'r') as fp:
            csv_staff_count = len(fp.readlines()) - 1
        with open(r"qdb/fixtures/unit.csv", 'r') as fp:
            csv_unit_count = len(fp.readlines()) - 1

        self.assertEqual(account_count, csv_accounts_count)
        self.assertEqual(staff_count, csv_staff_count)
        self.assertEqual(unit_count, csv_unit_count)


class AdminTestCase(TestCase):
    fixtures = ["sample_data.json"]
    nameunit = Unit.objects.get(name='Oral History')

    def test_recipientadmin(self):
        recipient = Recipient.objects.get(pk=1)
        self.assertEqual(recipient.recipient_id, 32)
        self.assertEqual(recipient.unit_id, 1)

        namestaff = Staff.objects.get(name='Todd Grappone')
        nameobj = Recipient.objects.get(id=namestaff.id)
        recipient = RecipientAdmin.name(RecipientAdmin, nameobj)
        self.assertEqual(str(recipient), str(namestaff))

        unit = Recipient.objects.get(pk=1)
        self.assertEqual(unit.unit_id, 1)


class ModelsTestCase(TestCase):

    fixtures = ["sample_data.json"]

    def test_staff(self):
        name = Staff.objects.create(name="Jane Bruin")
        self.assertEqual(str(name), "Jane Bruin")
        staff = Staff.objects.get(pk=1)
        self.assertEqual(str(staff), 'Sharon Farb')
        self.assertEqual(staff.name, 'Sharon Farb')
        self.assertEqual(staff.email, 'farb@library.ucla.edu')

    def test_unit(self):
        name = Unit.objects.create(name="Arts")
        self.assertEqual(str(name), "Arts")
        unit = Unit.objects.get(pk=1)
        self.assertEqual(str(unit), 'Oral History')
        self.assertEqual(unit.name, 'Oral History')

    def test_subcode(self):
        subcode = Subcode.objects.create(code="1234")
        self.assertEqual(str(subcode), "1234")

        subcode = Subcode.objects.get(pk=1)
        self.assertEqual(str(subcode), '00')
        self.assertEqual(subcode.titles, 'Salaries - Academic')
        self.assertEqual(subcode.notes,
                         'LBS will balance sub 00 fund 19900 at year end')

    def test_account(self):
        account = Account.objects.create(
            account="123456", unit=Unit.objects.get(pk=1))
        self.assertEqual(str(account), "123456")
        self.assertEqual(str(account), "123456")
        account = Account.objects.get(pk=2)
        self.assertEqual(str(account), '436000')
        self.assertEqual(account.account, '436000')
        self.assertEqual(account.cost_center, 'BF')
        self.assertEqual(account.title,
                         'LIBRARY:COLL DEV-ORAL HSTR/BUS FORECAST')
        self.assertEqual(account.unit_id, 1)

    def test_recipient(self):
        recipient = Recipient.objects.create(
            unit=Unit.objects.get(pk=1), recipient=Staff.objects.get(pk=1))
        self.assertEqual(str(recipient), "Sharon Farb")
        self.assertEqual(str(recipient.unit), "Oral History")
