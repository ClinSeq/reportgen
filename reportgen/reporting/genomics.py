# -*- coding: utf-8 -*-

import datetime


class GenomicReport(object):
    '''
    '''

    def __init__(self, report_json, metadata_json, doc_format, jinja_env, jinja_template):
        # Save the metadata and report json objects:
        self._report_json = report_json
        self._metadata_json = metadata_json

        # Store the document format object:
        self._doc_format = doc_format

        self.jinja_env = jinja_env
        self.jinja_template = jinja_template

    def make_latex(self):
        return self.jinja_template.render(metaJSON=self._metadata_json,
                                          genomicJSON=self._report_json,
                                          reportDate=unicode(datetime.date.today()),
                                          docFormat=self._doc_format)
