import unittest
from reportgen import genomics


def compareGenes(gene1, gene2):
    """Function to compare two genomics.Gene objects, to facilitate
    testing with Gene objects here."""

    print >> sys.stderr, "TRACE:", gene1, gene2

    if gene1.get_ID() != gene2.get_ID:
        raise unittest.TestCase.failureException("Gene IDs not equal.")

    # For two gene objects to be equal, they must have identical alteration objects:
    #for alteration in gene1.get_alterations:


class TestAlterationExtractor(unittest.TestCase):
    _extractor = None

    def setUp(self):
        self._extractor = genomics.AlterationExtractor()

        self.addTypeEqualityFunc(genomics.Gene, compareGenes)

        self._nras_gene = genomics.Gene("NRAS", "ENSG00000213281")
        test_alteration1 = genomics.Alteration(self._nras_gene, "ENST00000369535", "missense_variant", "Gln61His")
        self._nras_gene.add_alteration(test_alteration1)

        self._kras_gene = genomics.Gene("KRAS", "ENSG00000133703")
        test_alteration2 = genomics.Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "Ala146Pro")
        self._kras_gene.add_alteration(test_alteration2)
        test_alteration3 = genomics.Alteration(self._kras_gene, "ENST00000256078", "missense_variant", "Lys117Asn")
        self._kras_gene.add_alteration(test_alteration3)

    def test_extract_mutations_simple_input(self):
        self._extractor.extract_mutations(open("tests/simple_variant_input.vcf"))
        dict = self._extractor.to_dict()

        expected_dict = {"NRAS": self._nras_gene}
        self.assertDictEqual(dict, expected_dict, dict)

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















































