# -*- coding: utf-8 -*-
from reportgen.rules.general import MutationStatus
import pdb

class ReportFeature(object):
    '''
    ReportFeature abstract class.
    '''

    def __init__(self):
        '''
        '''

    # Concrete classes must implement toDict()


class AlasccaClassReport(ReportFeature):
    '''
    '''

    NAME = "alascca_class"

    MUTN_CLASS_A = "Mutation class A"
    MUTN_CLASS_B = "Mutation class B"
    NO_MUTN = "No mutation"
    NOT_DET = "Not determined"
    VALID_STRINGS = [MUTN_CLASS_A, MUTN_CLASS_B, NO_MUTN]

    def __init__(self):
        self._pathway_class = None

    @staticmethod
    def get_name():
        return "alascca_class_report"

    def set_class(self, pathway_class):
        assert pathway_class in self.VALID_STRINGS
        self._pathway_class = pathway_class

    def to_dict(self):
        return {self.NAME:self._pathway_class}


class MsiReport(ReportFeature):
    '''
    '''

    MSS = "MSS/MSI-L"
    MSI = "MSI-H"
    NOT_DETERMINED = "Not determined"
    VALID_STRINGS = [MSS, MSI, NOT_DETERMINED]

    NAME = "msi_status"

    def __init__(self):
        self._msi_status = None

    def to_dict(self):
        return {self.NAME:self._msi_status}

    def get_status(self):
        return self._msi_status

    def set_status(self, msi_status):
        self._msi_status = msi_status

    @staticmethod
    def get_name():
        return "msi_report"


class SimpleSomaticMutationsReport(ReportFeature):
    '''A report on mutation status of selected genes.
    '''

    def __init__(self):
        # Sets up an empty dictionary of geneSymbol->(mutationStatus, mutationList)
        # key value pairs, where mutationStatus is a string of restricted
        # values, and mutationList is an array of tuples each containing an
        # alteration and an associated alteration flag. Note that mutationList
        # can only be non-null if mutationStatus is "mutated":
        self._symbol2mutation_status = {}

    @staticmethod
    def get_name():
        return "simple_somatic_mutations_report"

    def add_gene(self, gene_name):
        # Adds a gene, with mutationStatus as "NoMutation" and mutationList as
        # empty by default:
        self._symbol2mutation_status[gene_name] = MutationStatus()

    def add_mutation(self, mutation, flag):
        gene_symbol = mutation.get_altered_gene().get_gene().get_symbol()
        assert self._symbol2mutation_status.has_key(gene_symbol)
        self._symbol2mutation_status[gene_symbol].add_mutation(mutation, flag)

    def to_dict(self):
        output_dict = {}
        for symbol in self._symbol2mutation_status.keys():
            mutation_status = self._symbol2mutation_status[symbol]
            output_dict[symbol] = mutation_status.to_dict()

        return output_dict
