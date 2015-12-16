# -*- coding: utf-8 -*-

'''
Created on Dec 1, 2015

@author: thowhi
'''

import collections, pdb


class ReportMetadata(object):
    '''
    metadata for a single sample analysis report
    '''

    def __init__(self, metadata_json):
        '''
        Extracts the metadata fields from an input JSON object.
        '''

        # FIXME: Check the fields for validty and report ValueError if not valid.

        self._personnummer = metadata_json["personnummer"]
        self._blood_sample_id = metadata_json["blood_sample_id"]
        self._tumor_sample_id = metadata_json["tumor_sample_id"]
        self._blood_sample_date = metadata_json["blood_sample_date"]
        self._tumor_sample_date = metadata_json["tumor_sample_date"]
        self._doctor = metadata_json["doctor"]
        self._doctor_address_line1 = metadata_json["doctor_address_line1"]
        self._doctor_address_line2 = metadata_json["doctor_address_line2"]
        self._doctor_address_line3 = metadata_json["doctor_address_line3"]

    def get_blood_sample_id(self):
        return self._blood_sample_id

    def get_tumor_sample_id(self):
        return self._tumor_sample_id

    def get_blood_sample_date(self):
        return self._blood_sample_date

    def get_tumor_sample_date(self):
        return self._tumor_sample_date

    def make_latex(self, doc_format):
        '''
        Generate a table to display relevant metadata fields:
        '''

        return u'''$\\begin{array}{ p{11cm} p{7cm} }
Pnr %s & %s \\tabularnewline
Analys genomförd %s & \\begin{tabular}[t]{@{}l@{}}%s\\\\%s\\\\%s\\end{tabular} \\tabularnewline
\\end{array}$''' % (self._personnummer, self._doctor, self._tumor_sample_date, self._doctor_address_line1, self._doctor_address_line2, self._doctor_address_line3)


class GenomicReport(object):
    '''
    '''

    def __init__(self, metadata_json, report_json, doc_format):
        # Save the metadata and report json objects:
        self._metadata_json = metadata_json
        self._report_json = report_json

        # Generate a representation of the report metadata:
        self._metadata = ReportMetadata(metadata_json)

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
        return format_header + u'''
\\begin{document}

\\pagenumbering{gobble}

\\vspace*{0cm}

%s
%s
\\end{document}''' % (metadata_header, body)


