#! /usr/bin/env python3

import os
import sys
import json
import subprocess

def ConvertTime(time_str):
    try:
        parts = time_str.split('m')
        minutes, seconds = int(parts[0]), float(parts[1].replace('s', ''))
        return minutes * 60 + seconds
    except:
        return time_str


def FrCheckWrapper(file_path):
    cmd = "time FrCheck -d 1 -i "+file_path+" && sleep 1"
    print("\n\n"+cmd+"\n")
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    output_str = str(output.decode("utf-8"))
    print(output_str)
    checksum_status = "No read error. File Checksum OK" in output_str and "No read error. Structure Checksums OK" in output_str
    output_str_lines = output_str.split("\n")
    time_real = ConvertTime(output_str_lines[-3].split("\t")[-1])
    time_user = ConvertTime(output_str_lines[-2].split("\t")[-1])
    time_sys = ConvertTime(output_str_lines[-1].split("\t")[-1])
    return {"checksum_status": checksum_status, "timer": {"real": time_real, "user": time_user, "sys": time_sys}}


def Handler(path):
    results = {}
    if os.path.isdir(path):
        for f_path in os.listdir(path):
            abs_path = os.path.join(path, f_path)
            if f_path in results:
                results[abs_path].append(FrCheckWrapper(os.path.abspath(abs_path)))
            else:
                results[abs_path] = [FrCheckWrapper(os.path.abspath(abs_path))]
    elif os.path.isfile(path):
        results[path] = [FrCheckWrapper(path)]
    else:
        raise Exception("Invalid path provided {}".format(path))
    return results


def BulkHandler(settings):
    results = {}
    paths = settings["paths_to_test"]

    for path in paths:
        for i in range(0, settings["settings"]["runs_per_file"]):
            partial_results = Handler(os.path.abspath(path))
            for p,measures in partial_results.items():
                if p in results:
                    results[p] += measures
                else:
                    results[p] = measures

    return results


def main():
    settings = json.load(open('settings.json'))
    results = BulkHandler(settings)
    print(json.dumps(results, indent=2), file=open("output.json", "w"))


if __name__ == "__main__":
    main()