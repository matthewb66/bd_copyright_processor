import regex
import itertools
import html2text


class CopyrightProcessor:
    """Process copyright to cleanup noise caused by licenses and unfiltered language parts"""
    def __init__(self, languages, max_lines):
        self.languages = languages
        self.max_lines = max_lines
        self.code_fragments = self.load_code_fragements()
        self.license_fragments = self.load_license_fragments() 
        
    # called by __init__
    def load_code_fragements(self):
        """Load code fragments sorted by language"""

        code_dict = {}
        code_dict['csharp'] = []
        code_dict['csharp'].append("#(using|define|if|else|endif|nullable).*")          # Remove C# preprocessor directives
        #code_dict['csharp'].append("(//|/\*|\*/)\s\w.*")                               # Remove comments

        code_dict['cpp'] = []
        code_dict['cpp'].append("#(include|define|if|else|endif|pragma).*")             # Remove C/C++ preprocessor directives
        #code_dict['cpp'].append("(//|/\*|\*/)\s\w.*")                                  # Remove comments
        code_dict['cpp'].append("print.*")                                              # Remove print

        code_dict['java'] = []
        code_dict['java'].append("@(Deprecated|SuppressWarnings|version|param).*")      # Remove Java attributions
        code_dict['java'].append("package \w.*")                                        # Remove Java packages
        #code_dict['java'].append("(//|/\*|\*/)\s\w.*")                                 # Remove comments


        code_dict['js'] = []
        code_dict['js'].append("^(static|public|protected|private|class|interface).*")  # Remove JavaScript
        #code_dict['js'].append("(//|/\*|\*/)\s\w.*")                                   # Remove comments

        code_dict['xml'] = []
        code_dict['xml'].append("<!--\s\w.*")                                           # Remove XML comments
        code_dict['xml'].append("-->\s\w.*")

        code_dict['shell'] = []
        #code_dict['shell'].append("#\s\w.*")                                           # Remove shell comments
        code_dict['shell'].append("REM\s\w.*")
        code_dict['shell'].append("<#\s\w.*")
        code_dict['shell'].append("@echo\s\w.*")

        #code_dict['sql'] = []
        #code_dict['sql'].append("--\s\w.*")                                             # Remove SQL comments
        
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

    # called by __init__
    def load_license_fragments(self):
        """Load license fragments to remove identified ones by remove_license_fragments"""
       
        license_fragments = []
        #license_fragments.append("It is.*")
        #license_fragments.append("You may.*")
        #license_fragments.append("Under the terms of.*")
        #license_fragments.append("(Licensed|Released) (under|to).*")
        #license_fragments.append("Redistribut.*")
        #license_fragments.append("Permission (is|to).*")
        #license_fragments.append("Everyone (is|must).*")
        #license_fragments.append("The.* this file.*",) 
        #license_fragments.append("Verbatim.* distribution.*")
        #license_fragments.append("This.* (is|file|script|software|library|program|product|license).*")

        license_fragments.append("Copyright[sed]{0,2}:?.?\s"
                                 "(see|all|and|or|on|is|as|in|to|if|are|for|the|attribut|situation|under|dnl|debian|follow|"
                                 "year|notice|uri|header|message|date|field|block|list|string|etc|stuff|line|like|"
                                 "act|law|patent|permission|grant|proposal|applies|disclaimer|software|interface|"
                                 "file|library|status|format|information|symbol|statement|tag|changelog)\s.*")
        license_fragments.append("Copyright.* [<\[]?year[>\]]?.*")
        license_fragments.append("Copyrights .*")
        license_fragments.append("\(c\) symbol.*")
        #license_fragments.append("(?<!\w\s)©.*")
        

        return license_fragments
    
    def contains_regex(self, text):
        return True if "*" in text else False

    def remove_code_fragments(self, copyright_text):
        """Remove code fragments using loaded code fragments only"""
        for code in self.code_fragments:
            # TODO do proper test for regular expression
            if self.contains_regex(code):
                copyright_text = regex.sub(code, "", copyright_text)
            else:
                copyright_text = copyright_text.replace(code, "")

        return copyright_text.strip()

    def remove_license_fragments(self, copyright_text):
        """Remove licenses, where copyright is part of a license and vice versa"""

        for lf in self.license_fragments:
            copyright_text = regex.sub(lf, "", copyright_text, flags=regex.IGNORECASE)

        return copyright_text.strip()

    def remove_copyright_lines(self, copyright_text):
        """Remove copyright lines that are garbage, like a third line"""
        
        # Concat all lines before max_linex with "\n"
        # Remove all lines after max_lines
        copyright_text = copyright_text                                     \
            .replace("\\t", " ").replace("\t", " ")                         \
            .replace("\\0", "\n").replace("\0", "\n")                       \
            .replace("\\r", "\r").replace("\\n", "\n").replace("\r\n", "\n")
        
        if (self.max_lines > 1):
            copyright_text = copyright_text.replace("\n", " ", self.max_lines-1)
        copyright_text = regex.sub("\n.*", "", copyright_text)

        return copyright_text.strip()

    def remove_separators_and_boxes(self, copyright_text):
        """Remove separators and boxes, which are ofter used to separate or delineate copyrights entries"""

        # Remove * and ~ , this often comes from comments where there is a box of asterisks like this:
        # **************
        # * box of text
        # **************
        copyright_text = copyright_text.replace("*","")
        copyright_text = copyright_text.replace("~ ~","")
        
        # Remove ============= , happens Often used to delineate text. i.e:
        # ===================================
        # copyright (C) 2020 Rob Haines
        copyright_text = regex.sub("======.*", "", copyright_text, flags=regex.IGNORECASE)
        copyright_text = regex.sub("------.*", "", copyright_text, flags=regex.IGNORECASE)
        
        return copyright_text
    
    def remove_whitespaces(self, copyright_text):
        """Reduce Multiple spaces to single spaces to improve merge"""
        copyright_text = copyright_text.strip()
        copyright_text = regex.sub("\s+", " ", copyright_text)  

        return copyright_text

    def remove_punctuations(self, copyright_text):
        """Remove punctuations, improves ability to merge copyrights"""
        copyright_text = regex.sub('[,.]\s?$', '', copyright_text)  
        copyright_text = regex.sub('".*', '', copyright_text)

        return copyright_text

    def remove_tags(self, copyright_text):
        """Remove tags by converting into text only"""
        copyright_text = html2text.html2text(copyright_text)

        return copyright_text

    def remove_brackets(self, copyright_text):
        """Remove < > and [ ] , typically used around mail and urls e.g. <fred@flintstones.com>"""
        copyright_text = copyright_text.replace("<", "").replace(">", "")
        copyright_text = copyright_text.replace("[", "").replace("]", "")
        #copyright_text = copyright_text.replace("{", "").replace("}", "")
        #copyright_text = copyright_text.replace("(", "").replace(")", "")

        return copyright_text.strip()

    def remove_control_chars(self, s):

        control_chars = ''.join(map(chr, itertools.chain(range(0x00, 0x20), range(0x7f, 0xa0))))
        control_char_regex = regex.compile('[%s]' % regex.escape(control_chars))

        return control_char_regex.sub(' ', s)
  
    def preprocess(self, copyright_text):
        """ Process raw copyrights to remove unnecessary text"""
    
        # Remove copyright lines that are garbage, like e.g. a third line"
        copyright_text = self.remove_copyright_lines(copyright_text)

        # Remove tags using html2text
        # copyright_text = self.remove_tags(copyright_text)        

        # Remove code fragments from different languages
        copyright_text = self.remove_code_fragments(copyright_text)

        # Remove licenses, where copyright contains license and vice versa
        copyright_text = self.remove_license_fragments(copyright_text)
                              
        # Remove brackets typically used around mail and urls
        # copyright_text = self.remove_brackets(copyright_text)

        # Remove all punctuations that are not required 
        # copyright_text = self.remove_punctuations(copyright_text)

        # Remove multiples of whitespaces 
        copyright_text = self.remove_whitespaces(copyright_text)

         # Remove separators and boxes
        copyright_text = self.remove_separators_and_boxes(copyright_text)

        # Remove any non unicode characters
        copyright_text = self.remove_control_chars(copyright_text)
        
        return copyright_text
    
    def postprocess(self, copyright_text, min_holder_len = 7):
        """ Postprocess to withdraw invalid copyrights """
        p = regex.compile(r'((?:copyright|\(c\)|[\u00A9])[\t ]*:?[\t ]*)+'
                          r'([<\[\(]?\d{4}~?:?,?(?:[\t ]*(?:-|,|\/)*(?:[\t ]*\d{4}))*[>\]\)]?[\t ]+)?'
                          r'([\w\t \-.,<>*&@\(\)\[\]]{3,255})', flags=regex.IGNORECASE)
            
        m = p.search(copyright_text)
        if m:
            copyright = m.group(1)
            date = m.group(2)
            holder = m.group(3)

            if copyright:
                if date and holder:
                    return copyright_text, ""
                elif holder:
                    if len(str(holder)) >= min_holder_len and str(holder).lower().find("copyright") == -1 :
                        return copyright_text, ""
            
        return "", copyright_text
