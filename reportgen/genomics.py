import vcf

class Gene:
    def __init__(self, symbol, gene_ID):
        self._symbol = symbol
        self._gene_ID = gene_ID
        self._alterations = []

    def addAlteration(self, alteration):
        self._alterations.append(alteration)


class Alteration:
    '''NOTE: This single concrete class will currently be used to represent
    all types of alterations, without having subclasses. The type of the
    alteration will be specified by self._sequence_ontology_term, which must
    contain a valid sequence ontology string.'''

    def __init__(self, gene, transcriptID, alterationType, positionalString):
        self._gene = gene
        self._sequence_ontology_term = alterationType
        self._transcript_ID = transcriptID
        self._position_string = positionalString

    # FIXME: Not sure where I intend to use this but I'm pretty sure this is broken:
    def to_dict(self):
        if self._position_string != None:
            return self._position_string + "_" + self._sequence_ontology_term
        else:
            return self._sequence_ontology_term


class AlterationExtractor:
    def __init__(self, vcfFile, cnvFile):
        self.symbol2gene = {}
        self.extract_mutations(vcfFile)
        self.extractCNVs(cnvFile) # FIXME: DO WE NEED TO SPECIFY GENE ANNOTATIONS HERE TOO?

    def extract_mutations(self, vcfFile):
        vcf_reader = vcf.Reader(open("/Users/thowhi/Desktop/Dropbox (KI)/ClinSeq/AlasscaReport/36-nras-braf-kras-variants.vcf", "r"))
        for mutation in vcf_reader:
            vep_annotations = mutation.INFO['CSQ']

            for annotation in vep_annotations:
                # Extract gene symbol, ID, transcript_ID, alteration position and alteration type:
                fields = annotation.split("|")
                symbol = fields[25]
                gene_id = fields[1]
                transcript_id = fields[2]
                alteration_type = fields[4].split("&")[0]
                aa_position = fields[35].split(".")[-1]

                # Add this gene if it has not already been added:
                if not self.symbol2gene.has_key(symbol):
                    curr_gene = Gene(symbol, gene_id)
                    self.symbol2gene[symbol] = curr_gene

                curr_gene = self.symbol2gene[symbol]

                # Record the current alteration:
                curr_alteration = Alteration(curr_gene, transcript_id, alteration_type, aa_position)
                curr_gene.add_alteration(curr_alteration)

    def extractCNVs(self, cnvFile):
        # FIXME: Not sure about the format of the input file: Need to discuss this
        # with Daniel in more detail. However, the output of this function is clear:
        # It's a dictionary with gene symbols as keys and Gene objects as keys, with
        # the Gene objects containing Alteration objects representing the CNVs using
        # appropriate sequence ontology terms.
        # FIXME: NOT SURE ABOUT THIS.

        pass

    def to_dict(self):
        return self.symbol2gene
