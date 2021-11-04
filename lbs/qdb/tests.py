from django.test import TestCase
from qdb.models import Staff, Unit, Account, Subcode, Recipient
from .admin import RecipientAdmin
import csv


class DataLoadTestCase(TestCase):

    def test_dataload(self):
        with open("qdb/fixtures/staff.csv", encoding="utf-8-sig", newline="") as csvfile:
            reader = csv.DictReader(csvfile, dialect="excel")
            csv_count = 0
            for row in reader:
                name = row["name"]
                email = row["email"]
                person = _create_person(name, email)
                csv_count += 1
        staff_count = Staff.objects.all().count()
        #print(staff_count, "--->staff_count")
        self.assertEqual(staff_count, csv_count)


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
        self.assertEqual(str(unit.unit_id), '1')


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

        subcode = Subcode.objects.create(code="12345")
        with self.assertRaises(ValueError):
            TestsRange.tests_range(subcode)

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


class TestsUrls(TestCase):
    def test_testadminpage(self):
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 301)
        # self.assertEqual(response.status_code, 200)


class TestsRange(object):
    def tests_range(i):
        range_1 = range(1, 5, 1)
        if len(str(i)) not in range_1:
            raise ValueError


def _create_person(name, email):
    # Staff (persons) might already exist, via small initial load
    staff, created = Staff.objects.get_or_create(name=name,
                                                 email=email)
    staff.save()
    return staff
