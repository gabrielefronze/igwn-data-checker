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


def FrCheckWrapper(file_path, verbose):
    cmd = "time FrCheck -d 1 -i "+file_path

    if verbose:
        print("\n\n"+cmd+"\n")
    else:
        print(cmd)

    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    output_str = str(output.decode("utf-8"))
    error_str = str(error.decode("utf-8"))
    if verbose:
        print(output_str)
        print(error_str)
    checksum_status = "No read error. File Checksum OK" in output_str and "No read error. Structure Checksums OK" in output_str
    
    if "real" in output_str and "sys" in output_str:
        output_str_lines = output_str.split("\n")
        time_real = ConvertTime(output_str_lines[-3].split("\t")[-1])
        time_user = ConvertTime(output_str_lines[-2].split("\t")[-1])
        time_sys = ConvertTime(output_str_lines[-1].split("\t")[-1])
    elif "elapsed" in error_str and "system" in error_str:
        time_user = float(error_str.split("user ")[0])
        time_sys = float(error_str.split("user ")[1].split("system ")[0])
        time_real = error_str.split("user ")[1].split("system ")[1].split("elapsed ")[0]
    
    return {"checksum_status": checksum_status, "timer": {"real": time_real, "user": time_user, "sys": time_sys}}


def Handler(path, verbose):
    results = {}
    if os.path.isdir(path):
        for f_path in os.listdir(path):
            abs_path = os.path.join(path, f_path)
            if f_path in results:
                results[abs_path]["results"].append(FrCheckWrapper(os.path.abspath(abs_path), verbose))
            else:
                results[abs_path] = {}
                results[abs_path]["size"] = os.path.getsize(abs_path)
                results[abs_path]["results"] = [FrCheckWrapper(os.path.abspath(abs_path), verbose)]
    elif os.path.isfile(path):
        results[abs_path] = {}
        results[abs_path]["size"] = os.path.getsize(path)
        results[path]["results"] = [FrCheckWrapper(path, verbose)]
    else:
        raise Exception("Invalid path provided {}".format(path))
    return results


def BulkHandler(settings):
    results = {}
    paths = settings["paths_to_test"]

    for path in paths:
        for i in range(0, settings["settings"]["runs_per_file"]):
            partial_results = Handler(os.path.abspath(path), settings["settings"]["verbose"])
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