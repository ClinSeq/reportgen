from mock import mock_open, patch
import unittest

from reportgen.rules.alascca import AlasccaClassRule

from reportgen.rules.msi import MsiStatusRule

from reportgen.rules.simple_somatic_mutations import SimpleSomaticMutationsRule

from reportgen.rules.util import FeatureStatus, extract_qc_call

from reportgen.rules.general import AlterationClassification, Gene, AlteredGene, Alteration, MSIStatus
from reportgen.reporting.features import AlasccaClassReport, MsiReport


class TestSimpleSomaticMutationsRule(unittest.TestCase):
    def setUp(self):
        braf_classification = AlterationClassification("BRAF", ["missense_variant"], "ENST00000288602", ["p.Val600Glu"], "BRAF_COMMON")
        kras_classification = AlterationClassification("KRAS", ["missense_variant"], "ENST00000256078", ["12", "13", "60", "61", "117", "146"], "KRAS_COMMON")
        nras_classification = AlterationClassification("NRAS", ["missense_variant"], "ENST00000369535", ["12", "13", "61"], "NRAS_COMMON")
        self._symbol2classifications = {"BRAF": [braf_classification], "KRAS": [kras_classification], "NRAS": [nras_classification]}

        braf = Gene("BRAF")
        braf.set_ID("ENSG00000157764")
        self._braf_gene_single_mutation = AlteredGene(braf)
        self._braf_alteration3 = Alteration(self._braf_gene_single_mutation, "ENST00000288602", "missense_variant", "p.Val600Glu")
        self._braf_gene_single_mutation.add_alteration(self._braf_alteration3)

        kras = Gene("KRAS")
        kras.set_ID("ENSG00000133703")
        self._kras_gene_multiple_mutations = AlteredGene(kras)
        self._kras_alteration1 = Alteration(self._kras_gene_multiple_mutations, "ENST00000256078", "missense_variant", "p.Ala146Pro")
        self._kras_gene_multiple_mutations.add_alteration(self._kras_alteration1)
        # Position only specified:
        self._kras_alteration2 = Alteration(self._kras_gene_multiple_mutations, "ENST00000256078", "missense_variant", "p.Lys117Asn")
        self._kras_gene_multiple_mutations.add_alteration(self._kras_alteration2)
        # A fake mutation that is *not* in the set of KRAS mutations:
        self._kras_alteration3 = Alteration(self._kras_gene_multiple_mutations, "ENST00000256078", "missense_variant", "p.Lys1Asn")
        self._kras_gene_multiple_mutations.add_alteration(self._kras_alteration3)

#    def test_classification_is_same(self):
#        rule = SimpleSomaticMutationsRule("reportgen/assets/COLORECTAL_MUTATION_TABLE.xlsx", {})
#        # FIXME (MAYBE): COULD HAVE THE RIGHT HAND SIDE OF THESE TESTS HARD-CODED INSTEAD OF READ FROM ABOVE.
#        # E.g. Test if there are three elements in the first nras gene alteration.
#        # XXX CONTINUE HERE: INVESTIGATE THIS APPROACH AS AN ALTERNATIVE TO USING ASSERTDICTEQUAL COMBINED WITH
#        # CUSTOM __EQ__ AND __NE__ METHODS.
#        self.assertEqual(rule._gene_symbol2classifications["NRAS"][0], self._symbol2classifications["NRAS"][0])

#    def test_symbol2classification_is_same(self):
#        rule = SimpleSomaticMutationsRule("reportgen/assets/COLORECTAL_MUTATION_TABLE.xlsx", {})
#        self.assertDictEqual(rule._gene_symbol2classifications, self._symbol2classifications)

#    # Test empty input symbol2gene dictionary:
#    def test_apply_empty_input(self):
#        # Mock the extract_mutation_spreadsheet_contents function XXX

