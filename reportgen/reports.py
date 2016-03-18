# -*- coding: utf-8 -*-

'''
Created on Dec 1, 2015

@author: thowhi
'''

import collections, genomics, pdb, re, sys
import openpyxl

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
        table_latex = None
        if doc_format.get_language() == doc_format.ENGLISH:
            table_latex = u'''$\\begin{array}{ p{11cm} p{7cm} }
Pnr %s & %s \\tabularnewline
Analysis performed %s & \\begin{tabular}[t]{@{}l@{}}%s\\\\%s\\\\%s\\end{tabular} \\tabularnewline
\\end{array}$''' % (self._personnummer, self._doctor, self._tumor_sample_date, self._doctor_address_line1, self._doctor_address_line2, self._doctor_address_line3)
        else:
            assert doc_format.get_language() == doc_format.SWEDISH
            table_latex = u'''$\\begin{array}{ p{11cm} p{7cm} }
Pnr %s & %s \\tabularnewline
Analys genomförd %s & \\begin{tabular}[t]{@{}l@{}}%s\\\\%s\\\\%s\\end{tabular} \\tabularnewline
\\end{array}$''' % (self._personnummer, self._doctor, self._tumor_sample_date, self._doctor_address_line1, self._doctor_address_line2, self._doctor_address_line3)
        return u'''
\\begin{adjustwidth}{0cm}{0cm}
%s
\\end{adjustwidth}''' % (table_latex)


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
    '''An ALASCCA project sample genomic status report. Can be used to generate
    a latex document displaying the report.'''

    def __init__(self, metadata_json, report_json, doc_format):
        super(AlasccaReport, self).__init__(metadata_json, report_json, doc_format)

        # Retrieve all relevant items from the report json object, checking
        # values as we proceed...

        # Pi3k pathway status string:
        pi3k_pathway_string = report_json[AlasccaClassReport.NAME]
        if not pi3k_pathway_string in AlasccaClassReport.VALID_STRINGS:
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

        self._pi3k_pathway_report = AlasccaClassReport(pi3k_pathway_string)
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
        title_latex = self.make_title(doc_format)
        body_latex = self.make_content_body(doc_format)
        feature_latex = u"\n"
        # If title latex or body latex is generated as None by the concrete
        # implementation, then don't generate latex for that part:
        if not title_latex == None:
            feature_latex = feature_latex + u"\\subsubsection*{%s}\n" % (title_latex)
        if not body_latex == None:
            feature_latex = feature_latex + body_latex + u"\\vspace{6pt}"
        return feature_latex

    def make_content_body(self, doc_format):
        '''All implementing classes must implement a function for generating
        a string containing latex code for the content body.'''

    def make_title(self, doc_format):
        '''All implementing classes must implement a function for generating
        a string containing latex code for a title.'''

    # Concrete classes must implement toDict() and fromDict()


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
        return None

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


class AlterationClassification:
    '''This class is used to assign a particular classification to input
    genetic alterations, if a match occurs.'''

    def __init__(self, consequences, transcriptID, positionInformationStrings, outputFlag):
        self._consequences = consequences
        self._transcript_ID = transcriptID
        self._position_strings = positionInformationStrings
        self._output_flag = outputFlag

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not self.get_consequences() == other.get_consequences():
            print >> sys.stderr, "Comparing consequences."
            return False
        if not self.get_transcript_ID() == other.get_transcript_ID():
            print >> sys.stderr, "Comparing transcript IDs."
            return False
        if not self.get_position_information() == other.get_position_information():
            print >> sys.stderr, "Comparing position information."
            return False
        if not self.get_output_flag() == other.get_output_flag():
            print >> sys.stderr, "Flags differ."
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_position_information(self):
        return self._position_strings

    def get_transcript_ID(self):
        return self._transcript_ID

    def get_consequences(self):
        return self._consequences

    def get_output_flag(self):
        return self._output_flag

    def match(self, alteration):
        match = True
        if not alteration.get_sequence_ontology() in self.get_consequences():
            match = False
        if not alteration.get_transcript_ID() == self.get_transcript_ID():
            match = False
        # FIXME: Perhaps I should make this mechanism more robust?
        # Zero position information fields means that position is not specified
        # and will not be used to discount a match:
        if len(self.get_position_information()) > 0:
            position_matches = self.matches_positions(alteration)
            if not position_matches:
                match = False

        return match

    def matches_positions(self, alteration):
        '''Returns true if the specified alteration's positional information
        "matches" the specified positions for this alteration classification.
        Returns false otherwise.'''

        matchObserved = False

        # FIXME: Possibly should refactor this code to make it more robust:
        # If the alteration position string is None, it means that the
        # alteration does not match any positions:
        if alteration.get_position_string() == None:
            return matchObserved

        for position_string in self._position_strings:
            if self.matches_position(position_string, alteration.get_position_string()):
                matchObserved = True

        return matchObserved

    def matches_position(self, classificationPositionString, alterationPositionString):
        # FIXME: POTENTIAL PROBLEMS:
        # The alteration position string may not always denote a single exact integer position.
        # E.g. what if it denotes a range? Also, what about complex substitutions? Need to
        # figure out how to deal with these. E.g. what if there are two ranges (alteration
        # range and classification range) and they partially overlap?

        if re.match("^[A-Z][a-z]{2}[0-9]+[A-Z][a-z]{2}$", classificationPositionString) != None:
            # The position string denotes a specific amino acid substitution
            # => Only match if the alteration matches that substitution
            # exactly:
            return classificationPositionString == alterationPositionString
        else:
            # The match depends soley on the position of the alteration,
            # disregarding the residue information...

            # Extract integer position from alterationPositionString:
            alterationIntegerPosition = int(re.search("[0-9]+", alterationPositionString).group())

            if re.match("^[0-9]+$", classificationPositionString) != None:
                # The classification position string is an exact integer position =>
                # There is a match if the integer information in the alteration
                # matches the classification position string exactly:
                return int(classificationPositionString) == alterationIntegerPosition

            else:
                # This classification position string must be an integer range:
                assert re.match("^[0-9]+:[0-9]+$", classificationPositionString) != None

                # Extract the start and end positions of the range:
                classificationRangeStart = int(classificationPositionString.split(":")[0])
                classificationRangeEnd = int(classificationPositionString.split(":")[1])

                # There is a match if the alteration position intersects the classification position range at all:
                return alterationIntegerPosition >= classificationRangeStart \
                       and alterationIntegerPosition <= classificationRangeEnd


