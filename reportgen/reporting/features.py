# -*- coding: utf-8 -*-
from reportgen.rules.general import MutationStatus
import pdb

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
        # FIXME: This whole way of doing this is broken. Fix properly at some point:
        #if not title_latex == None:
        #    feature_latex = feature_latex + u"\\subsubsection*{%s}\n" % (title_latex)
        if not body_latex == None:
            feature_latex = feature_latex + body_latex
        return feature_latex

    def make_content_body(self, doc_format):
        '''All implementing classes must implement a function for generating
        a string containing latex code for the content body.'''

    def make_title(self, doc_format):
        '''All implementing classes must implement a function for generating
        a string containing latex code for a title.'''

    # Concrete classes must implement toDict() and fromDict()


class DatesReport(ReportFeature):
    '''A report of key dates relevant to a given report.
    '''

    def __init__(self, blood_sample_id, tumor_sample_id,
                 blood_sample_date, tumor_sample_date,
                 blood_referral_id, tumor_referral_id):
        self._blood_sample_id = blood_sample_id
        self._tumor_sample_id = tumor_sample_id
        self._blood_referral_id = blood_referral_id
        self._tumor_referral_id = tumor_referral_id
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
            return u'''Blodprov taget %s, remiss-ID %s, etikett %s \\\\
Tumörprov taget %s, remiss-ID %s, etikett %s \\\\''' % \
                   (self._blood_sample_date, self._blood_referral_id, self._blood_sample_id,
                    self._tumor_sample_date, self._tumor_referral_id, self._tumor_sample_id)


class AlasccaClassReport(ReportFeature):
    '''
    '''

    NAME = "ALASCCA class"

    MUTN_CLASS_A = "Mutation class A"
    MUTN_CLASS_B = "Mutation class B"
    NO_MUTN = "No mutation"
    NOT_DET = "Not determined"
    VALID_STRINGS = [MUTN_CLASS_A, MUTN_CLASS_B, NO_MUTN]

    def __init__(self):
        self._pathway_class = None

    @staticmethod
    def get_name():
        return "ALASSCA Class Report"

    def set_class(self, pathway_class):
        assert pathway_class in self.VALID_STRINGS
        self._pathway_class = pathway_class

    def to_dict(self):
        return {self.NAME:self._pathway_class}

    def set_from_dict(self, input_dict):
        pathway_class = input_dict[self.NAME]
        self._pathway_class = pathway_class

    def make_title_latex(self, doc_format):
        if doc_format.get_language() == doc_format.ENGLISH:
            return u'''PI3K signaling pathway'''
        else:
            assert doc_format.get_language() == doc_format.SWEDISH
            return u'''{\\Large Randomisering till ALASCCA-studien}'''

    def make_content_body(self, doc_format):
        class_a_box = doc_format.get_unchecked_checkbox()
        class_b_box = doc_format.get_unchecked_checkbox()
        no_mutations_box = doc_format.get_unchecked_checkbox()
        not_determined_box = doc_format.get_unchecked_checkbox()
        if self._pathway_class == self.MUTN_CLASS_A:
            class_a_box = doc_format.get_checked_checkbox()
        if self._pathway_class == self.MUTN_CLASS_B:
            class_b_box = doc_format.get_checked_checkbox()
        if self._pathway_class == self.NO_MUTN:
            no_mutations_box = doc_format.get_checked_checkbox()
        if self._pathway_class == self.NOT_DET:
            not_determined_box = doc_format.get_checked_checkbox()

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
            return u'''\\tcbox[left=0mm,right=-1mm,top=0mm,bottom=0mm,boxsep=0mm,
       boxrule=0.4pt, colframe=grey, colback=white]
{
\\begin{tabular}{l l}
\\includegraphics{%s} & Mutationsklass A, patienten kan randomiseras \\\\
\\includegraphics{%s} & Mutationsklass B, patienten kan randomiseras \\\\
& \\\\
\\includegraphics{%s} & Inga mutationer, patienten kan \emph{ej} randomiseras \\\\
\\includegraphics{%s} & Ej utförd/ej bedömbar, patienten kan \emph{ej} randomiseras \\\\
\\end{tabular}
}''' % (class_a_box, class_b_box, no_mutations_box, not_determined_box)


