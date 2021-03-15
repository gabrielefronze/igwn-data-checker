#! /usr/bin/env python3

import os
import json
import argparse
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patches as patches

def main(json_path="output-PIC.json", normalize=False, title = None, save = None):
    if not title:
        title = "Input file: "+os.path.basename(json_path)

    paths = {}
    valid_counter = 0
    statuses = []
    checksum_results = []
    user_time_results = []
    first_user_time_results = []
    sys_time_results = []
    first_sys_time_results = []
    real_time_results = []
    first_real_time_results = []
    sys_MBps_results = []
    file_sizes = []
    data = json.load(open(os.path.abspath(json_path)))
    for path, data in data.items():
        avg_user_time = 0
        avg_sys_time = 0
        avg_real_time = 0
        size = data["size"]
        normalization = size/2**20 if normalize else 1
        file_sizes.append(size/2**20)
        results = data["results"]
        print(path)
        if path not in paths:
            paths[path] = 1
        else:
            paths[path] = len(results)
        counter = 0
        valid_counter += 1
        for i,r in enumerate(results):
            statuses.append(1 if r["status"] else 0)
            if r["status"]:
                checksum_results.append(1 if r["checksum_status"] else 0)
                real_time = r["timer"]["real"].split(":")

                if i == 0:
                    first_user_time_results.append(r["timer"]["user"]/normalization)
                    first_sys_time_results.append(r["timer"]["sys"]/normalization)
                    first_real_time_results.append((float(real_time[0])*60+float(real_time[1]))/normalization)
                else:
                    counter += 1
                    avg_user_time += r["timer"]["user"] if r["timer"]["user"]>0 else 0.01
                    avg_sys_time += r["timer"]["sys"] if r["timer"]["sys"]>0 else 0.01
                    avg_real_time += float(real_time[0])*60+float(real_time[1])

        user_time_results.append((avg_user_time/counter)/normalization)
        sys_time_results.append((avg_sys_time/counter)/normalization)
        sys_MBps_results.append((size/2**20)/(avg_sys_time/counter))
        real_time_results.append((avg_real_time/counter)/normalization)

    fig, axes = plt.subplots(nrows=5, ncols=2)
    fig.suptitle(title, fontsize=30)
    fig.set_size_inches(18.5, 12.5, forward=True)
    ax = axes.flatten()

    n_checksums = len(checksum_results)
    n_entries = valid_counter
    n_statuses = len(statuses)
    n_tests = counter + 1
    n_bins = int(max(n_entries / 2, 1))

    ax[0].hist(checksum_results, 2, histtype='bar', weights=[1/n_checksums*100] * n_checksums, color='navy')
    ax[0].set_facecolor("whitesmoke")
    plt.sca(ax[0])
    plt.xticks([.75, 1.25], ["wrong", "correct"])
    ax[0].set_title("Checksum verification distribution", position=(0.5, 0.6))
    ax[0].set_ylabel("percent [%]")
    leg_n_entries = mpatches.Patch(color='navy', label="{} files tested\n {} times each".format(n_entries, n_tests))
    plt.legend(handles=[leg_n_entries])

    ax[1].hist(statuses, 2, histtype='bar', weights=[1/n_statuses*100] * n_statuses, color='blue')
    ax[1].set_facecolor("whitesmoke")
    plt.sca(ax[1])
    plt.xticks([.75, 1.25], ["failed", "valid"])
    ax[1].set_title("Runtime failures distribution", position=(0.5, 0.6))
    ax[1].set_ylabel("percent [%]")
    leg_n_entries = mpatches.Patch(color='blue', label="{} files tested\n {} times each".format(n_entries, n_tests))
    plt.legend(handles=[leg_n_entries])

    ax[2].hist(user_time_results, n_bins, histtype='bar', color='darkgreen')
    ax[2].set_facecolor("whitesmoke")
    plt.sca(ax[2])
    ax[2].set_title("Average file access time (user)", position=(0.5, 0.6))
    ax[2].set_xlabel("seconds per MB [s/MB]" if normalize else "seconds [s]")
    ax[2].set_ylabel("counts")
    leg_n_entries = mpatches.Patch(color='darkgreen', label="{} files tested\n {} times each".format(n_entries, n_tests - 1))
    plt.legend(handles=[leg_n_entries])

    ax[3].hist(first_user_time_results, n_bins, histtype='bar', color='lime')
    ax[3].set_facecolor("whitesmoke")
    plt.sca(ax[3])
    ax[3].set_title("First file access time (user)", position=(0.5, 0.6))
    ax[3].set_xlabel("seconds per MB [s/MB]" if normalize else "seconds [s]")
    ax[3].set_ylabel("counts")
    leg_n_entries = mpatches.Patch(color='lime', label="{} files tested".format(n_entries))
    plt.legend(handles=[leg_n_entries])

    user_time_xlim = [min(ax[2].get_xlim()[0], ax[3].get_xlim()[0]), max(ax[2].get_xlim()[1], ax[3].get_xlim()[1])]
    ax[2].set_xlim(user_time_xlim)
    ax[3].set_xlim(user_time_xlim)

    ax[4].hist(sys_time_results, n_bins, histtype='bar', color='darkorange')
    ax[4].set_facecolor("whitesmoke")
    plt.sca(ax[4])
    ax[4].set_title("Average file access time (sys)", position=(0.5, 0.6))
    ax[4].set_xlabel("seconds per MB [s/MB]" if normalize else "seconds [s]")
    ax[4].set_ylabel("counts")
    leg_n_entries = mpatches.Patch(color='darkorange', label="{} files tested\n {} times each".format(n_entries, n_tests - 1))
    plt.legend(handles=[leg_n_entries])

    ax[5].hist(first_sys_time_results, n_bins, histtype='bar', color='gold')
    ax[5].set_facecolor("whitesmoke")
    plt.sca(ax[5])
    ax[5].set_title("First file access time (sys)", position=(0.5, 0.6))
    ax[5].set_xlabel("seconds per MB [s/MB]" if normalize else "seconds [s]")
    ax[5].set_ylabel("counts")
    leg_n_entries = mpatches.Patch(color='gold', label="{} files tested".format(n_entries))
    plt.legend(handles=[leg_n_entries])

    sys_time_xlim = [min(ax[4].get_xlim()[0], ax[5].get_xlim()[0]), max(ax[4].get_xlim()[1], ax[5].get_xlim()[1])]
    ax[4].set_xlim(sys_time_xlim)
    ax[5].set_xlim(sys_time_xlim)
    
    ax[6].hist(real_time_results, n_bins, histtype='bar', color='maroon')
    ax[6].set_facecolor("whitesmoke")
    plt.sca(ax[6])
    ax[6].set_title("Average file access time (real)", position=(0.5, 0.6))
    ax[6].set_xlabel("seconds per MB [s/MB]" if normalize else "seconds [s]")
    ax[6].set_ylabel("counts")
    leg_n_entries = mpatches.Patch(color='maroon', label="{} files tested\n {} times each".format(n_entries, n_tests - 1))
    plt.legend(handles=[leg_n_entries])

    ax[7].hist(first_real_time_results, n_bins, histtype='bar', color='orangered')
    ax[7].set_facecolor("whitesmoke")
    plt.sca(ax[7])
    ax[7].set_title("First file access time (real)", position=(0.5, 0.6))
    ax[7].set_xlabel("seconds per MB [s/MB]" if normalize else "seconds [s]")
    ax[7].set_ylabel("counts")
    leg_n_entries = mpatches.Patch(color='orangered', label="{} files tested".format(n_entries))
    plt.legend(handles=[leg_n_entries])

    real_time_xlim = [0, max(ax[6].get_xlim()[1], ax[7].get_xlim()[1])]
    rect = patches.Rectangle((0,0), ax[6].get_xlim()[1], ax[7].get_ylim()[1], linewidth=1, edgecolor='g', facecolor="#00FF0022")
    rect2 = patches.Rectangle((ax[6].get_xlim()[1],0), ax[7].get_xlim()[1], ax[7].get_ylim()[1], linewidth=1, edgecolor='g', facecolor="#FF000022")
    ax[7].add_patch(rect)
    ax[7].add_patch(rect2)
    ax[6].set_xlim(real_time_xlim)
    ax[7].set_xlim(real_time_xlim)

    ax[8].hist(file_sizes, n_bins, histtype='bar', color='deepskyblue')
    ax[8].set_facecolor("whitesmoke")
    plt.sca(ax[8])
    ax[8].set_title("File sizes distribution", position=(0.5, 0.6))
    ax[8].set_xlabel("MB")
    ax[8].set_ylabel("counts")
    leg_n_entries = mpatches.Patch(color='deepskyblue', label="{} files tested\n {} times each".format(n_entries, n_tests))
    plt.legend(handles=[leg_n_entries])

    ax[9].hist(sys_MBps_results, n_bins, histtype='bar', color='purple')
    ax[9].set_facecolor("whitesmoke")
    plt.sca(ax[9])
    ax[9].set_title("File transfer speed", position=(0.5, 0.6))
    ax[9].set_xlabel("Bandwidth [MB/s]")
    ax[9].set_ylabel("counts")
    leg_n_entries = mpatches.Patch(color='purple', label="{} files tested\n {} times each".format(n_entries, n_tests))
    plt.legend(handles=[leg_n_entries])
    
    plt.rcParams.update({'figure.autolayout': True})
    fig.subplots_adjust(hspace=0.4)
    plt.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.05)

    if not save:
        print("Showing")
        plt.show()
    else:
        print("Saving")
        plt.savefig('output.pdf')  


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize IGWN Data Checker output files')
    parser.add_argument("json_path", type=str, help='Path of input JSON file.')
    parser.add_argument('-t', "--title", help="Title of the output image.")
    parser.add_argument('-n', "--normalized", action='store_true', help="Normalize times over file size.")
    parser.add_argument('-s', "--save", action='store_true', help="Saves output as image.")
    args = parser.parse_args()
    main(json_path=args.json_path, normalize=args.normalized, title=args.title, save=args.save)