#!/usr/bin/env python3

import sys
import mmap
import regex
import shutil
import logging
import argparse
from copyrightprocessor import CopyrightProcessor

class ReportManager:

    __merge_file = ""
    __split_file = ""

    __split_dict = {}
    #__split_files = ["component.part", "copyright.part", "license.part"]
    #__split_strings = ["Components: ", "Copyrights: ", "Licenses: "]

    def __init__(self, split_file, merge_file):
        self.__split_file = split_file
        self.__merge_file = merge_file

        self.__split_dict["component"] = { "filename":"component.part", "separator":"Components: "}
        self.__split_dict["copyright"] = { "filename":"copyright.part", "separator":"Copyright Text: "} 
        self.__split_dict["license"]   = { "filename":"license.part", "separator":"Licenses: "} 


    def write_file(self, filename, lines):
        with open(filename, "w") as f: 
            for line in lines:
                f.write(line)
        logging.debug("File " + filename + ", written lines " + str(len(lines)))

    def split_file(self):

        with open(self.__split_file, 'r') as f:
            lines = f.readlines()
            
        n = 0
        ncopy = 0
        nlicense = 0
        for line in lines:
            if ncopy == 0 and line.find(self.__split_dict["copyright"]["separator"]) != -1:
                ncopy = n
            elif nlicense == 0 and line.find(self.__split_dict["license"]["separator"]) != -1:
                nlicense = n
            elif ncopy != 0 and nlicense != 0:
                break
            n += 1
        
        logging.debug("Report file lines " + str(len(lines)))
        logging.debug("ncopy = " + str(ncopy))
        logging.debug("nlicense = " + str(nlicense))
        
        self.write_file(self.__split_dict["component"]["filename"], lines[:ncopy])
        self.write_file(self.__split_dict["copyright"]["filename"], lines[ncopy:nlicense])
        self.write_file(self.__split_dict["license"]["filename"], lines[nlicense:])
        
        return self.__split_dict
    
    def merge_files(self):

        filenames = []
        filenames.append(self.__split_dict["component"]["filename"])
        filenames.append(self.__split_dict["copyright"]["filename"])
        filenames.append(self.__split_dict["license"]["filename"])

        with open(self.__merge_file, 'w') as outfile:
            for fname in filenames:
                with open(fname) as infile:
                    for line in infile:
                        outfile.write(line)

        return self.__merge_file
    
    def load_components(self):
        with open(self.__split_dict["component"]["filename"], 'r') as infile:
             lines = infile.readlines()

        component_list = []     
        ncomp_found = False
        for line in lines:
            if ncomp_found == False:
                if line.find(self.__split_dict["component"]["separator"]) != -1:
                    ncomp_found = True
            else:
                data = line.split(": ")
                if not data[0].isspace():
                    component_list.append(data[0].strip())
    
        return component_list

    def load_copyrights(self):
        logging.debug("Load copyrights")
        copyright_dict = {}
        skip = True
        component = ""

        with open(self.__split_dict["copyright"]["filename"], 'r') as infile:
            lines = infile.readlines()       

        for line in lines:
            # skip 
            if not line: 
                continue
            elif skip:
                if line.startswith(self.__split_dict["copyright"]["separator"]):
                    skip = False
            # component found
            elif line[0].isalpha():
                component = line.strip()
                copyright_dict[component]=[]
                #logging.debug("Found component " + component )
            # copyright found
            elif line[0].startswith("\t"):
                copyright = line.strip()
                copyright_dict[component].append(copyright)
                #logging.debug("Add copyright " + copyright)
                
        return copyright_dict
    
    def clean_copyrights(self, copyrights):
        logging.debug("Clean copyrights")
        cleaned_dict = {}
        garbage_dict = {}

        processor = CopyrightProcessor("all", 1)
        for component, copyright_list in copyrights.items():
            cleaned_dict[component] = []
            garbage_dict[component] = []
            for copyright in copyright_list:
                preprocessed = processor.preprocess(copyright)
                postprocessed, garbage = processor.postprocess(preprocessed)
                if len(postprocessed):
                    # logging.debug(postprocessed)
                    cleaned_dict[component].append(postprocessed)
                elif len(garbage):
                    logging.info("GARBAGE IN  " + copyright)
                    logging.info("GARBAGE OUT " + garbage)
                    garbage_dict[component].append(copyright)

        return cleaned_dict
    
    def save_copyrights(self, copyrights):
        header = self.__split_dict["copyright"]["separator"]
        filename = self.__split_dict["copyright"]["filename"]
        shutil.copy2(filename, filename + ".bak")

        with open(filename, 'w') as outfile:
            outfile.write(header + "\n\n")
            for component, copyright_list in copyrights.items():
                logging.debug(component)
                outfile.write(component + "\n")
                for copyright in copyright_list:
                    outfile.write("\t" + copyright + "\n")
        
        return filename
    
## test code ##

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Report manager to split and merge files")
    parser.add_argument("report_file",help="The report file name")
    parser.add_argument("-s","--split", action="store_true", help="Split files")
    parser.add_argument("-m","--merge", action="store_true", help="Merge files")
    parser.add_argument("-d","--debug", action="store_true", help="Enable debug output")
    parser.add_argument("-l","--list-components", action="store_true", help="List components require")
    parser.add_argument("-c","--clean", action="store_true", help="Clean copyrights require --split")
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', stream=sys.stderr, level=logging.DEBUG)
    logging.getLogger().setLevel(logging.INFO)
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

  

    
    manager = ReportManager(args.report_file, args.report_file)
    
    if (args.split):
        result = manager.split_file()
        print("Split files: " + str(result))

    if args.merge:
        result = manager.merge_files()
        print("Merged files: " + str(result))

    if (args.list_components):
        _ = manager.split_file()
        component_list = manager.load_components()
        print("Component list: " + str(component_list))

    if (args.clean):
        _ = manager.split_file()
        
        component_list = manager.load_components()
        copyright_dict = manager.load_copyrights()
        if len(component_list) != len(copyright_dict):
            print("Mismach length component_list {} != copyfight_dict {}"
                         .format(len(component_list),len(copyright_dict)))
            print("Component list: " + str(component_list))
            
        copyright_dict = manager.clean_copyrights(copyright_dict)
        filename = manager.save_copyrights(copyright_dict)
        print("Copyright list: " + str(filename))

        report = manager.merge_files()
        print("Cleaned report: " + str(report))
