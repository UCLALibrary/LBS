from django.test import TestCase
from ge.models import BFSImport, CDWImport, MTFImport, LibraryData
from ge.views_utils import (
    create_excel_output,
    get_data_from_excel,
    get_librarydata_results,
    import_excel_data,
    add_funds,
    update_data,
)


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


class AddFundsTestCase(TestCase):
    fixtures = [
        "sample_bfs_data.json",
        "sample_cdw_data.json",
        "sample_mtf_data.json",
        "sample_library_data.json",
    ]

    def test_new_fund_is_added(self):
        # The incoming data should add 1 fund to existing data.
        before = LibraryData.objects.count()
        add_funds()
        self.assertEqual(LibraryData.objects.count(), before + 1)

    def test_correct_new_fund_is_added(self):
        # The only new fund created should be an additional one for 48083.
        self.assertEqual(LibraryData.objects.filter(fau_fund="48083").count(), 1)
        add_funds()
        self.assertEqual(LibraryData.objects.filter(fau_fund="48083").count(), 2)

    def test_new_fund_title_is_correct(self):
        # The new fund is 48083 5T 432975.
        # Confirm the fund title was set correctly.
        add_funds()
        new_fund = LibraryData.objects.filter(
            fau_fund="48083", fau_cost_center="5T", fau_account="432975"
        ).first()
        self.assertEqual(
            new_fund.fund_title, "UCLA FDN/JOHN H. MITCHELL INFRASTRUCTURE"
        )

    def test_new_fund_type_is_correct(self):
        # The new fund is 48083 5T 432975.
        # Confirm the fund type was set correctly.
        add_funds()
        new_fund = LibraryData.objects.filter(
            fau_fund="48083", fau_cost_center="5T", fau_account="432975"
        ).first()
        self.assertEqual(new_fund.fund_type, "Current Expenditure")

    def test_new_fund_reg_fdn_is_correct(self):
        # The new fund is 48083 5T 432975.
        # Confirm the fund reg_fdn flag was set correctly.
        add_funds()
        new_fund = LibraryData.objects.filter(
            fau_fund="48083", fau_cost_center="5T", fau_account="432975"
        ).first()
        self.assertEqual(new_fund.reg_fdn, "F")

    def test_new_fund_flag_is_cleared(self):
        # The new fund is 48083 5T 432975.
        # Confirm the new_fund flag was correctly cleared (set to N).
        add_funds()
        new_fund = LibraryData.objects.filter(
            fau_fund="48083", fau_cost_center="5T", fau_account="432975"
        ).first()
        self.assertEqual(new_fund.new_fund, "N")


