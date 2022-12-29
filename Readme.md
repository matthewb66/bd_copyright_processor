# Copyright Processor - Async version

Python script to process copyrights from a Black Duck project version and generate an output file of
filtered copyrights.

## BACKGROUND
There is no standard way to add copyright text to source files or packages, but most software licenses
require copyrights to be reported when software is used in commercial releases.

Many copyrights follow a general text format (for example 'Copyright 1999 My Name'), but there are multiple
copyright identifiers ('(C)', '(c)', 'Copyright', '@author', '©' etc.) none of which are reserved
and are frequently used within source code and other text apart from copyright definitions. Additionally, the
copyright date string can comprise only a year, a year range, comma-delimited list of years, a full date or 
multiple other formats. The copyright name component is free form potentially including URLs and other non-ASCII text
of any size, often including copies of the software license text and unlimited size.

Copyrights are not always scoped within comments as they can be in plain text within license files or elsewhere,
and they can span multiple lines, making it difficult to know when a copyright ends.

Black Duck identifies all potential copyright matches which it stores in the KnowledgeBase for each component.
Filtering the list of copyrights when they are added to the KnowledgeBase would potentially cause some copyright text 
to be missed, especially as the interpretation of which copyrights are legal and should be included varies by 
local jurisdiction and source language of the project/files etc. 

It is therefore preferable for Black Duck to store full copyright information and allow administrators/users 
to filter and manage the copyright text according to their requirements. Black Duck
supports manual modification, deactivation and addition of copyrights in the KB for this purpose.

However, these manual processes can be challenging to repeat across large projects, and this script is 
designed to support creating an output list of filtered copyrights which have been deduplicated, 
with year ranges for where the same copyright has been specified many times across different years, 
removing those which contain code fragments etc.

The script is intended to be used after project version creation, and the resulting copyright text appended to the 
end of the Notices File generated separately from a Black Duck project.

## INSTALLATION

Optionally create a python virtual environment.
Clone the repo from GitHub and install the dependencies listed in the requirements file:

```
python3 -m pip install -r requirements.txt
```
## OPTIONS EXPLAINED

You will need to provide the BLACKDUCK_URL and BLACKDUCK_API_TOKEN to connect to a Black Duck server and 
specify a project and version for processing. Note that double quotes are required for names containing spaces.

The script will ignore all copyrights without a date (use the `--notstrict` option to accept all copyrights).

It will look for code fragments in all source languages (use the `--code-languages XXX` option to specify specific
languages to strip - available languages include `general,csharp,c,python,java,js,shell,xml,sql`).

Copyright text beyond 3 lines will be ignored (use the option `--max_lines X` to change the number of included lines).

Use the option `--show-original` to see all original copyrights and compare against the filtered set.

## USAGE

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
                            Maximum processed copyright lines (default 2)
      -c CODE_LANGUAGES, --code_languages CODE_LANGUAGES
                            Specify which code fragments should be removed:
                            Select from 'general,csharp,c,python,java,js,shell,xml,sql' - default is all
      -n, --notstrict       Include copyright text which does not contain a year or date
      -v, --version         Print script version

## Proxy Support

Set the environment variable HTTPS_PROXY with the proxy server URL and port, for example:

    export HTTPS_PROXY=https://myproxy.net:8080