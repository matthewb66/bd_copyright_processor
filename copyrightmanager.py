# from blackduck.HubRestApi import HubInstance
import regex
import html2text
import itertools
# import sys
import logging


class CopyrightManager:
    """Manage copyrights for a BOM component"""
    # component_name = ""
    # hubInstance = None
    # origin = None
    # copyrights = None
    # matches = {}
    # final_copyrights = []
    # rejected_matches = []

    def __init__(self, hub, component_name, copyrights):
        self.hub = hub
        self.component_name = component_name
        self.copyrights = copyrights
        self.matches = {}
        # hubInstance = None
        self.origin = None
        self.final_copyrights = []
        # self.rejected_matches = []

        logging.debug(f"Created copyright manager for {self.component_name}")

    def add_copyrights(self, copyrights):
        self.copyrights.extend(copyrights)

    # def load_copyrights(self):
    #     url = self.hub.get_link(self.origin, "component-origin-copyrights")
    #     url = url + "?limit=1000"
    #     self.copyrights = self.hub.execute_get(url).json().get('items', [])
    #     logging.debug("length {}".format(len(self.copyrights)))

    # def disable_all_copyrights(self, source='KB'):
    #     for copyright in self.copyrights:
    #         if source != copyright['source']:
    #             continue
    #         copyright.update({'active': False})
    #
    #     url = self.hub.get_link(self.origin, "component-origin-copyrights")
    #     response = self.hub.execute_put(url, data=self.copyrights)

    def count_orig_copyrights(self):
        return len(self.copyrights)

    def count_final_copyrights(self):
        return len(self.final_copyrights)

    def output_copyrights_text(self, showall):
        output_string = f"Component: {self.component_name}\n"

        if self.final_copyrights is None or len(self.final_copyrights) == 0:
            output_string += "  No Copyrights found\n"
        else:
            output_string += "Copyrights:\n"
            for copyright in self.final_copyrights:
                output_string += f"- {copyright}\n"
            if showall:
                output_string += "Original Copyrights:\n"
                for entry in self.copyrights:
                    output_string += f"- {entry['updatedCopyright']}\n"
        return output_string

    def output_copyrights_html(self, showall):
        output_string = f"<h2>Component: {self.component_name}</h2>\n"

        if self.final_copyrights is None or len(self.final_copyrights) == 0:
            output_string += "<ul><li>No Copyrights found</li></ul>\n"
        else:
            output_string += "<h3>Copyrights:</h3>\n<ul>"
            for copyright in self.final_copyrights:
                output_string += f"<li>{copyright}</li>\n"
            if showall:
                output_string += "</ul>\n<h3>Original Copyrights:</h3>\n<ul>"
                for entry in self.copyrights:
                    output_string += f"<li>{entry['updatedCopyright']}</li>\n"

            output_string += "</ul>"

        return output_string

    # def delete_all_custom_copyrights(self, source='CUSTOM'):
    #     for copyright in self.copyrights:
    #         if source != copyright['source']:
    #             continue
    #         url = copyright['_meta']['href']
    #         response = self.hub.execute_delete(url)
    #         logging.debug(f"{source} {url} {response}")

    # if args.not_filtered:
    #     copyright = copyright_entry['updatedCopyright'].replace("\r\n", " ").replace("\n", " ")
    #     copyright = copyright_entry['updatedCopyright']
    #     logging.debug("->" + copyright)
    #     output_file.write("   " + copyright + "\n")
    #
    #     return

    @staticmethod
    def remove_control_chars(s):
        # all_chars = (chr(i) for i in range(sys.maxunicode))
        # categories = {'Cc'}
        control_chars = ''.join(map(chr, itertools.chain(range(0x00, 0x20), range(0x7f, 0xa0))))

        control_char_regex = regex.compile('[%s]' % regex.escape(control_chars))

        return control_char_regex.sub(' ', s)

    def preprocess_copyrights(self):
        """ Process raw copyrights to remove unnecessary text"""
        # processed_copyrights = []
        strs_to_remove = ["\r\n", "\n", "\\n", "-->", "<!--", "// ", " //", "/*", "*/", "#", "rem ",
                          "<", ">", "[", "]", "*", "~ ~"]
        copyright_strs = ["&copy;", "&copy", "&#169;", "@author"]
        regex_to_remove = ["======.*",
                           "^\s*\*\s*",
                           "All rights Reserved.*",
                           "This library is free software.*",
                           "under the terms of.*",
                           "Licensed under.*",
                           "Released under.*",
                           "Permission is hereby.*",
                           "This product includes software.*",
                           "The .* licenses this file.*",
                           "Verbatim copying and distribution.*",
                           "This (file )*is free software.*",
                           "This program is made available under.*",
                           "package \w.*",
                           "@(Deprecated|SuppressWarnings|version|param).*",
                           "(static|public|protected|private|class|interface).*",
                           "[,.]\s?$"]

        for copyright_entry in self.copyrights:

            if not copyright_entry['active']:
                continue

            logging.debug("raw copyright:" + copyright_entry['updatedCopyright'])
            # Remove copyright symbols and replace with "(C)"
            copyright_text = copyright_entry['updatedCopyright']

            # Convert any html to text
            # copyright_text = html2text.html2text(copyright_text)

            # Remove any non unicode characters
            copyright_text = self.remove_control_chars(copyright_text)

            for reg in regex_to_remove:
                copyright_text = regex.sub(reg, "", copyright_text, flags=regex.IGNORECASE|regex.MULTILINE)

            for rem in strs_to_remove:
                copyright_text.replace(rem, '')

            for copy in copyright_strs:
                copyright_text.replace(copy, '(C)')

            # Clean up whitespace
            copyright_text = copyright_text.strip()

            logging.debug("processed copyright:" + copyright_text)
            copyright_entry["processed_copyright"] = copyright_text
        return

    def ignore_blank_copyrights(self):
        check_blank = []
        check_blank.append(
            regex.compile(r'(\bcopyright\b|\(c\)|&copy;|©|&#169;|@author\b)\s*([12][90][0-9]{2}[\s,]*){1,}$',
                          regex.IGNORECASE))
        check_blank.append(
            regex.compile(r'(\bcopyright\b|\(c\)|&copy;|©)\s*$', regex.IGNORECASE))

        for entry in self.copyrights:
            if not entry['active']:
                continue
            copyright_text = entry['processed_copyright']

            for reg in check_blank:
                m = reg.search(copyright_text)
                if m:
                    entry['active'] = False
                    break

            if not entry['active']:
                continue

            logging.debug("Trying to match: {}".format(copyright_text))
            # Look for url
            url_re = regex.compile(r"(\({0,1}+(?:https|http)://[^ ]*\){0,1})")
            url_matches = url_re.search(copyright_text)
            url = None
            if url_matches:
                url = url_matches.group(1)
                copyright_text = copyright_text.replace(url, "")
                copyright_text = copyright_text.strip()
                copyright_text = regex.sub('[,.]\s?$', '',
                                           copyright_text)  # Punctuation? Where we're going we don't need punctuation.
                logging.debug("Matched URL! :" + url)
                logging.debug("POST Processed:" + copyright_text + " url? " + str(url))

            key = copyright_text.lower()
            if key not in self.matches:
                self.matches[key] = {'url': {}, 'copyright': copyright_text, 'rejected': False}

            if url:
                self.matches[key]['url'][url] = 1

    def filter_copyrights(self):
        # p = regex.compile(r'copyright[ ][^0-9]{0,20}[12][90][0-9]{2}|\(C\)[ ,\-:;\w]{5}|©[ ,\-:\w]{5}|@author',
        #                   regex.IGNORECASE)

        # First check that the copyright contains the minimum required text (is this a copyright?)
        copy_minmatch = regex.compile(r'\bcopyright\b[\s:]|\(C\)\s|©|@author\b|\&\bcopy\b;\s|&#169;\s',
                          regex.IGNORECASE)
        copy_badmatch = regex.compile(
            r"((\bcopyright\b)(\s*[={}\)']|[-]|\(\)|\((true|false)\)|\ssign\b)|\bassert\b|\breturn\b|\bextends\b|\bself\.[_a-z]|\(self[,\)]|\bobject\)|\(void\)|\bnull\b)",
                          regex.IGNORECASE)

        for copyright in self.copyrights:
            url = None
            if not copyright['active']:
                logging.debug("Skipping inactive copyright")
                continue

            copyright_text = copyright['updatedCopyright']

            if copy_minmatch.search(copyright_text):
                # Looks like a copyright
                if not copy_badmatch.search(copyright_text):
                    # Not found a bad string

                    logging.debug("MATCHED Copyright text:" + copyright_text)
                    copyright['active'] = True
                    continue

            # Not a good copyright
            # self.rejected_matches.append(copyright['updatedCopyright'])
            copyright['active'] = False

        return

    def coalesce_dates(self):
        newMatches = {}
        non_coerced = []
        coerced = []
        coerce = []
        coerce.append(
            regex.compile(r'(?:\(c\)\s)((?:[12][90][0-9]{2}[\s,-]{1,3})+)(.*)$', regex.IGNORECASE))
        coerce.append(
            regex.compile(r'copyright\s(?:\(c\)\s|©\s){0,1}((?:[12][90][0-9]{2}[\s,]{1,3})+)(.*)$', regex.IGNORECASE))
        coerce.append(
            regex.compile(r'copyright\s(?:\(c\)\s|©\s){0,1}([12][90][0-9]{2}[-][12][90][0-9]{2}[\s,]{1,3})(.*)$',
                          regex.IGNORECASE))

        for match in self.matches:

            found = False
            for reg in coerce:
                m = reg.search(self.matches[match]['copyright'])
                if m:
                    date = m.group(1)
                    holder = m.group(2)
                    # logging.debug(f"    Coerced: {match}")
                    # logging.debug("     - Date:" + str(date) + " Holder:" + str(holder))
                    if holder not in newMatches:
                        newMatches[holder] = {'holder': holder, 'date': self.parse_date(date),
                                              'url': self.matches[match]['url']}
                    else:
                        newMatches[holder]['date'].update(self.parse_date(date))
                    found = True
                    break

            if not found:
                non_coerced.append(self.matches[match]['copyright'])

        for match in newMatches:
            # logging.debug(newMatches[match])
            output_string = "Copyright (C) {} {}".format(self.print_range(newMatches[match]['date']),
                                                         newMatches[match]['holder'])

            # print_range(newMatches[match])
            if 'url' in newMatches[match]:
                urls = newMatches[match]['url'].keys()
                for url in urls:
                    output_string = output_string + " " + url
            coerced.append(output_string)

        return coerced, non_coerced

    def parse_date(self, date):
        date_range = regex.compile(r'([12][90][0-9]{2})[-]{1,}([12][90][0-9]{2})')
        date = date.replace(" ", "")
        date = regex.sub("-$", "", date)
        date_data = {}
        for adate in date.split(','):
            # logging.debug("ADATE:" + adate)
            adate = adate.strip()

            m = date_range.match(adate)

            if m:
                #	logging.debug("Matched ADATE:" + adate)
                start_date = m.group(1)
                end_date = m.group(2)
                for k in range(int(start_date), int(end_date) + 1):
                    date_data.update({k: 1})
            else:
                if adate != '':
                    try:
                        date_data.update({int(adate): 1})
                    except Exception as e:
                        logging.warning(
                            "Cannot parse date:" + adate + " Defaulted to 1970. ACTION REQUIRED - Please update this manually")
                        date_data.update({1970: 1})

        return date_data

    @staticmethod
    def print_range(date):
        output = []
        year_list = list(date.keys())
        year_list.append(999999)
        year_list.sort()
        start_year = None
        last_year = None
        for year in year_list:
            # logging.debug("Process Year"+str(year))
            if start_year == None:
                start_year = int(year)
                last_year = int(year)
                continue

            if int(year) - last_year > 1:
                if start_year == last_year:
                    output.append(str(start_year))
                else:
                    output.append("{}-{}".format(str(start_year), str(last_year)))
                start_year = int(year)

            last_year = int(year)

        return ','.join(output)

    def process_copyrights(self):
        # Preprocess copyrights to remove noise
        self.filter_copyrights()
        self.preprocess_copyrights()
        self.ignore_blank_copyrights()

        coalesced_copyrights, non_coalesced_copyrights = self.coalesce_dates()

        self.final_copyrights = coalesced_copyrights
        if len(non_coalesced_copyrights) > 0:
            self.final_copyrights.extend(non_coalesced_copyrights)

        return


