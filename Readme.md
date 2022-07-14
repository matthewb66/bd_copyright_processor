# Black Duck Copyright Processor

# OVERVIEW

This script is provided under an OSS license (specified in the LICENSE file).

It does not represent any extension of licensed functionality of Synopsys software itself and is provided as-is, without warranty or liability.

# DESCRIPTION

This script processes an existing Black Duck project version to extract copyrights, which are filtered to remove duplicates and incorrectly identified copyrights, and export in a text format for use in a notices file.

## Installation

Clone the repo from git hub and install the dependencies listed in the requirements file
```
python3 -m pip install -r requirements.txt
```

Create a new file called .restconfig.json in the directory where the script is cloned to. Here are templates depending on whether you are using a username password or API token:
```
{  
 "baseurl": "https://hub-hostname",
 "username": "<username goes here>",
 "password": "<password goes here>",
 "insecure": true,
 "debug": false
 }
```
Or
```
{  
 "baseurl": "https://hub-hostname",
 "api_token": "<API token goes here>",
 "insecure": true,
 "debug": false
}
 ```
Replace the URL with the url of your BlackDuck instance and add your credentials.

## Usage

usage: Generate notice report with filtered copyright information

       generate_notices_report.py 
       [-h] [-d] [-nf] [-nd] [-sr] [-o OUTPUT_TEXT]
       [-oh OUTPUT_HTML]   project_name version

positional arguments:
-  project_name - The name of the project in Blackduck
-  version - The name of the version in Blackduck

optional arguments:
-  -h, --help -            show this help message and exit
-  -d, --debug -           Enable debug output
-  -nf, --not_filtered - Don't perform any filtering
-  -sr, --show_rejected - Show all lines that were processed for copyright but were  ultimately rejected
-  -o \<filename\>, --output-text \<filename\>  - Output report as text
-  -oh \<filename\>, --output-html \<filename\> -  Output report as html


