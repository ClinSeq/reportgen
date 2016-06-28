'''
Created on Dec 1, 2015

@author: thowhi
'''

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
