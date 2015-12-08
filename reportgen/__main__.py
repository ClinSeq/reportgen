'''
Created on Dec 1, 2015

@author: thowhi
'''

import json, os, pdb, subprocess, sys, tempfile
from optparse import OptionParser
import reports
import formatting


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
    parser.add_option("--boolFlag", action="store_true", dest="boolFlag",
                      default = False,
                      help = "")
    parser.add_option("--language", dest = "language",
                      default = "Swedish",
                      help = "Language in which the report text will be " + \
                          "generated. One of Swedish or English. Default=[%default]")
    parser.add_option("--fontfamily", dest = "fontfamily",
                      default = "Roman",
                      help = "Font in which the report text will be " + \
                          "generated. One of Roman or SansSerif. Default=[%default]")
    parser.add_option("--fontsize", dest = "fontsize",
                      default = "10pt",
                      help = "Font size for report text. " + \
                          "Default=[%default]")
    parser.add_option("--tablepos", dest = "tablepos",
                      default = "left",
                      help = "Position of tables in the document. " + \
                          "One of left or center. Default=[%default]")
    parser.add_option("--checked_checkbox", dest = "checked",
                      default = os.path.abspath(os.path.dirname(__file__) + "/../rsz_checked_checkbox.png"),
                      help = "png file for checked checkbox. " + \
                          "Default=[%default]")
    parser.add_option("--unchecked_checkbox", dest = "unchecked",
                      default = os.path.abspath(os.path.dirname(__file__) + "/../rsz_unchecked_checkbox.png"),
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
                                           options.tablepos, options.language)

    #alassca_report = reports.AlasscaReport(meta_json, report_json, doc_format)
    
    # Generate a string of latex code representing the report:
    #report_latex_string = alassca_report.make_latex()

    # Write the resulting latex string to a temporary output file:
    (_, tmp_latex_filename) = tempfile.mkstemp("tmp", "Metadata", options.tmp_dir)
    tmp_latex_file = open(tmp_latex_filename, 'w')
    #print >> tmp_latex_file, report_latex_string
    tmp_latex_file.close()
    
    # Convert latex to pdf by running pdflatex on the command line:
    #call_result = subprocess.call(["pdflatex", tmp_latex_filename])

    # Delete the temporary latex file unless told to retain it in the command line options:
    #if not options.keep_latex:
    #    subprocess.call(["rm", tmp_latex_filename])
    
    #if call_result != 0:
    #    sys.stderr, "ERROR: pdflatex conversion failed."
    #    sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
























































