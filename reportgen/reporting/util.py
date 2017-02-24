# -*- coding: utf-8 -*-

import re

import openpyxl

from reportgen.rules.general import AlterationClassification


def id_valid(id_string):
    '''Checks an input blood or tumor ID for validity.'''

    # Valid IDs must comprise exactly eight digits in [0-9]:
    if re.match("^[0-9]+$", id_string) != None:
        return True
    else:
        return False


def get_addresses(id2addresses, ids):
    '''Retrieves the unique set of return addresses for the given IDs, from
    the id2addresses dictionary.'''

    for id in ids:
        if not id2addresses.has_key(id):
            raise ValueError("Address ID {} is not in id2addresses.".format(id))

    all_addresses = reduce(lambda list1, list2: list1 + list2, map(lambda id: id2addresses[id], ids))
    all_addresses.sort()

    # O(N^^2) algorithm, but ok since list of addresses will be small:
    def reduce_pair(curr_list, next_item):
        if next_item not in curr_list:
            curr_list.append(next_item)
        return curr_list

    return reduce(reduce_pair, all_addresses, [])


class AddressFileParseException(Exception):
    pass


def parse_address_table(address_table_file):
    id2addresses = {}

    lines = address_table_file.readlines()

    header_line = lines[0].strip("\n")

    elems = header_line.split("\t")
    if not elems[0] == "Nr":
        raise AddressFileParseException("Invalid header line for address table:\n" + header_line)

    for data_line in lines[1:]:
        elems = data_line.strip().split("\t")
        if not len(elems) == 7:
            raise AddressFileParseException("Invalid line for address table:\n" + data_line)
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

    # FIXME: The hospital "id" value should be an int according to Daniel's
    # schema for AlasccaBloodReferral and AlasccaTissueReferral objects, but here
    # it must be a string in order to be used as a key in hashing. This is a trivial
    # problem but need to figure out a good solution.
    return id2addresses


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
