from mock import mock_open, patch, Mock, MagicMock
import reportgen.reporting.util as util
import unittest

class TestStandaloneFunctions(unittest.TestCase):
    def setUp(self):
        def wrapToken(token):
            wrappedToken = Mock()
            wrappedToken.value = token
            return wrappedToken

        rows = [["Consequence", "Symbol", "Gene", "Feature", "Amino_acid_changes", "Flag"],
        ["missense_variant", "BRAF", "ENSG00000157764", "ENST00000288602", "p.Val600Glu", "BRAF_COMMON"],
        ["missense_variant", "KRAS", "ENSG00000133703", "ENST00000256078", "12,13,60,61,117,146", "KRAS_COMMON"],
        ["missense_variant", "NRAS", "ENSG00000213281", "ENST00000369535", "12,13,61", "NRAS_COMMON"]]

        self.mock_iter_rows_valid_colorectal_mutations_table = \
            iter(map(lambda row: map(lambda token: wrapToken(token), row), rows))

        rows = [["Consequence", "Symbol", "Gene", "Feature", "Amino_acid_changes", "Flag"],
        ["amplification", "IGF2", "ENSG00000167244", "", "", "ALASCCA_CLASS_B_1"],
        ["start_lost,stop_gained,frameshift_variant,splice_acceptor_variant,splice_donor_variant,loss_of_heterozygosity", "PTEN", "ENSG00000171862", "ENST00000371953", "", "ALASCCA_CLASS_B_2"],
        ["homozygous_loss", "PTEN", "ENSG00000171862", "ENST00000371953", "", "ALASCCA_CLASS_B_1"],
        ["missense_variant", "PTEN", "ENSG00000171862", "ENST00000371953", "p.Cys124Ser,p.Gly129Glu,p.Arg130Gly,p.Arg130Gln", "ALASCCA_CLASS_B_1"],
        ["frameshift_variant,inframe_insertion,inframe_deletion,stop_gained,splice_acceptor_variant,splice_donor_variant", "PIK3R1", "ENSG00000145675", "ENST00000521381", "340:670", "ALASCCA_CLASS_B_1"],
        ["missense_variant", "PIK3R1", "ENSG00000145675", "ENST00000521381", "376,379,452,464,503,560,564,567,573,642", "ALASCCA_CLASS_B_1"],
        ["missense_variant", "PIK3CA", "ENSG00000121879", "ENST00000263967", "38,81,88,106,111,118,344,345,378,420,453,726", "ALASCCA_CLASS_B_1"],
        ["missense_variant", "PIK3CA", "ENSG00000121879", "ENST00000263967", "542,545,546,1021,1043,1044,1047", "ALASCCA_CLASS_A"]]

        self.mock_iter_rows_valid_alascca_table = \
            iter(map(lambda row: map(lambda token: wrapToken(token), row), rows))

    @patch('reportgen.reporting.util.openpyxl')
    def test_extract_mutation_spreadsheet_contents_valid_data1(self, mock_openpyxl):
        mock_openpyxl.load_workbook().get_sheet_by_name().iter_rows = MagicMock()
        mock_openpyxl.load_workbook().get_sheet_by_name().iter_rows.return_value = \
            self.mock_iter_rows_valid_colorectal_mutations_table

        spreadsheet_contents = util.extract_mutation_spreadsheet_contents("dummy_filename")

        self.assertEqual(len(spreadsheet_contents), 3)
        self.assertEqual(len(spreadsheet_contents[0]), 6)
        self.assertEqual(spreadsheet_contents[2][0], ["missense_variant"])
        self.assertEqual(spreadsheet_contents[1][4], ["12","13","60","61","117","146"])

    @patch('reportgen.reporting.util.openpyxl')
    def test_extract_mutation_spreadsheet_contents_valid_data2(self, mock_openpyxl):
        mock_openpyxl.load_workbook().get_sheet_by_name().iter_rows = MagicMock()
        mock_openpyxl.load_workbook().get_sheet_by_name().iter_rows.return_value = \
            self.mock_iter_rows_valid_alascca_table

        spreadsheet_contents = util.extract_mutation_spreadsheet_contents("dummy_filename")

        self.assertEqual(len(spreadsheet_contents), 8)
        self.assertEqual(len(spreadsheet_contents[3]), 6)
        self.assertEqual(spreadsheet_contents[2][1], "PTEN")
        self.assertEqual(spreadsheet_contents[4][0],
                         ["frameshift_variant", "inframe_insertion",
                          "inframe_deletion", "stop_gained",
                          "splice_acceptor_variant", "splice_donor_variant"])

    def test_id_valid_valid_input(self):
        self.assertTrue(util.id_valid("01234567"))

    def test_id_valid_letter_input(self):
        self.assertFalse(util.id_valid("ABCDEFGH"))

    def test_get_addresses_all_unique(self):
        id2addresses = {"100": [{"attn": "name1",
                                     "line1": "street1",
                                     "line2": "city1",
                                     "line3": "0123"},
                                     {"attn": "name2",
                                     "line1": "street2",
                                     "line2": "city2",
                                     "line3": "0124"}],
                        "101": [{"attn": "name3",
                                     "line1": "street3",
                                     "line2": "city3",
                                     "line3": "0125"}]}

        addresses = util.get_addresses(id2addresses, ["100", "101"])
        self.assertEqual(addresses, [{"attn": "name1", "line1": "street1", "line2": "city1", "line3": "0123"},
                                     {"attn": "name2", "line1": "street2", "line2": "city2", "line3": "0124"},
                                     {"attn": "name3", "line1": "street3", "line2": "city3", "line3": "0125"}])

    def test_get_addresses_non_unique(self):
        id2addresses = {"100": [{"attn": "name1",
                                     "line1": "street1",
                                     "line2": "city1",
                                     "line3": "0123"},
                                     {"attn": "name2",
                                     "line1": "street2",
                                     "line2": "city2",
                                     "line3": "0124"}],
                        "101": [{"attn": "name3",
                                     "line1": "street3",
                                     "line2": "city3",
                                     "line3": "0125"},
                                     {"attn": "name2",
                                     "line1": "street2",
                                     "line2": "city2",
                                     "line3": "0124"}]}

        addresses = util.get_addresses(id2addresses, ["100", "101"])

        self.assertEqual(addresses, [{"attn": "name1", "line1": "street1", "line2": "city1", "line3": "0123"},
                                     {"attn": "name2", "line1": "street2", "line2": "city2", "line3": "0124"},
                                     {"attn": "name3", "line1": "street3", "line2": "city3", "line3": "0125"}])

    def test_get_addresses_id_missing(self):
        id2addresses = {"100": [{"attn": "name1",
                                     "line1": "street1",
                                     "line2": "city1",
                                     "line3": "0123"},
                                     {"attn": "name2",
                                     "line1": "street2",
                                     "line2": "city2",
                                     "line3": "0124"}]}

        self.assertRaises(ValueError, util.get_addresses, id2addresses, ["100", "101"])


    def test_parse_address_table_invalid_header(self):
        open_name = '%s.open' % __name__
        with patch(open_name, mock_open(read_data='An invalid header\n1\tDummy hospital name\tDoctors name\tan.email @ email.com\tStreetname 1\tA hospital name, Suburb\t100 00 Cityname\n'), create=True):
            with open("dummy_filename.txt") as test_file:
                self.assertRaises(util.AddressFileParseException, lambda: util.parse_address_table(test_file))


    def test_parse_address_table_invalid_number_cols(self):
        open_name = '%s.open' % __name__
        with patch(open_name, mock_open(read_data='Nr\tKlinik\tAttn\tMail\tadress\tAdress\tAdress\tAdress\n1\tDummy hospital name\tDoctors name\tan.email @ email.com\tStreetname 1\tA hospital name, Suburb\t100 00 Cityname\tAn extra invalid column\n'), create=True):
            with open("dummy_filename.txt") as test_file:
                self.assertRaises(util.AddressFileParseException, lambda: util.parse_address_table(test_file))


    def test_parse_address_table_valid_data1(self):
        open_name = '%s.open' % __name__
        with patch(open_name, mock_open(read_data='Nr\tKlinik\tAttn\tMail\tadress\tAdress\tAdress\tAdress\n1\tDummy hospital name\tDoctors name\tan.email @ email.com\tStreetname 1\tA hospital name, Suburb\t100 00 Cityname\n'), create=True):
            with open("dummy_filename.txt") as test_file:
                correct_output = {"1": [
                    {"attn": "Doctors name", "line1": "Streetname 1", "line2": "A hospital name, Suburb",
                     "line3": "100 00 Cityname"}]}
                id2addresses = util.parse_address_table(test_file)
                self.assertDictEqual(id2addresses, correct_output)


#class TestMisc(unittest.TestCase):
#    '''Tests for miscellaneous functions in the reports module.'''

#    def setUp(self):
#        pass
        # NOTE: Reading config rather than explicitly defining dictionary here,
        # since the password is included in this information:
        #path = os.path.expanduser("~/.dbconfig.json")
        #self.config_dict = json.load(open(path))

#        self.cnxn = connect_clinseq_db(self.config_dict)

#    def test_retrieve_report_metadata_missing_sampleID(self):
#        self.assertRaises(ValueError, lambda: retrieve_report_metadata("12345678", "3098849", self.cnxn))

#    def test_retrieve_report_metadata_valid_input(self):
#        # Inputting a valid blood and tumor ID should produce a ReportMetadata
#        # object:
#        report_metadata = retrieve_report_metadata("03098121", "03098849", self.cnxn)
#        self.assertTrue(isinstance(report_metadata, ReportMetadata))

#    def test_retrieve_report_metadata_differing_personnummers(self):
#        # Inputting a valid blood and tumor ID should produce a ReportMetadata
#        # object:
#        self.assertRaises(ValueError, lambda: retrieve_report_metadata("02871131", "03019438", self.cnxn))
