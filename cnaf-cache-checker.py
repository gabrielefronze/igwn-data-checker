#! /usr/bin/env python3

import os
import subprocess

CACHE_CONTENT_FILE_BASE_PATH="srm://storm-fe-archive.cr.cnaf.infn.it:8444/virgoplain/"
CVMFS_BASE_PATH="/cvmfs/ligo.osgstorage.org/frames/O3/V1Online/V-V1Online-12389"
STASHCACHE_BASE_PATH="/storage/gpfs_xcache/virgo/user/ligo/"

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
        if ".gwf" in cached_filename and not ".cinfo" in cached_filename:
            cached_files.append(cached_filename.replace(STASHCACHE_BASE_PATH,''))

    print("{} files found".format(len(cached_files)))

    return cached_files


def crawler(cvmfs_path, cache_content):
    results = {}
    if not os.path.isfile(cvmfs_path):
        print("Handling {}".format(cvmfs_path))
        for node in os.listdir(cvmfs_path):
            results = {**results, **crawler(cvmfs_path+'/'+node, cache_content)}
    else:
        if ".gwf" in os.path.basename(cvmfs_path):
            relative_path = cvmfs_path.replace(CVMFS_BASE_PATH, '')
            if relative_path in cache_content:
                results[relative_path] = {'cached': True}
            else:
                results[relative_path] = {'cached': False}

    return results



def main():
    cached_files = getCachedContentList()
    results = crawler(CVMFS_BASE_PATH, cached_files)
    total = len(results)
    cached = sum(1 if r['cached'] else 0 for r in results.values())
    print("{} files checked. {} files in cache ({}%)".format(total, cached, cached/total*100))
    
    return

if __name__ == "__main__":
    main()