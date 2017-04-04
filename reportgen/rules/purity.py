from reportgen.reporting.features import PurityReport


class PurityRule:
    """
    Used for generating report content that warns if purity is low.
    """

    def __init__(self, purity_call):
        self._purity_ok = purity_call

    def apply(self):
        report = PurityReport()
        report.purity_ok = self._purity_ok
        return report