class UpdateDataTestCase(TestCase):
    fixtures = [
        "sample_bfs_data.json",
        "sample_cdw_data.json",
        "sample_mtf_data.json",
        "sample_library_data.json",
    ]

    @classmethod
    def setup(self):
        # All of these tests require that add_data() has already run.
        add_funds()

    def test_max_mtf_trf_amt_is_updated(self):
        # qryAAA_1UpdateMTF
        before = LibraryData.objects.filter(ucop_fdn_no="81081E").first()
        self.assertEqual(before.max_mtf_trf_amt, 0.0)
        update_data()
        after = LibraryData.objects.filter(ucop_fdn_no="81081E").first()
        self.assertEqual(after.max_mtf_trf_amt, 16159.28)

    def test_projected_annual_income_foundation_is_updated(self):
        # qryAAA_2ProjIncomFound
        before = LibraryData.objects.filter(ucop_fdn_no="81081E").first()
        self.assertEqual(before.projected_annual_income, 0.0)
        update_data()
        after = LibraryData.objects.filter(ucop_fdn_no="81081E").first()
        self.assertEqual(after.projected_annual_income, 64978.23)

    def test_projected_annual_income_regental_is_updated(self):
        # qryAAA_2ProjIncomReg (join conditions are different from qryAAA_2ProjIncomFound)
        before = LibraryData.objects.filter(fau_fund="16333").first()
        self.assertEqual(before.projected_annual_income, 0.0)
        update_data()
        after = LibraryData.objects.filter(fau_fund="16333").first()
        self.assertEqual(after.projected_annual_income, 262283.98)

    def test_total_fund_value_ucop_foundation_is_updated(self):
        # qryAAA_3FoundTotVal
        before = LibraryData.objects.filter(ucop_fdn_no="18980E").first()
        self.assertEqual(before.total_fund_value, 42819.14)
        update_data()
        after = LibraryData.objects.filter(ucop_fdn_no="18980E").first()
        self.assertEqual(after.total_fund_value, 42723.53)

    def test_total_fund_value_fau_foundation_is_updated(self):
        # qryAAA_3FoundTotVal_2 (join conditions are different from qryAAA_3FoundTotVal)
        before = LibraryData.objects.filter(fau_fund="50074").first()
        self.assertEqual(before.total_fund_value, 157538.94)
        update_data()
        after = LibraryData.objects.filter(fau_fund="50074").first()
        self.assertEqual(after.total_fund_value, 20939.95)

    #
    # qryAAA_3FoundTotVal_3 not implemented - no current values match, LBS says not really used.
    #

    def test_total_fund_value_fau_regental_u_and_r_is_updated(self):
        # qryAAA_3RegTotVal, qryAAA_3RegTotVal_2, qryAAA_3RegTotVal_3 together
        # for this fund (combines available / unavailable and market value)
        before = LibraryData.objects.filter(fau_fund="36699").first()
        self.assertEqual(before.total_fund_value, 1691852.78)
        update_data()
        after = LibraryData.objects.filter(fau_fund="36699").first()
        self.assertEqual(after.total_fund_value, 1691852.78)

    def test_total_fund_value_fau_regental_u_only_is_updated(self):
        # qryAAA_3RegTotVal; qryAAA_3RegTotVal_2 & _3 not relevant for this fund
        before = LibraryData.objects.filter(fau_fund="41594").first()
        self.assertEqual(before.total_fund_value, 1583.16)
        update_data()
        after = LibraryData.objects.filter(fau_fund="41594").first()
        self.assertEqual(after.total_fund_value, 1583.16)

    def test_total_fund_value_fau_regental_u_40k_updated(self):
        # qryAAA_3RegTotVal_4: different conditions / joins
        before = LibraryData.objects.filter(fau_fund_no="53798").first()
        self.assertEqual(before.total_fund_value, 0.0)
        update_data()
        after = LibraryData.objects.filter(fau_fund_no="53798").first()
        self.assertEqual(after.total_fund_value, 0.0)

    def test_funds_are_updated_from_cdw(self):
        # qryAAA_5_5400
        # Current data has same values for all matching funds,
        # so confirm... nothing changes.
        before = LibraryData.objects.filter(fau_fund_no="50743").first()
        self.assertEqual(before.ytd_appropriation, 533627.5)
        self.assertEqual(before.ytd_expenditure, 15000.00)
        self.assertEqual(before.commitments, 10000.00)
        self.assertEqual(before.operating_balance, 508627.50)
        update_data()
        after = LibraryData.objects.filter(fau_fund_no="50743").first()
        self.assertEqual(after.ytd_appropriation, 533627.5)
        self.assertEqual(after.ytd_expenditure, 15000.00)
        self.assertEqual(after.commitments, 10000.00)
        self.assertEqual(after.operating_balance, 508627.50)


class SearchLibraryDataTestCase(TestCase):
    fixtures = [
        "sample_bfs_data.json",
        "sample_cdw_data.json",
        "sample_mtf_data.json",
        "sample_library_data.json",
    ]

    def test_fund_search_results(self):
        results = get_librarydata_results(search_type="fund", search_term="63557O")
        self.assertEqual(len(results), 1)

    def test_keyword_search_results(self):
        results = get_librarydata_results(search_type="keyword", search_term="FY23")
        self.assertEqual(len(results), 3)

    def test_unit_search_results(self):
        results = get_librarydata_results(search_type="unit", search_term="studies")
        self.assertEqual(len(results), 2)

    def test_search_is_case_insensitive(self):
        # Data in record is "Ludwig"; should find "ludwig"
        results = get_librarydata_results(search_type="keyword", search_term="ludwig")
        self.assertEqual(len(results), 1)

    def test_new_data_is_searched(self):
        # No results before record is added
        results = get_librarydata_results(
            search_type="keyword", search_term="akohler test"
        )
        self.assertEqual(len(results), 0)
        # Add brief record and confirm it's found
        LibraryData.objects.create(fund_title="AKOHLER test record")
        results = get_librarydata_results(
            search_type="keyword", search_term="akohler test"
        )
        self.assertEqual(len(results), 1)

    def test_new_funds_are_found(self):
        # Per notes in AddFundsTestCase.test_correct_new_fund_is_added(),
        # only one new fund is added from our test data.
        add_funds()
        results = get_librarydata_results(search_type="new_funds", search_term="")
        self.assertEqual(len(results), 1)


