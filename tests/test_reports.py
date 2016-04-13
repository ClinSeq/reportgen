import json, os, unittest
import pyodbc
from reportgen.rules.msi import MsiStatusRule

from reportgen.reporting.features import AlasccaClassReport, MsiReport

from reportgen.rules.alascca import AlasccaClassRule

from reportgen.reporting.metadata import ReportMetadata

from reportgen.reporting.util import connect_clinseq_db, id_valid, retrieve_report_metadata, ReportCompiler

from reportgen.rules.simple_somatic_mutations import SimpleSomaticMutationsRule

from reportgen.rules.general import AlterationClassification, Gene, AlteredGene, Alteration, MSIStatus


class TestAlterationClassification(unittest.TestCase):
    _single_consequence_classification = None

    def setUp(self):
        self._braf_classification = AlterationClassification("BRAF", ["missense_variant"], "ENST00000288602", ["p.Val600Glu"], "BRAF_COMMON")

        braf = Gene("BRAF")
        braf.set_ID("ENSG00000157764")
        self._braf_gene = AlteredGene(braf)
        self._braf_alteration1 = Alteration(self._braf_gene, "ENST00000288602", "missense_variant", "p.Val600Glu")
        self._braf_gene.add_alteration(self._braf_alteration1)

        self._kras_classification = AlterationClassification("KRAS", ["missense_variant"], "ENST00000256078", ["12", "13", "60", "61", "117", "146"], "KRAS_COMMON")

        kras = Gene("KRAS")
        kras.set_ID("ENSG00000133703")
        self._kras_gene = AlteredGene(kras)
        self._kras_alteration1 = Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "p.Ala146Pro")
        self._kras_gene.add_alteration(self._kras_alteration1)
        # A fake mutation whose position is in the set of KRAS mutations:
        self._kras_alteration2 = Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "p.Lys60Pro")
        self._kras_gene.add_alteration(self._kras_alteration2)
        # A fake mutation that is *not* in the set of KRAS mutations:
        self._kras_alteration3 = Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "p.Lys1Asn")
        self._kras_gene.add_alteration(self._kras_alteration3)

        self._pik3r1_range_classification = AlterationClassification("PIK3R1", ["inframe_insertion"], "ENST00000521381", ["340:670"], "TEST")

        pik3r1 = Gene("PIK3R1")
        pik3r1.set_ID("ENSG00000145675")
        self._pik3r1_gene = AlteredGene(pik3r1)
        # Dummy alteration; position is important, substitution is not:
        self._pik3r1_alteration1 = Alteration(self._pik3r1_gene, "ENST00000521381", "inframe_insertion", "p.Val344Lys")

    def test_matches_positions_string_vs_string(self):
        self.assertTrue(self._braf_classification.matches_positions(self._braf_alteration1))

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

    def test_classification_is_same(self):
        rule = SimpleSomaticMutationsRule("COLORECTAL_MUTATION_TABLE.xlsx", {})
        # FIXME (MAYBE): COULD HAVE THE RIGHT HAND SIDE OF THESE TESTS HARD-CODED INSTEAD OF READ FROM ABOVE.
        # E.g. Test if there are three elements in the first nras gene alteration.
        self.assertEqual(rule._gene_symbol2classifications["NRAS"][0], self._symbol2classifications["NRAS"][0])

    def test_symbol2classification_is_same(self):
        rule = SimpleSomaticMutationsRule("COLORECTAL_MUTATION_TABLE.xlsx", {})
        self.assertDictEqual(rule._gene_symbol2classifications, self._symbol2classifications)

    # Test empty input symbol2gene dictionary:
    def test_apply_empty_input(self):
        rule = SimpleSomaticMutationsRule("COLORECTAL_MUTATION_TABLE.xlsx", {})
        test_report = rule.apply()
        expected_outdict = {'NRAS': {"Status" : 'Not mutated', "Alterations": []},
                            'BRAF': {"Status" : 'Not mutated', "Alterations": []},
                            'KRAS': {"Status": 'Not mutated', "Alterations" : []}}
        self.assertDictEqual(test_report.to_dict(), expected_outdict)

    # Test single mutation symbol2gene input dictionary:
    def test_apply_single_mutation_input(self):
        input_symbol2gene = {"BRAF": self._braf_gene_single_mutation}
        rule = SimpleSomaticMutationsRule("COLORECTAL_MUTATION_TABLE.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_outdict = {'NRAS': {"Status" : 'Not mutated', "Alterations": []},
                            'BRAF': {"Status": 'Mutated', "Alterations": [{"HGVSp": 'p.Val600Glu', "Flag": u'BRAF_COMMON'}]},
                            'KRAS': {"Status": 'Not mutated', "Alterations" : []}}
        self.assertDictEqual(test_report.to_dict(), expected_outdict)

    # Test multiple genes and multiple mutations symbol2gene input dictionary:
    def test_apply_multiple_mutation_input(self):
        input_symbol2gene = {"BRAF": self._braf_gene_single_mutation, "KRAS": self._kras_gene_multiple_mutations}
        rule = SimpleSomaticMutationsRule("COLORECTAL_MUTATION_TABLE.xlsx", input_symbol2gene)
        test_report = rule.apply()

        expected_outdict = {'NRAS': {"Status" : 'Not mutated', "Alterations": []},
                            'BRAF': {"Status": 'Mutated', "Alterations": [{"HGVSp": 'p.Val600Glu', "Flag": u'BRAF_COMMON'}]},
                            'KRAS': {"Status": 'Mutated', "Alterations" : [{"HGVSp": 'p.Ala146Pro', "Flag": u'KRAS_COMMON'},
                                                                           {"HGVSp": 'p.Lys117Asn', "Flag": u'KRAS_COMMON'},
                                                                           {"HGVSp": 'p.Lys1Asn', "Flag": None}]}}
        self.assertDictEqual(test_report.to_dict(), expected_outdict)


