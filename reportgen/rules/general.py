import json, re, sys

from reportgen.rules.util import FeatureStatus

import vcf


class AlterationClassification:
    '''This class is used to assign a particular classification to input
    genetic alterations, if a match occurs.'''

    def __init__(self, symbol, consequences, transcriptID, positionInformationStrings, outputFlag):
        self._symbol = symbol
        self._consequences = consequences
        self._transcript_ID = transcriptID
        self._position_strings = positionInformationStrings
        self._output_flag = outputFlag

    def get_position_information(self):
        return self._position_strings

    def get_transcript_ID(self):
        return self._transcript_ID

    def get_consequences(self):
        return self._consequences

    def get_output_flag(self):
        return self._output_flag

    def match(self, alteration):
        if not alteration.get_sequence_ontology() in self.get_consequences():
            return False
        if not alteration.get_transcript_ID() == self.get_transcript_ID():
            return False

        # FIXME: Perhaps I should make this mechanism more robust?
        # Absence of position information fields means that position is not
        # specified and will not be used to discount a match:
        if len(self.get_position_information()) > 0:
            position_matches = self.matches_positions(alteration)
            if not position_matches:
                return False

        return True

    def matches_positions(self, alteration):
        '''Returns true if the specified alteration's positional information
        "matches" the specified positions for this alteration classification.
        Returns false otherwise.'''

        matchObserved = False

        # FIXME: Possibly should refactor this code to make it more robust:
        # If the alteration position string is None, it means that the
        # alteration does not match any positions:
        if alteration.get_hgvsp() == None:
            return matchObserved

        for position_string in self._position_strings:
            if self.matches_position(position_string, alteration.get_hgvsp()):
                matchObserved = True

        return matchObserved

    def matches_position(self, classificationPositionString, alterationPositionString):
        # FIXME: POTENTIAL PROBLEMS:
        # The alteration position string may not always denote a single exact integer position.
        # E.g. what if it denotes a range? Also, what about complex substitutions? Need to
        # figure out how to deal with these. E.g. what if there are two ranges (alteration
        # range and classification range) and they partially overlap?

        if re.match("^p\.[A-Z][a-z]{2}[0-9]+[A-Z][a-z]{2}$", classificationPositionString) != None:
            # The position string denotes a specific amino acid substitution
            # => Only match if the alteration matches that substitution
            # exactly:
            return classificationPositionString == alterationPositionString
        else:
            # The match depends soley on the position of the alteration,
            # disregarding the residue information...

            # Extract integer position from alterationPositionString:
            alterationIntegerPosition = int(re.search("[0-9]+", alterationPositionString).group())

            if re.match("^[0-9]+$", classificationPositionString) != None:
                # The classification position string is an exact integer position =>
                # There is a match if the integer information in the alteration
                # matches the classification position string exactly:
                return int(classificationPositionString) == alterationIntegerPosition

            else:
                # This classification position string must be an integer range:
                assert re.match("^[0-9]+:[0-9]+$", classificationPositionString) != None

                # Extract the start and end positions of the range:
                classificationRangeStart = int(classificationPositionString.split(":")[0])
                classificationRangeEnd = int(classificationPositionString.split(":")[1])

                # There is a match if the alteration position intersects the classification position range at all:
                return alterationIntegerPosition >= classificationRangeStart \
                       and alterationIntegerPosition <= classificationRangeEnd


class MutationStatus:
    '''Mutation status of a given gene. Note: Currently, the gene is not
    directly stated, but can be accessed via the contained Alteration
    objects, which must all refer to the same AlteredGene object.'''

    def __init__(self):
        self._status = FeatureStatus.NOT_MUTATED
        self._mutation_list = []

    def to_dict(self):
        output_list = []
        for mutation_tup in self._mutation_list:
            output_list.append({
                "hgvsp" : mutation_tup[0].get_hgvsp(),
                "flag" : mutation_tup[1]
            })
        return {
            "status" : self._status,
            "alterations" : output_list
        }

    def is_positive(self):
        """
        :return: True if mutation status is positive (mutated), false otherwise.
        """
        return self._status == FeatureStatus.MUTATED

    def add_mutation(self, mutation, flag):
        self._status = FeatureStatus.MUTATED
        self._mutation_list.append((mutation, flag))

    def to_EB(self):
        self._status = FeatureStatus.NOT_DETERMINED


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
        self._hgvsp = positionalString

    def get_hgvsp(self):
        return self._hgvsp

    def get_altered_gene(self):
        return self._altered_gene

    def get_sequence_ontology(self):
        return self._sequence_ontology_term

    def get_transcript_ID(self):
        return self._transcript_ID


