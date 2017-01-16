import json
from zipfile import ZipFile

from reportgen.reporting.features import PurityReport


class Caveat(object):
    UNCHANGED = "UNCHANGED"
    NON_POSITIVE_TO_EB = "NON_POSITIVE_TO_EB"
    ALL_TO_EB = "ALL_TO_EB"

    def __init__(self):
        self._action = None


class CoverageCaveat(Caveat):
    def __init__(self, coverage_call):
        """
        Set the self._action field according to the given coverage call.

        :param coverage_call: XXX CONTINUE HERE; FIGURE OUT WHAT THE CALLS ARE. BOOLEANS? A SPECIAL TYPE?
        STRINGS WITH A MATCHING CONSTANT DEFINITION SOMEWHERE?
        """
        super(CoverageInfo, self).__init__()

        if coverage_call


class PurityRule:
    """
    Used for generating report content that warns if purity is low.
    """

    OK_PURITY = "OK"
    LOW_PURITY = "LOW"

    def __init__(self, purity_call):
        self._purity_ok = purity_call

    def apply(self):
        report = PurityReport(self._purity_ok)
        return report