class AlasccaClassReport(ReportFeature):
    '''
    '''

    NAME = "ALASCCA class"

    MUTN_CLASS_A = "Mutation class A"
    MUTN_CLASS_B = "Mutation class B"
    NO_MUTN = "No mutation"
    VALID_STRINGS = [MUTN_CLASS_A, MUTN_CLASS_B, NO_MUTN]

    def __init__(self, pathway_class):
        self._pathway_class = pathway_class

    def to_dict(self):
        return {self.NAME:self._pathway_class}

    def from_dict(self, input_dict):
        pathway_class = input_dict[self.NAME]
        self._pathway_class = pathway_class

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
  \\includegraphics{%s} & Mutation class B, patient can be randomised \\tabularnewline
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


class MutationStatus:
    '''Mutation status of a given gene.'''

    MUT = "Mutated"
    NO_MUT = "Not mutated"
    NOT_DETERMINED = "Not determined"
    VALID_STRINGS = [MUT, NO_MUT, NOT_DETERMINED]

    def __init__(self):
        self._status = self.NO_MUT
        self._mutation_list = []

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not self.get_status() == other.get_status():
            return False
        if not self.get_mutation_list() == other.get_mutation_list():
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_status(self):
        return self._status

    def get_mutation_list(self):
        return self._mutation_list

    def add_mutation(self, mutation, flag):
        self._status = self.MUT
        self._mutation_list.append((mutation,flag))

    def set_not_determined(self):
        assert self._status == self.NO_MUT
        assert self._mutation_list == []
        self._status = self.NOT_DETERMINED


class SimpleSomaticMutationsReport(ReportFeature):
    '''A report on mutation status of selected genes.
    '''

    # XXX ADAPT THIS - NOT SURE HOW YET. BASED ON MARKUS' RECENT MEETING WITH THE alascca BOARD,
    # IT SEEMS WE WILL NOT INCLUDE THIS TEXT, AS THE TEXT WILL BE THE SAME FOR EVERY REPORT:
    '''
    TEXT = {'ENG': {
        "NRAS_COMMON_MUT" : "blaha",
        "NRAS_UNCOMMON_MUT" : "qwerty"
    },
    'SWE': {
        "NRAS_COMMON_MUT" : "blaha",
        "NRAS_UNCOMMON_MUT" : "qwerty"
    }}'''

    def __init__(self):
        # Sets up an empty dictionary of geneSymbol->(mutationStatus, mutationList)
        # key value pairs, where mutationStatus is a string of restricted
        # values, and mutationList is an array of tuples each containing an
        # alteration and an associated alteration flag. Note that mutationList
        # can only be non-null if mutationStatus is "mutated":
        self._symbol2mutation_status = {}

    def add_gene(self, gene_name):
        # Adds a gene, with mutationStatus as "NoMutation" and mutationList as
        # empty by default:
        self._symbol2mutation_status[gene_name] = MutationStatus()

    def add_mutation(self, gene_symbol, mutation, flag):
        assert self._symbol2mutation_status.has_key(gene_symbol)
        self._symbol2mutation_status[gene_symbol].add_mutation(mutation, flag)

    def to_dict(self):
        return self._symbol2mutation_status
        #output_dict = {}
        #for symbol in self._symbol2mutation_status.keys():
        #    # XXX Problem: This doesn't seem to deal with multiple mutations:
        #    mutn_status_string = self._symbol2mutation_status[symbol][0]
        #    mutn = self._symbol2mutation_status[symbol][1]
        #    outputDict[symbol] = [mutnStatusString, mutn.toDict()]
        #
        #return outputDict

    def from_dict(self, input_dict):
        self._symbol2mutation_status = input_dict

    # XXX UPDATE THIS METHOD TO MAKE IT WORK WITH THE UPDATED _SYMBOL2MUTATIONSTATUS
    # ATTRIBUTE:
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
        for gene in self._symbol2mutationStatus.keys():
            # Set up box image paths and comments string:
            mut_box = doc_format.get_unchecked_checkbox()
            no_mut_box = doc_format.get_unchecked_checkbox()
            not_det_box = doc_format.get_unchecked_checkbox()
            mutn_info_tuple = self._symbol2mutationStatus[gene]
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