class AlterationExtractor:
    def __init__(self):
        self._symbol2gene = {}
        self._symbol_idx = None
        self._gene_id_idx = None
        self._transcript_id_idx = None
        self._alteration_type_idx = None
        self._aa_position_idx = None

    def extract_field_idxs(self, vcf_info_fieldnames):
        self._symbol_idx = vcf_info_fieldnames.index("SYMBOL")
        self._gene_id_idx = vcf_info_fieldnames.index("Gene")
        self._transcript_id_idx = vcf_info_fieldnames.index("Feature")
        self._alteration_type_idx = vcf_info_fieldnames.index("Consequence")
        self._aa_position_idx = vcf_info_fieldnames.index("HGVSp")

    def extract_symbol(self, annotation):
        fields = annotation.split("|")
        return fields[self._symbol_idx]

    def extract_gene_id(self, annotation):
        fields = annotation.split("|")
        return fields[self._gene_id_idx]

    def extract_transcript_id(self, annotation):
        fields = annotation.split("|")
        return fields[self._transcript_id_idx]

    def extract_alteration_type(self, annotation):
        fields = annotation.split("|")
        return fields[self._alteration_type_idx].split("&")[0]

    def extract_aa_position(self, annotation):
        fields = annotation.split("|")
        return fields[self._aa_position_idx].split(":")[-1]

    def extract_mutations(self, vcf_file):
        """
        Extract mutations from a VCF file.

        Note regarding a but in VEP:
        If no mutations are present when running VEP on a VCF file, VEP will
        create an empty file rather than a VCF file with a header only. This
        will cause pyvcf to raise a StopIteration when creating the reader
        since the header can't be parsed. For this reason, creation of the reader
        object is wrapped in a try-except below.
        """
        try:
            vcf_reader = vcf.Reader(vcf_file)
        except StopIteration:
            return

        # Retrieve the indexes of the relevant fields from the list of INFO
        # fields:
        self.extract_field_idxs(vcf_reader.infos["CSQ"].desc.split("|"))

        for mutation in vcf_reader:
            vep_annotations = mutation.INFO['CSQ']

            for annotation in vep_annotations:
                # Extract gene symbol, ID, transcript_ID, alteration position and alteration type:
                symbol = self.extract_symbol(annotation)
                gene_id = self.extract_gene_id(annotation)
                transcript_id = self.extract_transcript_id(annotation)
                alteration_type = self.extract_alteration_type(annotation)
                aa_position = self.extract_aa_position(annotation)

                # Add this gene if it has not already been added:
                if not self._symbol2gene.has_key(symbol):
                    curr_gene = Gene(symbol)
                    curr_gene.set_ID(gene_id)
                    altered_gene = AlteredGene(curr_gene)
                    self._symbol2gene[symbol] = altered_gene

                altered_gene = self._symbol2gene[symbol]

                # Record the current alteration:
                curr_alteration = Alteration(altered_gene, transcript_id, alteration_type, aa_position)
                altered_gene.add_alteration(curr_alteration)

    def extract_cnvs(self, cnvFile):
        cnv_dict = json.load(cnvFile)

        gene_symbol = cnv_dict["name"]
        call = cnv_dict["call"]
        gene_id = cnv_dict["ENSG"]
        transcript_id = cnv_dict["ENST"]
        call2sequence_ontology = {
            "HOMLOSS": "homozygous_loss",
            "HETLOSS_or_LOH": "loss_of_heterozygosity"
        }

        # Only record the CNV information if it is one of the CNV events of
        # interest:
        if call in call2sequence_ontology.keys():
            if not self._symbol2gene.has_key(gene_symbol):
                gene = Gene(gene_symbol)
                gene.set_ID(gene_id)
                self._symbol2gene[gene_symbol] = AlteredGene(gene)

            altered_gene = self._symbol2gene[gene_symbol]
            curr_alteration = Alteration(altered_gene, transcript_id,
                                         call2sequence_ontology[call],
                                         None)
            altered_gene.add_alteration(curr_alteration)

        else:
            if call != "NOCALL":
                raise ValueError("Invalid CNV call value: " + call)

    def to_dict(self):
        return self._symbol2gene


class MSIStatus:
    def __init__(self):
        self._total_sites = None
        self._somatic_sites = None
        self._percent = None

    def set_from_file(self, input_file):
        '''Extracts the relevant fields from the input file.'''

        print >> sys.stderr, "TRACE: Processing header."
        print >> sys.stderr, input_file

        header_elems = input_file.readline().strip().split("\t")

        print >> sys.stderr, "TRACE: Header elements:", header_elems

        if not (header_elems[0] == "Total_Number_of_Sites"
                and header_elems[1] == "Number_of_Somatic_Sites"
                and header_elems[2] == "%"):
            raise ValueError("Invalid MSI input file header.")

        print >> sys.stderr, "TRACE: Processed header."
        try:
            vals = map(lambda tok: float(tok), input_file.readline().split("\t"))

        except ValueError, e:
            print >> sys.stderr, "TRACE 1."
            raise ValueError("Invalid MSI data values.")

        print >> sys.stderr, "TRACE: Processed vals."

        if not (len(vals) == 3):
            print >> sys.stderr, "TRACE 2."
            raise ValueError("Invalid MSI data values.")

        print >> sys.stderr, "TRACE: Processed file."

        self._total_sites = vals[0]
        self._somatic_sites = vals[1]
        self._percent = vals[2]

    def get_total(self):
        return self._total_sites

    def get_percent(self):
        return self._percent