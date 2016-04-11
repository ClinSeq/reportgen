# -*- coding: utf-8 -*-

import re

import openpyxl

from reportgen.reporting.metadata import ReportMetadata
from reportgen.rules.general import AlterationClassification


def connect_clinseq_db(db_config_dict):
    # Retrieve the driver, database name, servername, username, and password,
    # for establishing a connection to MSSQL using ODBC:
    driver_name = db_config_dict["driver"]
    server = db_config_dict["server"]
    database = db_config_dict["database"]
    uid = db_config_dict["uid"]
    password = db_config_dict["password"]
    return pyodbc.connect("DRIVER=%s;SERVER=%s;DATABASE=%s;UID=%s;PWD=%s" % \
                          (driver_name, server, database, uid, password))


def id_valid(id_string):
    '''Checks an input blood or tumor ID for validity.'''

    # Valid IDs must comprise exactly eight digits in [0-9]:
    if re.match("^[0-9]{8}$", id_string) != None:
        return True
    else:
        return False


def retrieve_report_metadata(blood_sample_ID, tissue_sample_ID, connection):
    '''Returns a ReportMetadata object containing the metadata information to
    include in a report for a paired blood and tumor sample.'''

    # Retrieve the relevant records from the tables clinseqalascca.bloodref and
    # clinseqalascca.tissueref, by issuing queries with the input database
    # connection...

    cursor = connection.cursor()

    query1 = '''SELECT pnr, collection_date FROM
clinseqalascca.bloodref where sampleid = '%s' ''' % blood_sample_ID

    cursor.execute(query1)
    matching_rows = cursor.fetchall()

    if not len(matching_rows) == 1:
        raise ValueError("Blood sample ID does not yield a single unique entry: "
                         + blood_sample_ID)

    (blood_pnr, blood_date) = tuple(matching_rows[0])

    query2 = '''SELECT pnr, collection_date FROM
clinseqalascca.tissueref where sampleid_1 = '%s' or sampleid_2 = '%s' or
sampleid_3 = '%s' or sampleid_4 = '%s' or sampleid_5 = '%s' or sampleid_6 =
'%s' or sampleid_7 = '%s' or sampleid_8 = '%s' ''' % tuple([tissue_sample_ID] * 8)

    cursor.execute(query2)
    matching_rows = cursor.fetchall()

    if not len(matching_rows) == 1:
        raise ValueError("Tissue sample ID does not yield a single unique entry: "
                         + tissue_sample_ID)

    (tissue_pnr, tissue_date) = tuple(matching_rows[0])

    # Do a sanity check that the personnnummer is the same from both the blood
    # and tumor ID. Exit and report an error if this is not the case:
    if not blood_pnr == tissue_pnr:
        raise ValueError("Blood sample personnummer does not match tissue sample personnummer.")

    # Convert dates to strings:
    blood_date_str = str(blood_date)
    tumor_date_str = str(tissue_date)

    # Generate a ReportMetadata object, and specify the extracted fields to the
    # relevant setter methods:
    output_metadata = ReportMetadata()
    output_metadata.set_pnr(blood_pnr)
    output_metadata.set_blood_sample_ID(blood_sample_ID)
    output_metadata.set_blood_sample_date(blood_date_str)
    output_metadata.set_tumor_sample_ID(tissue_sample_ID)
    output_metadata.set_tumor_sample_date(tumor_date_str)

    return output_metadata


def extract_feature(genomics_dict, reportFeatureClassname):
    feature_name = reportFeatureClassname.get_name()
    feature_contents = genomics_dict[feature_name]

    extracted_feature = reportFeatureClassname()
    extracted_feature.set_from_dict(feature_contents)
    return extracted_feature


def parse_mutation_table(spreadsheet_filename):
    '''Parses a given excel spreadsheet, extracting mutation classification
    rows from the mutation table. Returns a dictionary of gene symbol to
    classification.'''

    # Break each row up and add it to the above dictionary of gene
    # decisions...

    # Use openpyxl to parse the input file:
    workbook = openpyxl.load_workbook(filename=spreadsheet_filename)
    mutation_table = workbook.get_sheet_by_name("MutationTable")

    # Get the initial rows containing data...
    rows_of_interest = []
    row_iter = mutation_table.iter_rows()

    # FIXME: This excel spreadsheet parsing may not be robust enough...
    # Skip over the first header row:
    curr_row = row_iter.next()
    for curr_row in row_iter:
        if curr_row[0].value != None:
            rows_of_interest.append(curr_row)

    gene_symbol2classifications = {}

    for row in rows_of_interest:
        # Extract consequence set, symbol, geneID, transcriptID, amino
        # acid change set, and flag from the current row:
        consequences = row[0].value.split(",")
        symbol = row[1].value
        gene_ID = row[2].value  # Not currently used.
        transcript_ID = row[3].value
        amino_acid_changes = []
        if row[4].value != None:
            amino_acid_changes = row[4].value.split(",")
        flag = row[5].value

        curr_classification = \
            AlterationClassification(symbol, consequences, transcript_ID,
                                     amino_acid_changes, flag)

        if not gene_symbol2classifications.has_key(symbol):
            gene_symbol2classifications[symbol] = []

        gene_symbol2classifications[symbol].append(curr_classification)

    return gene_symbol2classifications


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


'''$\\begin{array}{ p{1cm} p{10cm} }
  \\toprule
  \\includegraphics{%s} & Mutation klass A, patienten kan randomiseras \\tabularnewline
  \\includegraphics{%s} & Mutation klass B, patienten kan randomiseras \\tabularnewline
  \\tabularnewline
  \\includegraphics{%s} & Inga mutationer, patienten kan \emph{ej} randomiseras \\tabularnewline
  \\includegraphics{%s} & Ej utförd/Ej bedömbar, patienten kan \emph{ej} randomiseras \\tabularnewline
  \\bottomrule
\\end{array}$'''


