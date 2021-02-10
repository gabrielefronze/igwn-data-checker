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
    if not os.path.isfile("/cvmfs/virgo.ego-gw.it/software/VCS-12.1/python/anaconda2/bin/FrCheck"):
        print("Executable /cvmfs/virgo.ego-gw.it/software/VCS-12.1/python/anaconda2/bin/FrCheck not found. Aborting.".format(file_path))
        return {"checksum_status": False, "timer": {"real": 0, "user": 0, "sys": 0}, "status": False}

    if not os.path.isfile(file_path):
        print("File {} not found. Aborting.".format(file_path))
        return {"checksum_status": False, "timer": {"real": 0, "user": 0, "sys": 0}, "status": False}

    cmd = "time /cvmfs/virgo.ego-gw.it/software/VCS-12.1/python/anaconda2/bin/FrCheck -d 1 -i "+file_path

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
    
    return {"checksum_status": checksum_status, "timer": {"real": time_real, "user": time_user, "sys": time_sys}, "status": True}


def Handler(path, verbose):
    results = {}
    abs_path = os.path.abspath(path)
    if os.path.isdir(abs_path):
        for path in os.listdir(abs_path):
            r = Handler(os.path.join(abs_path, path), verbose)
            for p, data in r.items():
                if p in results:
                    results[p]["results"] += data["results"]
                else:
                    results[p] = {}
                    results[p]["size"] = data["size"]
                    results[p]["results"] = data["results"]
    elif os.path.isfile(abs_path):
        if abs_path.endswith(".gwf"):
            try:
                res = FrCheckWrapper(abs_path, verbose)
                if abs_path in results:
                    results[abs_path]["results"] += [res]
                else:
                    results[abs_path] = {}
                    results[abs_path]["size"] = os.path.getsize(abs_path)
                    results[abs_path]["results"] = [res]
            except:
                print("Error processing path {}. Skipping.".format(abs_path))
                res = {"checksum_status": False, "timer": {"real": 0, "user": 0, "sys": 0}, "status": False}
                if abs_path in results:
                    results[abs_path]["results"] += [res]
                else:
                    results[abs_path] = {}
                    results[abs_path]["size"] = os.path.getsize(abs_path)
                    results[abs_path]["results"] = [res]
        else:
            print("Path {} not valid. Not a .gwf file".format(abs_path))
    else:
        raise Exception("Invalid path provided {}".format(abs_path))
    return results


def BulkHandler(settings):
    results = {}
    paths = settings["paths_to_test"]

    for path in paths:
        for i in range(0, settings["settings"]["runs_per_file"]):
            partial_results = Handler(os.path.abspath(path), settings["settings"]["verbose"])
            for p,measures in partial_results.items():
                if p in results:
                    results[p]["results"] += measures["results"]
                else:
                    results[p] = measures

    return results


def main():
    settings = json.load(open('settings.json'))
    results = BulkHandler(settings)
    print(json.dumps(results, indent=2), file=open("output.json", "w"))


if __name__ == "__main__":
    main()