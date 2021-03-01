#! /usr/bin/env python3

import os
import sys
from datetime import date
import shutil
import subprocess

computing_centers = ["CNAF", "NIKHEF", "PIC", "CCIN2P3"]
submit_file_template = "igwn-data-checker.sub.template"

settings_string = "<SETTINGS_GO_HERE>"
executable_string = "<EXECUTABLE_GOES_HERE>"
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
    condor_submit_command = subprocess.run(["condor_submit", submit_file], stdout=subprocess.PIPE, , stderr=subprocess.PIPE)
    print("Condor output: {}".format(condor_submit_command.stdout))

def main():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    template_submit_file = os.path.join(root_dir, submit_file_template)
    settings_file_path = os.path.join(root_dir, "settings.json")
    executable_path = os.path.join(root_dir, "igwn-data-checker.py")
    output_root = os.path.join(root_dir, "output")

    mkdir_safe(output_root)

    for cc in computing_centers:
        print("\n\n=================================================================================================================================")
        print("Handling {}".format(cc))
        print("=================================================================================================================================")
        cc_path = os.path.join(output_root, cc)
        mkdir_safe(cc_path)

        output_path = os.path.join(cc_path, str(date.today()))
        mkdir_safe(output_path)
        print("Output will be found at: {}".format(output_path))

        submit_file_path = os.path.join(output_path, submit_file_template.replace(".template", ''))
        if os.path.isfile(submit_file_path):
            os.remove(submit_file_path)

        shutil.copy(template_submit_file, submit_file_path)
        shutil.copy(settings_file_path, os.path.join(output_path, "settings.json"))
        print("Submit file at: {}".format(submit_file_path))
        print("Settings at: {}".format(settings_file_path))

        replace_text_in_file(submit_file_path, [[settings_string, "./settings.json"], [executable_string, executable_path], [computing_center_string , cc]])
        
        os.chdir(output_path)
        condor_submit(submit_file_path)
        print("=================================================================================================================================")
        os.chdir(root_dir)


if __name__ == "__main__":
    main()