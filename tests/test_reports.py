import json, os, unittest
import pyodbc
from reportgen import reports
from reportgen import genomics


class TestAlterationClassification(unittest.TestCase):
    _single_consequence_classification = None

    def setUp(self):
        self._braf_classification = reports.AlterationClassification("BRAF", ["missense_variant"], "ENST00000288602", ["Val600Glu"], "BRAF_COMMON")

        braf = genomics.Gene("BRAF")
        braf.set_ID("ENSG00000157764")
        self._braf_gene = genomics.AlteredGene(braf)
        self._braf_alteration1 = genomics.Alteration(self._braf_gene, "ENST00000288602", "missense_variant", "Val600Glu")
        self._braf_gene.add_alteration(self._braf_alteration1)
        # A test alteration: Position only at 600:
        self._braf_alteration2 = genomics.Alteration(self._braf_gene, "ENST00000288602", "missense_variant", "600")
        self._braf_gene.add_alteration(self._braf_alteration2)

        self._kras_classification = reports.AlterationClassification("KRAS", ["missense_variant"], "ENST00000256078", ["12","13","60","61","117","146"], "KRAS_COMMON")

        kras = genomics.Gene("KRAS")
        kras.set_ID("ENSG00000133703")
        self._kras_gene = genomics.AlteredGene(kras)
        self._kras_alteration1 = genomics.Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "Ala146Pro")
        self._kras_gene.add_alteration(self._kras_alteration1)
        # Position only specified:
        self._kras_alteration2 = genomics.Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "60")
        self._kras_gene.add_alteration(self._kras_alteration2)
        # A fake mutation that is *not* in the set of KRAS mutations:
        self._kras_alteration3 = genomics.Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "Lys1Asn")
        self._kras_gene.add_alteration(self._kras_alteration3)

        self._pik3r1_range_classification = reports.AlterationClassification("PIK3R1", ["inframe_insertion"], "ENST00000521381", ["340:670"], "TEST")

        pik3r1 = genomics.Gene("PIK3R1")
        pik3r1.set_ID("ENSG00000145675")
        self._pik3r1_gene = genomics.AlteredGene(pik3r1)
        # Dummy alteration; position is important, substitution is not:
        self._pik3r1_alteration1 = genomics.Alteration(self._pik3r1_gene, "ENST00000521381", "inframe_insertion", "Val344Lys")

    def test_matches_positions_string_vs_string(self):
        self.assertTrue(self._braf_classification.matches_positions(self._braf_alteration1))

    def test_matches_positions_string_vs_position(self):
        self.assertFalse(self._braf_classification.matches_positions(self._braf_alteration2))

    def test_matches_positions_position_vs_string(self):
        self.assertTrue(self._kras_classification.matches_positions(self._kras_alteration1))

    def test_matches_positions_position_vs_position(self):
        self.assertTrue(self._kras_classification.matches_positions(self._kras_alteration2))

    def test_matches_positions_position_vs_string_no_match(self):
        self.assertFalse(self._kras_classification.matches_positions(self._kras_alteration3))

    def test_match_position_vs_string(self):
        self.assertTrue(self._kras_classification.match(self._kras_alteration1))

    def test_match_position_vs_string_no_match(self):
        self.assertFalse(self._kras_classification.match(self._kras_alteration3))

    def test_match_position_in_range(self):
        self.assertTrue(self._pik3r1_range_classification.match(self._pik3r1_alteration1))