#        rule = SimpleSomaticMutationsRule("dummy_filename", {})
#        test_report = rule.apply()
#        expected_outdict = {'NRAS': {"status" : 'Not mutated', "alterations": []},
#                            'BRAF': {"status" : 'Not mutated', "alterations": []},
#                            'KRAS': {"status": 'Not mutated', "alterations" : []}}
#        self.assertDictEqual(test_report.to_dict(), expected_outdict)

    # Test single mutation symbol2gene input dictionary:
    def test_apply_single_mutation_input(self):
        input_symbol2gene = {"BRAF": self._braf_gene_single_mutation}
        rule = SimpleSomaticMutationsRule("reportgen/assets/COLORECTAL_MUTATION_TABLE.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_outdict = {'NRAS': {"status" : 'Not mutated', "alterations": []},
                            'BRAF': {"status": 'Mutated', "alterations": [{"hgvsp": 'p.Val600Glu', "flag": u'BRAF_COMMON'}]},
                            'KRAS': {"status": 'Not mutated', "alterations" : []}}
        self.assertDictEqual(test_report.to_dict(), expected_outdict)

    # Test multiple genes and multiple mutations symbol2gene input dictionary:
    def test_apply_multiple_mutation_input(self):
        input_symbol2gene = {"BRAF": self._braf_gene_single_mutation, "KRAS": self._kras_gene_multiple_mutations}
        rule = SimpleSomaticMutationsRule("reportgen/assets/COLORECTAL_MUTATION_TABLE.xlsx", input_symbol2gene)
        test_report = rule.apply()

        expected_outdict = {'NRAS': {"status" : 'Not mutated', "alterations": []},
                            'BRAF': {"status": 'Mutated', "alterations": [{"hgvsp": 'p.Val600Glu', "flag": u'BRAF_COMMON'}]},
                            'KRAS': {"status": 'Mutated', "alterations" : [{"hgvsp": 'p.Ala146Pro', "flag": u'KRAS_COMMON'},
                                                                           {"hgvsp": 'p.Lys117Asn', "flag": u'KRAS_COMMON'}]}}
        self.assertDictEqual(test_report.to_dict(), expected_outdict)


