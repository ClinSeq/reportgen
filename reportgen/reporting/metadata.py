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

    def to_dict(self):
        return {"personnnummer": self._personnummer,
                "blood_sample_ID": self._blood_sample_ID,
                "blood_referral_ID": self._blood_referral_ID,
                "blood_sample_date": self._blood_sample_date,
                "tumor_sample_ID": self._tumor_sample_ID,
                "tumor_referral_ID": self._tumor_referral_ID,
                "tumor_sample_date": self._tumor_sample_date,
                "return_addresses:": self._return_addresses}

    def set_from_dict(self, metadata_dict):
        '''
        Extracts the metadata fields from an input JSON object.
        '''

        # FIXME: Inconsistent use of "set_from_dict" for the report metadata
        # compared with the report feature concrete classes. Not sure whether
        # to unify these somehow.

        # FIXME: Check the fields for validty and report ValueError if not valid.

        self._personnummer = metadata_dict["personnnummer"]
        self._blood_sample_id = metadata_dict["blood_sample_ID"]
        self._blood_referral_ID = metadata_dict["blood_referral_ID"]
        self._blood_sample_date = metadata_dict["blood_sample_date"]
        self._tumor_sample_id = metadata_dict["tumor_sample_ID"]
        self._tumor_sample_date = metadata_dict["tumor_sample_date"]
        self._tumor_referral_ID = metadata_dict["tumor_referral_ID"]
        self._return_addresses = metadata_dict["return_addresses"]

    def generate_dates_report(self):
        dates_report = DatesReport(self._blood_sample_id, self._tumor_sample_id,
                                   self._blood_sample_date, self._tumor_sample_date,
                                   self._blood_referral_ID, self._tumor_referral_ID)
        return dates_report

    def get_blood_sample_id(self):
        return self._blood_sample_id

    def get_tumor_sample_id(self):
        return self._tumor_sample_id

    def get_blood_sample_date(self):
        return self._blood_sample_date

    def get_tumor_sample_date(self):
        return self._tumor_sample_date

    def make_latex_strings(self, doc_format):
        '''
        Returns an array of latex tables, one for each of the separate return
        addresses.
        '''
        latex_tables = []

        # FIXME: Hard-coding keys in the dictionary _return_addresses here.
        # This seems nasty. Perhaps use some "address" class instead of
        # a dictionary, but then need to fix json/dict conversion for that
        # object:
        for address in self._return_addresses:
            attn = address["attn"]
            line1 = address["line1"]
            line2 = address["line2"]
            line3 = address["line3"]
            curr_latex_table = u'''\\begin{tabular}{ l l }
\\multirow{2}{10.5cm}{\\begin{tabular}{l}Personnummer %s \\\\
Analys genomförd %s\\\\
\\end{tabular}} &
\\multirow{4}{7cm}{
\\begin{tabular}{l}%s\\\\
%s\\\\
%s\\\\
%s\\\\
\\end{tabular}} \\\\
 & \\\\
 & \\\\
 & \\\\
\\end{tabular}''' % (util.format_personnummer(self._personnummer),
                     self._tumor_sample_date, attn, line1, line2, line3)
            latex_tables.append(curr_latex_table)

        return latex_tables