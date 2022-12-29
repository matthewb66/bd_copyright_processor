import regex
import itertools
import html2text
from unidecode import unidecode


class CopyrightProcessor:
    """Process copyright to cleanup noise caused by licenses and unfiltered language parts"""

    def __init__(self, languages, max_lines):
        self.languages = languages
        self.max_lines = max_lines
        self.code_fragments = self.load_code_fragments()
        self.license_fragments = self.load_license_fragments()

    def load_code_fragments(self):
        """Load code fragments sorted by language"""

        code_dict = {}

        code_dict['general'] = []
        code_dict['general'].append(r"(\bobject\b|\bvoid\b|\bnull\b|\bassert\b|\breturn\b|\bself\b).*")  # statements
        code_dict['general'].append(r"(//|/\*|\*/|\*)")  # comments
        code_dict['general'].append(r"#(\binclude\b|\bdefine\b|\bif\b|\belse\b|\bend\b|\bpragma\b).*")  # preprocessor directives

        code_dict['csharp'] = []
        code_dict['csharp'].append(r"#(\busing\b|\bnullable\b).*")  # C# preprocessor directives

        # code_dict['c'] = []

        code_dict['python'] = []
        code_dict['python'].append(r"@(\bstaticmethod\b|\bproperty\b|\bclassmethod\b)")

        code_dict['java'] = []
        code_dict['java'].append(r"@(\bDeprecated\b|\bSuppressWarnings\b|\bversion\b|\bparam\b).*")  # Java attributions
        code_dict['java'].append(r"(\bpackage\b|\$Id).*")  # Java packages

        code_dict['js'] = []
        code_dict['js'].append(r"(\bstatic\b|\bpublic\b|\bprotected\b|\bprivate\b|\bclass\b|\binterface\b).*")  # JavaScript

        code_dict['xml'] = []
        code_dict['xml'].append(r"\<\!\-\-.*")  # XML comments
        code_dict['xml'].append(r"\-\->.*")

        code_dict['shell'] = []
        code_dict['shell'].append(r"#.*$")  # shell comments
        code_dict['shell'].append(r"\brem\b.*$")
        code_dict['shell'].append(r"<#.*$")

        code_dict['sql'] = []
        code_dict['sql'].append(r"\-\-.*$")  # SQL comments

        filtered_code_fragments = []

        # add unique all code fragments
        if len(self.languages) == 0 or "all" in self.languages:
            self.languages = list(code_dict.keys())

        # add unique code fragments sorted by languages
        for language in self.languages:
            if language in list(code_dict.keys()):
                for centry in code_dict[language]:
                    if centry not in filtered_code_fragments:
                        filtered_code_fragments.append(centry)

        return filtered_code_fragments

    def load_license_fragments(self):
        """Load license fragments to remove identified ones by remove_license_fragments"""

        license_fragments = []
        license_fragments.append("Under the terms of.*")
        license_fragments.append("(Licensed|Released) under.*")
        license_fragments.append("Redistribution and.*")
        license_fragments.append("Permission (is|to).*")
        license_fragments.append("Everyone (is|must).*")
        license_fragments.append("The.* licenses this file.*", )
        license_fragments.append("Verbatim copying and distribution.*")
        license_fragments.append("This.* (is|file|script|library|program|product|license).*")

        # Need to check if this is OK? Possibly add it back again after merging?
        # license_fragments.append("All rights Reserved.*")

        return license_fragments

    # def contains_regex(self, copyright_text, thisregex):
    #     # return True if "*" in text else False
    #     search_regex = regex.compile(thisregex, regex.IGNORECASE)
    #     if search_regex.search(copyright_text):
    #         return True
    #     else:
    #         return False

    def remove_code_fragments(self, copyright_lines):
        """Remove code fragments using loaded code fragments only"""
        mod_lines = []
        for line in copyright_lines:
            mod_line = line
            for code in self.code_fragments:
                code_regex = regex.compile(code, regex.IGNORECASE)
                if code_regex.search(mod_line):
                    mod_line = code_regex.sub('', mod_line)
            mod_lines.append(mod_line.strip())

        return mod_lines

    def remove_license_fragments(self, copyright_lines):
        """Remove licenses, where copyright is part of a license and vice versa"""
        mod_lines = []

        for line in copyright_lines:
            mod_line = line
            for lf in self.license_fragments:
                mod_line = regex.sub(lf, "", mod_line, flags=regex.IGNORECASE)
            mod_lines.append(mod_line.strip())

        return mod_lines

    def remove_extra_lines(self, copyright_lines):
        """Remove copyright lines that are garbage, like a third line"""

        # Concat all lines before max_linex with "\n"
        # Remove all lines after max_line
        mod_lines = []
        linenum = 0
        for line in copyright_lines:
            modline = regex.sub(r'(\r\n|\\n|\t)', '\n', line)
            mod_lines.append(modline.strip())
            if linenum >= self.max_lines:
                break
            linenum += 1

        return mod_lines

    def remove_separators_and_boxes(self, copyright_lines):
        """Remove separators and boxes, which are ofter used to separate or delineate copyrights entries"""

        # Remove * and ~ , this often comes from comments where there is a box of asterisks like this:
        # **************
        # * box of text
        # **************
        mod_lines = []
        for line in copyright_lines:
            mod_line = line.replace("*", "").replace("~ ~*", "").replace("##*", "#")
            # Remove ============= , happens Often used to delineate text. i.e:
            # ===================================
            # copyright (C) 2020 Rob Haines
            mod_line = regex.sub("======*", "", mod_line, flags=regex.IGNORECASE)
            mod_line = regex.sub("------*", "", mod_line, flags=regex.IGNORECASE)
            mod_lines.append(mod_line)

        return mod_lines

    def remove_whitespaces(self, copyright_lines):
        """Reduce Multiple spaces to single spaces to improve merge"""
        mod_lines = []
        for line in copyright_lines:
            mod_line = regex.sub(r"\s+", " ", line.strip())
            mod_lines.append(mod_line)

        return mod_lines

    def remove_punctuations(self, copyright_lines):
        """Remove punctuations, improves ability to merge copyrights"""
        mod_lines = []
        for line in copyright_lines:
            mod_line = regex.sub(r'[,.]\s?$', '', line)
            mod_line = regex.sub(r'".*', '', mod_line)
            mod_lines.append(mod_line)

        return mod_lines

    def remove_tags(self, copyright_lines):
        """Remove tags by converting into text only"""
        mod_lines = []
        for line in copyright_lines:
            mod_line = html2text.html2text(line)
            mod_lines.append(mod_line.strip())

        return mod_lines

    def remove_brackets(self, copyright_lines):
        """Remove < > and [ ] , typically used around mail and urls e.g. <fred@flintstones.com>"""
        mod_lines = []
        for line in copyright_lines:
            # mod_line = regex.sub(r'(\<|\>|\[|\]|\{|\}|\(|\))', '', line)
            mod_line = regex.sub(r'(\<|\>|\[|\]|\{|\})', '', line)

            mod_lines.append(mod_line.strip())

        return mod_lines

    def remove_control_chars(self, copyright_lines):

        control_chars = ''.join(map(chr, itertools.chain(range(0x00, 0x20), range(0x7f, 0xa0))))
        control_char_regex = regex.compile('[%s]' % regex.escape(control_chars))
        mod_lines = []
        for line in copyright_lines:
            mod_line = control_char_regex.sub(' ', line)
            mod_line = unidecode(mod_line)
            mod_lines.append(mod_line)

        return mod_lines

    def replace_copyright_text(self, copyright_lines):
        """Replace copyright sign by (C)"""
        """Replace 'Copyright' by 'Copyright (C)'"""
        """Replace '(C)' by 'Copyright (C)'"""
        mod_lines = []
        copyright_regex = regex.compile(r"\bcopyright\b", regex.IGNORECASE)

        for line in copyright_lines:
            mod_line = line.replace("&copy", "(C)").replace("&#169;", "(C)").replace("©", "(C)").\
                replace("@author", "(C)").replace("(c)", "(C)")
            mod_line = copyright_regex.sub('Copyright', mod_line)
            mod_line = regex.sub(r"^((?!Copyright)\(C\) |Copyright (?!\(C\)))", "Copyright (C) ", mod_line)

            mod_lines.append(mod_line)

        return mod_lines

    def remove_blank_lines(self,copyright_lines):
        mod_lines = []
        for line in copyright_lines:
            if len(line.strip()) > 0:
                mod_lines.append(line.strip())
        return mod_lines

    def preprocess(self, copyright_text):
        """ Process raw copyrights to remove unnecessary text"""
        # input = copyright_text
        copyright_lines = copyright_text.split('\n')

        # Remove copyright lines that are garbage, like e.g. a third line"
        copyright_lines = self.remove_extra_lines(copyright_lines)

        # Remove tags using html2text
        copyright_lines = self.remove_tags(copyright_lines)

        # Remove code fragments from different languages
        copyright_lines = self.remove_code_fragments(copyright_lines)

        # Remove licenses, where copyright contains license and vice versa
        copyright_lines = self.remove_license_fragments(copyright_lines)

        # Remove brackets typically used around mail and urls
        copyright_lines = self.remove_brackets(copyright_lines)

        # Remove all punctuations that are not required
        copyright_lines = self.remove_punctuations(copyright_lines)

        # Remove multiples of whitespaces
        copyright_lines = self.remove_whitespaces(copyright_lines)

        # Remove separators and boxes
        copyright_lines = self.remove_separators_and_boxes(copyright_lines)

        # Remove any non unicode characters
        copyright_lines = self.remove_control_chars(copyright_lines)

        # Remove copyright symbols and replace with "(C)"
        copyright_lines = self.replace_copyright_text(copyright_lines)

        copyright_lines = self.remove_blank_lines(copyright_lines)

        return ' '.join(copyright_lines)