# XXX IMPLEMENT THIS:
class MsiStatusRule:
    '''A rule for generating an MSI status class.'''

    # FIXME: Still need to generate exact algorithm for the constructor and
    # the apply() method. It should be fairly straightforward now though. See
    # SimpleSomaticMutationsRule as a template.

    # FIXME: We need to agree on the format of the input file and parameter file.

    def __init__(self, excel_spreadsheet, symbol2gene):
        pass

    def apply(self, excel_spreadsheet):
        pass


class AlasccaClassRule:
    '''A rule for generating an alascca class (A/B/None) summarising PI3K
    pathway mutational status. The rule parameters are specified in an
    input excel spreadsheet.'''

    # These possible alteration flags must match the flags defined in the
    # ALASCCA_MUTATION_TABLE excel spreadsheet:
    CLASS_B_1 = "ALASCCA_CLASS_B_1"
    CLASS_B_2 = "ALASCCA_CLASS_B_2"
    CLASS_A = "ALASCCA_CLASS_A"

    # FIXME: Still need to generate exact algorithm for the constructor and
    # the apply() method. It should be fairly straightforward now though. See
    # SimpleSomaticMutationsRule as a template.

    def __init__(self, excel_spreadsheet):
        self._gene_symbol2classifications = parse_mutation_table(excel_spreadsheet)

    # FIXME: It is currently unclear when we should be calling
    # "not determined".

    def apply(self, symbol2gene):
        # If there is one or more genes with at least one class A alteration,
        # then call class A. Otherwise, if there is one or more genes with at
        # least one class B_1 mutation, then call class B. Otherwise, if there
        # are at least two class B_2 mutations, then call class B. Otherwise,
        # call no mutation.

        # Classify alterations and count the flag instances...
        flag_instances = {self.CLASS_B_1: 0, self.CLASS_B_2: 0,
                          self.CLASS_A: 0}

        for symbol in self._gene_symbol2classifications.keys():
            # Retrieve all the classifications for the current gene:
            gene_classifications = self._gene_symbol2classifications[symbol]

            # Find all mutations matching this gene's rules:
            alterations = []
            gene = None
            if symbol2gene.has_key(symbol):
                gene = symbol2gene[symbol]
                alterations = gene.get_alterations()

            for alteration in alterations:
                # Apply all rules to this alteration:
                for classification in gene_classifications:
                    flag = None
                    if classification.match(alteration):
                        flag = classification.get_output_flag()
                        assert flag_instances.has_key(flag)
                        flag_instances[flag] = flag_instances[flag] + 1

        # Apply logic based on numbers of flag instances:
        if flag_instances[self.CLASS_A] > 0:
            return AlasccaClassReport(AlasccaClassReport.MUTN_CLASS_A)
        elif flag_instances[self.CLASS_B_1] > 0:
            return AlasccaClassReport(AlasccaClassReport.MUTN_CLASS_B)
        elif flag_instances[self.CLASS_B_2] >= 2:
            return AlasccaClassReport(AlasccaClassReport.MUTN_CLASS_B)
        else:
            return AlasccaClassReport(AlasccaClassReport.NO_MUTN)