class ExcelOutputTestCase(TestCase):
    fixtures = [
        "sample_library_data.json",
    ]

    def test_master_report_worksheets(self):
        result = create_excel_output("master")
        # Only one worksheet in Master report
        self.assertEqual(len(result.sheetnames), 1)

    def test_master_report_cols(self):
        result = create_excel_output("master")
        # Last column is "LBS Notes" in column W
        self.assertEqual(result["G&E"]["W2"].value, "LBS Notes")

    def test_master_report_rows(self):
        result = create_excel_output("master")
        # 13 rows in sample data. Data starts on row 5, so we should have data in rows 5-17 and not in 18
        # Master report isn't sorted, so just check if data exists
        self.assertNotEqual(result["G&E"]["A17"].value, None)
        self.assertEqual(result["G&E"]["A18"].value, None)

    def test_unit_report_worksheets(self):
        result = create_excel_output("hssd")
        # two worksheets in HSSD report
        self.assertEqual(len(result.sheetnames), 2)

    def test_unit_report_cols(self):
        result = create_excel_output("hssd")
        # HSSD sample data has fund restriction for Endowments, but not Gifts
        # So "Fund Restriction" should be in column S for Endowments,
        # and Gifts should have "LBS Notes" in column S
        self.assertEqual(result["Endowments"]["S2"].value, "Fund Restriction")
        self.assertEqual(result["Gifts"]["S2"].value, "LBS Notes")

    def test_unit_report_rows(self):
        result = create_excel_output("hssd")
        # HSSD data has 1 gift and 2 endowments, starting on row 5
        self.assertEqual(result["Gifts"]["A5"].value, "HSSD")
        self.assertEqual(result["Gifts"]["A6"].value, None)
        self.assertEqual(result["Endowments"]["A5"].value, "HSSD")
        self.assertEqual(result["Endowments"]["A7"].value, None)

    def test_unit_report_totals(self):
        result = create_excel_output("hssd")
        # Gifts should have totals in cols L, M, N, O. Endowments in L, M, N, O, Q
        # SUM is calculated by Excel, so just check the formulas
        self.assertEqual(result["Gifts"]["L6"].value, "=SUM(L5:L5)")
        self.assertEqual(result["Gifts"]["M6"].value, "=SUM(M5:M5)")
        self.assertEqual(result["Gifts"]["N6"].value, "=SUM(N5:N5)")
        self.assertEqual(result["Gifts"]["O6"].value, "=SUM(O5:O5)")
        self.assertEqual(result["Endowments"]["L7"].value, "=SUM(L5:L6)")
        self.assertEqual(result["Endowments"]["M7"].value, "=SUM(M5:M6)")
        self.assertEqual(result["Endowments"]["N7"].value, "=SUM(N5:N6)")
        self.assertEqual(result["Endowments"]["O7"].value, "=SUM(O5:O6)")
        self.assertEqual(result["Endowments"]["Q7"].value, "=SUM(Q5:Q6)")

    def test_ul_report_worksheets(self):
        result = create_excel_output("ul")
        # two worksheets in UL report
        self.assertEqual(len(result.sheetnames), 2)

    def test_ul_report_cols(self):
        result = create_excel_output("ul")
        #  Max MTF Transfer Amt should be in column P on both sheets
        self.assertEqual(result["Endowments"]["P2"].value, "Max MTF Transfer Amt")
        self.assertEqual(result["Gifts"]["P2"].value, "Max MTF Transfer Amt")
        # No fund restrictions, so "LBS Notes" should be in column V for Endowments, U for Gifts
        self.assertEqual(result["Endowments"]["V2"].value, "LBS Notes")
        self.assertEqual(result["Gifts"]["U2"].value, "LBS Notes")

    def test_ul_report_rows(self):
        result = create_excel_output("ul")
        # UL data has 1 gift and 1 endowment, starting on row 5
        self.assertEqual(result["Gifts"]["A5"].value, "UL")
        self.assertEqual(result["Gifts"]["A6"].value, None)
        self.assertEqual(result["Endowments"]["A5"].value, "UL")
        self.assertEqual(result["Endowments"]["A6"].value, None)

    def test_ul_report_totals(self):
        result = create_excel_output("ul")
        # Gifts should have totals in cols L, M, N, O, P, Q. Endowments in L, M, N, O, P, Q, S
        # SUM is calculated by Excel, so just check the formulas
        self.assertEqual(result["Gifts"]["L6"].value, "=SUM(L5:L5)")
        self.assertEqual(result["Gifts"]["M6"].value, "=SUM(M5:M5)")
        self.assertEqual(result["Gifts"]["N6"].value, "=SUM(N5:N5)")
        self.assertEqual(result["Gifts"]["O6"].value, "=SUM(O5:O5)")
        self.assertEqual(result["Gifts"]["P6"].value, "=SUM(P5:P5)")
        self.assertEqual(result["Gifts"]["Q6"].value, "=SUM(Q5:Q5)")
        self.assertEqual(result["Endowments"]["L6"].value, "=SUM(L5:L5)")
        self.assertEqual(result["Endowments"]["M6"].value, "=SUM(M5:M5)")
        self.assertEqual(result["Endowments"]["N6"].value, "=SUM(N5:N5)")
        self.assertEqual(result["Endowments"]["O6"].value, "=SUM(O5:O5)")
        self.assertEqual(result["Endowments"]["P6"].value, "=SUM(P5:P5)")
        self.assertEqual(result["Endowments"]["Q6"].value, "=SUM(Q5:Q5)")
        self.assertEqual(result["Endowments"]["S6"].value, "=SUM(S5:S5)")

    def test_aul_report_worksheets(self):
        result = create_excel_output("aul_grappone")
        # two worksheets in AUL report
        self.assertEqual(len(result.sheetnames), 2)

    def test_aul_report_cols(self):
        result = create_excel_output("aul_grappone")
        # Grappone sample data has fund restriction for Gifts, but not Endowments
        # So "Fund Restriction" should be in column R for Gifts,
        # and Endowments should have "LBS Notes" in column T
        self.assertEqual(result["Gifts"]["R2"].value, "Fund Restriction")
        self.assertEqual(result["Endowments"]["T2"].value, "LBS Notes")

    def test_aul_report_rows(self):
        result = create_excel_output("aul_grappone")
        # 1 gift and 1 endowment, starting on row 5
        self.assertEqual(result["Gifts"]["A5"].value, "AUL Grappone")
        self.assertEqual(result["Gifts"]["A6"].value, None)
        self.assertEqual(result["Endowments"]["A5"].value, "AUL Grappone")
        self.assertEqual(result["Endowments"]["A6"].value, None)

    def test_aul_report_totals(self):
        result = create_excel_output("aul_grappone")
        # Gifts should have totals in cols L, M, N, O. Endowments in L, M, N, O, Q
        # SUM is calculated by Excel, so just check the formulas
        self.assertEqual(result["Gifts"]["L6"].value, "=SUM(L5:L5)")
        self.assertEqual(result["Gifts"]["M6"].value, "=SUM(M5:M5)")
        self.assertEqual(result["Gifts"]["N6"].value, "=SUM(N5:N5)")
        self.assertEqual(result["Gifts"]["O6"].value, "=SUM(O5:O5)")
        self.assertEqual(result["Endowments"]["L6"].value, "=SUM(L5:L5)")
        self.assertEqual(result["Endowments"]["M6"].value, "=SUM(M5:M5)")
        self.assertEqual(result["Endowments"]["N6"].value, "=SUM(N5:N5)")
        self.assertEqual(result["Endowments"]["O6"].value, "=SUM(O5:O5)")
        self.assertEqual(result["Endowments"]["Q6"].value, "=SUM(Q5:Q5)")