class AlasccaReport(GenomicReport):
    '''An ALASCCA project sample genomic status report. Can be used to generate
    a latex document displaying the report.
    '''

    def __init__(self, metadata_json, report_json, doc_format):
        super(AlasccaReport, self).__init__(metadata_json, report_json, doc_format)

        # Retrieve all relevant items from the report json object, checking
        # values as we proceed...

        # Pi3k pathway status string:
        pi3k_pathway_string = report_json["PI3K_pathway"]
        if not pi3k_pathway_string in Pi3kPathwayReport.VALID_STRINGS:
            raise ValueError("Invalid PI3K pathway string: " + pi3k_pathway_string)

        # MSI status string:
        msi_status_string = report_json["MSI_status"]
        if not msi_status_string in MsiReport.VALID_STRINGS:
            raise ValueError("Invalid MSI status string: " + msi_status_string)

        # Extract status tuples for BRAF, KRAS and NRAS:
        other_mutation_statuses = collections.OrderedDict()
        braf_status = report_json["BRAF"]
        if (not type(braf_status) is list) or (len(braf_status) != 2) or \
            (not braf_status[0] in OtherMutationsReport.VALID_STRINGS):
            raise ValueError("Invalid BRAF status: ", braf_status)
        other_mutation_statuses["BRAF"] = tuple(braf_status)

        kras_status = report_json["KRAS"]
        if (not type(braf_status) is list) or (len(kras_status) != 2) or \
            (not kras_status[0] in OtherMutationsReport.VALID_STRINGS):
            raise ValueError("Invalid KRAS status: ", kras_status)
        other_mutation_statuses["KRAS"] = tuple(kras_status)

        nras_status = report_json["NRAS"]
        if (not type(braf_status) is list) or (len(nras_status) != 2) or \
            (not nras_status[0] in OtherMutationsReport.VALID_STRINGS):
            raise ValueError("Invalid NRAS status: ", nras_status)
        other_mutation_statuses["NRAS"] = tuple(nras_status)

        # Instantiate the relevant report elements, derived from the
        # information retrieved above:
        report_metadata = self.get_metadata()
        self._initial_comment = InitialComment(report_metadata.get_blood_sample_id(),
                                              report_metadata.get_tumor_sample_id(),
                                              report_metadata.get_blood_sample_date(),
                                              report_metadata.get_tumor_sample_date())

        self._pi3k_pathway_report = Pi3kPathwayReport(pi3k_pathway_string)
        self._msi_report = MsiReport(msi_status_string)
        self._other_mutations_report = OtherMutationsReport(other_mutation_statuses)
        self._clinical_genetics = ClinicalRecommendationsReport(braf_status, msi_status_string)
        self._final_comment = FinalCommentAlasccaReport()

    def make_body_latex(self):
        title_latex = None
        alascca_title_latex = None
        clinseq_title_latex = None
        if self._doc_format.get_language() == self._doc_format.ENGLISH:
            title_latex = u'''\\section*{ClinSeq Analysis Report}\\label{clinseq-alascca-analysisreport}'''
            alascca_title_latex = u'''\\subsection*{Report for ALASCCA study}\\label{alascca-report}'''
            clinseq_title_latex = u'''\\subsection*{Other Information from ClinSeq Profile}\\label{clinseq-report}'''
        else:
            assert self._doc_format.get_language() == self._doc_format.SWEDISH
            title_latex = u'''\\section*{ClinSeq Analysrapport}\\label{clinseq-alascca-analysisreport}'''
            alascca_title_latex = u'''\\subsection*{Rapport för ALASCCA Studien}\\label{alascca-report}'''
            clinseq_title_latex = u'''\\subsection*{Övriga Information Från ClinSeq-profilen}\\label{clinseq-report}'''
        initial_comment_latex = self._initial_comment.make_latex(self._doc_format)
        pi3k_pathway_latex = self._pi3k_pathway_report.make_latex(self._doc_format)
        msi_latex = self._msi_report.make_latex(self._doc_format)
        other_mutations_latex = self._other_mutations_report.make_latex(self._doc_format)
        clinical_genetics_latex = self._clinical_genetics.make_latex(self._doc_format)
        final_comment_latex = self._final_comment.make_latex(self._doc_format)

        return title_latex + \
               initial_comment_latex + \
               alascca_title_latex + \
               pi3k_pathway_latex + \
               clinseq_title_latex + \
               msi_latex + \
               other_mutations_latex + \
               clinical_genetics_latex + \
               final_comment_latex


class ReportFeature(object):
    '''
    ReportFeature abstract class.
    '''

    def __init__(self):
        '''
        '''

    def make_latex(self, doc_format):
        return u'''
\\subsubsection*{%s}
\\vspace{6pt}
%s
\\vspace{6pt}
''' % (self.make_title(doc_format), self.make_content_body(doc_format))

    def make_content_body(self, doc_format):
        '''All implementing classes must implement a function for generating
        a string containing latex code for the content body.'''

    def make_title(self, doc_format):
        '''All implementing classes must implement a function for generating
        a string containing latex code for a title.'''


class InitialComment(ReportFeature):
    '''
    '''

    def __init__(self, blood_sample_id, tumor_sample_id, blood_sample_date, tumor_sample_date):
        super(InitialComment, self).__init__()
        self._blood_sample_id = blood_sample_id
        self._tumor_sample_id = tumor_sample_id
        self._blood_sample_date = blood_sample_date
        self._tumor_sample_date = tumor_sample_date

    def make_title(self, doc_format):
        return u''''''

    def make_content_body(self, doc_format):
        if doc_format.get_language() == doc_format.ENGLISH:
            return u'''Analysis completed for blood sample %d taken %s and tumor sample %d taken %s''' % \
                (self._blood_sample_id, self._blood_sample_date,
                self._tumor_sample_id, self._tumor_sample_date)
        else:
            assert doc_format.get_language() == doc_format.SWEDISH
            return u'''Analys genomförd för blodprov %d taget %s och tumörprov %d taget %s''' % \
                (self._blood_sample_id, self._blood_sample_date,
                self._tumor_sample_id, self._tumor_sample_date)


