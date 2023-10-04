from django.test import TestCase
from ge.models import BFSImport, CDWImport, MTFImport
from ge.views_utils import get_data_from_excel, import_excel_data


class ImportExcelDataTestCase(TestCase):
    # 5 sample rows
    bfs_sample_file = "sample_files/sample_consolidated.xls"
    bfs_expected_funds = {"07808", "14049", "14050", "14248"}
    # 6 sample rows
    cdw_sample_file = "sample_files/sample_ledger.xls"
    cdw_expected_depts = {"0461", "5400"}
    # 4 sample rows
    mtf_sample_file = "sample_files/sample_mtf.xls"
    mtf_expected_bals = [93020.74, 182.49, 9696.30, 15679.78]

    def test_bfs_read(self):
        data = get_data_from_excel(self.bfs_sample_file)
        self.assertEqual(len(data), 5)
        # Confirm the 0-padded Fund values are read correctly.
        data_funds = set([row["Fund"] for row in data])
        self.assertEqual(data_funds, self.bfs_expected_funds)

    def test_bfs_import(self):
        import_excel_data(self.bfs_sample_file, BFSImport)
        self.assertEqual(BFSImport.objects.count(), 5)
        # Confirm the 0-padded Fund values are stored and read correctly.
        model_funds = set(BFSImport.objects.all().values_list("fau_fund", flat=True))
        self.assertEqual(model_funds, self.bfs_expected_funds)

    def test_cdw_read(self):
        data = get_data_from_excel(self.cdw_sample_file)
        self.assertEqual(len(data), 6)
        # Confirm the 0-padded Department values are read correctly.
        data_depts = set([row["Account Department Code"] for row in data])
        self.assertEqual(data_depts, self.cdw_expected_depts)

    def test_cdw_import(self):
        import_excel_data(self.cdw_sample_file, CDWImport)
        self.assertEqual(CDWImport.objects.count(), 6)
        # Confirm the 0-padded Department values are stored and read correctly.
        model_depts = set(CDWImport.objects.all().values_list("fau_dept", flat=True))
        self.assertEqual(model_depts, self.cdw_expected_depts)

    def test_mtf_read(self):
        data = get_data_from_excel(self.mtf_sample_file)
        self.assertEqual(len(data), 4)
        # Confirm the floating point balances are read correctly.
        data_bals = [row["available_bal"] for row in data]
        self.assertEqual(data_bals, self.mtf_expected_bals)

    def test_mtf_import(self):
        import_excel_data(self.mtf_sample_file, MTFImport)
        self.assertEqual(MTFImport.objects.count(), 4)
        # Confirm the floating point balances are stored and read correctly.
        model_bals = [
            val
            for val in MTFImport.objects.all().values_list(
                "available_balance", flat=True
            )
        ]
        self.assertEqual(model_bals, self.mtf_expected_bals)
