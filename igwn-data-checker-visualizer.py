#! /usr/bin/env python3

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def main(json_path="output-cnaf.json"):
    paths = {}
    checksum_results = []
    user_time_results = []
    sys_MBps_results = []
    sys_time_results = []
    real_time_results = []
    file_sizes = []
    data = json.load(open(os.path.abspath(json_path)))
    for path, data in data.items():
        avg_user_time = 0
        avg_sys_time = 0
        avg_real_time = 0
        size = data["size"]
        file_sizes.append(size/2**20)
        results = data["results"]
        print(path)
        if path not in paths:
            paths[path] = 1
        else:
            paths[path] = len(results)
        for r in results:
            checksum_results.append(1 if r["checksum_status"] else 0)
            avg_user_time += r["timer"]["user"]
            avg_sys_time += r["timer"]["sys"]
            real_time = r["timer"]["real"].split(":")
            avg_real_time += float(real_time[0])*60+float(real_time[1])
        user_time_results.append((avg_user_time/len(results)))
        sys_time_results.append((avg_sys_time/len(results)))
        sys_MBps_results.append((size/2**20)/(avg_sys_time/len(results)))
        real_time_results.append((avg_real_time/len(results)))

    fig, axes = plt.subplots(nrows=3, ncols=2)
    ax = axes.flatten()

    n_checksums = len(checksum_results)
    n_entries = len(paths)
    n_tests = int(n_checksums/n_entries)

    ax[0].hist(checksum_results, 2, histtype='bar', weights=[1/n_checksums*100] * n_checksums, color='blue')
    plt.sca(ax[0])
    plt.xticks([.75, 1.25], ["wrong", "correct"])
    ax[0].set_title("Checksum verification distribution")
    ax[0].set_ylabel("percent [%]")
    leg_n_entries = mpatches.Patch(color='blue', label="{} files tested\n {} times each".format(n_entries, n_tests))
    plt.legend(handles=[leg_n_entries])

    ax[1].hist(user_time_results, 100, histtype='bar', color='lime')
    plt.sca(ax[1])
    ax[1].set_title("File access time (user)")
    ax[1].set_xlabel("seconds [s]")
    ax[1].set_ylabel("counts")
    leg_n_entries = mpatches.Patch(color='lime', label="{} files tested\n {} times each".format(n_entries, n_tests))
    plt.legend(handles=[leg_n_entries])

    ax[2].hist(sys_time_results, 100, histtype='bar', color='orange')
    plt.sca(ax[2])
    ax[2].set_title("File access time (sys)")
    ax[2].set_xlabel("seconds [s]")
    ax[2].set_ylabel("counts")
    leg_n_entries = mpatches.Patch(color='orange', label="{} files tested\n {} times each".format(n_entries, n_tests))
    plt.legend(handles=[leg_n_entries])
    
    ax[3].hist(real_time_results, 100, histtype='bar', color='red')
    plt.sca(ax[3])
    ax[3].set_title("File access time (real)")
    ax[3].set_xlabel("seconds [s]")
    ax[3].set_ylabel("counts")
    leg_n_entries = mpatches.Patch(color='red', label="{} files tested\n {} times each".format(n_entries, n_tests))
    plt.legend(handles=[leg_n_entries])

    ax[4].hist(file_sizes, 100, histtype='bar', color='deepskyblue')
    plt.sca(ax[4])
    ax[4].set_title("File sizes distribution")
    ax[4].set_xlabel("MB")
    ax[4].set_ylabel("counts")
    leg_n_entries = mpatches.Patch(color='deepskyblue', label="{} files tested\n {} times each".format(n_entries, n_tests))
    plt.legend(handles=[leg_n_entries])

    ax[5].hist(sys_MBps_results, 100, histtype='bar', color='purple')
    plt.sca(ax[5])
    ax[5].set_title("File transfer speed")
    ax[5].set_xlabel("Bandwidth [MB/s]")
    ax[5].set_ylabel("counts")
    leg_n_entries = mpatches.Patch(color='purple', label="{} files tested\n {} times each".format(n_entries, n_tests))
    plt.legend(handles=[leg_n_entries])
    
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()