class MsiReport(ReportFeature):
    '''
    '''

    MSS = "MSS/MSI-L"
    MSI = "MSI-H"
    NOT_DETERMINED = "Not determined"
    VALID_STRINGS = [MSS, MSI, NOT_DETERMINED]

    NAME = "MSI Status"

    def __init__(self):
        self._msi_status = None

    def to_dict(self):
        return {self.NAME:self._msi_status}

    def set_from_dict(self, input_dict):
        msi_status = input_dict[self.NAME]
        self._msi_status = msi_status

    def get_status(self):
        return self._msi_status

    def set_status(self, msi_status):
        self._msi_status = msi_status

    @staticmethod
    def get_name():
        return "MSI Report"

    def make_title_latex(self, doc_format):
        if doc_format.get_language() == doc_format.ENGLISH:
            return u'''Microsatellite instability (MSI)'''
        else:
            assert doc_format.get_language() == doc_format.SWEDISH
            return u'''{\\large Mikrosatellitinstabilitet\\\\(MSI)}'''

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
            return u'''  \\begin{tabular}{l | l}
MSI-H\\textsuperscript{1} & \\includegraphics{%s} \\\\
MSS/MSI-L\\textsuperscript{2} & \\includegraphics{%s} \\\\
Ej bedömbar & \\includegraphics{%s} \\\\
  \\end{tabular}''' % (mss_box, msi_box, not_determined_box)


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

    @staticmethod
    def get_name():
        return "Simple Somatic Mutations Report"

    def add_gene(self, gene_name):
        # Adds a gene, with mutationStatus as "NoMutation" and mutationList as
        # empty by default:
        self._symbol2mutation_status[gene_name] = MutationStatus()

    def add_mutation(self, mutation, flag):
        gene_symbol = mutation.get_altered_gene().get_gene().get_symbol()
        assert self._symbol2mutation_status.has_key(gene_symbol)
        self._symbol2mutation_status[gene_symbol].add_mutation(mutation, flag)

    def to_dict(self):
        output_dict = {}
        for symbol in self._symbol2mutation_status.keys():
            mutation_status = self._symbol2mutation_status[symbol]
            output_dict[symbol] = mutation_status.to_dict()

        return output_dict

    def set_from_dict(self, input_dict):
        self._symbol2mutation_status = input_dict

    # XXX UPDATE THIS METHOD TO MAKE IT WORK WITH THE UPDATED _SYMBOL2MUTATIONSTATUS
    # ATTRIBUTE:
    def make_title_latex(self, doc_format):
        if doc_format.get_language() == doc_format.ENGLISH:
            return u'''Other mutations'''
        else:
            assert doc_format.get_language() == doc_format.SWEDISH
            return u'''{\\large Övriga mutationer}'''

    def make_content_body(self, doc_format):
        body_string = u'''  \\begin{tabular}{l | l | l | l | l}
  '''
        assert doc_format.get_language() == doc_format.SWEDISH
        body_string = body_string + u'''Gen & Mutation & Ej mutation & Ej bedömbar & Kommentar \\tabularnewline
\\arrayrulecolor{grey}\hline
\\arrayrulecolor{grey}\hline
'''
        genes = self._symbol2mutation_status.keys()
        genes.sort()
        for gene in genes:
            # Set up box image paths and comments string:
            mut_box = doc_format.get_unchecked_checkbox()
            no_mut_box = doc_format.get_unchecked_checkbox()
            not_det_box = doc_format.get_unchecked_checkbox()
            mutn_info = self._symbol2mutation_status[gene]

            # FIXME: This is not nice. The structure of symbol2mutation_status
            # is different when the object is generated in the first place and
            # when it is read from the JSON file. This affects how the HGVSp
            # values are retrieved here:
            mutn_status = mutn_info["Status"]
            comments = " ".join(map(lambda alteration_dict: alteration_dict["HGVSp"],
                                    mutn_info["Alterations"]))
            if len(comments) == 0:
                comments = ""

            if mutn_status == MutationStatus.MUT:
                mut_box = doc_format.get_checked_checkbox()
            if mutn_status == MutationStatus.NO_MUT:
                no_mut_box = doc_format.get_checked_checkbox()
            if mutn_status == MutationStatus.NOT_DETERMINED:
                not_det_box = doc_format.get_checked_checkbox()

            # HACK: Need to display a superscript if the gene is NRAS, BRAF,
            # or KRAS. Hard-coding this at this point:
            superscript_text = ""
            if gene == "BRAF":
                superscript_text = "\\textsuperscript{3}"
            elif gene == "NRAS":
                superscript_text = "\\textsuperscript{4}"
            elif gene == "KRAS":
                superscript_text = "\\textsuperscript{4}"

            # Add a row for the current gene:
            body_string = body_string + u'''\\textit{%s}%s &
            \\includegraphics{%s} &
            \\includegraphics{%s} &
            \\includegraphics{%s} & %s \\\\''' % (gene, superscript_text, mut_box, no_mut_box, not_det_box, comments)

        body_string += u'\n\\end{tabular}'
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


