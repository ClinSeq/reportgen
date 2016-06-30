'''
Created on Dec 1, 2015

@author: thowhi
'''

import json, os, pdb, subprocess, sys, tempfile
import jinja2

from optparse import OptionParser

import reportgen.reporting.genomics
import reportgen.reporting.util
from reportgen.rules.general import AlterationExtractor, MSIStatus

import reportgen.rules.alascca
import reportgen.rules.msi
import reportgen.rules.simple_somatic_mutations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from referralmanager.cli.models.referrals import Base


def compileMetadata():
    description = """usage: %prog [options] <bloodID> <tumorID>\n
Inputs:
- Blood sample ID. NOTE: Sticker ID, not referral ID.
- Tumor sample ID. NOTE: Sticker ID, not referral ID.

Outputs:
- JSON file containing the required fields:
-- personnummer
-- blood_sample_id
-- tumor_sample_id
-- blood_sample_date
-- tumor_sample_date
-- Patient name
-- Doctor name
-- Doctor address fields

FIXME: Currently, the patient name, doctor name, and doctor address will be
hard-coded.
"""

    parser = OptionParser(usage = description)
    parser.add_option("--db_config_file", dest = "db_config_file",
                      default = "/nfs/ALASCCA/clinseq-referraldb-config.json",
                      help = "Configuration file for logging into the " + \
                          "database, including password. Default=[%default]")
    parser.add_option("--address_table_file", dest = "address_table_file",
                      default = "/nfs/ALASCCA/referrals/addresses.csv",
                      help = "File specifying addresses. Default=[%default]")
    parser.add_option("--output", dest = "output_file",
                      default = "MetadataOutput.json",
                      help = "Output location. Default=[%default]")
    parser.add_option("--debug", action="store_true", dest="debug",
                      help = "Debug the program using pdb.")
    (options, args) = parser.parse_args()

    # Parse the input parameters...

    if (options.debug):
        pdb.set_trace()

    # Make sure the required input arguments exist:
    if (len(args) != 2):
        print >> sys.stderr, "WRONG # ARGS: ", len(args)
        parser.print_help()
        sys.exit(1)

    # Check the input IDs:
    blood_sample_ID = args[0]
    if not reportgen.reporting.util.id_valid(blood_sample_ID):
        print >> sys.stderr, "Invalid blood sample ID:", blood_sample_ID
        sys.exit(1)

    tumor_sample_ID = args[1]
    if not reportgen.reporting.util.id_valid(tumor_sample_ID):
        print >> sys.stderr, "Invalid tumor sample ID:", tumor_sample_ID
        sys.exit(1)

    # Establish an sqlalchemy session connecting to the KI biobank database:

    config_dict = None
    try:
        cred_conf = json.load(open(options.db_config_file))
        uri = cred_conf['dburi']
        engine = create_engine(uri, echo=True)
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()
    except Exception, e:
        print >> sys.stderr, "Could not load/parse JSON database config file, " + \
                             options.db_config_file + "."
        sys.exit(1)

    # Open the output file:
    output_file = None
    try:
        output_file = open(options.output_file, 'w')
    except Exception, e:
        print >> sys.stderr, "Could not open output file, " + \
                             options.output_file + "."
        sys.exit(1)

    id2addresses = reportgen.reporting.util.parse_address_table(options.address_table_file)

    # FIXME: Casting the blood and tumor IDs to ints here. Not sure if they should be ints,
    # but even if they are, I'm not sure if the casting should occur here:
    reportMetadata = reportgen.reporting.util.retrieve_report_metadata(int(blood_sample_ID), int(tumor_sample_ID),
                                                                       session, id2addresses)

    # Output the report to a dictionary and write that dictionary to a JSON
    # file:
    metadata_json = reportMetadata.to_dict()

    json.dump(metadata_json, output_file, indent=4, sort_keys=True)
    output_file.close()


