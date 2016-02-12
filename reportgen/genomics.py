import sys

class Gene:
    def __init__(self, gene_ID):
        self._symbol = symbol
        self._gene_ID = gene_ID
        self._alterations = []

    def addAlteration(alteration):
        self._alterations.append(alteration)

class Alteration:
    '''NOTE: This single concrete class will currently be used to represent
    all types of alterations, without having subclasses. The type of the
    alteration will be specified by self._sequence_ontology_term, which must
    contain a valid sequence ontology string.'''

    def __init__(self, transcriptID, alterationType, positionalString):
        self._gene = gene
        self._sequence_ontology_term = alterationType
        self._transcript_ID = transcriptID
        self._position_string = positionalString

    def toDict():
        if self._position_string != null:
            return self._position_string + "_" + self.sequence_ontology_term
        else:
            return self.sequence_ontology_term

    def positionInformationMatches(self, positionInformationString):
        '''Returns true if the specified string matches this position
        information, or false otherwise.'''

        # FIXME: IMPLEMENT THIS:
#**** If it's an exact match then return true
#**** If the position information string is an integer and nothing more then this will be matched against this position information's integer value, taking nothing else into consideration:
#***** NOTE: I think this is valid, especially since the

class AlterationExtractor:
    def __init__(self, vcfFile, cnvFile):
        self.symbol2mutation = extractMutations(vcfFile)
        self.symbol2cnv = extractCNVs(cnvFile) # FIXME: DO WE NEED TO SPECIFY GENE ANNOTATIONS HERE TOO?

    def extractMutations(self, vcfFile):
        # FIXME: IMPLEMENT THIS:
#******* symbol2gene = {}
#******* parse vcf using pyvcf
#******* For each alteration:
#******** Extract all resulting identified protein sequence alterations as identified by VEP
#******** For each protein alteration:
#********* Extract gene symbol, ID, transcript_ID (is this optional?), alteration position (optional I think?) and alteration type (sequence ontology term)
#********* Format the alteration position into the required position string structure.
#********* if not symbol2gene.has_key[symbol]:
#********** currGene = Gene(symbol, geneID)
#********** symbol2gene[symbol] = currGene
#********* currGene = symbol2gene[symbol]
#********* currAlteration = Alteration(gene, transcriptID, alterationType, positionString)
#********* currGene.addAlteration(currAlteration)
#******* return symbol2gene

    def extractCNVs(self, cnvFile):
        # FIXME: Not sure about the format of the input file: Need to discuss this
        # with Daniel in more detail. However, the output of this function is clear:
        # It's a dictionary with gene symbols as keys and Gene objects as keys, with
        # the Gene objects containing Alteration objects representing the CNVs using
        # appropriate sequence ontology terms.
        # FIXME: NOT SURE ABOUT THIS:
        # return symbol2gene

    def combineMutationAndCopyNumber(self):
        # FIXME: Implement this:
        # Add all of the cnv alterations to the genes listed in the mutation
        # alterations, and return the resulting symbol2gene dictionary.

    def compileAlterations(self):
        # FIXME: Not sure about this:
        return self.combineMutationAndCopyNumber()
