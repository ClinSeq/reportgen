import unittest
from reportgen import genomics


class TestAlterationExtractor(unittest.TestCase):
    _extractor = None

    def setUp(self):
        self._extractor = genomics.AlterationExtractor()

        nras = genomics.Gene("NRAS")
        nras.set_ID("ENSG00000213281")
        self._nras_gene = genomics.AlteredGene(nras)
        test_alteration1 = genomics.Alteration(self._nras_gene, "ENST00000369535", "missense_variant", "Gln61His")
        self._nras_gene.add_alteration(test_alteration1)

        kras = genomics.Gene("KRAS")
        kras.set_ID("ENSG00000133703")
        self._kras_gene = genomics.AlteredGene(kras)
        test_alteration2 = genomics.Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "Ala146Pro")
        self._kras_gene.add_alteration(test_alteration2)
        test_alteration3 = genomics.Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "Lys117Asn")
        self._kras_gene.add_alteration(test_alteration3)

    def test_gene(self):
        self._extractor.extract_mutations(open("tests/simple_variant_input.vcf"))
        output_dict = self._extractor.to_dict()

        expected_dict = {"NRAS": self._nras_gene}

        self.assertEqual(output_dict["NRAS"].get_gene().get_symbol(), "NRAS")

    def test_extract_mutations_simple_input(self):
        self._extractor.extract_mutations(open("tests/simple_variant_input.vcf"))
        output_dict = self._extractor.to_dict()

        expected_dict = {"NRAS": self._nras_gene}

        self.assertDictEqual(output_dict, expected_dict)

    def test_extract_mutations_multiple_mutations(self):
        self._extractor.extract_mutations(open("tests/multiple_mutations_variant_input.vcf"))
        dict = self._extractor.to_dict()

        expected_dict = {"KRAS": self._kras_gene}
        self.assertDictEqual(dict, expected_dict, dict)

    def test_extract_mutations_multiple_genes(self):
        self._extractor.extract_mutations(open("tests/multiple_genes_variant_input.vcf"))
        dict = self._extractor.to_dict()

        expected_dict = {"KRAS": self._kras_gene, "NRAS": self._nras_gene}
        self.assertDictEqual(dict, expected_dict, dict)


class TestMSIStatus(unittest.TestCase):
    def setUp(self):
        pass

    def test_set_from_file_test_percent(self):
        msi_status = genomics.MSIStatus()
        msi_status.set_from_file(open("tests/msi_high_eg.txt"))
        self.assertTrue(msi_status._percent == 72.60)

    def test_set_from_file_test_somatic_sites(self):
        msi_status = genomics.MSIStatus()
        msi_status.set_from_file(open("tests/msi_high_eg.txt"))
        self.assertTrue(msi_status._somatic_sites == 53)

    def test_set_from_file_test_total_sites(self):
        msi_status = genomics.MSIStatus()
        msi_status.set_from_file(open("tests/msi_high_eg.txt"))
        self.assertTrue(msi_status._total_sites == 73)








































