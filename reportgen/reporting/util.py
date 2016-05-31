# -*- coding: utf-8 -*-

import pdb, re
import openpyxl, pyodbc

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
    if re.match("^[0-9]+$", id_string) != None:
        return True
    else:
        return False


def query_unique_row(cursor, query_str):
    cursor.execute(query_str)
    matching_rows = cursor.fetchall()

    if not len(matching_rows) == 1:
        raise ValueError("Query does not yield a single unique entry: "
                         + query_str)

    return(tuple(matching_rows[0]))


def get_addresses(id2addresses, ids):
    for id in ids:
        if not id2addresses.has_key(id):
            raise ValueError("Address ID {} is not in id2addresses.".format(id))

    return [id2addresses[id] for id in ids]


class AddressFileParseException(Exception):
    pass


def parse_address_table(address_table_filename):
    id2addresses = {}

    # NOTE: Using custom csv parsing code here, as it seems ridiculous to import
    # pandas to do rudimentary parsing of one small csv file.
    with open(address_table_filename) as address_table_file:
        currline = address_table_filename.readline().strip("\n")
        elems = currline.split("\t")
        if not elems[0] == "Nr":
            raise AddressFileParseException("Invalid header line for address table:\n" + currline)
        currline = address_table_filename.readline()
        while currline != "":
            elems = currline.strip().split("\t")
            if not len(elems) == 7:
                raise AddressFileParseException("Invalid line for address table:\n" + currline)
            id = elems[0]
            attn = elems[2]
            address_line1 = elems[4]
            address_line2 = elems[5]
            address_line3 = elems[6]
            if not id2addresses.has_key(id):
                id2addresses[id] = []
            id2addresses[id].append({"attn": attn,
                                     "line1": address_line1,
                                     "line2": address_line2,
                                     "line3": address_line3})


def retrieve_report_metadata(blood_sample_ID, tissue_sample_ID, connection, id2addresses):
    '''Returns a ReportMetadata object containing the metadata information to
    include in a report for a paired blood and tumor sample.

    id2addresses is a dictionary with address ID keys and address array values.'''

    # Retrieve the relevant records from the tables clinseqalascca.bloodref and
    # clinseqalascca.tissueref, by issuing queries with the input database
    # connection...

    cursor = connection.cursor()

    query1 = '''SELECT pnr, crid, collection_date FROM
clinseqalascca.bloodref where barcode1 = '%s' or barcode2 = '%s' or barcode3 = '%s' ''' % \
             (blood_sample_ID, blood_sample_ID, blood_sample_ID)

    (blood_pnr, blood_referral_ID, blood_date) = query_unique_row(connection, query1)

    query2 = '''SELECT pnr, crid, collection_date FROM
clinseqalascca.tissueref where barcode1 = '%s' or barcode2 = '%s' ''' % (tissue_sample_ID, tissue_sample_ID)

    (tissue_pnr, tissue_referral_ID, tissue_date) = query_unique_row(connection, query2)

    # Do a sanity check that the personnnummer is the same from both the blood
    # and tumor ID. Exit and report an error if this is not the case:
    if not blood_pnr == tissue_pnr:
        raise ValueError("Blood sample personnummer does not match tissue sample personnummer.")

    # Convert dates to strings:
    blood_date_str = str(blood_date)
    tumor_date_str = str(tissue_date)

    # Obtain the address information for those two referrals:
    return_addresses = get_addresses(id2addresses, list({blood_referral_ID, tissue_referral_ID}))

    # Generate a ReportMetadata object, and specify the extracted fields to the
    # relevant setter methods:
    output_metadata = ReportMetadata()
    output_metadata.set_pnr(blood_pnr)

    output_metadata.set_blood_sample_ID(blood_sample_ID)
    output_metadata.set_blood_referral_ID(blood_referral_ID)
    output_metadata.set_blood_sample_date(blood_date_str)

    output_metadata.set_tumor_sample_ID(tissue_sample_ID)
    output_metadata.set_tumor_referral_ID(tissue_referral_ID)
    output_metadata.set_tumor_sample_date(tumor_date_str)

    output_metadata.set_return_addresses(return_addresses)

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


def format_personnummer(personnummer):
    assert re.match("^[0-9]{12}$", personnummer)
    return personnummer[2:8] + "-" + personnummer[8:]


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


