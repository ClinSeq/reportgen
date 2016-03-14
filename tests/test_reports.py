import unittest
from reportgen import reports
from reportgen import genomics


class TestAlterationClassification(unittest.TestCase):
    _single_consequence_classification = None

    def setUp(self):
        self._kras_classification = reports.AlterationClassification(["missense_variant"], "ENST00000369535", ["12","13","60","61","117","146"], "KRAS_COMMON")

        self._kras_gene = genomics.Gene("KRAS", "ENSG00000133703")

        self._kras_alteration1 = genomics.Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "Ala146Pro")
        self._kras_gene.add_alteration(self._kras_alteration1)

        # A fake mutation that is *not* in the set of KRAS mutations:
        self._kras_alteration2 = genomics.Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "Lys1Asn")
        self._kras_gene.add_alteration(self._kras_alteration2)

    # XXX CONTINUE HERE: ADD TESTS FOR THE MATCH POSITION METHODS, AND THEN GET THIS TEST TO PASS:
    def test_match_true(self):
        self.assertTrue(self._kras_classification.match(self._kras_alteration1))

    def test_match_false(self):
        self.assertFalse(self._kras_classification.match(self._kras_alteration2))
