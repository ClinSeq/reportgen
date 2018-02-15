import reportgen.rules.general as general
import unittest
from mock import mock_open, patch, Mock, MagicMock
import reportgen.reporting.metadata as metadata

class TestStandaloneFunctions(unittest.TestCase):
    def setUp(self):
        self.id2addresses = {"101": None}

    @patch('reportgen.reporting.metadata.sqlalchemy')
    def test_query_database_no_barcode_attributes(self, mock_sqlalchemy):
        mock_sqlalchemy.or_ = Mock()

        mock_referral_type = Mock()
        mock_session = Mock()
        mock_session.query = Mock()
        mock_session.query().filter().all = Mock(side_effect=[["dummy"]])

        self.assertRaises(ValueError, metadata.query_database, "03098121", mock_referral_type, mock_session)

    @patch('reportgen.reporting.metadata.sqlalchemy')
    def test_query_database_no_hit(self, mock_sqlalchemy):
        mock_sqlalchemy.or_ = Mock()
        
        mock_referral_type = Mock()
        mock_referral_type.barcode1 = "03098121"
        mock_session = Mock()
        mock_session.query = Mock()
        mock_session.query().filter().all = Mock(side_effect=[[]])

        self.assertRaises(ValueError, metadata.query_database, "03098121", mock_referral_type, mock_session)

    @patch('reportgen.reporting.metadata.sqlalchemy')
    def test_query_database_one_hit(self, mock_sqlalchemy):
        mock_sqlalchemy.or_ = Mock()

        mock_referral_type = Mock()
        mock_referral_type.barcode1 = "03098121"
        mock_session = Mock()
        mock_session.query = Mock()
        mock_session.query().filter().all = Mock(side_effect=[["dummy"]])
        
        output = metadata.query_database("03098121", mock_referral_type, mock_session)
        self.assertEqual(output, "dummy")

    @patch('reportgen.reporting.metadata.sqlalchemy')
    def test_query_database_two_hit(self, mock_sqlalchemy):
        mock_sqlalchemy.or_ = Mock()

        mock_referral_type = Mock()
        mock_referral_type.barcode1 = "03098121"
        mock_session = Mock()
        mock_session.query = Mock()
        mock_session.query().filter().all = Mock(side_effect=[["dummy", "dummy2"]])

        self.assertRaises(ValueError, metadata.query_database, "03098121", mock_referral_type, mock_session)

    @patch('reportgen.reporting.metadata.sqlalchemy')
    def test_retrieve_report_metadata_missing_blood_ref(self, mock_sqlalchemy):
        mock_sqlalchemy.or_ = Mock()

        mock_session = Mock()
        mock_session.query = Mock()
        mock_session.query().filter().all = Mock(side_effect=[[], []])

        self.assertRaises(ValueError, metadata.retrieve_report_metadata, "03098121", "03098849", mock_session, self.id2addresses)

    @patch('reportgen.reporting.metadata.sqlalchemy')
    def test_retrieve_report_metadata_double_tumor_ref(self, mock_sqlalchemy):
        mock_sqlalchemy.or_ = Mock()

        mock_session = Mock()
        mock_session.query = Mock()
        mock_session.query().filter().all = Mock(side_effect=[["dummy"], ["dummy1", "dummy2"]])

        self.assertRaises(ValueError, metadata.retrieve_report_metadata, "03098121", "03098849", mock_session, self.id2addresses)

    @patch('reportgen.reporting.metadata.sqlalchemy')
    def test_retrieve_report_metadata_mismatching_ids(self, mock_sqlalchemy):
        mock_sqlalchemy.or_ = Mock()

        mock_session = Mock()
        mock_session.query = Mock()
        mock_blood_ref = Mock()
        mock_blood_ref.pnr = "1212121212"

        mock_tissue_ref = Mock()
        mock_tissue_ref.pnr = "1212121213"
        mock_session.query().filter().all = Mock(side_effect=[[mock_blood_ref], [mock_tissue_ref]])

        self.assertRaises(ValueError, metadata.retrieve_report_metadata, "03098121", "03098849", mock_session, self.id2addresses)

    @patch('reportgen.reporting.metadata.sqlalchemy')
    @patch('reportgen.reporting.metadata.get_addresses')
    def test_retrieve_report_metadata_valid_inputs(self, get_addresses, mock_sqlalchemy):
        get_addresses = Mock(return_value="dummyAddresses")

        mock_sqlalchemy.or_ = Mock()

        mock_session = Mock()
        mock_session.query = Mock()
        mock_blood_ref = Mock()
        mock_blood_ref.pnr = "1212121212"
        mock_blood_ref.crid = "1111111"
        mock_blood_ref.collection_date = "2016-01-01"

        mock_tissue_ref = Mock()
        mock_tissue_ref.pnr = "1212121212"
        mock_tissue_ref.crid = "2222222"
        mock_tissue_ref.collection_date = "2016-01-01"
        mock_session.query().filter().all = Mock(side_effect=[[mock_blood_ref], [mock_tissue_ref]])

        out_dict = metadata.retrieve_report_metadata("03098121", "03098849", mock_session, self.id2addresses)
        self.assertEqual(out_dict["personnummer"], "1212121212")
        self.assertEqual(out_dict["blood_sample_ID"], "03098121")
        self.assertEqual(out_dict["blood_sample_date"], "2016-01-01")
        self.assertEqual(out_dict["tumor_sample_ID"], "03098849")
