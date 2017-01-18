# -*- coding: utf-8 -*-
import unittest
from mock import Mock

from reportgen.reporting.features import *
from reportgen.reporting.caveats import *

class TestAlasccaClassReport(unittest.TestCase):
    def setUp(self):
        self.test_obj = AlasccaClassReport()

    def test_get_component_name(self):
        self.assertEquals(self.test_obj.component_name(), "alascca_class_report")

    def test_starts_no_class(self):
        self.assertEquals(self.test_obj.pathway_class, None)

    def test_setting_class(self):
        self.test_obj.pathway_class = AlasccaClassReport.MUTN_CLASS_A
        self.assertEquals(self.test_obj.pathway_class, AlasccaClassReport.MUTN_CLASS_A)

    def test_to_dict_with_val(self):
        self.test_obj.pathway_class = AlasccaClassReport.MUTN_CLASS_A
        self.assertEquals(self.test_obj.to_dict,
                          {AlasccaClassReport.ALASCCA_CLASS_FEATURENAME:AlasccaClassReport.MUTN_CLASS_A})

    def test_apply_caveat_no_change_neg(self):
        self.test_obj.pathway_class = FeatureStatus.NOT_MUTATED
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=False)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=False)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj.pathway_class, FeatureStatus.NOT_MUTATED)

    def test_apply_caveat_no_change_pos(self):
        self.test_obj.pathway_class = AlasccaClassReport.MUTN_CLASS_A
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=False)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=False)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj.pathway_class, AlasccaClassReport.MUTN_CLASS_A)

    def test_apply_caveat_all_to_eb_neg(self):
        self.test_obj.pathway_class = FeatureStatus.NOT_MUTATED
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=True)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=False)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj.pathway_class, FeatureStatus.NOT_DETERMINED)

    def test_apply_caveat_all_to_eb_pos(self):
        self.test_obj.pathway_class = AlasccaClassReport.MUTN_CLASS_A
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=True)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=False)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj.pathway_class, FeatureStatus.NOT_DETERMINED)

    def test_apply_caveat_non_pos_to_eb_neg(self):
        self.test_obj.pathway_class = FeatureStatus.NOT_MUTATED
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=False)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=True)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj.pathway_class, FeatureStatus.NOT_DETERMINED)

    def test_apply_caveat_non_pos_to_eb_pos(self):
        self.test_obj.pathway_class = AlasccaClassReport.MUTN_CLASS_A
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=False)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=True)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj.pathway_class, AlasccaClassReport.MUTN_CLASS_A)
