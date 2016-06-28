# -*- coding: utf-8 -*-

from reportgen.reporting.features import DatesReport
import util


class ReportMetadata(object):
    '''
    metadata for a single sample analysis report
    '''

    def __init__(self):
        self._personnummer = None
        self._blood_sample_ID = None
        self._tumor_sample_ID = None
        self._blood_sample_date = None
        self._tumor_sample_date = None
        self._return_addresses = None

    def set_pnr(self, pnr):
        self._personnummer = pnr

    def set_blood_sample_ID(self, blood_sample_ID):
        self._blood_sample_ID = blood_sample_ID

    def set_blood_referral_ID(self, blood_referral_ID):
        self._blood_referral_ID = blood_referral_ID

    def set_blood_sample_date(self, blood_sample_date):
        self._blood_sample_date = blood_sample_date

    def set_tumor_sample_ID(self, tumor_sample_ID):
        self._tumor_sample_ID = tumor_sample_ID

    def set_tumor_sample_date(self, tumor_sample_date):
        self._tumor_sample_date = tumor_sample_date

    def set_tumor_referral_ID(self, tumor_referral_ID):
        self._tumor_referral_ID = tumor_referral_ID

    def set_return_addresses(self, addresses):
        self._return_addresses = addresses

    def get_name(self):
        return "Report Metadata"

    # FIXME: I don't like these two methods as the hard-coded
    # keys seem to represent duplication of data.
    def to_dict(self):
        return {"personnummer": self._personnummer,
                "blood_sample_ID": self._blood_sample_ID,
                "blood_referral_ID": self._blood_referral_ID,
                "blood_sample_date": self._blood_sample_date,
                "tumor_sample_ID": self._tumor_sample_ID,
                "tumor_referral_ID": self._tumor_referral_ID,
                "tumor_sample_date": self._tumor_sample_date,
                "return_addresses": self._return_addresses}

    def get_blood_sample_id(self):
        return self._blood_sample_id

    def get_tumor_sample_id(self):
        return self._tumor_sample_id

    def get_blood_sample_date(self):
        return self._blood_sample_date

    def get_tumor_sample_date(self):
        return self._tumor_sample_date