class Pi3kPathwayReport(ReportFeature):
    '''
    '''

    MUTN_CLASS_A = "Mutation class A"
    MUTN_CLASS_B = "Mutation class B"
    NO_MUTN = "No mutation"
    VALID_STRINGS = [MUTN_CLASS_A, MUTN_CLASS_B, NO_MUTN]

    def __init__(self, pi3k_pathway_string):
        self._pi3k_pathway_status = pi3k_pathway_string

    def make_title(self, doc_format):
        if doc_format.get_language() == doc_format.ENGLISH:
            return u'''PI3K signaling pathway'''
        else:
            assert doc_format.get_language() == doc_format.SWEDISH
            return u'''PI3K-signalväg'''

    def make_content_body(self, doc_format):
        class_a_box = doc_format.get_unchecked_checkbox()
        class_b_box = doc_format.get_unchecked_checkbox()
        no_mutations_box = doc_format.get_unchecked_checkbox()
        if self._pi3k_pathway_status == self.MUTN_CLASS_A:
            class_a_box = doc_format.get_checked_checkbox()
        if self._pi3k_pathway_status == self.MUTN_CLASS_B:
            class_b_box = doc_format.get_checked_checkbox()
        if self._pi3k_pathway_status == self.NO_MUTN:
            no_mutations_box = doc_format.get_checked_checkbox()

        if doc_format.get_language() == doc_format.ENGLISH:
            return u'''$\\begin{array}{ p{1cm} p{8cm} }
  \\toprule
  \\includegraphics{%s} & Mutation class A, patient can be randomised \\tabularnewline
  \\includegraphics{%s} & Mutation klass B, patient can be randomised \\tabularnewline
  \\includegraphics{%s} & No mutations, patient can \emph{not} be randomised \\tabularnewline
  \\bottomrule
\\end{array}$
''' % (class_a_box, class_b_box, no_mutations_box)
        else:
            assert doc_format.get_language() == doc_format.SWEDISH
            return u'''$\\begin{array}{ p{1cm} p{8cm} }
  \\toprule
  \\includegraphics{%s} & Mutation klass A, patienten kan randomiseras \\tabularnewline
  \\includegraphics{%s} & Mutation klass B, patienten kan randomiseras \\tabularnewline
  \\includegraphics{%s} & Inga mutationer, patienten kan \emph{ej} randomiseras \\tabularnewline
  \\bottomrule
\\end{array}$
''' % (class_a_box, class_b_box, no_mutations_box)


class MsiReport(ReportFeature):
    '''
    '''

    MSS = "MSS/MSI-L"
    MSI = "MSI-H"
    NOT_DETERMINED = "Not determined"
    VALID_STRINGS = [MSS, MSI, NOT_DETERMINED]

    def __init__(self, msi_status_string):
        self._msi_status = msi_status_string

    def make_title(self, doc_format):
        if doc_format.get_language() == doc_format.ENGLISH:
            return u'''Microsatellite instability (MSI)'''
        else:
            assert doc_format.get_language() == doc_format.SWEDISH
            return u'''Mikrosatellitinstabilitet (MSI)'''

    def make_content_body(self, doc_format):
        mss_box = doc_format.get_unchecked_checkbox()
        msi_box = doc_format.get_unchecked_checkbox()
        not_determined_box = doc_format.get_unchecked_checkbox()
        if self._msi_status == self.MSS:
            mss_box = doc_format.get_checked_checkbox()
        if self._msi_status == self.MSI:
            msi_box = doc_format.get_checked_checkbox()
        if self._msi_status == self.NOT_DETERMINED:
            not_determined_box = doc_format.get_checked_checkbox()

        if doc_format.get_language() == doc_format.ENGLISH:
            return u'''$\\begin{array}{ p{1cm} p{3cm} }
  \\toprule
  \\includegraphics{%s} & MSS/MSI-L \\tabularnewline
  \\includegraphics{%s} & MSI-H \\tabularnewline
  \\includegraphics{%s} & Not determined \\tabularnewline
  \\bottomrule
\\end{array}$
''' % (mss_box, msi_box, not_determined_box)
        else:
            assert doc_format.get_language() == doc_format.SWEDISH
            return u'''$\\begin{array}{ p{1cm} p{3cm} }
  \\toprule
  \\includegraphics{%s} & MSS/MSI-L \\tabularnewline
  \\includegraphics{%s} & MSI-H \\tabularnewline
  \\includegraphics{%s} & Ej utförd \\tabularnewline
  \\bottomrule
\\end{array}$
''' % (mss_box, msi_box, not_determined_box)


