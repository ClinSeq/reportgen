'''
Created on Dec 1, 2015

@author: thowhi
'''

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

        # Retrieve all relevant items from the report json object...

        # Pi3k pathway status string:
        # XXX

        # MSI status string:
        # XXX

        # Status tuples for BRAF, KRAS and NRAS:
        # XXX

        # Instantiate the relevant report elements, derived from the
        # information retrieved above:
        self.initial_comment = reports.InitialComment(self.report_metadata.blood_sample_id, self.report_metadata.tumor_sample_id, self.report_metadata.blood_sample_date, self.report_metadata.tumor_sample_date)
        self.pi3k_pathway_report = reports.Pi3kPathwayReport(pi3k_status)
        self.msi_report = reports.MsiReport(msi_status)
        self.msi_report = reports.MsiReport(msi_status)


class ReportFeature(object):
    '''
    '''

    def __init__(self, metadataJSON):
        '''
        '''


class Pick3caReport(object):
    '''
    '''

    def __init__(self, metadataJSON):
        '''
        '''


class MsiReport(object):
    '''
    '''

    def __init__(self, metadataJSON):
        '''
        '''


class OtherInfoAlasccaReport(object):
    '''
    '''

    def __init__(self, metadataJSON):
        '''
        '''






















































