#! /usr/bin/env python3

import os
import sys
import subprocess

def main():
    root_path = os.path.dirname(__file__)
    path = os.path.join(root_path, "output")
    for cc in os.listdir(path):
        cc_dir = os.path.join(path, cc)
        for date in os.listdir(cc_dir):
            date_path = os.path.join(cc_dir, date)
            for time in os.listdir(date_path):
                time_path = os.path.join(date_path, time)
                if os.path.isfile(os.path.join(time_path, "output.json")):
                    print("Output found.")
                    os.chdir(time_path)
                    vis = subprocess.run([os.path.join(root_path, "igwn-data-checker-visualizer.py"),
                                         "./output.json", 
                                         "-t {} status - {} @ {} ".format(cc, date, time),
                                         "-n",
                                         "-s"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if vis.stderr:
                        print("Errors occurred.")
                        print(vis.stderr.decode("utf-8"))
                    else:
                        os.rename("./output.json", "./output.processed.json")
                    os.chdir(root_path)
                elif os.path.isfile(os.path.join(time_path, "output.processed.json")):
                    print("Output already processed.")
                else:
                    print("No output found.")

if __name__ == "__main__":
    main()
