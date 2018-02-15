# -*- coding: utf-8 -*-
import sqlalchemy
import pdb

from referralmanager.cli.models.referrals import AlasccaBloodReferral, AlasccaTissueReferral

from reportgen.reporting.util import get_addresses

def query_database(sample_ID, referral_type, session):
    '''Queries the given database wih the given referral type and sample ID.
    If one and only one record is found, the data for it is returned.'''

    # Find the barcode attributes for this referral type (different number of barcodes per referral depending on type)
    referral_attributes = dir(referral_type)
    barcode_attributes = filter(lambda x: "barcode" in x, referral_attributes)
    if len(barcode_attributes) == 0:
        raise ValueError("Referral type %s has no barcode attributes" % referral_type.__class__.__name__)
    
    # Perform the query
    query = session.query(referral_type).filter(sqlalchemy.or_(getattr(referral_type, barcode_attr) == sample_ID
                                                               for barcode_attr in barcode_attributes))
    result = query.all()
    
    # Check that there's one and only one record
    if not len(result) == 1:
        raise ValueError("Query does not yield a single unique entry: %d" % int(sample_ID))

    return result[0]


def retrieve_report_metadata(blood_sample_ID, tissue_sample_ID, session, id2addresses):
    '''Returns a ReportMetadata object containing the metadata information to
    include in a report for a paired blood and tumor sample.

    id2addresses is a dictionary with address ID keys and address array values.'''

    # Retrieve the relevant records from the tables clinseqalascca.bloodref and
    # clinseqalascca.tissueref, by issuing queries with the input database
    # connection...
    blood_ref = query_database(blood_sample_ID, AlasccaBloodReferral, session)
    tissue_ref = query_database(tissue_sample_ID, AlasccaTissueReferral, session)

    # Do a sanity check that the personnummer is the same from both the `
    # and tumor ID. Exit and report an error if this is not the case:
    if not blood_ref.pnr == tissue_ref.pnr:
        raise ValueError("Blood sample personnummer does not match tissue sample personnummer.")

    # Convert dates to strings:
    blood_date_str = str(blood_ref.collection_date)
    tumor_date_str = str(tissue_ref.collection_date)

    # Obtain the address information for those two referrals:
    return_addresses = get_addresses(id2addresses, list({str(blood_ref.hospital_code), str(tissue_ref.hospital_code)}))

    # Simply construct a dictionary from the relevant fields:
    output_metadata = {"personnummer": blood_ref.pnr,
                       "blood_sample_ID": blood_sample_ID,
                       "blood_referral_ID": blood_ref.crid,
                       "blood_sample_date": blood_date_str,
                       "tumor_sample_ID": tissue_sample_ID,
                       "tumor_referral_ID": tissue_ref.crid,
                       "tumor_sample_date": tumor_date_str,
                       "return_addresses": return_addresses}

    return output_metadata
