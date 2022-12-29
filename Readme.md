# Copyright Processor - Async version

## Installation

Optionally create a python virtual environment.
Clone the repo from GitHub and install the dependencies listed in the requirements file:

```
python3 -m pip install -r requirements.txt
```

## Usage

    usage: python3 bd_copyright_processor.py [-h] [--blackduck_url BLACKDUCK_URL]
                                 [--blackduck_api_token BLACKDUCK_API_TOKEN]
                                 [--blackduck_trust_cert] [-d] [-os]
                                 [-o OUTPUT_TEXT] [-oh OUTPUT_HTML] [-l] [-c] [-s] [-v]
                                 project version
    
    Description: Generate filtered copyrights
    
    positional arguments:
      project               The name of the project in Blackduck
      version               The name of the project version in Blackduck
    
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
      -s, --show_orig       Show all original copyrights as well as processed
                            copyrights
      -o OUTPUT_TEXT_FILE, --output-text OUTPUT_TEXT_FILE
                            Output report as text file
      -oh OUTPUT_HTML_FILE, --output-html OUTPUT_HTML_FILE
                            Output report as html file
      -l MAX_LINES, --max_lines MAX_LINES
                            Maximum processed copyright lines
      -c CODE_LANGUAGES, --code_languages CODE_LANGUAGES
                            Specify which code fragments should be removed:
                            Select from 'general,csharp,c,python,java,js,shell,xml,sql' - default is all
      -s, --strict          Ignore copyright text which does not contain a year/date
      -v, --version         Print script version

## Proxy Support

Set the environment variable HTTPS_PROXY with the proxy server URL and port, for example:

    export HTTPS_PROXY=https://myproxy.net:8080