class TestMisc(unittest.TestCase):
    '''Tests for miscellaneous functions in the reports module.'''

    def setUp(self):
        # NOTE: Reading config rather than explicitly defining dictionary here,
        # since the password is included in this information:
        path = os.path.expanduser("~/.dbconfig.json")
        self.config_dict = json.load(open(path))

        self.cnxn = connect_clinseq_db(self.config_dict)

    def test_connect_clinseq_db_good_data(self):
        # FIXME: Not really sure how to test if a connection object is produced
        # upon valid input. Better to test this than testing nothing, though?:
        self.assertTrue(isinstance(self.cnxn, pyodbc.Connection))

    def test_connect_clinseq_db_empty_data(self):
        self.assertRaises(KeyError, lambda: connect_clinseq_db({}))

    def test_id_valid_valid_input(self):
        self.assertTrue(id_valid("01234567"))

    def test_id_valid_short_input(self):
        self.assertFalse(id_valid("0123456"))

    def test_id_valid_letter_input(self):
        self.assertFalse(id_valid("ABCDEFGH"))

    def test_retrieve_report_metadata_missing_sampleID(self):
        self.assertRaises(ValueError, lambda: retrieve_report_metadata("12345678", "3098849", self.cnxn))

    def test_retrieve_report_metadata_valid_input(self):
        # Inputting a valid blood and tumor ID should produce a ReportMetadata
        # object:
        report_metadata = retrieve_report_metadata("3098121", "3098849", self.cnxn)
        self.assertTrue(isinstance(report_metadata, ReportMetadata))

#    def test_retrieve_report_metadata_differing_personnummers(self):
#        # Inputting a valid blood and tumor ID should produce a ReportMetadata
#        # object:
#        self.assertRaises(ValueError, lambda: retrieve_report_metadata("02871131", "03019438", self.cnxn))


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

    def test_init(self):
        rule = AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", {})
        self.assertDictEqual(rule._gene_symbol2classifications, self._symbol2classifications)

    def test_apply_single_pten(self):
        input_symbol2gene = {"PTEN": self._pten_gene_single_mutation}
        rule = AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pten_not_enough(self):
        input_symbol2gene = {"PTEN": self._pten_gene_single_mutation_not_enough}
        rule = AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: AlasccaClassReport.NO_MUTN}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3r1_frameshift(self):
        input_symbol2gene = {"PIK3R1": self._pik3r1_gene_frameshift}
        rule = AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3r1_frameshift_off(self):
        input_symbol2gene = {"PIK3R1": self._pik3r1_gene_frameshift_off}
        rule = AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: AlasccaClassReport.NO_MUTN}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_double_pten(self):
        input_symbol2gene = {"PTEN": self._pten_gene_double_mutation}
        rule = AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3r1_missense(self):
        input_symbol2gene = {"PIK3R1": self._pik3r1_gene_missense}
        rule = AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3ca_class_b(self):
        input_symbol2gene = {"PIK3CA": self._pik3ca_gene_missense1}
        rule = AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3ca_class_a(self):
        input_symbol2gene = {"PIK3CA": self._pik3ca_gene_missense2}
        rule = AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: AlasccaClassReport.MUTN_CLASS_A}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_pik3ca_class_a_test2(self):
        input_symbol2gene = {"PIK3CA": self._pik3ca_gene_missense_a_and_b}
        rule = AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx", input_symbol2gene)
        test_report = rule.apply()
        expected_output_dict = {
            AlasccaClassReport.NAME: AlasccaClassReport.MUTN_CLASS_A}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)


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
        self.assertEqual(msi_report.get_status(), MsiReport.NOT_DETERMINED)



























































