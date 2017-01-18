from reportgen.reporting.features import MsiReport
from reportgen.rules.util import FeatureStatus


class MsiStatusRule:
    '''A rule for generating an MSI status class.'''

    # FIXME: At some point I need to make these thresholds settable
    # somewhere. Currently hard-coding them here.
    MIN_TOTAL_SITES = 50
    PERCENT_MSI_H = 5

    def __init__(self, msi_status):
        self.msi_status = msi_status

    def apply(self):

        status_string = None
        if self.msi_status.get_total() < self.MIN_TOTAL_SITES:
            status_string = FeatureStatus.NOT_DETERMINED
        else:
            if self.msi_status.get_percent() > self.PERCENT_MSI_H:
                status_string = MsiReport.MSI
            else:
                status_string = MsiReport.MSS

        report = MsiReport()
        report.msi_status = status_string
        return report