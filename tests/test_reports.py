import unittest
from reportgen import reports
from reportgen import genomics


class TestAlterationClassification(unittest.TestCase):
    _single_consequence_classification = None

    def setUp(self):
        self._braf_classification = reports.AlterationClassification(["missense_variant"], "ENST00000288602", ["Val600Glu"], "BRAF_COMMON")

        self._braf_gene = genomics.Gene("BRAF", "ENSG00000157764")
        self._braf_alteration1 = genomics.Alteration(self._braf_gene, "ENST00000288602", "missense_variant", "Val600Glu")
        self._braf_gene.add_alteration(self._braf_alteration1)
        # A test alteration: Position only at 600:
        self._braf_alteration2 = genomics.Alteration(self._braf_gene, "ENST00000288602", "missense_variant", "600")
        self._braf_gene.add_alteration(self._braf_alteration2)

        self._kras_classification = reports.AlterationClassification(["missense_variant"], "ENST00000256078", ["12","13","60","61","117","146"], "KRAS_COMMON")

        self._kras_gene = genomics.Gene("KRAS", "ENSG00000133703")
        self._kras_alteration1 = genomics.Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "Ala146Pro")
        self._kras_gene.add_alteration(self._kras_alteration1)
        # Position only specified:
        self._kras_alteration2 = genomics.Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "60")
        self._kras_gene.add_alteration(self._kras_alteration2)
        # A fake mutation that is *not* in the set of KRAS mutations:
        self._kras_alteration3 = genomics.Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "Lys1Asn")
        self._kras_gene.add_alteration(self._kras_alteration3)

        self._pik3r1_range_classification = reports.AlterationClassification(["inframe_insertion"], "ENST00000521381", ["340:670"], "TEST")

        self._pik3r1_gene = genomics.Gene("PIK3R1", "ENSG00000145675")
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
        braf_classification = reports.AlterationClassification(["missense_variant"], "ENST00000288602", ["Val600Glu"], "BRAF_COMMON")
        kras_classification = reports.AlterationClassification(["missense_variant"], "ENST00000256078", ["12","13","60","61","117","146"], "KRAS_COMMON")
        nras_classification = reports.AlterationClassification(["missense_variant"], "ENST00000369535", ["12","13","61"], "NRAS_COMMON")
        self._symbol2classifications = {"BRAF": [braf_classification], "KRAS": [kras_classification], "NRAS": [nras_classification]}

        self._braf_gene_single_mutation = genomics.Gene("BRAF", "ENSG00000157764")
        self._braf_alteration3 = genomics.Alteration(self._braf_gene_single_mutation, "ENST00000288602", "missense_variant", "Val600Glu")
        self._braf_gene_single_mutation.add_alteration(self._braf_alteration3)

        self._kras_gene_multiple_mutations = genomics.Gene("KRAS", "ENSG00000133703")
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
        self.assertEqual(self._rule._gene_symbol2classifications["NRAS"][0], self._symbol2classifications["NRAS"][0])

    def test_symbol2classification_is_same(self):
        self.assertDictEqual(self._rule._gene_symbol2classifications, self._symbol2classifications)

    # Test empty input symbol2gene dictionary:
    def test_apply_empty_input(self):
        test_report = self._rule.apply({})
        expected_outdict = {'NRAS': reports.MutationStatus(), 'BRAF': reports.MutationStatus(), 'KRAS': reports.MutationStatus()}
        self.assertDictEqual(test_report.to_dict(), expected_outdict)

    # Test single mutation symbol2gene input dictionary:
    def test_apply_single_mutation_input(self):
        input_symbol2gene = {"BRAF": self._braf_gene_single_mutation}
        test_report = self._rule.apply(input_symbol2gene)
        braf_status = reports.MutationStatus()
        braf_status.add_mutation(self._braf_alteration3, "BRAF_COMMON")
        expected_outdict = {'NRAS': reports.MutationStatus(), 'BRAF': braf_status, 'KRAS': reports.MutationStatus()}
        self.assertDictEqual(test_report.to_dict(), expected_outdict)

    # Test multiple genes and multiple mutations symbol2gene input dictionary:
    def test_apply_multiple_mutation_input(self):
        input_symbol2gene = {"BRAF": self._braf_gene_single_mutation, "KRAS": self._kras_gene_multiple_mutations}
        test_report = self._rule.apply(input_symbol2gene)

        braf_status = reports.MutationStatus()
        braf_status.add_mutation(self._braf_alteration3, "BRAF_COMMON")

        kras_status = reports.MutationStatus()
        kras_status.add_mutation(self._kras_alteration1, "KRAS_COMMON")
        kras_status.add_mutation(self._kras_alteration2, "KRAS_COMMON")
        kras_status.add_mutation(self._kras_alteration3, None)

        expected_outdict = {'NRAS': reports.MutationStatus(), 'BRAF': braf_status, 'KRAS': kras_status}
        self.assertDictEqual(test_report.to_dict(), expected_outdict)


