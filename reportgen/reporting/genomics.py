# -*- coding: utf-8 -*-

from reportgen.reporting.util import extract_feature
from reportgen.reporting.metadata import ReportMetadata
from reportgen.reporting.features import AlasccaClassReport, MsiReport, SimpleSomaticMutationsReport, ReportLegend


class GenomicReport(object):
    '''
    '''

    def __init__(self, report_json, metadata_json, doc_format):
        # Save the metadata and report json objects:
        self._report_json = report_json
        self._metadata_json = metadata_json

        # Generate a representation of the report metadata:
        self._metadata = ReportMetadata()
        self._metadata.set_from_dict(metadata_json)

        # Store the document format object:
        self._doc_format = doc_format

    def get_metadata(self):
        return self._metadata

    def get_metadata_json(self):
        return self._metadata_json

    def get_report_json(self):
        return self._report_json

    def get_doc_format(self):
        return self._doc_format

    def make_latex(self):
        format_header = self._doc_format.make_latex()
        metadata_header = self._metadata.make_latex(self._doc_format)
        body = self.make_body_latex()
        footer = self._doc_format.make_footer_latex()
        return u'''
%s
\\begin{document}

%s

\\pagenumbering{gobble}

\\vspace*{0cm}

%s
%s
\\end{document}''' % (format_header, footer, metadata_header, body)


class AlasccaReport(GenomicReport):
    """An ALASCCA project sample genomic status report. Can be used to generate
    a latex document displaying the report."""

    def __init__(self, genomics_dict, metadata_dict, doc_format):
        super(AlasccaReport, self).__init__(genomics_dict, metadata_dict, doc_format)

        # Generate report on dates:
        self._dates_report = self.get_metadata().generate_dates_report()

        # Extract reporting features from the report json object...
        self._alascca_class_report = extract_feature(genomics_dict, AlasccaClassReport)
        self._somatic_mutations_report = extract_feature(genomics_dict, SimpleSomaticMutationsReport)
        self._msi_report = extract_feature(genomics_dict, MsiReport)

        # Note: The section with the metadata is generated separately, not
        # here.

        # The section of the report with the text explaining the report
        # content:
        self._report_legend = ReportLegend()

    def make_body_latex(self):
        title_latex = None
        clinseq_title_latex = None
        if self._doc_format.get_language() == self._doc_format.ENGLISH:
            title_latex = u'''\\section*{ClinSeq Analysis Report}\\label{clinseq-alascca-analysisreport}'''
            clinseq_title_latex = u'''\\subsection*{Other Information from ClinSeq Profile}\\label{clinseq-report}'''
        else:
            assert self._doc_format.get_language() == self._doc_format.SWEDISH
            title_latex = u'''\\begin{center}
\\huge{ClinSeq Analysrapport}
\\end{center}'''
            clinseq_title_latex = u'''\\Large*{Övrig information från ClinSeq-profil}\\label{clinseq-report}'''
        msi_title_latex = self._alascca_class_report.make_title_latex(self._doc_format)
        alascca_title_latex = self._alascca_class_report.make_title_latex(self._doc_format)
        somatic_mutations_title_latex = self._somatic_mutations_report.make_title_latex(self._doc_format)

        logos_latex = self._doc_format.make_logo_latex()
        dates_latex = self._dates_report.make_latex(self._doc_format)
        alascca_class_latex = self._alascca_class_report.make_latex(self._doc_format)
        somatic_mutations_latex = self._somatic_mutations_report.make_latex(self._doc_format)
        msi_latex = self._msi_report.make_latex(self._doc_format)
        report_legend_latex = self._report_legend.make_latex(self._doc_format)

        # FIXME: This is getting a bit hacky (adding mybox and other such things here):
        return title_latex + \
            "\n\\vspace{-0.3cm}" + \
            logos_latex + \
            "\n\\vspace{0.3cm}" + \
            self._metadata.make_latex() + \
            '''\n\\vspace{1cm}
\\onehalfspacing
{''' + \
            dates_latex + \
            '''Blodprov taget 2016-01-01, remiss-ID 98765432, etikett 12345678 \\\\
Tumörprov taget 2016-01-02, remiss-ID 14253647, etikett 34567890 \\\\
}
\\par
\singlespacing

\\setlength{\\fboxsep}{10pt}
\setlength{\\fboxrule}{3pt}

\\rowcolors{1}{ratherlightgrey}{}
\\fcolorbox{blue}{white}{%
  \\parbox{18.9cm}{%
\\centering
{''' + \
            alascca_title_latex + \
            "\n\\vspace{0.2cm}" + \
            alascca_class_latex + \
            '''}
\\begin{center}''' + \
            clinseq_title_latex + \
'''\\end{center}

\\vspace{-0.5cm}

\\begin{minipage}{.4\\linewidth}
\\fcolorbox{lightgrey}{white}{%
  \\parbox[t][3cm][t]{6.1cm}{%
\\centering

{''' + \
            msi_title_latex + \
            '''} \\par
\\vspace{0.4cm}

\\tcbox[left=0mm,right=0mm,top=0mm,bottom=0mm,boxsep=0mm,
  boxrule=0.4pt, colframe=grey, colback=white]% set to your wish
{''' + \
            msi_latex + \
            '''}
}}
\\end{minipage}
\\begin{minipage}{.6\linewidth}
\\fcolorbox{lightgrey}{white}{%
  \\parbox[t][3cm][t]{11cm}{%
    \\centering

    \\rowcolors{2}{}{ratherlightgrey}

    {''' + \
            somatic_mutations_title_latex + \
            '''} \par
\\vspace{0.3cm}

\\tcbox[left=0mm,right=0mm,top=0mm,bottom=0mm,boxsep=0mm,
  boxrule=0.4pt, colframe=grey, colback=white]% set to your wish
{
  ''' + \
            somatic_mutations_latex + \
            '''}
}}
    \\end{minipage}%

\\vspace{0.3cm}
''' + \
            report_legend_latex