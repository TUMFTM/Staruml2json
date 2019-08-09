######################################################################
#
# This main file is the entry point in using this script. 
# We handle input parameters and instatiate the modj_to_json class here
#
######################################################################
__author__ = "Lukas Merkle"
__copyright__ = "Copyright 2019, Institute of Automotive Technology"
__license__ = "LGPL V3"
__version__ = "1.0"
__maintainer__ = "Lukas Merkle"
__email__ = "lukas.merkle@tum.de"
######################################################################

import json
import mdj_to_json as md
import sys
import ast
import os
sys.setrecursionlimit(20000)



class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def main():

    mdjparser_mdj = md.Mdj_parser(MDJ_FILE, file_mode="mdj")
    mdjparser_mdj.decompose_mdj()
    names = "Module"
    model_dict = mdjparser_mdj.compose_dict(names, "model-")

    print(1)


if __name__ == "__main__":
    args = sys.argv

    if len(args) == 1:
        print(bcolors.FAIL + "No arguments given. For help run 'python main.py -h'. Exiting..."+bcolors.ENDC)
        exit()
    else:
        # defaults
        model_mode = ""
        model_file = ""
        subsystem = ""
        file_mode = ""
        output_file = ""
        classesOnly = False

        # scan arguments
        arg_iter = iter(args)
        for arg in arg_iter:
            if arg == "-h":
                print('---------------------------------------------------------------------------------------------')
                print('Help')
                print('Usage: python main.py -m modelfile.mdj/xmi -s subsystem -file_mode mdj/xmi -o filename -model_mode')
                print("")
                print('\t -m modelfile:  the modelfile, can either be an .mdj Staruml file or a .xmi file')
                print("\t -s subsystem: subsystem is the part of the model serving as root for the translation ")
                print("\t -file_mode mode: mode can eiter be mdj or xmi")
                print("\t -o filename: textfile to put the result in")
                print("\t -classesOnly: True: only classes returned. False (default): Object values are refined")
                print("\t -model_mode: if argument set, model_mode is used and heriting children are included")
                print("")
                print('---------------------------------------------------------------------------------------------')
                exit()
            if arg == '-m':
                model_file = next(arg_iter)
            if arg == '-s':
                subsystem = next(arg_iter)
            if arg == '-file_mode':
                file_mode = next(arg_iter)
            if arg == "-model_mode":
                model_mode ='model-mode'
            if arg == "-o":
                output_file =next(arg_iter)
            if arg == "-classesOnly":
                classesOnly = ast.literal_eval(next(arg_iter))

        # Check if arguments not set
        if model_file == "":
            print(bcolors.FAIL + "No model_file given. Exiting..."+bcolors.ENDC)
            exit()
        if subsystem == "":
            print(bcolors.FAIL +"No subsystem given. Exiting..."+bcolors.ENDC)
            exit()
        if file_mode == "":
            if model_file != "":
                extension = os.path.splitext(model_file)[1]
                file_mode = extension.split(".")[1]
                print(bcolors.WARNING + "Extracting file_mode from model_file. Set to: "+bcolors.BOLD + file_mode+bcolors.ENDC)
            else:
                print(bcolors.FAIL +"No model_file given. Exiting..."+bcolors.ENDC)
                exit()

        if output_file == "":
            print(bcolors.WARNING +"No output_file given. Saving under "+bcolors.BOLD+"./result.txt"+bcolors.ENDC)
            output_file = "result.txt"

        
        # Instantiate mdj_to_model parser
        parser = md.Mdj_parser(model_file, file_mode=file_mode)
        parser.decompose()

        # Decide if only classes or also objects. 
        if classesOnly == True:
            print(bcolors.WARNING + "Refining only classes. No Values set!" + bcolors.ENDC)
            model_dict = parser.compose_dict(subsystem=subsystem, mode=model_mode)
        else:
            model_dict = parser.compose_objects(top_level_obj=subsystem)

        # Write generated dict to json-file
        f = open(output_file, "w")
        f.write(json.dumps(model_dict, indent=2))
        print(bcolors.OKGREEN + "Saved file: " +bcolors.BOLD+ str(output_file)+bcolors.ENDC)


