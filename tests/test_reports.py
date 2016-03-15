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
        self._kras_gene.add_alteration(self._kras_alteration2)

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


class TestSimpleSomaticMutationsRule(unittest.TestCase):
    def setUp(self):
        braf_classification = reports.AlterationClassification(["missense_variant"], "ENST00000288602", ["Val600Glu"], "BRAF_COMMON")
        kras_classification = reports.AlterationClassification(["missense_variant"], "ENST00000256078", ["12","13","60","61","117","146"], "KRAS_COMMON")
        nras_classification = reports.AlterationClassification(["missense_variant"], "ENST00000369535", ["12","13","61"], "NRAS_COMMON")
        self._symbol2classifications = {"BRAF": [braf_classification], "KRAS": [kras_classification], "NRAS": [nras_classification]}

        self._rule = reports.SimpleSomaticMutationsRule("COLORECTAL_MUTATION_TABLE.xlsx")

    def test_classification_is_same(self):
        self.assertEqual(self._rule._gene_symbol2classifications["NRAS"][0], self._symbol2classifications["NRAS"][0])

    def test_symbol2classification_is_same(self):
        self.assertDictEqual(self._rule._gene_symbol2classifications, self._symbol2classifications)






































