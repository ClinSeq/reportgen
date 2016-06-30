# -*- coding: utf-8 -*-
from sqlalchemy import or_

from reportgen.reporting.util import get_addresses


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