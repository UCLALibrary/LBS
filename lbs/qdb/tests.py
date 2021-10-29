from django.test import TestCase


from .models import Staff, Unit, Recipient, Subcode, Account


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
        code = Subcode.objects.create(code="1234")
        self.assertEqual(str(code), "1234")
        subcode = Subcode.objects.get(pk=1)
        self.assertEqual(str(subcode), '00')
        self.assertEqual(subcode.titles, 'Salaries - Academic')
        self.assertEqual(subcode.notes,
                         'LBS will balance sub 00 fund 19900 at year end')

    def test_account(self):
        account = Account.objects.create(
            account="123456", unit=Unit.objects.get(pk=1))
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
        ###self.assertEqual(response.status_code, 200)
