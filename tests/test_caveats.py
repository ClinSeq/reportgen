import unittest

from reportgen.reporting.caveats import Caveat, CoverageCaveat, ContaminationCaveat, PurityCaveat
from reportgen.rules.util import QC_Call


class TestCoverageCaveat(unittest.TestCase):
    def setUp(self):
        self._cov_caveat_ok = CoverageCaveat(QC_Call.OK)
        self._cov_caveat_warn = CoverageCaveat(QC_Call.WARN)
        self._cov_caveat_fail = CoverageCaveat(QC_Call.FAIL)

    def test_constructor_ok(self):
        self.assertEquals(self._cov_caveat_ok._action, Caveat.UNCHANGED)

    def test_constructor_warn(self):
        self.assertEquals(self._cov_caveat_warn._action, Caveat.NON_POSITIVE_TO_EB)

    def test_constructor_fail(self):
        self.assertEquals(self._cov_caveat_fail._action, Caveat.ALL_TO_EB)

    def test_setting_all_to_eb_ok(self):
        self.assertFalse(self._cov_caveat_ok.setting_all_to_eb())

    def test_setting_all_to_eb_warn(self):
        self.assertFalse(self._cov_caveat_warn.setting_all_to_eb())

    def test_setting_all_to_eb_fail(self):
        self.assertTrue(self._cov_caveat_fail.setting_all_to_eb())

    def test_setting_non_positive_to_eb_ok(self):
        self.assertFalse(self._cov_caveat_ok.setting_non_positive_to_eb())

    def test_setting_non_positive_to_eb_warn(self):
        self.assertTrue(self._cov_caveat_warn.setting_non_positive_to_eb())

    def test_setting_non_positive_to_eb_fail(self):
        self.assertFalse(self._cov_caveat_fail.setting_non_positive_to_eb())


class TestPurityCaveat(unittest.TestCase):
    def setUp(self):
        self._purity_caveat_ok = PurityCaveat(QC_Call.OK)
        self._purity_caveat_fail = PurityCaveat(QC_Call.FAIL)

    def test_constructor_ok(self):
        self.assertEquals(self._purity_caveat_ok._action, Caveat.UNCHANGED)

    def test_constructor_warn(self):
        with self.assertRaises(ValueError):
            purity_caveat_warn = PurityCaveat(QC_Call.WARN)

    def test_constructor_fail(self):
        self.assertEquals(self._purity_caveat_fail._action, Caveat.NON_POSITIVE_TO_EB)


class TestContaminationCaveat(unittest.TestCase):
    def setUp(self):
        self._contamination_caveat_ok = ContaminationCaveat(QC_Call.OK)
        self._contamination_caveat_warn = ContaminationCaveat(QC_Call.WARN)
        self._contamination_caveat_fail = ContaminationCaveat(QC_Call.FAIL)

    def test_constructor_ok(self):
        self.assertEquals(self._contamination_caveat_ok._action, Caveat.UNCHANGED)

    def test_constructor_warn(self):
        self.assertEquals(self._contamination_caveat_warn._action, Caveat.ALL_TO_EB)

    def test_constructor_fail(self):
        self.assertEquals(self._contamination_caveat_fail._action, Caveat.ALL_TO_EB)
