# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from reportgen.rules.general import MutationStatus
from reportgen.rules.util import FeatureStatus


class ReportComponent(object):
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

    @abstractmethod
    def component_name(self):
        pass

    def apply_caveat(self, caveat):
        """
        The default is to not alter the report in any way; i.e. just ignore the caveat.
        :return:
        """
        pass


class AlasccaClassReport(ReportComponent):
    '''
    '''

    ALASCCA_CLASS_FEATURENAME = "alascca_class"

    MUTN_CLASS_A = "Mutation class A"
    MUTN_CLASS_B = "Mutation class B"

    def __init__(self):
        self._pathway_class = None

    def component_name(self):
        return "alascca_class_report"

    @property
    def pathway_class(self):
        return self._pathway_class

    @pathway_class.setter
    def pathway_class(self, pathway_class):
        self._pathway_class = pathway_class

    def apply_caveat(self, caveat):
        """
        If told all to ej bedömbar, then do that; otherwise, if told to set non-positive
        to E.B. then only do that if the mutation class was "not mutated".

        :param caveat: The caveat indicating whether/how to change this report feature.
        :return:
        """
        if caveat.setting_all_to_eb():
            self._pathway_class = FeatureStatus.NOT_DETERMINED
        elif caveat.setting_non_positive_to_eb() and self._pathway_class == FeatureStatus.NOT_MUTATED:
            self._pathway_class = FeatureStatus.NOT_DETERMINED

    def to_dict(self):
        return {self.ALASCCA_CLASS_FEATURENAME:self._pathway_class}


class MsiReport(ReportComponent):
    '''
    '''

    MSS = "MSS/MSI-L"
    MSI = "MSI-H"

    MSI_FEATURENAME = "msi_status"

    def __init__(self):
        self._msi_status = None

    def to_dict(self):
        return {self.MSI_FEATURENAME:self._msi_status}

    @property
    def msi_status(self):
        return self._msi_status

    @msi_status.setter
    def msi_status(self, msi_status):
        self._msi_status = msi_status

    def apply_caveat(self, caveat):
        """
        No MSI calls are considered definitively positive, when it comes to changing non-positive
        calls to E.B. as a result of caveats.

        :param caveat: The caveat indicating whether/how to change this report feature.
        :return:
        """
        if caveat.setting_all_to_eb() or caveat.setting_non_positive_to_eb():
            self._msi_status = FeatureStatus.NOT_DETERMINED

    def component_name(self):
        return "msi_report"


class SimpleSomaticMutationsReport(ReportComponent):
    '''A report on mutation status of selected genes.
    '''

    def __init__(self):
        # Sets up an empty dictionary of geneSymbol->(mutationStatus, mutationList)
        # key value pairs, where mutationStatus is a string of restricted
        # values, and mutationList is an array of tuples each containing an
        # alteration and an associated alteration flag. Note that mutationList
        # can only be non-null if mutationStatus is "mutated":
        self._symbol2mutation_status = {}

    def component_name(self):
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
            if caveat.setting_all_to_eb():
                curr_mutn_status.to_EB()
            elif caveat.setting_non_positive_to_eb() and not curr_mutn_status.is_positive():
                curr_mutn_status.to_EB()

    def to_dict(self):
        output_dict = {}
        for symbol in self._symbol2mutation_status.keys():
            mutation_status = self._symbol2mutation_status[symbol]
            output_dict[symbol] = mutation_status.to_dict()

        return output_dict


class PurityReport(ReportComponent):
    '''A report on tumor sample purity.'''

    PURITY_FEATURENAME = "purity"

    def __init__(self):
        self._purity_ok = None

    @property
    def purity_ok(self):
        return self._purity_ok

    @purity_ok.setter
    def purity_ok(self, purity_ok):
        self._purity_ok = purity_ok

    def component_name(self):
        return "purity_report"

    def to_dict(self):
        return {self.PURITY_FEATURENAME:self._purity_ok}