def compileAlasccaGenomicReport():
    # Parse the command-line arguments...
    # FIXME: Need to add msi file input too once we've decided on the format for this information.
    # FIXME: ADD MORE PRECISE DESCRIPTION of CNV file ONCE WE HAVE AGREED ON THE FILE FORMAT
    description = """usage: %prog [options] <vcfFile> <cnvFile> <msiFile>\n
Inputs:
- VCF file specifying somatic mutations
- Text file specifying CNVs
- Text file specifying MSI information
- Excel spreadsheet specifying rules regarding how to report colorectal cancer mutations
- Excel spreadsheet specifying rules regarding how to report ALASSCA class

Outputs:
- A JSON file specifying the contents of the genomic status report. FIXME: Link to precise description
of this file's format.
"""

    parser = OptionParser(usage = description)
    parser.add_option("--output", dest = "output_file",
                      default = "GenomicOutput.json",
                      help = "Output location. Default=[%default]")
    parser.add_option("--crcMutationRules", dest = "crc_mutation_rules_file",
                      default = os.path.abspath(os.path.dirname(__file__) + "/assets/COLORECTAL_MUTATION_TABLE.xlsx"),
                      help = "Rules for flagging mutations in colorectal cancer. Default=[%default]")
    parser.add_option("--alasccaMutationRules", dest = "alascca_mutation_rules_file",
                      default = os.path.abspath(os.path.dirname(__file__) + "/assets/ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx"),
                      help = "Rules for determining ALASCCA class status. Default=[%default]")
    parser.add_option("--debug", action="store_true", dest="debug",
                      help = "Debug the program using pdb.")
    (options, args) = parser.parse_args()

    # Parse the input parameters...

    if (options.debug):
        pdb.set_trace()

    # Make sure the required input arguments exist:
    if (len(args) != 3):
        print >> sys.stderr, "WRONG # ARGS: ", len(args)
        parser.print_help()
        sys.exit(1)

    # FIXME: Currently I have no error checking on the opening of the input and output
    # files. Need to implement this.
    vcf_file = open(args[0])
    cnv_file = open(args[1])
    msi_file = open(args[2])

    # Generate a dictionary of AlteredGene objects from the input files:
    alteration_extractor = AlterationExtractor()
    alteration_extractor.extract_mutations(vcf_file)
    # FIXME: Add cnv_file cnv extraction later:
    #alteration_extractor.extract_cnvs(cnv_file)

    symbol2altered_gene = alteration_extractor.to_dict()

    # Extract msi status from an input file too:
    msi_status = MSIStatus()
    msi_status.set_from_file(msi_file)

    crc_mutations_spreadsheet = options.crc_mutation_rules_file
    alascca_class_spreadsheet = options.alascca_mutation_rules_file

    # FIXME/ISSUE:
    # It seems like we should be passing the genomic features to the rule
    # objects when we call ".apply()", and not when we create the actual
    # rule objects. The trouble with this is that another object then
    # needs to keep track of what object should be passed to which rule.
    # Currently, I'll implement it such that the Rule objects are passed
    # the relevant information they need when they are created, so that
    # their ".apply()" methods then accept no arguments.

    # Extract rules from the input excel spreadsheets (zero or one spreadsheet
    # per rule object):
    mutationsRule = reportgen.rules.simple_somatic_mutations.SimpleSomaticMutationsRule(crc_mutations_spreadsheet,
                                                                                        symbol2altered_gene)
    alasccaRule = reportgen.rules.alascca.AlasccaClassRule(alascca_class_spreadsheet,
                                                           symbol2altered_gene)
    msiRule = reportgen.rules.msi.MsiStatusRule(msi_status)

    report_compiler = reportgen.reporting.util.ReportCompiler([mutationsRule, alasccaRule, msiRule])
    report_compiler.extract_features()

    # Set output file according to options:
    json_output_file = open(options.output_file, 'w')

    # Write the genomic report to output in JSON format:
    # FIXME: We may just want toDict instead of toJSON here.
    output_dict = report_compiler.to_dict()
    json.dump(output_dict, json_output_file, indent=4, sort_keys=True)
    json_output_file.close()

    # FIXME: Perhaps need to implement some kind of progress reporting. I normally do this with
    # print statements to sys.stderr, but perhaps we want to write to log files instead?


