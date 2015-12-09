# -*- coding: utf-8 -*-

'''
Created on Dec 1, 2015

@author: thowhi
'''

import collections


class ReportMetadata(object):
    '''
    metadata for a single sample analysis report
    '''

    def __init__(self, metadataJSON):
        '''
        Extracts the metadata fields from an input JSON object.
        '''

    def make_latex(self):
        '''
        Generate a table to display relevant metadata fields:
        '''

        # XXX


class GenomicReport(object):
    '''
    '''

    def __init__(self, metadata_json, report_json, doc_format):
        # Save the metadata and report json objects:
        self._metadata_json = metadata_json
        self._report_json = report_json

        # Generate a representation of the report metadata:
        self._metadata = metadata_json

        # Store the document format object:
        self._doc_format = doc_format

    def get_metadata(self):
        return self._metadata

    def get_metadata_json(self):
        return self._metadata_json

    def get_report_json(self):
        return self._report_json

    def get_doc_format(self):
        return self._doc_format


class AlasccaReport(GenomicReport):
    '''An ALASCCA project sample genomic status report. Can be used to generate
    a latex document displaying the report.
    '''

    def __init__(self, metadata_json, report_json, doc_format):
        super(GenomicReport, self).__init__()

        # Retrieve all relevant items from the report json object, checking
        # values as we proceed...

        # Pi3k pathway status string:
        pi3k_pathway_string = report_json["PI3K_pathway"]
        if not pi3k_pathway_string in Pi3kPathwayReport.VALID_STRINGS:
            raise ValueError("Invalid PI3K pathway string: " + pi3k_pathway_string)

        # MSI status string:
        msi_status_string = report_json["MSI_status"]
        if not msi_status_string in MsiReport.VALID_STRINGS:
            raise ValueError("Invalid MSI status string: " + msi_status_string)

        # Extract status tuples for BRAF, KRAS and NRAS:
        other_mutation_statuses = collections.OrderedDict()
        braf_status = report_json["BRAF"]
        if (not type(braf_status) is list) or (len(braf_status) != 2) or \
            (not braf_status[0] in OtherMutationsReport.VALID_STRINGS):
            raise ValueError("Invalid BRAF status: ", braf_status)
        other_mutation_statuses["BRAF"] = tuple(braf_status)

        kras_status = report_json["KRAS"]
        if (not type(braf_status) is list) or (len(braf_status) != 2) or \
            (not kras_status[0] in OtherMutationsReport.VALID_STRINGS):
            raise ValueError("Invalid KRAS status: ", braf_status)
        other_mutation_statuses["KRAS"] = tuple(kras_status)

        nras_status = report_json["NRAS"]
        if (not type(braf_status) is list) or (len(braf_status) != 2) or \
            (not nras_status[0] in OtherMutationsReport.VALID_STRINGS):
            raise ValueError("Invalid NRAS status: ", braf_status)
        other_mutation_statuses["NRAS"] = tuple(nras_status)

        # Instantiate the relevant report elements, derived from the
        # information retrieved above:
        report_metadata = self.get_metadata()
        self._initial_comment = InitialComment(report_metadata.blood_sample_id,
                                              report_metadata.tumor_sample_id,
                                              report_metadata.blood_sample_date,
                                              report_metadata.tumor_sample_date)

        self._pi3k_pathway_report = Pi3kPathwayReport(pi3k_pathway_string)
        self._msi_report = MsiReport(msi_status_string)
        self._other_mutations_report = OtherMutationsReport(other_mutation_statuses)

    def make_latex(self):
        return self._initial_comment.make_latex(self._doc_format)


class ReportFeature(object):
    '''
    ReportFeature abstract class.
    '''

    def __init__(self):
        '''
        '''

    def make_latex(self, doc_format):
        return u"subsubsection*{" + self.make_title(doc_format) + "}\n" + self.make_content_body(doc_format)

    def make_content_body(self, doc_format):
        '''All implementing classes must implement a function for generating
        a string containing latex code for the content body.'''

    def make_title(self, doc_format):
        '''All implementing classes must implement a function for generating
        a string containing latex code for a title.'''


class InitialComment(ReportFeature):
    '''
    '''

    def __init__(self, blood_sample_id, tumor_sample_id, blood_sample_date, tumor_sample_date):
        super(ReportFeature).__init__()
        self._blood_sample_id = blood_sample_id
        self._tumor_sample_id = tumor_sample_id
        self._blood_sample_date = blood_sample_date
        self._tumor_sample_date = tumor_sample_date

    def make_title(self, doc_format):
        if doc_format.get_language() == doc_format.ENGLISH:
            return u'''Other information'''
        else:
            assert doc_format.get_language() == doc_format.SWEDISH
            return u'''Övriga information'''

    def make_content_body(self, doc_format):
        if doc_format.get_language() == doc_format.ENGLISH:
            return u'''Analysis completed for blood sample %d taken %s and tumor sample %d taken %s''' % \
                (self._blood_sample_id, self._blood_sample_date,
                self._tumor_sample_id, self._tumor_sample_date)
        else:
            assert doc_format.get_language() == doc_format.SWEDISH
            return u'''Analys genomförd för blodprov %d taget %s och tumörprov %d taget %s''' % \
                (self._blood_sample_id, self._blood_sample_date,
                self._tumor_sample_id, self._tumor_sample_date)


class Pi3kPathwayReport(ReportFeature):
    '''
    '''

    VALID_STRINGS = ["Mutation class A", "Mutation class B", "No mutation"]

    def __init__(self, pi3k_pathway_string):
        self._pi3k_pathway_status = pi3k_pathway_string


class MsiReport(ReportFeature):
    '''
    '''

    VALID_STRINGS = ["MSS/MSI-L", "MSI-H", "Not determined"]

    def __init__(self, msi_status_string):
        self._msi_status = msi_status_string


class OtherMutationsReport(ReportFeature):
    '''
    '''

    VALID_STRINGS = ["Mutation", "No mutation", "Not determined"]

    def __init__(self, mutation_statuses):
        self._mutation_statuses = mutation_statuses


class ClinicalRecommendationsReport(ReportFeature):
    '''
    '''

    def __init__(self, braf_status, msi_status):
        self._braf_status = braf_status
        self._msi_status = msi_status


class FooterInfoAlasccaReport(ReportFeature):
    '''
    '''

    def __init__(self, metadataJSON):
        '''
        '''






















































