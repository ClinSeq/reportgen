from reportgen.reporting.util import parse_mutation_table
from reportgen.reporting.features import AlasccaClassReport


class AlasccaClassRule:
    """A rule for generating an alascca class (A/B/None) summarising PI3K
    pathway mutational status. The rule parameters are specified in an
    input excel spreadsheet."""

    # These possible alteration flags must match the flags defined in the
    # ALASCCA_MUTATION_TABLE excel spreadsheet:
    CLASS_B_1 = "ALASCCA_CLASS_B_1"
    CLASS_B_2 = "ALASCCA_CLASS_B_2"
    CLASS_A = "ALASCCA_CLASS_A"

    # FIXME: Still need to generate exact algorithm for the constructor and
    # the apply() method. It should be fairly straightforward now though. See
    # SimpleSomaticMutationsRule as a template.

    def __init__(self, excel_spreadsheet, symbol2gene):
        self._gene_symbol2classifications = parse_mutation_table(excel_spreadsheet)

        self._symbol2gene = symbol2gene

    # FIXME: It is currently unclear when we should be calling
    # "not determined".

    def apply(self):
        # If there is one or more genes with at least one class A alteration,
        # then call class A. Otherwise, if there is one or more genes with at
        # least one class B_1 mutation, then call class B. Otherwise, if there
        # are at least two class B_2 mutations, then call class B. Otherwise,
        # call no mutation.

        # Classify alterations and count the flag instances...
        flag_instances = {self.CLASS_B_1: 0, self.CLASS_B_2: 0,
                          self.CLASS_A: 0}

        for symbol in self._gene_symbol2classifications.keys():
            # Retrieve all the classifications for the current gene:
            gene_classifications = self._gene_symbol2classifications[symbol]

            # Find all mutations matching this gene's rules:
            alterations = []
            gene = None
            if self._symbol2gene.has_key(symbol):
                gene = self._symbol2gene[symbol]
                alterations = gene.get_alterations()

            for alteration in alterations:
                # Apply all rules to this alteration:
                for classification in gene_classifications:
                    flag = None
                    if classification.match(alteration):
                        flag = classification.get_output_flag()
                        assert flag_instances.has_key(flag)
                        flag_instances[flag] = flag_instances[flag] + 1

        # Apply logic based on numbers of flag instances:
        report = AlasccaClassReport()
        if flag_instances[self.CLASS_A] > 0:
            alasccaClass = AlasccaClassReport.MUTN_CLASS_A
        elif flag_instances[self.CLASS_B_1] > 0:
            alasccaClass = AlasccaClassReport.MUTN_CLASS_B
        elif flag_instances[self.CLASS_B_2] >= 2:
            alasccaClass = AlasccaClassReport.MUTN_CLASS_B
        else:
            alasccaClass = AlasccaClassReport.NO_MUTN

        # FIXME/NOTE: Currently there is no way of setting it to "not
        # determined". We need to figure out how/when to define this
        # and then we will need to adapt this and other code accordingly.

        report.set_class(alasccaClass)
        return report