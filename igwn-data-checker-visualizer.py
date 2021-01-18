#! /usr/bin/env python3

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def main(json_path="output-cnaf.json"):
    checksum_results = []
    user_time_results = []
    sys_time_results = []
    real_time_results = []
    data = json.load(open(os.path.abspath(json_path)))
    for path, results in data.items():
        avg_user_time = 0
        avg_sys_time = 0
        avg_real_time = 0
        for r in results:
            checksum_results.append(1 if r["checksum_status"] else 0)
            avg_user_time += r["timer"]["user"]
            avg_sys_time += r["timer"]["sys"]
            real_time = r["timer"]["real"].split(":")
            avg_real_time += float(real_time[0])*60+float(real_time[1])
        user_time_results.append(avg_user_time/len(results))
        sys_time_results.append(avg_sys_time/len(results))
        real_time_results.append(avg_real_time/len(results))

    fig, axes = plt.subplots(nrows=2, ncols=2)
    ax0, ax1, ax2, ax3 = axes.flatten()

    ax0.hist(checksum_results, 2, histtype='bar', color='blue')
    plt.sca(ax0)
    plt.xticks([.75, 1.25], ["wrong", "correct"])
    ax0.set_title("Checksum verification distribution")
    ax0.set_ylabel("percent [%]")

    ax1.hist(user_time_results, 100, histtype='bar', color='lime')
    ax1.set_title("File access time (user)")
    ax1.set_xlabel("seconds [s]")
    ax1.set_ylabel("counts")
    
    ax2.hist(sys_time_results, 100, histtype='bar', color='orange')
    ax2.set_title("File access time (sys)")
    ax2.set_xlabel("seconds [s]")
    ax2.set_ylabel("counts")
    
    ax3.hist(real_time_results, 100, histtype='bar', color='red')
    ax3.set_title("File access time (real)")
    ax3.set_xlabel("seconds [s]")
    ax3.set_ylabel("counts")
    
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()