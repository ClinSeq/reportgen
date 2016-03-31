import vcf


class Gene:
    def __init__(self, symbol):
        self._symbol = symbol
        self._gene_ID = None

    def set_ID(self, gene_ID):
        # Should only be set once:
        assert self._gene_ID == None
        self._gene_ID = gene_ID

    def get_ID(self):
        return self._gene_ID

    def get_symbol(self):
        return self._symbol

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not self.get_ID() == other.get_ID():
            return False
        if not self.get_symbol() == other.get_symbol():
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class AlteredGene:
    def __init__(self, gene):
        self._gene = gene
        self._alterations = []

    def add_alteration(self, alteration):
        self._alterations.append(alteration)

    def get_alterations(self):
        return self._alterations

    def get_gene(self):
        return self._gene

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not self._gene == other._gene:
            return False
        for alteration in self.get_alterations():
            if not alteration in other.get_alterations():
                return False
        for alteration in other.get_alterations():
            if not alteration in self.get_alterations():
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class Alteration:
    '''NOTE: This single concrete class will currently be used to represent
    all types of alterations, without having subclasses. The type of the
    alteration will be specified by self._sequence_ontology_term, which must
    contain a valid sequence ontology string.'''

    def __init__(self, alteredGene, transcriptID, alterationType, positionalString):
        self._altered_gene = alteredGene
        self._sequence_ontology_term = alterationType
        self._transcript_ID = transcriptID
        # Note: positing string can be None, when the alteration type does
        # not imply positional information.
        self._position_string = positionalString

    # FIXME: Not sure where I intend to use this but I'm pretty sure this is broken:
    def to_dict(self):
        if self._position_string != None:
            return self._position_string + "_" + self._sequence_ontology_term
        else:
            return self._sequence_ontology_term

    def get_altered_gene(self):
        return self._altered_gene

    def get_sequence_ontology(self):
        return self._sequence_ontology_term

    def get_transcript_ID(self):
        return self._transcript_ID

    def get_position_string(self):
        return self._position_string

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not self.get_altered_gene().get_gene() == other.get_altered_gene().get_gene():
            return False
        if not self.get_sequence_ontology() == other.get_sequence_ontology():
            return False
        if not self.get_transcript_ID() == other.get_transcript_ID():
            return False
        if not self.get_position_string() == other.get_position_string():
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class AlterationExtractor:
    def __init__(self):
        self.symbol2gene = {}

    def extract_mutations(self, vcf_file):
        vcf_reader = vcf.Reader(vcf_file)
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
                    curr_gene = Gene(symbol)
                    curr_gene.set_ID(gene_id)
                    altered_gene = AlteredGene(curr_gene)
                    self.symbol2gene[symbol] = altered_gene

                altered_gene = self.symbol2gene[symbol]

                # Record the current alteration:
                curr_alteration = Alteration(altered_gene, transcript_id, alteration_type, aa_position)
                altered_gene.add_alteration(curr_alteration)

    def extract_cnvs(self, cnvFile):
        # FIXME: Not sure about the format of the input file: Need to discuss this
        # with Daniel in more detail. However, the output of this function is clear:
        # It's a dictionary with gene symbols as keys and Gene objects as keys, with
        # the Gene objects containing Alteration objects representing the CNVs using
        # appropriate sequence ontology terms.
        # FIXME: NOT SURE ABOUT THIS.

        pass

    def to_dict(self):
        return self.symbol2gene






