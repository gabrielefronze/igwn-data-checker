#! /usr/bin/env python3

import os
import subprocess

CACHE_CONTENT_FILE_BASE_PATH="srm://storm-fe-archive.cr.cnaf.infn.it:8444/virgoplain/"
CVMFS_BASE_PATH="/cvmfs/ligo.osgstorage.org/"
STASHCACHE_BASE_PATH="/storage/gpfs_xcache/virgo/user/ligo/"

def getCachedContentList():
    ls = "gfal-ls -l {} | tail -n 1".format(CACHE_CONTENT_FILE_BASE_PATH)
    process = subprocess.Popen(ls.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    filename = CACHE_CONTENT_FILE_BASE_PATH+output.split()[-1]
    print(filename)

    cat = "gfal-cat {}".format(filename)
    process = subprocess.Popen(cat.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    print(output)

    cached_files = []

    for line in output.splitlines():
        cached_filename = line.split[-1]
        if ".gwf" in cached_filename and not ".cinfo" in cached_filename:
            cached_files.append(cached_filename.replace(STASHCACHE_BASE_PATH,''))

    return cached_files


def crawler(path, cache_content):
    results = {}
    if os.path.isdir(path):
        for node in os.listdir(os.path.abspath(path)):
            results = results | crawler(node)
    else:
        pass



def main():
    cached_files = getLatestContentFile()
    print(cached_files)
    return

if __name__ == "__file__":
    main()