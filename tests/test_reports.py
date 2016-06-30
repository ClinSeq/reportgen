import json, os, unittest

from reportgen.reporting.genomics import ReportCompiler

from mock import mock_open, patch, Mock, MagicMock


# Very basic testing of this class at the moment. Perhaps add more tests here.
class TestReportCompiler(unittest.TestCase):
    def setUp(self):
        pass

    def test_extract_features_empty(self):
        compiler = ReportCompiler([])
        compiler.extract_features()
        self.assertEqual({}, compiler._name2feature)

    def test_to_dict_empty(self):
        compiler = ReportCompiler([])
        compiler.extract_features()
        self.assertEqual({}, compiler.to_dict())


























































