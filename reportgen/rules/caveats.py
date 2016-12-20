from reportgen.reporting.features import PurityReport


class Caveat:
    UNCHANGED = "UNCHANGED"
    NON_POSITIVE_TO_EB = "NON_POSITIVE_TO_EB"
    ALL_TO_EB = "ALL_TO_EB"

    def __init__(self):
        self._action = None


class CoverageInfo(Caveat):
    def __init__(self, multi_qc_zip_file):
        super(CoverageInfo, self).__init__()

        # Extract coverage information from the MultiQC file...

        # Set the self._action field according to the tumor/normal coverage values and the specified thresholds.


class PurityRule:
    LOW_PURITY = "LOW"

    def __init__(self, purity_dicts):
        self._purity_ok = True
        uniq_purity_calls = set(map(lambda dict: dict["purity.call"], purity_dicts))
        if len(uniq_purity_calls) == 1 and uniq_purity_calls[0] == PurityRule.LOW_PURITY:
            self._purity_ok = False

    def apply(self):
        report = PurityReport(self._purity_ok)