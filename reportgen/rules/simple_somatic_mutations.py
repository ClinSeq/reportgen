import pdb
from reportgen.reporting.util import parse_mutation_table
from reportgen.reporting.features import SimpleSomaticMutationsReport


class SimpleSomaticMutationsRule:
    '''A rule for generating summary (intended to be printed as a table) of
    mutations in a set of genes, with the set of genes and mutation flagging
    determined by an excel spreadsheet.

    The idea here is that someone can update the spreadsheet defining mutations
    of interest and how they should be flagged, and these rules then get applied
    to a set of gene mutations by an instance of this class.'''

    def __init__(self, excel_spreadsheet, symbol2gene):
        # FIXME: Somewhere, we need to have an exact specification of the structure
        # of the excel spreadsheet specifying rules. Writing this down here for
        # the time being.

        # Excel spreadsheet must contain a set of rows, each containin the
        # following columns:
        # - Consequence (comma separated list of one or more sequence ontology
        # terms)
        # - Symbol (exactly one HUGO gene name)
        # - Gene (exactly one Ensembl gene ID, must match the Symbol)
        # - Transcript (Optional (zero or one) Ensembl transcript ID). This
        # must be specified if the consequence types pertain to transcript
        # annotations, such as amino acid substitutions.
        # - Amino acid changes (comma separated list of codon position
        # strings). Each codon position string must match one of the following
        # patterns:
        # <positionOnly> ::= [0-9]+
        # <residueChange> ::= [A-Z]{1}[0-9]+[A-Z]{1}
        # <positionRange> ::= [0-9]+:[0-9]+
        # - Flag (string)

        # This data structure is ugly but I think it should work; it will
        # facilitate matching mutations to rules:
        self._gene_symbol2classifications = parse_mutation_table(excel_spreadsheet)

        self._symbol2gene = symbol2gene

    def apply(self):
        '''Generates a new SimpleSomaticMutationsReport object, summarising all
        somatic mutations of interest observed in the specified gene
        mutations.'''

        report = SimpleSomaticMutationsReport()

        for symbol in self._gene_symbol2classifications.keys():
            # Retrieve all the classifications for the current gene:
            gene_classifications = self._gene_symbol2classifications[symbol]

            report.add_gene(symbol)

            # Find all mutations matching this gene's rules:
            alterations = []
            if self._symbol2gene.has_key(symbol):
                gene = self._symbol2gene[symbol]
                alterations = gene.get_alterations()

            for alteration in alterations:
                # Apply all rules to this alteration, in order of precedence.
                # In this way, later matched rules will overwrite any preceding
                # flag result:
                for classification in gene_classifications:
                    flag = None
                    if classification.match(alteration):
                        flag = classification.get_output_flag()
                    report.add_mutation(alteration, flag)

        return report