class TestAlasccaClassRule(unittest.TestCase):
    def setUp(self):
        igf2_classification = AlterationClassification("IGF2", ["amplification"], None, [], "ALASCCA_CLASS_B_1")
        pten_classification_b_2 = AlterationClassification("PTEN", ["start_lost", "stop_gained", "frameshift_variant", "splice_acceptor_variant", "splice_donor_variant", "loss_of_heterozygosity"], "ENST00000371953", [], "ALASCCA_CLASS_B_2")
        pten_classification_b_1 = AlterationClassification("PTEN", ["homozygous_loss"], "ENST00000371953", [], "ALASCCA_CLASS_B_1")
        pten_classification_b_1_missense = AlterationClassification("PTEN", ["missense_variant"], "ENST00000371953", ["p.Cys124Ser", "p.Gly129Glu", "p.Arg130Gly", "p.Arg130Gln"], "ALASCCA_CLASS_B_1")
        pik3r1_classification_b_1 = AlterationClassification("PIK3R1", ["frameshift_variant", "inframe_insertion", "inframe_deletion", "stop_gained", "splice_acceptor_variant", "splice_donor_variant"], "ENST00000521381", ["340:670"], "ALASCCA_CLASS_B_1")
        pik3r1_classification_b_1_missense = AlterationClassification("PIK3R1", ["missense_variant"], "ENST00000521381", ["376", "379", "452", "464", "503", "560", "564", "567", "573", "642"], "ALASCCA_CLASS_B_1")
        pik3ca_classification_b_1 = AlterationClassification("PIK3CA", ["missense_variant"], "ENST00000263967", ["38", "81", "88", "106", "111", "118", "344", "345", "378", "420", "453", "726"], "ALASCCA_CLASS_B_1")
        pik3ca_classification_a = AlterationClassification("PIK3CA", ["missense_variant"], "ENST00000263967", ["542", "545", "546", "1021", "1043", "1044", "1047"], "ALASCCA_CLASS_A")
        self._symbol2classifications = {"IGF2": [igf2_classification], "PTEN": [pten_classification_b_2, pten_classification_b_1, pten_classification_b_1_missense], "PIK3R1": [pik3r1_classification_b_1, pik3r1_classification_b_1_missense], "PIK3CA": [pik3ca_classification_b_1, pik3ca_classification_a]}

        pten = Gene("PTEN")
        pten.set_ID("ENSG00000171862")
        self._pten_gene_single_mutation = AlteredGene(pten)
        self._pten_hzl = Alteration(self._pten_gene_single_mutation, "ENST00000371953", "homozygous_loss", None)
        self._pten_gene_single_mutation.add_alteration(self._pten_hzl)

        self._pten_gene_single_mutation_not_enough = AlteredGene(pten)
        self._pten_frameshift = Alteration(self._pten_gene_single_mutation_not_enough, "ENST00000371953", "frameshift_variant", None)
        self._pten_gene_single_mutation_not_enough.add_alteration(self._pten_frameshift)

        self._pten_gene_double_mutation = AlteredGene(pten)
        self._pten_stop_gained = Alteration(self._pten_gene_double_mutation, "ENST00000371953", "stop_gained", "p.Gly301Leu")
        self._pten_splice_acceptor_variant = Alteration(self._pten_gene_double_mutation, "ENST00000371953", "splice_acceptor_variant", "p.Gly10Leu")
        self._pten_gene_double_mutation.add_alteration(self._pten_stop_gained)
        self._pten_gene_double_mutation.add_alteration(self._pten_splice_acceptor_variant)

        pik3r1 = Gene("PIK3R1")
        pik3r1.set_ID("ENSG00000145675")
        self._pik3r1_gene_frameshift = AlteredGene(pik3r1)
        # Note: Dummy amino acid change here; the position is important but not
        # the actual residue change:
        self._pik3r1_frameshift = Alteration(self._pik3r1_gene_frameshift, "ENST00000521381", "frameshift_variant", "p.Val351Leu")
        self._pik3r1_gene_frameshift.add_alteration(self._pik3r1_frameshift)

        self._pik3r1_gene_frameshift_off = AlteredGene(pik3r1)
        # Note: Dummy amino acid change here; the position is important but not
        # the actual residue change:
        self._pik3r1_frameshift_off = Alteration(self._pik3r1_gene_frameshift_off, "ENST00000521381", "frameshift_variant", "p.Val10Leu")
        self._pik3r1_gene_frameshift_off.add_alteration(self._pik3r1_frameshift_off)

        self._pik3r1_gene_missense = AlteredGene(pik3r1)
        # Note: Dummy amino acid change here; the position is important but not
        # the actual residue change:
        self._pik3r1_missense = Alteration(self._pik3r1_gene_missense, "ENST00000521381", "missense_variant", "p.Val376Leu")
        self._pik3r1_gene_missense.add_alteration(self._pik3r1_missense)

        pik3ca = Gene("PIK3CA")
        pik3ca.set_ID("ENSG00000145675")
        self._pik3ca_gene_missense1 = AlteredGene(pik3ca)
        # Note: Dummy amino acid change here; the position is important but not
        # the actual residue change:
        self._pik3ca_missense1 = Alteration(self._pik3ca_gene_missense1, "ENST00000263967", "missense_variant", "p.Val38Leu")
        self._pik3ca_gene_missense1.add_alteration(self._pik3ca_missense1)

        self._pik3ca_gene_missense2 = AlteredGene(pik3ca)
        # Note: Dummy amino acid change here; the position is important but not
        # the actual residue change:
        self._pik3ca_missense2 = Alteration(self._pik3ca_gene_missense2, "ENST00000263967", "missense_variant", "p.Val542Leu")
        self._pik3ca_gene_missense2.add_alteration(self._pik3ca_missense2)

        self._pik3ca_gene_missense_a_and_b = AlteredGene(pik3ca)
        # Note: Dummy amino acid change here; the position is important but not
        # the actual residue change:
        self._pik3ca_missense3 = Alteration(self._pik3ca_gene_missense_a_and_b, "ENST00000263967", "missense_variant", "p.Val38Leu")
        self._pik3ca_missense4 = Alteration(self._pik3ca_gene_missense_a_and_b, "ENST00000263967", "missense_variant", "p.Val542Leu")
        self._pik3ca_gene_missense_a_and_b.add_alteration(self._pik3ca_missense3)
        self._pik3ca_gene_missense_a_and_b.add_alteration(self._pik3ca_missense4)