class TestAlasscaClassRule(unittest.TestCase):
    def setUp(self):
        igf2_classification = reports.AlterationClassification(["amplification"], None, [], "ALASSCA_CLASS_B_1")
        pten_classification_b_2 = reports.AlterationClassification(["start_lost","stop_gained","frameshift_variant","splice_acceptor_variant","splice_donor_variant"], "ENST00000371953", [], "ALASSCA_CLASS_B_2")
        pten_classification_b_1 = reports.AlterationClassification(["loss_of_heterozygosity","homozygous_loss"], "ENST00000371953", [], "ALASSCA_CLASS_B_1")
        pten_classification_b_1_missense = reports.AlterationClassification(["missense_variant"], "ENST00000371953", ["C124S","G129E","R130G","R130Q"], "ALASSCA_CLASS_B_1")
        pik3r1_classification_b_1 = reports.AlterationClassification(["frameshift_variant","inframe_insertion","inframe_deletion","stop_gained","splice_acceptor_variant","splice_donor_variant"], "ENST00000521381", ["340:670"], "ALASSCA_CLASS_B_1")
        pik3r1_classification_b_1_missense = reports.AlterationClassification(["missense_variant"], "ENST00000521381", ["376","379","452","464","503","560","564","567","573","642"], "ALASSCA_CLASS_B_1")
        pik3ca_classification_b_1 = reports.AlterationClassification(["missense_variant"], "ENST00000263967", ["38","81","88","106","111","118","344","345","378","420","453","726"], "ALASSCA_CLASS_B_1")
        pik3ca_classification_a = reports.AlterationClassification(["missense_variant"], "ENST00000263967", ["542","545","546","1021","1043","1044","1047"], "ALASSCA_CLASS_A")
        self._symbol2classifications = {"IGF2": [igf2_classification], "PTEN": [pten_classification_b_2, pten_classification_b_1, pten_classification_b_1_missense], "PIK3R1": [pik3r1_classification_b_1, pik3r1_classification_b_1_missense], "PIK3CA": [pik3ca_classification_b_1, pik3ca_classification_a]}

        self._rule = reports.AlasccaClassRule("ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx")

        self._pten_gene_single_mutation = genomics.Gene("PTEN", "ENSG00000171862")
        self._pten_loh = genomics.Alteration(self._pten_gene_single_mutation, "ENST00000371953", "loss_of_heterozygosity", None)
        self._pten_gene_single_mutation.add_alteration(self._pten_loh)

        self._pten_gene_single_mutation_not_enough = genomics.Gene("PTEN", "ENSG00000171862")
        self._pten_frameshift = genomics.Alteration(self._pten_gene_single_mutation_not_enough, "ENST00000371953", "frameshift_variant", None)
        self._pten_gene_single_mutation_not_enough.add_alteration(self._pten_frameshift)

        self._pik3r1_gene_frameshift = genomics.Gene("PIK3R1", "ENSG00000145675")
        # Note: Dummy amino acid change here; the position is important but not
        # the actual residue change:
        self._pik3r1_frameshift = genomics.Alteration(self._pik3r1_gene_frameshift, "ENST00000521381", "frameshift_variant", "Val351Leu")
        self._pik3r1_gene_frameshift.add_alteration(self._pik3r1_frameshift)

        self._pik3r1_gene_frameshift_off = genomics.Gene("PIK3R1", "ENSG00000145675")
        # Note: Dummy amino acid change here; the position is important but not
        # the actual residue change:
        self._pik3r1_frameshift_off = genomics.Alteration(self._pik3r1_gene_frameshift_off, "ENST00000521381", "frameshift_variant", "Val10Leu")
        self._pik3r1_gene_frameshift_off.add_alteration(self._pik3r1_frameshift_off)

    def test_init(self):
        self.assertDictEqual(self._rule._gene_symbol2classifications, self._symbol2classifications)

    # XXX CONTINUE HERE: DEBUG TO GET THESE TESTS WORKING.
    def test_apply_single_pten(self):
        input_symbol2gene = {"PTEN": self._pten_gene_single_mutation}
        test_report = self._rule.apply(input_symbol2gene)
        expected_output_dict = {"ALASCCA CLASS", reports.AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pten_not_enough(self):
        input_symbol2gene = {"PTEN": self._pten_gene_single_mutation_not_enough}
        test_report = self._rule.apply(input_symbol2gene)
        expected_output_dict = {"ALASCCA CLASS", reports.AlasccaClassReport.NO_MUTN}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3r1_frameshift(self):
        input_symbol2gene = {"PIK3R1": self._pik3r1_gene_frameshift}
        test_report = self._rule.apply(input_symbol2gene)
        expected_output_dict = {"ALASCCA CLASS", reports.AlasccaClassReport.MUTN_CLASS_B}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

    def test_apply_single_pik3r1_frameshift_off(self):
        input_symbol2gene = {"PIK3R1": self._pik3r1_gene_frameshift_off}
        test_report = self._rule.apply(input_symbol2gene)
        expected_output_dict = {"ALASCCA CLASS", reports.AlasccaClassReport.NO_MUTN}
        self.assertDictEqual(test_report.to_dict(), expected_output_dict)

#    def test_apply_double_pten(self):

#    def test_apply_single_pik3r1(self):

#    def test_apply_pik3ca_class_b(self):

#    def test_apply_pik3ca_class_a(self):





































































