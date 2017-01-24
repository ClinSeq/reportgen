# -*- coding: utf-8 -*-
import unittest
from mock import Mock, MagicMock, patch
from reportgen.rules.general import Alteration, AlteredGene, Gene

from reportgen.reporting.features import *

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
        self.assertEquals(self.test_obj.to_dict(),
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


class TestMsiReport(unittest.TestCase):
    def setUp(self):
        self.test_obj = MsiReport()

    def test_get_component_name(self):
        self.assertEquals(self.test_obj.component_name(), "msi_report")

    def test_starts_with_no_status(self):
        self.assertEquals(self.test_obj.msi_status, None)

    def test_setting_status(self):
        self.test_obj.msi_status = MsiReport.MSI
        self.assertEquals(self.test_obj.msi_status, MsiReport.MSI)

    def test_to_dict_with_val(self):
        self.test_obj.msi_status = MsiReport.MSS
        self.assertEquals(self.test_obj.to_dict(), {MsiReport.MSI_FEATURENAME: MsiReport.MSS})

    def test_apply_caveat_no_change_neg(self):
        self.test_obj.msi_status = MsiReport.MSS
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=False)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=False)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj.msi_status, MsiReport.MSS)

    def test_apply_caveat_no_change_msi(self):
        self.test_obj.msi_status = MsiReport.MSI
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=False)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=False)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj.msi_status, MsiReport.MSI)

    def test_apply_caveat_all_to_eb_neg(self):
        self.test_obj.msi_status = MsiReport.MSS
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=True)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=False)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj.msi_status, FeatureStatus.NOT_DETERMINED)

    def test_apply_caveat_all_to_eb_msi(self):
        self.test_obj.msi_status = MsiReport.MSI
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=True)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=False)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj.msi_status, FeatureStatus.NOT_DETERMINED)

    def test_apply_caveat_non_pos_to_eb_neg(self):
        self.test_obj.msi_status = MsiReport.MSS
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=False)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=True)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj.msi_status, FeatureStatus.NOT_DETERMINED)

    def test_apply_caveat_non_pos_to_eb_msi(self):
        self.test_obj.msi_status = MsiReport.MSI
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=False)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=True)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj.msi_status, FeatureStatus.NOT_DETERMINED)


class TestSimpleSomaticMutationsReport(unittest.TestCase):
    def setUp(self):
        self.test_obj = SimpleSomaticMutationsReport()
        self.test_gene_name = "TestGene"
        test_gene = Gene(self.test_gene_name)
        test_altered_gene = AlteredGene(test_gene)
        self.test_mutn = Alteration(test_altered_gene, "TestTranscriptID", "missense_variant", "p.Val1Glu")

    def test_get_component_name(self):
        self.assertEquals(self.test_obj.component_name(), "simple_somatic_mutations_report")

    def test_starts_empty(self):
        self.assertEquals(self.test_obj.to_dict(), {})

    def test_add_gene(self):
        self.test_obj.add_gene("TestGeneName")
        self.assertEquals(self.test_obj.to_dict(), {"TestGeneName":MutationStatus().to_dict()})

    def test_add_mutation(self):
        test_flag = "TestFlag"
        test_mutn = Mock()
        self.test_obj.add_gene(self.test_gene_name)
        test_mutn.get_altered_gene().get_gene().get_symbol = MagicMock(return_value=self.test_gene_name)
        self.test_obj.add_mutation(test_mutn, test_flag)
        self.assertEquals(self.test_obj._symbol2mutation_status.keys(), [self.test_gene_name])

    def test_to_dict_one_gene(self):
        test_gene_name = "TestGeneName"
        self.test_obj.add_gene(test_gene_name)
        mock_dict = {}
        with patch('reportgen.rules.general.MutationStatus.to_dict', return_value=mock_dict):
            self.assertEquals(self.test_obj.to_dict(), {test_gene_name:mock_dict})

    def test_apply_caveat_no_change_pos(self):
        self.test_obj.add_gene(self.test_gene_name)
        self.test_obj.add_mutation(self.test_mutn, "TestFlag")
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=False)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=False)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj._symbol2mutation_status[self.test_gene_name]._status, FeatureStatus.MUTATED)

    def test_apply_caveat_no_change_neg(self):
        self.test_obj.add_gene(self.test_gene_name)
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=False)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=False)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj._symbol2mutation_status[self.test_gene_name]._status, FeatureStatus.NOT_MUTATED)

    def test_apply_caveat_all_to_eb_pos(self):
        self.test_obj.add_gene(self.test_gene_name)
        self.test_obj.add_mutation(self.test_mutn, "TestFlag")
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=True)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=False)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj._symbol2mutation_status[self.test_gene_name]._status, FeatureStatus.NOT_DETERMINED)

    def test_apply_caveat_all_to_eb_neg(self):
        self.test_obj.add_gene(self.test_gene_name)
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=True)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=False)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj._symbol2mutation_status[self.test_gene_name]._status, FeatureStatus.NOT_DETERMINED)

    def test_apply_caveat_non_pos_to_eb_pos(self):
        self.test_obj.add_gene(self.test_gene_name)
        self.test_obj.add_mutation(self.test_mutn, "TestFlag")
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=True)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=False)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj._symbol2mutation_status[self.test_gene_name]._status, FeatureStatus.MUTATED)

    def test_apply_caveat_non_pos_to_eb_pos(self):
        self.test_obj.add_gene(self.test_gene_name)
        mock_caveat = Mock()
        mock_caveat.setting_all_to_eb = Mock(return_value=True)
        mock_caveat.setting_non_positive_to_eb = Mock(return_value=False)
        self.test_obj.apply_caveat(mock_caveat)
        self.assertEquals(self.test_obj._symbol2mutation_status[self.test_gene_name]._status, FeatureStatus.NOT_DETERMINED)
