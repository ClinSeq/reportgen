# -*- coding: utf-8 -*-
from abc import ABCMeta
from reportgen.rules.general import MutationStatus
from reportgen.rules.util import FeatureStatus


class ReportFeature(object):
    __metaclass__ = ABCMeta

    '''
    An individual feature of a report.
    '''

    def __init__(self):
        '''
        '''

    @abstractmethod
    def to_dict(self):
        pass

    def apply_caveat(self, caveat):
        """
        The default is to not alter the report in any way; i.e. just ignore the caveat.
        :return:
        """
        pass


class AlasccaClassReport(ReportFeature):
    '''
    '''

    NAME = "alascca_class"

    MUTN_CLASS_A = "Mutation class A"
    MUTN_CLASS_B = "Mutation class B"

    def __init__(self):
        self._pathway_class = None

    @staticmethod
    def get_name():
        return "alascca_class_report"

    def set_class(self, pathway_class):
        self._pathway_class = pathway_class

    def apply_caveat(self, caveat):
        """
        If told all to ej bedömbar, then do that; otherwise, if told to set non-positive
        to E.B. then only do that if the mutation class was "not mutated".

        :param caveat: The caveat indicating whether/how to change this report feature.
        :return:
        """
        if caveat.all_to_eb():
            self._pathway_class = FeatureStatus.NOT_DETERMINED
        elif caveat.non_positive_to_eb() and self._pathway_class == FeatureStatus.NOT_MUTATED:
            self._pathway_class = FeatureStatus.NOT_DETERMINED

    def to_dict(self):
        return {self.NAME:self._pathway_class}


class MsiReport(ReportFeature):
    '''
    '''

    MSS = "MSS/MSI-L"
    MSI = "MSI-H"

    NAME = "msi_status"

    def __init__(self):
        self._msi_status = None

    def to_dict(self):
        return {self.NAME:self._msi_status}

    def get_status(self):
        return self._msi_status

    def set_status(self, msi_status):
        self._msi_status = msi_status

    def apply_caveat(self, caveat):
        """
        No MSI calls are considered definitively positive, when it comes to changing non-positive
        calls to E.B. as a result of caveats.

        :param caveat: The caveat indicating whether/how to change this report feature.
        :return:
        """
        if caveat.all_to_eb() or caveat.non_positive_to_eb():
            self._msi_status = FeatureStatus.NOT_DETERMINED

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

    def apply_caveat(self, caveat):
        """
        If told to set non-positive calls to E.B., then do this for each gene with a
        negative mutation status. If told to set all calls to E.B. then do this for all
        genes irrespective of their mutation status.

        :param caveat: The caveat indicating whether/how to change this report feature.
        :return:
        """
        for gene_name in self._symbol2mutation_status.keys():
            curr_mutn_status = self._symbol2mutation_status[gene_name]
            if caveat.all_to_eb():
                curr_mutn_status.to_EB()
            elif caveat.non_positive_to_eb() and not curr_mutn_status.is_positive():
                curr_mutn_status.to_EB()

    def to_dict(self):
        output_dict = {}
        for symbol in self._symbol2mutation_status.keys():
            mutation_status = self._symbol2mutation_status[symbol]
            output_dict[symbol] = mutation_status.to_dict()

        return output_dict


class PurityReport(ReportFeature):
    '''A report on tumor sample purity.'''

    def __init__(self, purity_ok):
        self._purity_ok = purity_ok

    def to_dict(self):
        return {self.Name:self._purity_ok}

    @property
    def get_purity_status(self):
        return self._purity_ok
