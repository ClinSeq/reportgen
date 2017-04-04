# -*- coding: utf-8 -*-
from abc import ABCMeta
from reportgen.rules.util import QC_Call


class Caveat(object):
    __metaclass__ = ABCMeta

    UNCHANGED = "UNCHANGED"
    NON_POSITIVE_TO_EB = "NON_POSITIVE_TO_EB"
    ALL_TO_EB = "ALL_TO_EB"

    def __init__(self):
        self._action = None

    def setting_all_to_eb(self):
        """
        :return: True if this caveat indicates that all items should be set to "Ej Bedömbar", False otherwise.
        """
        return self._action == Caveat.ALL_TO_EB

    def setting_non_positive_to_eb(self):
        """
        :return: True if this caveat indicates that negative items should be set to "Ej Bedömbar", False otherwise.
        """
        return self._action == Caveat.NON_POSITIVE_TO_EB


class CoverageCaveat(Caveat):
    def __init__(self, qc_call):
        """
        :param qc_call: String defining QC state, see the JSON schema for possible values.
        """
        super(CoverageCaveat, self).__init__()

        if qc_call == QC_Call.OK:
            self._action = Caveat.UNCHANGED
        elif qc_call == QC_Call.WARN:
            self._action = Caveat.NON_POSITIVE_TO_EB
        elif qc_call == QC_Call.FAIL:
            self._action = Caveat.ALL_TO_EB


class PurityCaveat(Caveat):
    def __init__(self, qc_call):
        """
        :param qc_call: String defining QC state, see the JSON schema for possible values.

        Must be one of either OK or FAIL, when specifying a purity caveat.
        """
        super(PurityCaveat, self).__init__()

        if qc_call == QC_Call.OK:
            self._action = Caveat.UNCHANGED
        elif qc_call == QC_Call.FAIL:
            self._action = Caveat.NON_POSITIVE_TO_EB
        else:
            raise ValueError("Invalid QC_Call value for a purity caveat: " + qc_call)


class ContaminationCaveat(Caveat):
    def __init__(self, qc_call):
        """
        :param qc_call: String defining QC state, see the JSON schema for possible values.
        """
        super(ContaminationCaveat, self).__init__()

        if qc_call == QC_Call.OK:
            self._action = Caveat.UNCHANGED
        elif qc_call == QC_Call.WARN:
            self._action = Caveat.ALL_TO_EB
        elif qc_call == QC_Call.FAIL:
            self._action = Caveat.ALL_TO_EB