def parse_mutation_table(spreadsheet_filename):
    '''Parses a given excel spreadsheet, extracting mutation classification
    rows from the mutation table. Returns a dictionary of gene symbol to
    classification.'''

    # Break each row up and add it to the above dictionary of gene
    # decisions...

    # Use openpyxl to parse the input file:
    workbook = openpyxl.load_workbook(filename = spreadsheet_filename)
    mutation_table = workbook.get_sheet_by_name("MutationTable")

    # Get the initial rows containing data...
    rows_of_interest = []
    row_iter = mutation_table.iter_rows()

    # FIXME: This excel spreadsheet parsing may not be robust enough...
    # Skip over the first header row:
    curr_row = row_iter.next()
    for curr_row in row_iter:
        if curr_row[0].value != None:
            rows_of_interest.append(curr_row)

    gene_symbol2classifications = {}

    for row in rows_of_interest:
        # Extract consequence set, symbol, geneID, transcriptID, amino
        # acid change set, and flag from the current row:
        consequences = row[0].value.split(",")
        symbol = row[1].value
        gene_ID = row[2].value # Not currently used.
        transcript_ID = row[3].value
        amino_acid_changes = []
        if row[4].value != None:
            amino_acid_changes = row[4].value.split(",")
        flag = row[5].value

        curr_classification = \
            AlterationClassification(consequences, transcript_ID,
                                     amino_acid_changes, flag)

        if not gene_symbol2classifications.has_key(symbol):
            gene_symbol2classifications[symbol] = []

        gene_symbol2classifications[symbol].append(curr_classification)

    return gene_symbol2classifications


class SimpleSomaticMutationsRule:
    '''A rule for generating summary (intended to be printed as a table) of
    mutations in a set of genes, with the set of genes and mutation flagging
    determined by an excel spreadsheet.

    The idea here is that someone can update the spreadsheet defining mutations
    of interest and how they should be flagged, and these rules then get applied
    to a set of gene mutations by an instance of this class.'''

    def __init__(self, excel_spreadsheet):
        # FIXME: Somewhere, we need to have an exact specification of the structure
        # of the excel spreadsheet specifying rules. Writing this down here for
        # the time being.

        # Excel spreadsheet must contain a set of rows, each containin the
        # following columns:
        # - Consequence (comma separated list of one or more sequence ontology
        # terms)
        # - Symbol (exactly one HUGO gene name)
        # - Gene (exactly one Ensembl gene ID, must match the Symbol)
        # - Transcript (Optional (zero or one) Ensembl transcript ID). This
        # must be specified if the consequence types pertain to transcript
        # annotations, such as amino acid substitutions.
        # - Amino acid changes (comma separated list of codon position
        # strings). Each codon position string must match one of the following
        # patterns:
        # <positionOnly> ::= [0-9]+
        # <residueChange> ::= [A-Z]{1}[0-9]+[A-Z]{1}
        # <positionRange> ::= [0-9]+:[0-9]+
        # - Flag (string)

        # This data structure is ugly but I think it should work; it will
        # facilitate matching mutations to rules:
        self._gene_symbol2classifications = parse_mutation_table(excel_spreadsheet)

    def apply(self, symbol2gene):
        '''Generates a new SimpleSomaticMutationsReport object, summarising all
        somatic mutations of interest observed in the specified gene
        mutations.'''

        report = SimpleSomaticMutationsReport()

        for symbol in self._gene_symbol2classifications.keys():
            # Retrieve all the classifications for the current gene:
            gene_classifications = self._gene_symbol2classifications[symbol]

            report.add_gene(symbol)

            # Find all mutations matching this gene's rules:
            alterations = []
            gene = None
            if symbol2gene.has_key(symbol):
                gene = symbol2gene[symbol]
                alterations = gene.get_alterations()

            for alteration in alterations:
                # Apply all rules to this alteration, in order of precedence.
                # In this way, later matched rules will overwrite any preceding
                # flag result:
                for classification in gene_classifications:
                    flag = None
                    if classification.match(alteration):
                        flag = classification.get_output_flag()
                    report.add_mutation(gene.get_symbol(), alteration, flag)

        return report


class ReportCompiler:
    '''Compiles a genomic report given input genomic features and rules. Can then
    output a JSON formatted representation of the report. NOTE: There is no
    alascca report subtype: The particular type of report is determined by
    the composition of rules the compiler is using to generate corresponding
    report features.'''

    def __init__(self, rules):
        self.rules = rules

        # This will contain the report features once they have been generated
        # by applying the rules:
        self.name2feature = {}

    def extractFeatures(self):
        # Apply each rule, generating a corresponding report feature, which is
        # then stored in this object:
        for currRule in self.rules:
            currFeature = currRule.applyRule()

            # Store the current feature under this feature's name:
            self.name2feature[currFeature.getName()] = currFeature

    def toJSON(self):
        pass
        # Generate the output JSON file of the extracted features...

        # XXX FIXME: Implement by doing the following:
        # Just convert self.name2feature to a dictionary of dictionaries by calling
        # toDict() on each feature, and then return that final dictionary as a JSON
        # string.

        # return report_json_string

















