def writeAlasccaReport():
    # Parse the command-line arguments...
    description = """usage: %prog [options] <reportJSONfile> <metadataJSONfile>\n
Inputs:
- JSON file containing metadata for the sample
- JSON file containing the genomic status report data for the sample
FIXME: Need to agree on a structure for these files and document this somewhere
and then link to that documentation here

Outputs:
- Generates a pdf file displaying the formatted report
"""

    parser = OptionParser(usage = description)
    parser.add_option("--language", dest = "language",
                      default = "Swedish",
                      help = "Language in which the report text will be " + \
                          "generated. One of Swedish or English. Default=[%default]")
    parser.add_option("--output_name", dest = "output_name",
                      default = "Report",
                      help = "Output file name (not including file extension). Default=[%default]")
    parser.add_option("--output_dir", dest = "output_dir",
                      default = ".",
                      help = "Output directory for pdf. Default=[%default]")
    parser.add_option("--fontfamily", dest = "fontfamily",
                      default = "SansSerif",
                      help = "Font in which the report text will be " + \
                          "generated. One of Roman or SansSerif. Default=[%default]")
    parser.add_option("--sansfont", dest = "sansfont",
                      default = "phv",
                      help = "Sans-Serif font to use. " + \
                          "Default=[%default]")
    parser.add_option("--fontsize", dest = "fontsize",
                      default = "10pt",
                      help = "Font size for report text. " + \
                          "Default=[%default]")
    parser.add_option("--margin", dest = "margin",
                      default = "3cm",
                      help = "Top margin size for report. " + \
                          "Default=[%default]")
    parser.add_option("--lmargin", dest = "lmargin",
                      default = "1cm",
                      help = "Left margin size for report. " + \
                          "Default=[%default]")
    parser.add_option("--rmargin", dest = "rmargin",
                      default = "1cm",
                      help = "Right margin size for report. " + \
                          "Default=[%default]")
    parser.add_option("--tablepos", dest = "tablepos",
                      default = "left",
                      help = "Position of tables in the document. " + \
                          "One of left or center. Default=[%default]")
    parser.add_option("--checked_checkbox", dest = "checked",
                      default = os.path.abspath(os.path.dirname(__file__) + "/assets/rsz_checked_checkbox.png"),
                      help = "png file for checked checkbox. " + \
                          "Default=[%default]")
    parser.add_option("--logos", dest = "logos",
                      default = os.path.abspath(os.path.dirname(__file__) + "/assets/ki-logo_cmyk_5.png") + "," + \
                          os.path.abspath(os.path.dirname(__file__) + "/assets/ALASCCA_logo.png"),
                      help = "Comma-separated list of logos to include. " + \
                          "Default=[%default]")
    parser.add_option("--unchecked_checkbox", dest = "unchecked",
                      default = os.path.abspath(os.path.dirname(__file__) + "/assets/rsz_unchecked_checkbox.png"),
                      help = "png file for checked checkbox. " + \
                          "Default=[%default]")
    parser.add_option("--tmp_dir", dest = "tmp_dir",
                      default = "/tmp",
                      help = "Folder for containing temporary files. " + \
                          "Default=[%default]")
    parser.add_option("--debug", action="store_true", dest="debug",
                      help = "Debug the program using pdb.")
    (options, args) = parser.parse_args()

    # Parse the input parameters...

    if (options.debug):
        pdb.set_trace()

    # Make sure the required input arguments exist:
    if (len(args) != 2):
        print >> sys.stderr, "WRONG # ARGS: ", len(args)
        parser.print_help()
        sys.exit(1)

    # Try to open the input files; report an error if this fails:
    report_json_filename = args[0]
    meta_json_filename = args[1]
    meta_json_file = None
    report_json_file = None
    try:
        meta_json_file = open(meta_json_filename)
    except IOError, e:
        print >> sys.stderr, "ERROR: Could not open metadata file, " + meta_json_filename + "."
        print >> sys.stderr, e
        sys.exit(1)

    try:
        report_json_file = open(report_json_filename)
    except IOError, e:
        print >> sys.stderr, "ERROR: Could not open genomic status report file, " + report_json_filename + "."
        print >> sys.stderr, e
        sys.exit(1)

    # Try to parse the input files and exit with error if they cannot be parsed:
    # FIXME: Not sure what type of exception is raised upon a parsing error in json.load
    try:
        meta_json = json.load(meta_json_file)
    except ValueError, e:
        print >> sys.stderr, "ERROR: Problem parsing metadata file, " + meta_json_filename + "."
        print >> sys.stderr, e
        sys.exit(1)

    try:
        report_json = json.load(report_json_file)
    except ValueError, e:
        print >> sys.stderr, "ERROR: Problem parsing genomic status report file, " + report_json_filename + "."
        print >> sys.stderr, e
        sys.exit(1)

    doc_format = {"_checked": options.checked,
                  "_unchecked": options.unchecked,
                  "_logo_files": options.logos.split(",")}

    jinja_env = jinja2.Environment(
	    block_start_string = '\BLOCK{',
	    block_end_string = '}',
    	variable_start_string = '\VAR{',
    	variable_end_string = '}',
    	comment_start_string = '\#{',
    	comment_end_string = '}',
    	line_statement_prefix = '%%',
    	line_comment_prefix = '%#',
    	trim_blocks = True,
    	autoescape = False,
    	loader = jinja2.FileSystemLoader(os.path.abspath(os.path.dirname(__file__) +
                                                         "/assets/templates"))
    )

    jinja_template = jinja_env.get_template("alascca.tex")

    try:
        alascca_report = reportgen.reporting.genomics.GenomicReport(report_json, meta_json, doc_format,
                                                                    jinja_env, jinja_template)
    except ValueError, e:
        print >> sys.stderr, "ERROR: Invalid report."
        print >> sys.stderr, e
        sys.exit(1)

    # Generate a string of latex code representing the report:
    report_latex_string = alascca_report.make_latex()

    # Write the resulting latex string to a temporary output file:
    (_, tmp_latex_filename) = tempfile.mkstemp("tmp", "LatexCode", options.tmp_dir)
    tmp_latex_file = open(tmp_latex_filename, 'w')
    print >> sys.stderr, "Writing latex to output file:", tmp_latex_filename
    tmp_latex_file.write(report_latex_string.encode('utf8'))
    tmp_latex_file.close()

    # Convert latex to pdf by running pdflatex on the command line:
    # -job-name=Report
    call_result = subprocess.call(["pdflatex", "-jobname", options.output_name,
                                   "-output-directory", options.output_dir, tmp_latex_filename])

    print >> sys.stderr, tmp_latex_filename

    # Delete the temporary latex file unless told to retain it in the command line options:
    #if not options.keep_latex:
    #    subprocess.call(["rm", tmp_latex_filename])

    if call_result != 0:
        print >> sys.stderr, "ERROR: pdflatex conversion failed."
        sys.exit(1)


def main():
    writeAlasccaReport()


if __name__ == '__main__':
    sys.exit(main())
























































