from reportgen.reporting.features import PurityReport

class PurityRule:
    LOW_PURITY = "LOW"

    def __init__(self, purity_dicts):
        self._purity_ok = True
        uniq_purity_calls = set(map(lambda dict: dict["purity.call"], purity_dicts))
        if len(uniq_purity_calls) == 1 and uniq_purity_calls[0] == PurityRule.LOW_PURITY:
            self._purity_ok = False

    def apply(self):
        report = PurityReport(self._purity_ok)