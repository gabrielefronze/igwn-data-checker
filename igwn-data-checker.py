#! /usr/bin/env python3

import os
import sys
import json
import subprocess
import argparse
import random

def ConvertTime(time_str):
    try:
        parts = time_str.split('m')
        minutes, seconds = int(parts[0]), float(parts[1].replace('s', ''))
        return minutes * 60 + seconds
    except:
        return time_str


def FrCheckWrapper(frcheck_executable, file_path, verbose):
    if not os.path.isfile(frcheck_executable):
        print("Executable {} not found. Aborting.".format(frcheck_executable, file_path))
        return {"checksum_status": False, "timer": {"real": 0, "user": 0, "sys": 0}, "status": False}

    if not os.path.isfile(file_path):
        print("File {} not found. Aborting.".format(file_path))
        return {"checksum_status": False, "timer": {"real": 0, "user": 0, "sys": 0}, "status": False}

    cmd = "time " + frcheck_executable + " -d 1 -i "+file_path

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


def Handler(frcheck_executable, path, verbose, policy):
    results = {}
    abs_path = os.path.abspath(path)
    if os.path.isdir(abs_path):
        for path in os.listdir(abs_path):
            r = Handler(frcheck_executable, os.path.join(abs_path, path), verbose, policy)
            for p, data in r.items():
                if p in results:
                    results[p]["results"] += data["results"]
                else:
                    results[p] = {}
                    results[p]["size"] = data["size"]
                    results[p]["results"] = data["results"]
    elif os.path.isfile(abs_path):
        if abs_path.endswith(".gwf"):
            process_file = None
            
            if policy == "all":
                print("Processing file since policy is \"all\"")
                process_file = True
            elif policy.endswith('%'):
                fraction = int(policy.replace('%',''))/100
                process_file = (random.random() <= fraction)
                if process_file:
                    print("Processing file due to policy.")
                else:
                    print("Skipping file due to policy.")
            else:
                print("Unrecognized policy. Falling back to \"all\"")
                process_file = True
            
            if process_file:
                try:
                    res = FrCheckWrapper(frcheck_executable, abs_path, verbose)
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


def BulkHandler(frcheck_executable, settings):
    results = {}
    paths = settings["paths_to_test"]
    
    if "policy" in settings["settings"]:
        policy = settings["settings"]["policy"]
    else:
        policy = "all"

    for path in paths:
        for i in range(0, settings["settings"]["runs_per_file"]):
            partial_results = Handler(frcheck_executable, os.path.abspath(path), settings["settings"]["verbose"], policy)
            for p,measures in partial_results.items():
                if p in results:
                    results[p]["results"] += measures["results"]
                else:
                    results[p] = measures

    return results


def main():
    parser = argparse.ArgumentParser("IGWN data checker")
    parser.add_argument("frcheck_executable", nargs='?', help="FrCheck executable path.", default="/cvmfs/oasis.opensciencegrid.org/ligo/deploy/sw/conda/envs/igwn-py38-20210107/bin/FrCheck")
    parser.add_argument("settings", nargs='?', help="Settings file path.", default="./settings.json")
    args = parser.parse_args()
    settings = json.load(open(args.settings))
    results = BulkHandler(args.frcheck_executable, settings)
    print(json.dumps(results, indent=2), file=open("output.json", "w"))


if __name__ == "__main__":
    main()