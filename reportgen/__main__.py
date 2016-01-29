'''
Created on Dec 1, 2015

@author: thowhi
'''

import json, os, pdb, subprocess, sys, tempfile
from optparse import OptionParser
import reports
import formatting


def compileGenomicReport():
    # Parse the command-line arguments...
    # FIXME: Need to add msi file input too once we've decided on the format for this information.
    # FIXME: ADD MORE PRECISE DESCRIPTION of CNV file ONCE WE HAVE AGREED ON THE FILE FORMAT
    description = """usage: %prog [options] <vcfFile> <cnvFile> <crcMutationRules> <alasscaMutationRules>\n
Inputs:
- VCF file specifying somatic mutations
- Text file specifying CNVs.
- Excel spreadsheet specifying rules regarding how to report colorectal cancer mutations
- Excel spreadsheet specifying rules regarding how to report ALASSCA class

Outputs:
- A JSON file specifying the contents of the genomic status report. FIXME: Link to precise description
of this file's format.
"""

    parser = OptionParser(usage = description)
    parser.add_option("--debug", action="store_true", dest="debug",
                      help = "Debug the program using pdb.")
    (options, args) = parser.parse_args()

    # Parse the input parameters...

    if (options.debug):
        pdb.set_trace()

    # Make sure the required input arguments exist:
    if (len(args) != 4):
        print >> sys.stderr, "WRONG # ARGS: ", len(args)
        parser.add_option("--output", dest = "oututFileLoc",
                          default = "GenomicReport.json",
                          help = "Output location. Default=[%default]")
        parser.print_help()
        sys.exit(1)

    # FIXME: Currently I have no error checking on the opening of the input and output
    # files. Need to implement this.
    vcf_file = open(args[0])
    cnv_file = open(args[1])

    # Generate a dictionary of Gene objects from the input files:
    alteration_extractor = reports.AlterationExtractor(vcfFile, cnvFile)
    symbol2alteredGene = alteration_extractor.compileAlterations()

    crc_mutations_spreadsheet = args[2]
    alassca_class_spreadsheet = args[3]

    # Extract rules from the input excel spreadsheets (zero or one spreadsheet
    # per rule object):
    mutationsRule = reports.SimpleSomaticMutationsRule(crc_mutations_spreadsheet, symbol2alteredGene)
    alasscaRule = reports.AlasscaClassRule(alassca_class_spreadsheet, symbol2alteredGene)

    # Extract msiInfo from an input file too:
    msiInfo = None # FIXME: This could be some kind of filename where msi rules are specified, if needed.
    msiRule = reports.MsiStatusRule(msiInfo)

    reportCompiler = reports.ReportCompiler([msiRule, mutationsRule, alasscaRule])
    reportCompiler.extractFeatures()

    # Set output file according to options:
    jsonOutputFile = open(options.outputFileLoc)

    # Write the genomic report to output in JSON format:
    reportCompiler.writeJSON(jsonOutputFile)


def main():
    # Parse the command-line arguments...
    description = """usage: %prog [options] <metadataJSONfile> <reportJSONfile>\n
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
    parser.add_option("--fontfamily", dest = "fontfamily",
                      default = "Roman",
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
                      help = "Margin size for report. " + \
                          "Default=[%default]")
    parser.add_option("--tablepos", dest = "tablepos",
                      default = "left",
                      help = "Position of tables in the document. " + \
                          "One of left or center. Default=[%default]")
    parser.add_option("--checked_checkbox", dest = "checked",
                      default = os.path.abspath(os.path.dirname(__file__) + "/rsz_checked_checkbox.png"),
                      help = "png file for checked checkbox. " + \
                          "Default=[%default]")
    parser.add_option("--logos", dest = "logos",
                      default = os.path.abspath(os.path.dirname(__file__) + "/ki-logo_cmyk_5.png") + "," + \
                          os.path.abspath(os.path.dirname(__file__) + "/ALASCCA_logo.png"),
                      help = "Comma-separated list of logos to include. " + \
                          "Default=[%default]")
    parser.add_option("--unchecked_checkbox", dest = "unchecked",
                      default = os.path.abspath(os.path.dirname(__file__) + "/rsz_unchecked_checkbox.png"),
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
    meta_json_filename = args[0]
    report_json_filename = args[1]
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

    doc_format = formatting.DocumentFormat(options.checked, options.unchecked,
                                           options.fontfamily, options.fontsize,
                                           options.tablepos, options.language,
                                           options.margin, options.sansfont,
                                           options.logos)

    try:
        alascca_report = reports.AlasccaReport(meta_json, report_json, doc_format)
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
    call_result = subprocess.call(["pdflatex", "-jobname", "Report", tmp_latex_filename])

    # Delete the temporary latex file unless told to retain it in the command line options:
    #if not options.keep_latex:
    #    subprocess.call(["rm", tmp_latex_filename])
    
    if call_result != 0:
        sys.stderr, "ERROR: pdflatex conversion failed."
        sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
























