#    def test_init(self):
#        rule = AlasccaClassRule("reportgen/assets/ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", {})
#        self.assertDictEqual(rule._gene_symbol2classifications, self._symbol2classifications)

    def test_apply_single_pten(self):
        input_symbol2gene = {"PTEN": self._pten_gene_single_mutation}
        rule = AlasccaClassRule("reportgen/assets/ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pten_not_enough(self):
        input_symbol2gene = {"PTEN": self._pten_gene_single_mutation_not_enough}
        rule = AlasccaClassRule("reportgen/assets/ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: FeatureStatus.NOT_MUTATED}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3r1_frameshift(self):
        input_symbol2gene = {"PIK3R1": self._pik3r1_gene_frameshift}
        rule = AlasccaClassRule("reportgen/assets/ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3r1_frameshift_off(self):
        input_symbol2gene = {"PIK3R1": self._pik3r1_gene_frameshift_off}
        rule = AlasccaClassRule("reportgen/assets/ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: FeatureStatus.NOT_MUTATED}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_double_pten(self):
        input_symbol2gene = {"PTEN": self._pten_gene_double_mutation}
        rule = AlasccaClassRule("reportgen/assets/ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3r1_missense(self):
        input_symbol2gene = {"PIK3R1": self._pik3r1_gene_missense}
        rule = AlasccaClassRule("reportgen/assets/ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3ca_class_b(self):
        input_symbol2gene = {"PIK3CA": self._pik3ca_gene_missense1}
        rule = AlasccaClassRule("reportgen/assets/ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3ca_class_a(self):
        input_symbol2gene = {"PIK3CA": self._pik3ca_gene_missense2}
        rule = AlasccaClassRule("reportgen/assets/ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: AlasccaClassReport.MUTN_CLASS_A}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_pik3ca_class_a_test2(self):
        input_symbol2gene = {"PIK3CA": self._pik3ca_gene_missense_a_and_b}
        rule = AlasccaClassRule("reportgen/assets/ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: AlasccaClassReport.MUTN_CLASS_A}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)


class TestMsiStatusRule(unittest.TestCase):
    def setUp(self):
        pass

    def test_apply_high(self):
        msi_status = MSIStatus()
        msi_status.set_from_file(open("tests/msi_high_eg.txt"))
        rule = MsiStatusRule(msi_status)
        msi_report = rule.apply()
        self.assertEqual(msi_report.get_status(), MsiReport.MSI)

    def test_apply_low(self):
        msi_status = MSIStatus()
        msi_status.set_from_file(open("tests/msi_low_eg.txt"))
        rule = MsiStatusRule(msi_status)
        msi_report = rule.apply()
        self.assertEqual(msi_report.get_status(), MsiReport.MSS)

    def test_apply_not_determined(self):
        msi_status = MSIStatus()
        msi_status.set_from_file(open("tests/msi_not_determined_eg.txt"))
        rule = MsiStatusRule(msi_status)
        msi_report = rule.apply()
        self.assertEqual(msi_report.get_status(), FeatureStatus.NOT_DETERMINED)


class TestExtractQCCalls(unittest.TestCase)
    def setUp(self):
        pass

    def test_extract_qc_ok(self):
        mocked_open = mock_open(read_data='{"CALL":"OK"}')
        with patch('dummy', mocked_open, create=True):
            self.assertEquals(extract_qc_call(mocked_open), "OK")

    def test_extract_qc_none(self):
        infile = None
        self.assertEquals(extract_qc_call(infile), None)