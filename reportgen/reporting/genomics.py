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


class ReportCompiler:
    '''Compiles a genomic report given input genomic features and rules. Can then
    output a JSON formatted representation of the report. NOTE: There is no
    alascca report subtype: The particular type of report is determined by
    the composition of rules the compiler is using to generate corresponding
    report features.'''

    def __init__(self, rules):
        self._rules = rules

        # This will contain the report features once they have been generated
        # by applying the rules:
        self._name2feature = {}

    def extract_features(self):
        # Apply each rule, generating a corresponding report feature, which is
        # then stored in this object:
        for curr_rule in self._rules:
            curr_feature = curr_rule.apply()

            # Store the current feature under this feature's name:
            self._name2feature[curr_feature.get_name()] = curr_feature

    def to_dict(self):
        output_dict = {}
        for name in self._name2feature.keys():
            feature = self._name2feature[name]
            output_dict[name] = feature.to_dict()

        return output_dict