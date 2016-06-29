# -*- coding: utf-8 -*-

import re
import openpyxl

from reportgen.reporting.metadata import ReportMetadata
from reportgen.rules.general import AlterationClassification

from referralmanager.cli.models.referrals import AlasccaBloodReferral, AlasccaTissueReferral

from sqlalchemy import or_

def id_valid(id_string):
    '''Checks an input blood or tumor ID for validity.'''

    # Valid IDs must comprise exactly eight digits in [0-9]:
    if re.match("^[0-9]+$", id_string) != None:
        return True
    else:
        return False


def get_addresses(id2addresses, ids):
    for id in ids:
        if not id2addresses.has_key(id):
            raise ValueError("Address ID {} is not in id2addresses.".format(id))

    return reduce(lambda list1, list2: list1 + list2, map(lambda id: id2addresses[id], ids))


class AddressFileParseException(Exception):
    pass


def parse_address_table(address_table_filename):
    id2addresses = {}

    # NOTE: Using custom csv parsing code here, as it seems ridiculous to import
    # pandas to do rudimentary parsing of one small csv file.
    with open(address_table_filename) as address_table_file:
        currline = address_table_file.readline().strip("\n")
        elems = currline.split("\t")
        if not elems[0] == "Nr":
            raise AddressFileParseException("Invalid header line for address table:\n" + currline)
        currline = address_table_file.readline()
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
            currline = address_table_file.readline()

    # FIXME: The hospital "id" value should be an int according to Daniel's
    # schema for AlasccaBloodReferral and AlasccaTissueReferral objects, but here
    # it must be a string in order to be used as a key in hashing. This is a trivial
    # problem but need to figure out a good solution.
    return id2addresses


def retrieve_report_metadata(blood_sample_ID, tissue_sample_ID, session, id2addresses):
    '''Returns a ReportMetadata object containing the metadata information to
    include in a report for a paired blood and tumor sample.

    id2addresses is a dictionary with address ID keys and address array values.'''

    # Retrieve the relevant records from the tables clinseqalascca.bloodref and
    # clinseqalascca.tissueref, by issuing queries with the input database
    # connection...

    query1 = session.query(AlasccaBloodReferral).filter(or_(AlasccaBloodReferral.barcode1 == blood_sample_ID,
                                                        AlasccaBloodReferral.barcode2 == blood_sample_ID,
                                                        AlasccaBloodReferral.barcode3 == blood_sample_ID))
    result = query1.all()
    if not len(result) == 1:
        raise ValueError("Query does not yield a single unique entry: " + blood_sample_ID)
    blood_ref = result[0]

    query2 = session.query(AlasccaTissueReferral).filter(or_(AlasccaTissueReferral.barcode1 == tissue_sample_ID,
                                                        AlasccaTissueReferral.barcode2 == tissue_sample_ID))
    result = query2.all()
    if not len(result) == 1:
        raise ValueError("Query does not yield a single unique entry: " + tissue_sample_ID)
    tissue_ref = result[0]

    # Do a sanity check that the personnummer is the same from both the `
    # and tumor ID. Exit and report an error if this is not the case:
    if not blood_ref.pnr == tissue_ref.pnr:
        raise ValueError("Blood sample personnummer does not match tissue sample personnummer.")

    # Convert dates to strings:
    blood_date_str = str(blood_ref.collection_date)
    tumor_date_str = str(tissue_ref.collection_date)

    # Obtain the address information for those two referrals:
    return_addresses = get_addresses(id2addresses, list({str(blood_ref.hospital_code), str(tissue_ref.hospital_code)}))

    # Generate a ReportMetadata object, and specify the extracted fields to the
    # relevant setter methods:
    output_metadata = ReportMetadata()
    output_metadata.set_pnr(blood_ref.pnr)

    output_metadata.set_blood_sample_ID(blood_sample_ID)
    output_metadata.set_blood_referral_ID(blood_ref.crid)
    output_metadata.set_blood_sample_date(blood_date_str)

    output_metadata.set_tumor_sample_ID(tissue_sample_ID)
    output_metadata.set_tumor_referral_ID(tissue_ref.crid)
    output_metadata.set_tumor_sample_date(tumor_date_str)

    output_metadata.set_return_addresses(return_addresses)

    return output_metadata


def extract_mutation_spreadsheet_contents(spreadsheet_filename):
    # Break each row up, generating a data structure representing
    # the spreadsheet...

    # Use openpyxl to parse the input file:
    workbook = openpyxl.load_workbook(filename=spreadsheet_filename)
    mutation_table = workbook.get_sheet_by_name("MutationTable")

    # Get the initial rows containing data...
    rows_of_interest = []
    row_iter = mutation_table.iter_rows()

    # Skip over the first header row:
    curr_row = row_iter.next()

    for curr_row in row_iter:
        if curr_row[0].value != None:
            rows_of_interest.append(curr_row)

    extracted_content = []
    for row in rows_of_interest:
        consequences = row[0].value.split(",")
        symbol = row[1].value
        gene_ID = row[2].value  # Not currently used.
        transcript_ID = row[3].value
        amino_acid_changes = []
        if row[4].value != None:
            amino_acid_changes = row[4].value.split(",")
        flag = row[5].value
        extracted_content.append([consequences, symbol, gene_ID, transcript_ID,
                                 amino_acid_changes, flag])

    return extracted_content


def parse_mutation_table(spreadsheet_filename):
    '''Parses a given excel spreadsheet, extracting mutation classification
    rows from the mutation table. Returns a dictionary of gene symbol to
    classification.'''

    spreadsheet_contents = extract_mutation_spreadsheet_contents(spreadsheet_filename)

    gene_symbol2classifications = {}

    for row in spreadsheet_contents:
        # Extract consequence set, symbol, geneID, transcriptID, amino
        # acid change set, and flag from the current row:
        consequences = row[0]
        symbol = row[1]
        gene_ID = row[2]
        transcript_ID = row[3]
        amino_acid_changes = row[4]
        flag = row[5]

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
