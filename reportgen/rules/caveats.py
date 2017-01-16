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