from decimal import Decimal
import arrow
from django.test import TestCase
from qdb.models import Staff, Unit, Account, Subcode, Recipient
from .admin import RecipientAdmin
from qdb.scripts.settings import DEFAULT_RECIPIENTS, REPORTS_DIR
from qdb.scripts.formatter import calculate_fiscal_year_remainder
from qdb.scripts.orchestrator import Orchestrator
from qdb.scripts.parser import Parser
import os


class AdminTestCase(TestCase):
    fixtures = ["sample_data.json"]

    def test_recipientadmin(self):
        recipient = Recipient.objects.get(pk=1)
        self.assertEqual(recipient.recipient_id, 32)
        self.assertEqual(recipient.unit_id, 1)

        namestaff = Staff.objects.get(name="Todd Grappone")
        nameobj = Recipient.objects.get(id=namestaff.id)
        recipient = RecipientAdmin.get_name(RecipientAdmin, nameobj)
        self.assertEqual(str(recipient), str(namestaff))

        unit = Recipient.objects.get(pk=1)
        self.assertEqual(unit.unit_id, 1)


class ModelsTestCase(TestCase):
    fixtures = ["sample_data.json"]

    def test_staff(self):
        name = Staff.objects.create(name="Jane Bruin")
        self.assertEqual(str(name), "Jane Bruin")
        staff = Staff.objects.get(pk=1)
        self.assertEqual(str(staff), "Sharon Farb")
        self.assertEqual(staff.name, "Sharon Farb")
        self.assertEqual(staff.email, "farb@library.ucla.edu")

    def test_unit(self):
        name = Unit.objects.create(name="Arts")
        self.assertEqual(str(name), "Arts")
        unit = Unit.objects.get(pk=1)
        self.assertEqual(str(unit), "Oral History")
        self.assertEqual(unit.name, "Oral History")

    def test_subcode(self):
        subcode = Subcode.objects.create(code="1234")
        self.assertEqual(str(subcode), "1234")

        subcode = Subcode.objects.get(pk=1)
        self.assertEqual(str(subcode), "00")
        self.assertEqual(subcode.titles, "Salaries - Academic")
        self.assertEqual(
            subcode.notes, "LBS will balance sub 00 fund 19900 at year end"
        )

    def test_account(self):
        account = Account.objects.create(account="123456", unit=Unit.objects.get(pk=1))
        self.assertEqual(str(account), "123456")
        self.assertEqual(str(account), "123456")
        account = Account.objects.get(pk=2)
        self.assertEqual(str(account), "436000")
        self.assertEqual(account.account, "436000")
        self.assertEqual(account.cost_center, "BF")
        self.assertEqual(account.title, "LIBRARY:COLL DEV-ORAL HSTR/BUS FORECAST")
        self.assertEqual(account.unit_id, 1)

    def test_recipient(self):
        recipient = Recipient.objects.create(
            unit=Unit.objects.get(pk=1), recipient=Staff.objects.get(pk=1)
        )
        self.assertEqual(str(recipient), "Sharon Farb")
        self.assertEqual(str(recipient.unit), "Oral History")


class FormatterTest(TestCase):
    def test_calculates_fiscal_year_remainder(self):
        self.assertEqual(calculate_fiscal_year_remainder(7), "92%")
        self.assertEqual(calculate_fiscal_year_remainder(12), "50%")
        self.assertEqual(calculate_fiscal_year_remainder(1), "42%")
        self.assertEqual(calculate_fiscal_year_remainder(6), "0%")


