# IGWN Data Checker

This repository contains a software capable of testing data access and performance for the International Gravitational Waves Network data distribution.

It is based on python 3 and is to be run as a HTCondor job on the IGWN facilities.

## Usage and settings

This software can be executed by simply calling `./igwn-data-checker.py`, provided the `settings.json` file is available alongside the main script.

The `settings.json` file contains all th required information to run the test job.
Such `json` file is composed of two blocks:

1. `"settngs"` block which allows control over the execution parameters, such as:
    - `"runs_per_file"` to specify how many time to test each file. A value greater than one can highlight files not yet available in the cache;
    - `"verbose"` to enable additional output.

2. `"paths_to_test"` is mapped to an array of values. Additional values can be inserted here as separate values. Such values can be:
    - directories: in this case each file found in the directory is tested;
    - files: the file is tested `"runs_per_file"` times.

## Output
The output format looks as follows:

```json
{
    "<tested_path>": [
        {
            "checksum_status": true,
            "timer": {
                "real": 2.364,
                "user": 1.881,
                "sys": 0.408
            }
        },
            {
            "checksum_status": true,
            "timer": {
                "real": 2.364,
                "user": 1.881,
                "sys": 0.408
            }
        }
    ]
}
```

For each tested path an entry is created. Each path key corresponds to a dictionary containing the result of checksum verification and the measured runtime for the verification to happen.