class OtherMutationsReport(ReportFeature):
    '''
    '''

    MUT = "Mutated"
    NO_MUT = "Not mutated"
    NOT_DETERMINED = "Not determined"
    VALID_STRINGS = [MUT, NO_MUT, NOT_DETERMINED]

    def __init__(self, mutation_statuses):
        # Precondition: Input argument must have the behaviour of an ordered
        # dictionary, with items ordered in the order that they shall be
        # reported in. Keys are gene names and values are tuples showing
        # mutation info for the given gene:
        self._mutation_statuses = mutation_statuses

    def make_title(self, doc_format):
        if doc_format.get_language() == doc_format.ENGLISH:
            return u'''Other mutations'''
        else:
            assert doc_format.get_language() == doc_format.SWEDISH
            return u'''Övriga mutationer'''

    def make_content_body(self, doc_format):
        body_string = u'''$\\begin{array}{ p{2cm} p{2cm} p{2cm} p{2cm} p{2cm} }
  \\toprule
  '''
        if doc_format.get_language() == doc_format.ENGLISH:
            body_string = body_string + u'''Gene & Mut. & No mut. & Not Det. & Comments \\tabularnewline
  \\midrule
'''
        else:
            assert doc_format.get_language() == doc_format.SWEDISH
            body_string = body_string + u'''Gene & Mut. & Ej mut. & Ej utförd & Kommentar \\tabularnewline
  \\midrule
'''
        for gene in self._mutation_statuses.keys():
            # Set up box image paths and comments string:
            mut_box = doc_format.get_unchecked_checkbox()
            no_mut_box = doc_format.get_unchecked_checkbox()
            not_det_box = doc_format.get_unchecked_checkbox()
            mutn_info_tuple = self._mutation_statuses[gene]
            mutn_status = mutn_info_tuple[0]
            comments = mutn_info_tuple[1]
            if comments == None:
                comments = ""

            if mutn_status == self.MUT:
                mut_box = doc_format.get_checked_checkbox()
            if mutn_status == self.NO_MUT:
                no_mut_box = doc_format.get_checked_checkbox()
            if mutn_status == self.NOT_DETERMINED:
                not_det_box = doc_format.get_checked_checkbox()

            # Add a row for the current gene:
            body_string = body_string + u'''%s & \\includegraphics{%s} & \\includegraphics{%s} & \\includegraphics{%s} & %s \\tabularnewline
''' % (gene, mut_box, no_mut_box, not_det_box, comments)

        body_string = body_string + u'''
  \\bottomrule
\\end{array}$
'''
        return body_string


class ClinicalRecommendationsReport(ReportFeature):
    '''
    '''

    def __init__(self, braf_status, msi_status):
        # FIXME: This is not nice: Need to come up with better engineering for
        # where to check this information:
        braf_not_mutated = not (braf_status[0] == OtherMutationsReport.MUT)
        msi_high = msi_status == MsiReport.MSI
        # FIXME: This seems weird having the logic here, I suspect we may
        # need to rethink this at some point:
        self._add_report = braf_not_mutated and msi_status

    def make_title(self, doc_format):
        if self._add_report:
            if doc_format.get_language() == doc_format.ENGLISH:
                return u'''Comments'''
            else:
                assert doc_format.get_language() == doc_format.SWEDISH
                return u'''Kommentar'''
        else:
            return u''''''

    def make_content_body(self, doc_format):
        if self._add_report:
            if doc_format.get_language() == doc_format.ENGLISH:
                return u'''Patient has high instability in microsatellites (MSI-H) but no mutations in BRAF, therefore the patient should be referred to genetic counceling.'''
            else:
                assert doc_format.get_language() == doc_format.SWEDISH
                return u'''Patienten har hög instabilitet i mikrosatelliter (MSI-H) men inte mutation i BRAF varför remiss till cancergenetisk mottagning rekommenderas.'''
        else:
            return u''''''


class FinalCommentAlasccaReport(ReportFeature):
    '''
    '''

    def __init__(self):
        '''
        '''


    def make_title(self, doc_format):
        if doc_format.get_language() == doc_format.ENGLISH:
            return u'''Other information'''
        else:
            assert doc_format.get_language() == doc_format.SWEDISH
            return u'''Övriga information'''

    def make_content_body(self, doc_format):
        # FIXME: Need to double-check these texts:
        if doc_format.get_language() == doc_format.ENGLISH:
            return u'''Mutations examined are BRAF codon 600, KRAS exon 2-4 and NRAS codons 12, 13, 59, 61, 117 and 146.'''
        else:
            assert doc_format.get_language() == doc_format.SWEDISH
            return u'''Mutationer som undersöks är BRAF kodon 600, KRAS exon 2-4 samt för NRAS 12, 13, 59, 61, 117 och 146.'''




















































