#! /usr/bin/env python3

import os
import subprocess
import argparse

CACHE_CONTENT_FILE_BASE_PATH="srm://storm-fe-archive.cr.cnaf.infn.it:8444/virgoplain/"
CVMFS_BASE_PATH="/cvmfs/ligo.osgstorage.org/frames"
STASHCACHE_BASE_PATH="/storage/gpfs_xcache/virgo/user/ligo/frames"
FILE_EXTENSION=".gwf"

def getCachedContentList():
    ls = "gfal-ls -l {}".format(CACHE_CONTENT_FILE_BASE_PATH)
    print(ls)
    process = subprocess.Popen(ls.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    filename = CACHE_CONTENT_FILE_BASE_PATH+((output.decode('utf-8').splitlines()[-1]).split()[-1])
    print(filename)

    cat = "gfal-cat {}".format(filename)
    process = subprocess.Popen(cat.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    cached_files = []

    for line in (output.decode('utf-8')).splitlines():
        cached_filename = line.split()[-1]
        if FILE_EXTENSION in cached_filename and not ".cinfo" in cached_filename:
            cached_files.append(cached_filename.replace(STASHCACHE_BASE_PATH,CVMFS_BASE_PATH))

    print("{} files found".format(len(cached_files)))

    return cached_files


def crawler(cvmfs_path, cache_content):
    results = {}
    n_total = 0
    n_cached = 0
    if not os.path.isfile(cvmfs_path):
        for node in os.listdir(cvmfs_path):
            results = {**results, **crawler(cvmfs_path+'/'+node, cache_content)}
        
        total = len(results)
        cached = sum(1 if r['cached'] else 0 for r in results.values())
        if not total == 0:
            print("{}: {}/{} ({}%)".format(cvmfs_path, cached, total, round(cached/total*100, 2)))
        else:
            print("{}: zero {} files in CVMFS".format(cvmfs_path, FILE_EXTENSION)) 
    else:
        if FILE_EXTENSION in os.path.basename(cvmfs_path):
            relative_path = cvmfs_path
            if relative_path in cache_content:
                results[relative_path] = {'cached': True}
            else:
                results[relative_path] = {'cached': False}

    return results



def main(subfolder = "/O3"):
    cached_files = getCachedContentList()
    results = crawler(CVMFS_BASE_PATH+subfolder, cached_files)
    total = len(results)
    cached = sum(1 if r['cached'] else 0 for r in results.values())
    print("============================================================================================================")
    print("{} TOTAL: {} files checked. {} files in cache ({}%)".format(CVMFS_BASE_PATH+subfolder, total, cached, cached/total*100))
    
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CNAF-specific cache checker')
    parser.add_argument("--subfolder", '-s', type=str, help="{} subfolder to crawl in".format(CVMFS_BASE_PATH), default="/O3")
    args = parser.parse_args()
    main(subfolder=args.subfolder)