class OrchestratorTest(TestCase):
    fixtures = ["sample_data.json"]

    def setUp(self):
        self.orch = Orchestrator(REPORTS_DIR, DEFAULT_RECIPIENTS)

    def test_get_recipients(self):
        actual = self.orch.get_recipients(21, "DIIT Software Development")
        expected = set(
            ["joshuagomez@library.ucla.edu", "grappone@library.ucla.edu"]
        ).union(DEFAULT_RECIPIENTS)
        self.assertEqual(actual, expected)

    def test_exclude_UL(self):
        actual = self.orch.get_recipients(3, "Communication")
        expected = set(["abicho@library.ucla.edu"]).union(DEFAULT_RECIPIENTS)
        self.assertEqual(actual, expected)

    def test_exclude_everyone_but_LBS(self):
        actual = self.orch.get_recipients(2, "LBS")
        expected = set(["doris@library.ucla.edu"]).union(DEFAULT_RECIPIENTS)
        self.assertEqual(actual, expected)

    def test_filename(self):
        unit_name = "DIIT Software Development"
        fullpath = self.orch.generate_filename(unit_name, "202101")
        actual = os.path.split(fullpath)[1]
        self.assertEqual(actual, "DIIT_Software_Development_2021_01.xlsx")

    def test_valid_date(self):
        self.assertEqual(self.orch.validate_date(2019, 1), (2019, 1))

    def test_empty_date(self):
        year, month = self.orch.validate_date()
        self.assertEqual(type(year), int)
        self.assertEqual(type(month), int)
        self.assertTrue(year > 2020)
        self.assertTrue(month >= 1)
        self.assertTrue(month <= 12)

    def test_invalid_month_year_combo(self):
        with self.assertRaises(ValueError):
            self.orch.validate_date(year=2020)
        with self.assertRaises(ValueError):
            self.orch.validate_date(year=2020)

    def test_invalid_months(self):
        with self.assertRaises(ValueError):
            self.orch.validate_date(year=2020, month=0)
        with self.assertRaises(ValueError):
            self.orch.validate_date(year=2020, month=13)
        with self.assertRaises(ValueError):
            self.orch.validate_date(year=2020, month=-6)

    def test_invalid_future_date(self):
        with self.assertRaises(ValueError):
            d1 = arrow.now().shift(months=1)
            self.orch.validate_date(year=d1.year, month=d1.month)
        with self.assertRaises(ValueError):
            d2 = arrow.now().shift(years=1)
            self.orch.validate_date(year=d2.year, month=d2.month)

    def test_yyyymm_format(self):
        self.assertEqual(self.orch.validate_date(2020, 5, True), "202005")
        self.assertEqual(self.orch.validate_date(2020, 12, True), "202012")
        with self.assertRaises(ValueError):
            self.orch.validate_date(2020, 13, True)

    def test_get_all_units(self):
        # get_units() with no parameter gets all units
        units = self.orch.get_units()
        self.assertEqual(type(units), list)
        self.assertTrue(len(units) > 0)

    def test_get_single_unit(self):
        units = self.orch.get_units(27)
        self.assertEqual(type(units), list)
        self.assertEqual(len(units), 1)

    def test_get_accounts_for_unit(self):
        results = self.orch.get_accounts_for_unit(27)
        self.assertEqual(len(results), 7)
        accts = [432974, 432975, 432976, 622975, 622976, 782975, 782976]
        for i in range(len(accts)):
            with self.subTest(i=i):
                self.assertTrue(str(accts[i]) in [t[0] for t in results])

    def test_get_cost_centers_for_accounts_for_unit(self):
        results = self.orch.get_accounts_for_unit(27)
        self.assertEqual(len(results), 7)
        ccs = [
            "2A",
            "2B",
            "3A",
            "3M",
            "5A",
            "5B",
            "5C",
            "5D",
            "5T",
            "5X",
            "6A",
            "6C",
            "S1",
            "S2",
        ]
        for i in range(len(ccs)):
            with self.subTest(i=i):
                self.assertTrue(str(ccs[i]) in results[1][1])

    def test_get_accounts_for_units_structure(self):
        results = self.orch.get_accounts_for_unit(27)
        self.assertEqual(type(results), list)
        for acct, ccs in results:
            with self.subTest(i=acct):
                self.assertEqual(len(acct), 6)
                self.assertEqual(type(ccs), list)
                for cc in ccs:
                    with self.subTest(i=cc):
                        self.assertTrue(len(cc) == 2)


