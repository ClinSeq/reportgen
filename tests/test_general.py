from mock import mock_open, patch, Mock, MagicMock
import unittest

from reportgen.rules.general import AlterationExtractor, AlterationClassification, Gene, AlteredGene, Alteration, MSIStatus


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


class TestMSIStatus(unittest.TestCase):
    def setUp(self):
        self._msi_status = MSIStatus()

    def test_set_from_file_test_percent(self):
        self._msi_status.set_from_file(open("tests/msi_high_eg.txt"))
        self.assertTrue(self._msi_status._percent == 72.60)

    def test_set_from_file_test_somatic_sites(self):
        self._msi_status.set_from_file(open("tests/msi_high_eg.txt"))
        self.assertTrue(self._msi_status._somatic_sites == 53)

    def test_set_from_file_test_total_sites(self):
        self._msi_status.set_from_file(open("tests/msi_high_eg.txt"))
        self.assertTrue(self._msi_status._total_sites == 73)

    def test_set_from_file_invalid_header(self):
        open_name = '%s.open' % __name__
        with patch(open_name, mock_open(read_data='An invalid header\nA second line'), create=True):
            with open("dummy_filename.txt") as test_file:
                self.assertRaises(ValueError, lambda: self._msi_status.set_from_file(open(test_file)))


class TestAlterationExtractor(unittest.TestCase):
    _extractor = None

    def setUp(self):
        self._extractor = AlterationExtractor()

        nras = Gene("NRAS")
        nras.set_ID("ENSG00000213281")
        self._nras_gene = AlteredGene(nras)
        test_alteration1 = Alteration(self._nras_gene, "ENST00000369535", "missense_variant", "p.Gln61His")
        self._nras_gene.add_alteration(test_alteration1)

        kras = Gene("KRAS")
        kras.set_ID("ENSG00000133703")
        self._kras_gene = AlteredGene(kras)
        test_alteration2 = Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "p.Ala146Pro")
        self._kras_gene.add_alteration(test_alteration2)
        test_alteration3 = Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "p.Lys117Asn")
        self._kras_gene.add_alteration(test_alteration3)

        pten = Gene("PTEN")
        pten.set_ID(None)
        self._pten_gene_loh = AlteredGene(pten)
        test_alteration4 = Alteration(self._pten_gene_loh, None, "loss_of_heterozygosity", None)
        self._pten_gene_loh.add_alteration(test_alteration4)

        self._pten_gene_hloss = AlteredGene(pten)
        test_alteration5 = Alteration(self._pten_gene_hloss, None, "homozygous_loss", None)
        self._pten_gene_hloss.add_alteration(test_alteration5)

    def test_gene(self):
        self._extractor.extract_mutations(open("tests/simple_variant_input.vcf"))
        output_dict = self._extractor.to_dict()

        self.assertEqual(output_dict["NRAS"].get_gene().get_symbol(), "NRAS")
        self.assertEqual(output_dict["NRAS"].get_gene().get_ID(), self._nras_gene.get_gene().get_ID())

    def test_extract_mutations_empty_input(self):
        self._extractor.extract_mutations(open("tests/empty_input.vcf"))
        output_dict = self._extractor.to_dict()

        expected_dict = {}

        self.assertDictEqual(output_dict, expected_dict)

    def test_extract_mutations_empty_input_without_header(self):
        self._extractor.extract_mutations(open("tests/empty_input_without_header.vcf"))
        output_dict = self._extractor.to_dict()

        expected_dict = {}

        self.assertDictEqual(output_dict, expected_dict)

    def test_extract_mutations_multiple_mutations(self):
        self._extractor.extract_mutations(open("tests/multiple_mutations_variant_input.vcf"))
        output_dict = self._extractor.to_dict()

        expected_dict = {"KRAS": self._kras_gene}
        self.assertEqual(len(output_dict.keys()), len(expected_dict.keys()))
        self.assertEqual(output_dict["KRAS"].get_gene().get_ID(), expected_dict["KRAS"].get_gene().get_ID())

    def test_extract_mutations_multiple_genes(self):
        self._extractor.extract_mutations(open("tests/multiple_genes_variant_input.vcf"))
        output_dict = self._extractor.to_dict()

        expected_dict = {"KRAS": self._kras_gene, "NRAS": self._nras_gene}
        self.assertEqual(len(output_dict.keys()), len(expected_dict.keys()))
        self.assertEqual(output_dict["NRAS"].get_gene().get_ID(), expected_dict["NRAS"].get_gene().get_ID())

    def test_extract_cnvs_gene_no_call(self):
        self._extractor.extract_cnvs(open("tests/pten_no_call.json"))
        output_dict = self._extractor.to_dict()

        # Output dictionary should be empty as there is no call:
        self.assertDictEqual(output_dict, {})

    def test_extract_cnvs_gene_hom_loss(self):
        self._extractor.extract_cnvs(open("tests/pten_hom_loss.json"))
        output_dict = self._extractor.to_dict()

        # Output dictionary should be empty as there is no call:
        self.assertEqual(output_dict["PTEN"].get_gene().get_symbol(), "PTEN")
        self.assertEqual(len(output_dict["PTEN"].get_alterations()), 1)
        self.assertEqual(output_dict["PTEN"].get_alterations()[0].get_sequence_ontology(), "homozygous_loss")

    def test_extract_cnvs_gene_het_loss(self):
        self._extractor.extract_cnvs(open("tests/pten_het_loss.json"))
        output_dict = self._extractor.to_dict()

        # Output dictionary should be empty as there is no call:
        self.assertEqual(output_dict["PTEN"].get_gene().get_symbol(), "PTEN")
        self.assertEqual(output_dict["PTEN"].get_gene().get_ID(), "ENSG00000171862")
        self.assertEqual(len(output_dict["PTEN"].get_alterations()), 1)
        self.assertEqual(output_dict["PTEN"].get_alterations()[0].get_sequence_ontology(), "loss_of_heterozygosity")
        self.assertEqual(output_dict["PTEN"].get_alterations()[0].get_transcript_ID(), "ENST00000371953")

    def test_extract_cnvs_invalid_inputs1(self):
        self.assertRaises(ValueError, self._extractor.extract_cnvs, open("tests/pten_invalid_call.json"))
