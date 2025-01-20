# Bulk DNS Query Tool
[![PyPI Downloads](https://static.pepy.tech/badge/bulkdnsquery)](https://pepy.tech/projects/bulkdnsquery)  
This tool allow for bulk DNS lookups via CSV or TXT file passed as an argument.

### Requirements:

* Python 3.9+

### Installing the Package

You can install the tool using the following command directly from Github.

```
pip install git+https://github.com/pfptcommunity/bulkdnsquery.git
```

or can install the tool using pip.

```
# When testing on Ubuntu 24.04 the following will not work:
pip install bulkdnsquery
```

If you see an error similar to the following:

```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.

    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.

    If you wish to install a non-Debian packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.

    See /usr/share/doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
```

You should use install pipx or you can configure your own virtual environment and use the command referenced above.

```
pipx install bulkdnsquery
```

### Usage Options:

```
usage: dnscheck [-h] -i <file> [--input-type {txt,csv}] [--host-ip IP/HOST] [--ns 8.8.8.8 [8.8.8.8 ...]] [--dmarc]
                [--spf] [--mx] [-a] [-x] [--include-all] [-c] -o <xlsx>
                [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

Bulk DNS Lookup Tool

options:
  -h, --help                                       show this help message and exit
  -i <file>, --input <file>                        CSV file containing a list of domains
  --input-type {txt,csv}                           Type of input file to process (txt or csv). (Default=csv)
  --host-ip IP/HOST                                CSV field of host or IP. (default=Host)
  --ns 8.8.8.8 [8.8.8.8 ...]                       List of DNS server addresses
  --dmarc                                          DMARC record lookup
  --spf                                            SPF record lookup
  --mx                                             MX record lookup
  -a, --forward                                    A record lookup
  -x, --reverse                                    PTR record lookup, ip to host
  --include-all                                    Include all lookups.
  -c, --compact                                    Compact format will add multiple records to single column.
  -o <xlsx>, --output <xlsx>                       Output file
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}  Set the logging level (default: INFO).
```

### Sample Output

Data tabs are base on the selected lookup information. In the examples below DMARC, SPF, MX, and A records were selected for the the batch lookup. The ouput is in compact form.

View of DMARC Records
![image](https://github.com/pfptcommunity/dnscheck/assets/83429267/6ff467fa-42d0-4f8f-8927-d27c8c9d466b)

View of SPF Data
![image](https://github.com/pfptcommunity/dnscheck/assets/83429267/2360b8e0-9c03-46a8-af99-7213d8a458aa)

View of MX Data
![image](https://github.com/pfptcommunity/dnscheck/assets/83429267/a50bbbe4-f787-4112-8df5-9657bf9a24ca)

View of A Data
![image](https://github.com/pfptcommunity/dnscheck/assets/83429267/017ee0fc-7452-4c5e-9956-0424f3c2cc70)

View of PTR Data
![image](https://github.com/user-attachments/assets/166d856f-96cf-43f7-8267-1cbe967a2149)