class TestSimpleSomaticMutationsRule(unittest.TestCase):
    def setUp(self):
        braf_classification = reports.AlterationClassification("BRAF", ["missense_variant"], "ENST00000288602", ["Val600Glu"], "BRAF_COMMON")
        kras_classification = reports.AlterationClassification("KRAS", ["missense_variant"], "ENST00000256078", ["12","13","60","61","117","146"], "KRAS_COMMON")
        nras_classification = reports.AlterationClassification("NRAS", ["missense_variant"], "ENST00000369535", ["12","13","61"], "NRAS_COMMON")
        self._symbol2classifications = {"BRAF": [braf_classification], "KRAS": [kras_classification], "NRAS": [nras_classification]}

        braf = genomics.Gene("BRAF")
        braf.set_ID("ENSG00000157764")
        self._braf_gene_single_mutation = genomics.AlteredGene(braf)
        self._braf_alteration3 = genomics.Alteration(self._braf_gene_single_mutation, "ENST00000288602", "missense_variant", "Val600Glu")
        self._braf_gene_single_mutation.add_alteration(self._braf_alteration3)

        kras = genomics.Gene("KRAS")
        kras.set_ID("ENSG00000133703")
        self._kras_gene_multiple_mutations = genomics.AlteredGene(kras)
        self._kras_alteration1 = genomics.Alteration(self._kras_gene_multiple_mutations, "ENST00000256078", "missense_variant", "Ala146Pro")
        self._kras_gene_multiple_mutations.add_alteration(self._kras_alteration1)
        # Position only specified:
        self._kras_alteration2 = genomics.Alteration(self._kras_gene_multiple_mutations, "ENST00000256078", "missense_variant", "Lys117Asn")
        self._kras_gene_multiple_mutations.add_alteration(self._kras_alteration2)
        # A fake mutation that is *not* in the set of KRAS mutations:
        self._kras_alteration3 = genomics.Alteration(self._kras_gene_multiple_mutations, "ENST00000256078", "missense_variant", "Lys1Asn")
        self._kras_gene_multiple_mutations.add_alteration(self._kras_alteration3)

        self._rule = reports.SimpleSomaticMutationsRule("COLORECTAL_MUTATION_TABLE.xlsx")

    def test_classification_is_same(self):
        # FIXME (MAYBE): COULD HAVE THE RIGHT HAND SIDE OF THESE TESTS HARD-CODED INSTEAD OF READ FROM ABOVE.
        # E.g. Test if there are three elements in the first nras gene alteration.
        self.assertEqual(self._rule._gene_symbol2classifications["NRAS"][0], self._symbol2classifications["NRAS"][0])

    def test_symbol2classification_is_same(self):
        self.assertDictEqual(self._rule._gene_symbol2classifications, self._symbol2classifications)

    # Test empty input symbol2gene dictionary:
    def test_apply_empty_input(self):
        test_report = self._rule.apply({})
        expected_outdict = {'NRAS': ['Not mutated', []], 'BRAF': ['Not mutated', []], 'KRAS': ['Not mutated', []]}
        self.assertDictEqual(test_report.to_dict(), expected_outdict)

    # Test single mutation symbol2gene input dictionary:
    def test_apply_single_mutation_input(self):
        input_symbol2gene = {"BRAF": self._braf_gene_single_mutation}
        test_report = self._rule.apply(input_symbol2gene)
        expected_outdict = {'NRAS': ['Not mutated', []],
                            'BRAF': ['Mutated', [['Val600Glu', u'BRAF_COMMON']]],
                            'KRAS': ['Not mutated', []]}
        self.assertDictEqual(test_report.to_dict(), expected_outdict)

    # Test multiple genes and multiple mutations symbol2gene input dictionary:
    def test_apply_multiple_mutation_input(self):
        input_symbol2gene = {"BRAF": self._braf_gene_single_mutation, "KRAS": self._kras_gene_multiple_mutations}
        test_report = self._rule.apply(input_symbol2gene)

        expected_outdict = {'NRAS': ['Not mutated', []],
                            'BRAF': ['Mutated', [['Val600Glu', u'BRAF_COMMON']]],
                            'KRAS': ['Mutated', [['Ala146Pro', u'KRAS_COMMON'],
                                                 ['Lys117Asn', u'KRAS_COMMON'],
                                                 ['Lys1Asn', None]]]}
        self.assertDictEqual(test_report.to_dict(), expected_outdict)


class TestMisc(unittest.TestCase):
    '''Tests for miscellaneous functions in the reports module.'''

    def setUp(self):
        # NOTE: Reading config rather than explicitly defining dictionary here,
        # since the password is included in this information:
        path = os.path.expanduser("~/.dbconfig.json")
        self.config_dict = json.load(open(path))

        self.cnxn = reports.connect_clinseq_db(self.config_dict)

    def test_connect_clinseq_db_good_data(self):
        # FIXME: Not really sure how to test if a connection object is produced
        # upon valid input. Better to test this than testing nothing, though?:
        self.assertTrue(isinstance(self.cnxn, pyodbc.Connection))

    def test_connect_clinseq_db_empty_data(self):
        self.assertRaises(KeyError, lambda: reports.connect_clinseq_db({}))

    def test_id_valid_valid_input(self):
        self.assertTrue(reports.id_valid("01234567"))

    def test_id_valid_short_input(self):
        self.assertFalse(reports.id_valid("0123456"))

    def test_id_valid_letter_input(self):
        self.assertFalse(reports.id_valid("ABCDEFGH"))

    def test_retrieve_report_metadata_missing_sampleID(self):
        # Inputting a valid blood and tumor ID should produce a ReportMetadata
        # object:
        self.assertRaises(ValueError, lambda: reports.retrieve_report_metadata("12345678", "02871255", self.cnxn))

    def test_retrieve_report_metadata_valid_input(self):
        # Inputting a valid blood and tumor ID should produce a ReportMetadata
        # object:
        report_metadata = reports.retrieve_report_metadata("02871131", "02871255", self.cnxn)
        self.assertTrue(isinstance(report_metadata, reports.ReportMetadata))

    def test_retrieve_report_metadata_differing_personnummers(self):
        # Inputting a valid blood and tumor ID should produce a ReportMetadata
        # object:
        self.assertRaises(ValueError, lambda: reports.retrieve_report_metadata("02871131", "03019438", self.cnxn))


