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
                 tablepos="left", language="Swedish"):
        '''
        Raises a ValueError if any of the specified option values are invalid.

        checked: string specifying file location
        unchecked: string specifying file location
        fontfamily: Roman/SansSerif
        fontsize: latex font size specifier string
        tablepos: left/center
        language: Swedish/English
        '''

        self._checked = checked
        self._unchecked = unchecked
        if not fontfamily in ["Roman", "SansSerif"]:
            raise ValueError("Invalid font family for DocumenFormat: " + fontfamily)
        self._fontfamily = fontfamily
        self._fontsize = fontsize
        if not tablepos in ["left", "center"]:
            raise ValueError("Invalid table position for DocumenFormat: " + tablepos)
        self._tablepos = tablepos
        if not language in ["Swedish", "English"]:
            raise ValueError("Invalid language for DocumenFormat: " + language)
        self._language = language

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

    def make_latex(self):
        return '''\documentclass[%s]{article}
\usepackage{booktabs}
\usepackage[margin=2cm]{geometry}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
''' % (self.get_fontsize())


































