'''
Created on Dec 1, 2015

@author: thowhi
'''

import pdb

class DocumentFormat(object):
    '''
    Document formatting options, initially intended for specifying the format
    of genomic report latex documents.
    '''

    ENGLISH = "English"
    SWEDISH = "Swedish"

    def __init__(self, checked, unchecked, fontfamily="Roman", fontsize="10pt",
                 tablepos="left", language="Swedish", margin="3cm", lmargin="1cm",
                 rmargin="1cm", sans_font_default="phv", logos=""):
        '''
        Raises a ValueError if any of the specified option values are invalid.

        checked: string specifying file location
        unchecked: string specifying file location
        fontfamily: Roman/SansSerif
        fontsize: latex font size specifier string
        tablepos: left/center
        language: Swedish/English
        margin: latex margin size specifier string
        sans_font_default: latex string indicating default sans serif font
        logos: string containing a comma-separated list of logos to include
        '''

        self._checked = checked
        self._unchecked = unchecked
        if not fontfamily in ["Roman", "SansSerif"]:
            raise ValueError("Invalid font family for DocumenFormat: " + fontfamily)
        self._fontfamily = None
        if fontfamily == "Roman":
            self._fontfamily = "\\rmdefault"
        elif fontfamily == "SansSerif":
            self._fontfamily = "\\sfdefault"
        self._fontsize = fontsize
        if not tablepos in ["left", "center"]:
            raise ValueError("Invalid table position for DocumenFormat: " + tablepos)
        self._tablepos = tablepos
        if not language in ["Swedish", "English"]:
            raise ValueError("Invalid language for DocumenFormat: " + language)
        self._language = language
        self._margin = margin
        self._lmargin = lmargin
        self._rmargin = rmargin
        self._sans_font_default = sans_font_default
        self._logo_files = logos.split(",")

    def get_checked_checkbox(self):
        return self._checked

    def get_unchecked_checkbox(self):
        return self._unchecked

    def get_fontfamily(self):
        return self._fontfamily

    def get_fontsize(self):
        return self._fontsize

    def get_table_pos(self):
        return self._tablepos

    def get_language(self):
        return self._language

    def get_margin(self):
        return self._margin

    def get_lmargin(self):
        return self._lmargin

    def get_rmargin(self):
        return self._rmargin

    def get_sans_font_default(self):
        return self._sans_font_default

    def get_logo_files(self):
        return self._logo_files

    def make_latex(self):
        return u'''\\documentclass[10pt]{article}
\\usepackage[table]{xcolor}
\\usepackage{booktabs}
\\usepackage[top=0.75cm,lmargin=1cm,rmargin=1cm,bottom=1cm]{geometry}
\\usepackage[utf8]{inputenc}
\\usepackage{graphicx}
\\usepackage{longtable}
\\usepackage{changepage}
\\usepackage{fancyhdr}
\\usepackage[many]{tcolorbox}
\\usepackage{colortbl}
\\usepackage{multicol}
\\usepackage{multirow}
\\usepackage{setspace}

\\setlength{\\parindent}{0pt}


\\definecolor{grey}{rgb}{0.2, 0.2, 0.2}

\\definecolor{lightgrey}{rgb}{0.7, 0.7, 0.7}

\\definecolor{ratherlightgrey}{rgb}{0.9, 0.9, 0.9}

\renewcommand*{\familydefault}{%s}
\renewcommand{\sfdefault}{%s}
''' % (self.get_fontfamily(), self.get_sans_font_default()) #self.get_fontsize(), self.get_margin(), self.get_lmargin(), self.get_rmargin(),
    # NOTE: I have hard-coded the font size and margin sizes above rather than
    # allowing these to be flexible as I had originally planned. I think this
    # is necessary in order to achieve the required document appearance.

    def make_logos_latex(self):
        '''\includegraphics[width=50mm]{/Users/thowhi/reportgen/ki-logo_cmyk_5.png} & \includegraphics[width=50mm]{/Users/thowhi/reportgen/ALASCCA_logo.png}'''
        format_string = " c " * len(self.get_logo_files())
        toks = ["\includegraphics[width=35mm]{" + filename + "}" for filename in self.get_logo_files()]
        contents_string = " & ".join(toks)
        return u'''
\\begin{tabular}[t]{ %s }
    %s \\tabularnewline
\\end{tabular}
}
''' % (format_string, contents_string)