class ParserTest(TestCase):
    def setUp(self):
        self.parser = Parser("202101", "Access Services")

    def test_calculate_percent(self):
        actual = self.parser.calculate_percent_left(100, 50)
        self.assertEqual(actual, Decimal(0.50))
        actual2 = self.parser.calculate_percent_left(90, 30)
        self.assertAlmostEqual(actual2, Decimal(0.33), places=2)
        actual3 = self.parser.calculate_percent_left(10000.00, 2375.00)
        self.assertEqual(actual3, Decimal(0.2375))

    def test_calculate_negative_percent(self):
        actual = self.parser.calculate_percent_left(100, -50)
        self.assertEqual(actual, Decimal(0.00))

    def test_calculate_zero_approp(self):
        actual = self.parser.calculate_percent_left(0, 50)
        self.assertEqual(actual, Decimal(0.00))

    def test_calculate_negative_approp(self):
        actual = self.parser.calculate_percent_left(-50, 50)
        self.assertEqual(actual, Decimal(0.00))

    def test_calculate_double_negative(self):
        actual = self.parser.calculate_percent_left(1100, -100)
        self.assertEqual(actual, Decimal(0.00))

    def test_calculate_totals(self):
        subs = {
            "01": {
                "Amount": Decimal("496804.04"),
                "Appropriation": Decimal("1195663.83"),
                "Encumbrance": Decimal("0"),
                "Expense": Decimal("698859.79"),
                "Memo Lien": Decimal("0"),
                "Percent": Decimal("41.55047828117373091398106439"),
            },
            "02": {
                "Amount": Decimal("-39603.08"),
                "Appropriation": Decimal("0"),
                "Encumbrance": Decimal("0"),
                "Expense": Decimal("39603.08"),
                "Memo Lien": Decimal("0"),
                "Percent": Decimal("0"),
            },
            "03": {
                "Amount": Decimal("14474.57"),
                "Appropriation": Decimal("27105.05"),
                "Encumbrance": Decimal("44.1"),
                "Expense": Decimal("12586.38"),
                "Memo Lien": Decimal("0"),
                "Percent": Decimal("53.40174616907181503077839738"),
            },
        }
        totals = self.parser.calculate_totals(subs)
        self.assertAlmostEqual(totals["Amount"], Decimal(471675.53), places=2)
        self.assertAlmostEqual(totals["Appropriation"], Decimal(1222768.88), places=2)
        self.assertAlmostEqual(totals["Encumbrance"], Decimal(44.10), places=2)
        self.assertAlmostEqual(totals["Expense"], Decimal(751049.25), places=2)
        self.assertAlmostEqual(totals["Memo Lien"], Decimal(0), places=2)

    def test_omits_all_zeroes(self):
        row = {
            "account_number": "605000",
            "account_title": "LIBRARY: SYSTEMS-SYSTEMS                ",
            "aul": "AUL",
            "cost_center_code": "LD",
            "department": "DEPARTMENT",
            "department_head": "DEPT_HEAD",
            "encumbrance": Decimal("0"),
            "fau": "605000 LD 18084 LIBRARY: SYSTEMS-SYSTEMS                 OBSOLETE "
            "EQUIPMENT (LOTTERY FUNDS)      ",
            "fund_number": "18084",
            "fund_title": "OBSOLETE EQUIPMENT (LOTTERY FUNDS)      ",
            "memo_lien": Decimal("0"),
            "operating_bal_am": Decimal("0"),
            "sub_code": "08",
            "sub_code_name": "SUB_CODE_NAME",
            "ytd_approp": Decimal("0"),
            "ytd_expense": Decimal("0"),
        }
        self.assertTrue(self.parser.exclude(row))
