#! /usr/bin/env python3

import os
import sys
from datetime import date, now
import shutil
import subprocess
import argparse

computing_centers = ["CNAF", "NIKHEF", "PIC", "CCIN2P3"]
submit_file_template = "igwn-data-checker.sub.template"

settings_string = "<SETTINGS_GO_HERE>"
settings_argument_string = "<SETTINGS_FILE_GOES_HERE>"
executable_string = "<EXECUTABLE_GOES_HERE>"
frcheck_executable_string = "<FRCHECK_EXECUTABLE_GOES_HERE>"
computing_center_string = "<PUT_COMPUTING_CENTER_HERE>"

def mkdir_safe(path):
    if not os.path.isdir(path):
        os.mkdir(path)

def replace_text_in_file(path, replacements):
    f = open(path,'r')
    filedata = f.read()
    f.close()

    newdata = filedata
    for r in replacements:
        newdata = newdata.replace(r[0],r[1])

    f = open(path,'w')
    f.write(newdata)
    f.close()

def condor_submit(submit_file):
    condor_submit_command = subprocess.run(["condor_submit", submit_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Condor output: {}".format(condor_submit_command.stdout))

def main(frcheck_path = None, settings_file_path = None):
    root_dir = os.path.abspath(os.path.dirname(__file__))
    template_submit_file = os.path.join(root_dir, submit_file_template)
    executable_path = os.path.join(root_dir, "igwn-data-checker.py")
    
    if not settings_file_path:
        settings_file_path = os.path.join(root_dir, "settings.json")
    else:
        settings_file_path = os.path.abspath(settings_file_path)

    if not frcheck_path:
        frcheck_path = "/cvmfs/oasis.opensciencegrid.org/ligo/deploy/sw/conda/envs/igwn-py38-20210107/bin/FrCheck"
    else:
        frcheck_path = os.path.abspath(frcheck_path)

    output_root = os.path.join(root_dir, "output")

    mkdir_safe(output_root)

    for cc in computing_centers:
        print("\n\n=================================================================================================================================")
        print("Handling {}".format(cc))
        print("=================================================================================================================================")
        cc_path = os.path.join(output_root, cc)
        mkdir_safe(cc_path)

        today_path = os.path.join(cc_path, str(date.today()))
        mkdir_safe(today_path)
        output_path = os.path.join(today_path, now.strftime("%H:%M:%S"))
        mkdir_safe(output_path)
        print("Output will be found at: {}".format(output_path))

        submit_file_path = os.path.join(output_path, submit_file_template.replace(".template", ''))
        if os.path.isfile(submit_file_path):
            os.remove(submit_file_path)

        shutil.copy(template_submit_file, submit_file_path)
        shutil.copy(settings_file_path, os.path.join(output_path, "settings.json"))
        print("Submit file at: {}".format(submit_file_path))
        print("Settings at: {}".format(settings_file_path))

        replace_text_in_file(submit_file_path, 
                             [[settings_string, "./settings.json"],
                              [executable_string, executable_path],
                              [frcheck_executable_string, frcheck_path],
                              [computing_center_string , cc]])
        
        os.chdir(output_path)
        condor_submit(submit_file_path)
        print("=================================================================================================================================")
        os.chdir(root_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Bulk submitter for IGWN data checker")
    parser.add_argument("frcheck_executable", nargs='?', help="FrCheck executable path.", default="/cvmfs/oasis.opensciencegrid.org/ligo/deploy/sw/conda/envs/igwn-py38-20210107/bin/FrCheck")
    parser.add_argument("settings", nargs='?', help="Settings file path.", default="./settings.json")
    args = parser.parse_args()
    main(frcheck_path = args.frcheck_executable, settings_file_path=args.settings)