class ComponentList:
    # components_dict = {}

    def __init__(self):
        self.components_dict = {}

    def add(self, compname, copyrightmgr):
        self.components_dict[compname] = copyrightmgr

    def count_comps(self):
        return len(self.components_dict)

    def count_orig_copyrights(self):
        count = 0
        for compname, copyrightmgr in self.components_dict.items():
            count += copyrightmgr.count_orig_copyrights()
        return count

    def count_final_copyrights(self):
        count = 0
        for compname, copyrightmgr in self.components_dict.items():
            count += copyrightmgr.count_final_copyrights()
        return count

    def process_bom(self, bd, bom_components, all_copyrights):
        logging.info("Processing BOM components ...")
        for compurl, bom_component in bom_components.items():

            if 'componentVersionName' in bom_component:
                bom_component_name = f"{bom_component['componentName']}:{bom_component['componentVersionName']}"
            else:
                bom_component_name = f"{bom_component['componentName']}"
                logging.warning(f"Component found with no version: {bom_component_name}")
                continue

            logging.info(f"Processing: {bom_component_name}")

            if bom_component_name in self.components_dict.keys():
                logging.warning(f"Skipping {bom_component_name} : Already processed")
                continue

            copyrightmanager = None
            if 'origins' in bom_component:
                for origin in bom_component['origins']:
                    #
                    # Find copyright for origin in all_copyrights dict
                    origcopyrights = []
                    if origin['origin'] in all_copyrights:
                        origcopyrights = all_copyrights[origin['origin']]
                    if len(origcopyrights) > 0:
                        if copyrightmanager is None:
                            copyrightmanager = CopyrightManager(bd, bom_component_name, origcopyrights)
                        else:
                            copyrightmanager.add_copyrights(origcopyrights)

            # copyright_list = []
            # rejected_copyrights = []
            if copyrightmanager is not None:
                copyrightmanager.process_copyrights()
                self.add(bom_component_name, copyrightmanager)

        return

    def generate_text_report(self, project, version, showall=False):
        output_string = "\n" + project + " " + version + "\n================================\n"
        for compname, copyrightmgr in self.components_dict.items():
            output_string += '\n' + copyrightmgr.output_copyrights_text(showall)
            # if args.show_rejected:
            #     for copyright in copyrights[component][origin]['rejected']:
            #         output_string = output_string + "  REJECTED: " + copyright + "\n"

        return output_string

    def generate_html_report(self, project, version, showall=False):
        output = f"""
            <!doctype html>
            <html lang="en">
            <head>
              <meta charset="utf-8">
              <title>Copyright Report</title>
              <meta name="description" content="Copyright Report">
              <meta name="author" content="BlackDuck">
            </head>
            <body>
            <h1>Project: {project} Version: {version}<h1>
            """

        for compname, copyrightmgr in self.components_dict.items():
            output += copyrightmgr.output_copyrights_html(showall)

        output = output + """
        </body>
        </html>	
        """
        return output
