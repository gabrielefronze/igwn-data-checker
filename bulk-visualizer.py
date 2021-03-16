#! /usr/bin/env python3

import os
import sys
import subprocess

def main():
    root_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(root_path, "output")
    for cc in os.listdir(path):
        print("\n\n=================================================================================================================================")
        print("Handling {}".format(cc))
        print("=================================================================================================================================")
        cc_dir = os.path.join(path, cc)
        for date in os.listdir(cc_dir):
            print("\tDate {}".format(date))
            date_path = os.path.join(cc_dir, date)
            for time in os.listdir(date_path):
                print("\t\tTime {}".format(time))
                time_path = os.path.join(date_path, time)
                if os.path.isfile(os.path.join(time_path, "output.json")):
                    os.symlink(time_path, os.path.join(cc_dir, "latest"))
                    print("\t\tOutput found.")
                    os.chdir(time_path)
                    vis = subprocess.run([os.path.join(root_path, "igwn-data-checker-visualizer.py"),
                                         "./output.json", 
                                         "-t {} status - {} @ {} ".format(cc, date, time),
                                         "-n",
                                         "-s"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if vis.stderr:
                        print("\t\tErrors occurred.")
                        print(vis.stderr.decode("utf-8"))
                    else:
                        os.rename("./output.json", "./output.processed.json")
                    os.chdir(root_path)
                elif os.path.isfile(os.path.join(time_path, "output.processed.json")):
                    print("\t\tOutput already processed.")
                else:
                    print("\t\tNo output found.")

if __name__ == "__main__":
    main()
