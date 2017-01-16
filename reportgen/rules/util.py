import json


class FeatureStatus:
    """
    Enumeration of different possible generic genomic item statuses.
    """

    MUTATED = "Mutated"
    NOT_MUTATED = "Not mutated"
    NOT_DETERMINED = "Not determined"


class QC_Call:
    """
    Enumeration of different possible QC call values.
    """

    OK = "OK"
    WARN = "WARN"
    FAIL = "FAIL"


def extract_qc_calls(purity_json, tumor_cov_json, normal_cov_json, contam_json):
    """
    Extract the various qc calls from the specified JSON files.

    :param purity_json: Purity call JSON file.
    :param tumor_cov_json: Coverage call JSON file for tumour.
    :param normal_cov_json: Coverage call JSON file for normal.
    :param contam_json: Contamination call JSON file.
    :return: A tuple of the four QC calls, with None for a given QC call if it's JSON file was none.
    """

    purity_call = None
    if purity_json is not None:
        purity_call = json.load(purity_json)["CALL"]

    tumor_cov_call = None
    if tumor_cov_json is not None:
        tumor_cov_call = json.load(tumor_cov_json)["CALL"]

    normal_cov_call = None
    if normal_cov_json is not None:
        normal_cov_call = json.load(normal_cov_json)["CALL"]

    contam_call = None
    if contam_json is not None:
        contam_call = json.load(contam_json)["CALL"]

    return purity_call, tumor_cov_call, normal_cov_call, contam_call
