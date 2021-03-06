#! /usr/bin/env python3

import os
import sys
import subprocess
import datetime

def main():
    root_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(root_path, "output")
    for cc in os.listdir(path):
        print("\n\n=================================================================================================================================")
        print("Handling {}".format(cc))
        print("=================================================================================================================================")
        cc_dir = os.path.join(path, cc)
        for date in os.listdir(cc_dir):
            if not date == "latest":
                print("\tDate {}".format(date))
                date_path = os.path.join(cc_dir, date)
                prev_timestamp = None
                for time in os.listdir(date_path):
                    print("\t\tTime {}".format(time))
                    time_path = os.path.join(date_path, time)
                    
                    if os.path.isfile(os.path.join(time_path, "output.json")):
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

                    timestamp = datetime.datetime.strptime("{} {}.0".format(date, time), '%Y-%m-%d %H:%M:%S.%f')

                    if (not prev_timestamp or timestamp > prev_timestamp) and os.path.isfile(os.path.join(time_path, "output.pdf")):
                        prev_timestamp = timestamp
                        link_path = os.path.join(cc_dir, "latest")
                        if os.path.islink(link_path):
                            print("\t\tRerouting latest symlink.")
                            os.remove(link_path)
                        else:
                            print("\t\tCreating latest symlink.")
                        os.chdir(cc_dir)
                        os.symlink("./{}/{}".format(date, time), link_path)
                        os.chdir(root_path)
                    else:
                        print("\t\tNot latest results. Avoiding symlink.")

if __name__ == "__main__":
    main()
