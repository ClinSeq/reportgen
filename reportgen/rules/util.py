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


def extract_qc_call(qc_json_file):
    """
    Extract the various qc calls from the specified JSON file.

    :param qc_json_file: QC JSON filename
    :return: The QC call extracted from the input files.
    """

    # FIXME: Add JSON schema validation here.
    if qc_json_file != None:
        return json.load(qc_json_file)["CALL"]
    else:
        return None