class ReportLegend(ReportFeature):
    '''
    '''

    def __init__(self):
        '''
        '''

    # XXX CONTINUE HERE: ADD CODE FOR GENERATING LATEX CODE AS REQUIRED BY MARKUS'
    # UPDATED REQUIREMENTS.
    def make_title(self, doc_format):
        if doc_format.get_language() == doc_format.ENGLISH:
            return u'''Other information'''
        else:
            assert doc_format.get_language() == doc_format.SWEDISH
            return u'''Övriga information'''

    def make_content_body(self, doc_format):
        # FIXME: Need to double-check these texts:
        assert doc_format.get_language() == doc_format.SWEDISH
        return u'''\\textbf{Tolkning} \\par
{\\small
Tilläggsinformationen från ClinSeq-panelen är av potentiellt klinisk betydelse. Analyserna är utförda på forskningsbasis med en för forskning validerad men inte kliniskt ackrediterad metod. För tolkningsstöd se nedan. \\\\

\\textbf{Mikrosatellitinstabilitet (MSI)}\\\\
\\textbf{\\textsuperscript{1} MSI-H (MSI-high):} Tumören uppvisar höggradig mikrosatellitinstabilitet, vilket innebär inaktivering av DNA mismatch-reparation. MSI-H kan orsakas av förvärvade (somatiska) eller medfödda (ärftliga) genetiska förändringar. \\\\
\\textbf{\\textsuperscript{2} MSS/MSI-L (MSI-low):} Tumören uppvisar mikrosatellitstabilitet eller visar MSI för enstaka markörer. \\\\

\\textbf{Kliniska situationer där MSI kan ha betydelse}\\\\
Tumörer med MSI-H i stadium II har en god prognos med lägre recidivrisk än tumörer med MSS/MSI-L. Fyndet bör vägas in i beslut om adjuvant cytostatikabehandling enligt nationellt vårdprogram. Vid fynd av MSI-H utan samtidig \\textit{BRAF}-mutation (se nedan) bör familjeanamnes göras och ställningstagande till vidare onkogenetisk utredning tas. Syftet med en onkogenetisk utredning är att identifiera familjer med ärftlig kolorektalcancer. I dessa familjer skall särskilda kontrollprogram erbjudas för familjemedlemmar med ökad risk. \\\\

\\textbf{Aktiverande mutationer i \\textit{BRAF}, \\textit{KRAS} och \\textit{NRAS}}\\\\
\\textbf{\\textsuperscript{3} För \\textit{BRAF}} rapporteras den mutation som med nuvarande kunskap betraktas som aktiverande (V600E). Tumörer med denna \\textit{BRAF}-mutation är resistenta mot EGFR-hämmande behandling med antikropparna cetuximab och panitumumab, och denna behandling skall enligt nationellt vårdprogram då inte användas. \\textit{BRAF}-mutation är vid avancerade tumörer (stadium IV) en negativ prognostisk faktor. \\\\
\\textbf{\\textsuperscript{4} För \\textit{KRAS} och \\textit{NRAS}} rapporteras de mutationer som med nuvarande kunskap betraktas som aktiverande (kodon 12, 13, 59, 61, 117 och 146). Tumörer med dessa \\textit{KRAS}/\\textit{NRAS}-mutationer är resistenta mot EGFR-hämmande behandling med antikropparna cetuximab och panitumumab, och denna behandling skall enligt nationellt vårdprogram då inte användas. \\\\

\\textbf{Kontakt}\\\\
Frågor om analysmetoden i ALASCCA-studien kan skickas till ALASCCA@meb.ki.se
}
\\par
'''