class TestAlasccaClassRule(unittest.TestCase):
    def setUp(self):
        igf2_classification = reports.AlterationClassification("IGF2", ["amplification"], None, [], "ALASCCA_CLASS_B_1")
        pten_classification_b_2 = reports.AlterationClassification("PTEN", ["start_lost","stop_gained","frameshift_variant","splice_acceptor_variant","splice_donor_variant","loss_of_heterozygosity"], "ENST00000371953", [], "ALASCCA_CLASS_B_2")
        pten_classification_b_1 = reports.AlterationClassification("PTEN", ["homozygous_loss"], "ENST00000371953", [], "ALASCCA_CLASS_B_1")
        pten_classification_b_1_missense = reports.AlterationClassification("PTEN", ["missense_variant"], "ENST00000371953", ["Cys124Ser","Gly129Glu","Arg130Gly","Arg130Gln"], "ALASCCA_CLASS_B_1")
        pik3r1_classification_b_1 = reports.AlterationClassification("PIK3R1", ["frameshift_variant","inframe_insertion","inframe_deletion","stop_gained","splice_acceptor_variant","splice_donor_variant"], "ENST00000521381", ["340:670"], "ALASCCA_CLASS_B_1")
        pik3r1_classification_b_1_missense = reports.AlterationClassification("PIK3R1", ["missense_variant"], "ENST00000521381", ["376","379","452","464","503","560","564","567","573","642"], "ALASCCA_CLASS_B_1")
        pik3ca_classification_b_1 = reports.AlterationClassification("PIK3CA", ["missense_variant"], "ENST00000263967", ["38","81","88","106","111","118","344","345","378","420","453","726"], "ALASCCA_CLASS_B_1")
        pik3ca_classification_a = reports.AlterationClassification("PIK3CA", ["missense_variant"], "ENST00000263967", ["542","545","546","1021","1043","1044","1047"], "ALASCCA_CLASS_A")
        self._symbol2classifications = {"IGF2": [igf2_classification], "PTEN": [pten_classification_b_2, pten_classification_b_1, pten_classification_b_1_missense], "PIK3R1": [pik3r1_classification_b_1, pik3r1_classification_b_1_missense], "PIK3CA": [pik3ca_classification_b_1, pik3ca_classification_a]}

        pten = genomics.Gene("PTEN")
        pten.set_ID("ENSG00000171862")
        self._pten_gene_single_mutation = genomics.AlteredGene(pten)
        self._pten_hzl = genomics.Alteration(self._pten_gene_single_mutation, "ENST00000371953", "homozygous_loss", None)
        self._pten_gene_single_mutation.add_alteration(self._pten_hzl)

        self._pten_gene_single_mutation_not_enough = genomics.AlteredGene(pten)
        self._pten_frameshift = genomics.Alteration(self._pten_gene_single_mutation_not_enough, "ENST00000371953", "frameshift_variant", None)
        self._pten_gene_single_mutation_not_enough.add_alteration(self._pten_frameshift)

        self._pten_gene_double_mutation = genomics.AlteredGene(pten)
        self._pten_stop_gained = genomics.Alteration(self._pten_gene_double_mutation, "ENST00000371953", "stop_gained", "Gly301Leu")
        self._pten_splice_acceptor_variant = genomics.Alteration(self._pten_gene_double_mutation, "ENST00000371953", "splice_acceptor_variant", "Gly10Leu")
        self._pten_gene_double_mutation.add_alteration(self._pten_stop_gained)
        self._pten_gene_double_mutation.add_alteration(self._pten_splice_acceptor_variant)

        pik3r1 = genomics.Gene("PIK3R1")
        pik3r1.set_ID("ENSG00000145675")
        self._pik3r1_gene_frameshift = genomics.AlteredGene(pik3r1)
        # Note: Dummy amino acid change here; the position is important but not
        # the actual residue change:
        self._pik3r1_frameshift = genomics.Alteration(self._pik3r1_gene_frameshift, "ENST00000521381", "frameshift_variant", "Val351Leu")
        self._pik3r1_gene_frameshift.add_alteration(self._pik3r1_frameshift)

        self._pik3r1_gene_frameshift_off = genomics.AlteredGene(pik3r1)
        # Note: Dummy amino acid change here; the position is important but not
        # the actual residue change:
        self._pik3r1_frameshift_off = genomics.Alteration(self._pik3r1_gene_frameshift_off, "ENST00000521381", "frameshift_variant", "Val10Leu")
        self._pik3r1_gene_frameshift_off.add_alteration(self._pik3r1_frameshift_off)

        self._pik3r1_gene_missense = genomics.AlteredGene(pik3r1)
        # Note: Dummy amino acid change here; the position is important but not
        # the actual residue change:
        self._pik3r1_missense = genomics.Alteration(self._pik3r1_gene_missense, "ENST00000521381", "missense_variant", "Val376Leu")
        self._pik3r1_gene_missense.add_alteration(self._pik3r1_missense)

        pik3ca = genomics.Gene("PIK3CA")
        pik3ca.set_ID("ENSG00000145675")
        self._pik3ca_gene_missense1 = genomics.AlteredGene(pik3ca)
        # Note: Dummy amino acid change here; the position is important but not
        # the actual residue change:
        self._pik3ca_missense1 = genomics.Alteration(self._pik3ca_gene_missense1, "ENST00000263967", "missense_variant", "Val38Leu")
        self._pik3ca_gene_missense1.add_alteration(self._pik3ca_missense1)

        self._pik3ca_gene_missense2 = genomics.AlteredGene(pik3ca)
        # Note: Dummy amino acid change here; the position is important but not
        # the actual residue change:
        self._pik3ca_missense2 = genomics.Alteration(self._pik3ca_gene_missense2, "ENST00000263967", "missense_variant", "Val542Leu")
        self._pik3ca_gene_missense2.add_alteration(self._pik3ca_missense2)

        self._pik3ca_gene_missense_a_and_b = genomics.AlteredGene(pik3ca)
        # Note: Dummy amino acid change here; the position is important but not
        # the actual residue change:
        self._pik3ca_missense3 = genomics.Alteration(self._pik3ca_gene_missense_a_and_b, "ENST00000263967", "missense_variant", "Val38Leu")
        self._pik3ca_missense4 = genomics.Alteration(self._pik3ca_gene_missense_a_and_b, "ENST00000263967", "missense_variant", "Val542Leu")
        self._pik3ca_gene_missense_a_and_b.add_alteration(self._pik3ca_missense3)
        self._pik3ca_gene_missense_a_and_b.add_alteration(self._pik3ca_missense4)

    def test_init(self):
        rule = reports.AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", {})
        self.assertDictEqual(rule._gene_symbol2classifications, self._symbol2classifications)

    def test_apply_single_pten(self):
        input_symbol2gene = {"PTEN": self._pten_gene_single_mutation}
        rule = reports.AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {reports.AlasccaClassReport.NAME: reports.AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pten_not_enough(self):
        input_symbol2gene = {"PTEN": self._pten_gene_single_mutation_not_enough}
        rule = reports.AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {reports.AlasccaClassReport.NAME: reports.AlasccaClassReport.NO_MUTN}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3r1_frameshift(self):
        input_symbol2gene = {"PIK3R1": self._pik3r1_gene_frameshift}
        rule = reports.AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {reports.AlasccaClassReport.NAME: reports.AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3r1_frameshift_off(self):
        input_symbol2gene = {"PIK3R1": self._pik3r1_gene_frameshift_off}
        rule = reports.AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {reports.AlasccaClassReport.NAME: reports.AlasccaClassReport.NO_MUTN}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_double_pten(self):
        input_symbol2gene = {"PTEN": self._pten_gene_double_mutation}
        rule = reports.AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {reports.AlasccaClassReport.NAME: reports.AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3r1_missense(self):
        input_symbol2gene = {"PIK3R1": self._pik3r1_gene_missense}
        rule = reports.AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {reports.AlasccaClassReport.NAME: reports.AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3ca_class_b(self):
        input_symbol2gene = {"PIK3CA": self._pik3ca_gene_missense1}
        rule = reports.AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {reports.AlasccaClassReport.NAME: reports.AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3ca_class_a(self):
        input_symbol2gene = {"PIK3CA": self._pik3ca_gene_missense2}
        rule = reports.AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {reports.AlasccaClassReport.NAME: reports.AlasccaClassReport.MUTN_CLASS_A}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_pik3ca_class_a_test2(self):
        input_symbol2gene = {"PIK3CA": self._pik3ca_gene_missense_a_and_b}
        rule = reports.AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {reports.AlasccaClassReport.NAME: reports.AlasccaClassReport.MUTN_CLASS_A}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)


# Very basic testing of this class at the moment. Perhaps add more tests here.
class TestReportCompiler(unittest.TestCase):
    def setUp(self):
        pass

    def test_extract_features_empty(self):
        compiler = reports.ReportCompiler([])
        compiler.extract_features()
        self.assertEqual({}, compiler._name2feature)

    def test_to_dict_empty(self):
        compiler = reports.ReportCompiler([])
        compiler.extract_features()
        self.assertEqual({}, compiler.to_dict())
































































