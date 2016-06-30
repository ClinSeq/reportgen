from mock import mock_open, patch, Mock, MagicMock
import unittest

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

    def test_match_transcript_mismatch(self):
        mock_alteration = Mock()
        mock_alteration.get_sequence_ontology = Mock(return_value="inframe_insertion")
        mock_alteration.get_transcript_ID = Mock(return_value="ENST00000521382")
        self.assertFalse(self._pik3r1_range_classification.match(mock_alteration))

    def test_matches_positions_no_hgvsp(self):
        mock_alteration = Mock()
        mock_alteration.get_hgvsp = Mock(return_value=None)
        self.assertFalse(self._pik3r1_range_classification.matches_positions(mock_alteration))
