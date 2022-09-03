# Copyright Processor - Async version

## Installation

Clone the repo from git hub and install the dependencies listed in the requirements file
```
python3 -m pip install -r requirements.txt
```

## Usage

    usage: bd_copyright_procssor [-h] [--blackduck_url BLACKDUCK_URL]
                                 [--blackduck_api_token BLACKDUCK_API_TOKEN]
                                 [--blackduck_trust_cert] [-d] [-sr]
                                 [-o OUTPUT_TEXT] [-oh OUTPUT_HTML]
                                 [--save_json SAVE_JSON] [--use_json USE_JSON]
                                 project version
    
    Description: Generate filtered copyrights
    
    Required arguments:
      -o outputfile         Output file in text format OR
      -oh htmlfile          Output file in text format
      project               The name of the project in Blackduck
      version               The name of the version in Blackduck
    
    optional arguments:
      -h, --help            show this help message and exit
      --blackduck_url BLACKDUCK_URL
                            Black Duck server URL (can also be set as env-var
                            BLACKDUCK_URL)
      --blackduck_api_token BLACKDUCK_API_TOKEN
                            Black Duck API token URL (can also be set as env-var
                            BLACKDUCK_API_TOKEN)
      --blackduck_trust_cert
                            BLACKDUCK trust cert
      -d, --debug           Enable debug output
      -sr, --show_rejected  Show all lines that were processed for copyright but
                            ultimately rejected
      --save_json SAVE_JSON
                            Store the query made to the database, use option
                            --use_json to re-use data. This option is for re-
                            running the script offline to improve results
      --use_json USE_JSON   Store the query made to the database, use option
                            --use_json to re-use data. This option is for re-
                            running the script offline to improve results

## Proxy Support

Set the environment variable HTTPS_PROXY with the proxy server URL and port, for example:

    export HTTPS_PROXY=https://myproxy.net:8080