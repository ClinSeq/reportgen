from reportgen.reporting.features import MsiReport
from reportgen.rules.util import FeatureStatus


class MsiStatusRule:
    '''A rule for generating an MSI status class.'''

    # FIXME: At some point I need to make these thresholds settable
    # somewhere. Currently hard-coding them here.
    MIN_TOTAL_SITES = 50
    PERCENT_MSI_LOW_THRESH = 5
    PERCENT_MSI_HIGH_THRESH = 30

    def __init__(self, msi_status):
        self.msi_status = msi_status

    def apply(self):

        if self.msi_status.get_total() < self.MIN_TOTAL_SITES:
            status_string = FeatureStatus.NOT_DETERMINED
        else:
            if self.msi_status.get_percent() > self.PERCENT_MSI_HIGH_THRESH:
                status_string = MsiReport.MSI
            elif self.msi_status.get_percent() < self.PERCENT_MSI_LOW_THRESH:
                status_string = MsiReport.MSS
            else:
                status_string = FeatureStatus.NOT_DETERMINED

        report = MsiReport()
        report.msi_status = status_string
        return report