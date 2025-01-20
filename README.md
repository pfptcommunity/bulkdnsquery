# Bulk DNS Query Tool
[![PyPI Downloads](https://static.pepy.tech/badge/dnscheck)](https://pepy.tech/projects/dnscheck)
This tool allow for bulk DNS lookups via CSV or TXT file passed as an argument.

### Requirements:

* Python 3.9+

### Installing the Package

You can install the tool using the following command directly from Github.

```
pip install git+https://github.com/pfptcommunity/dnscheck.git
```

or can install the tool using pip.

```
pip install dnscheck
```

### Usage Options:

```
usage: dnscheck [-h] -i <file> [--input-type {txt,csv}] [--host-ip IP/HOST] [--ns 8.8.8.8 [8.8.8.8 ...]] [--dmarc] [--spf] [--mx] [-a] [-x] [-c] -o <xlsx>

Bulk DNS Lookup Tool

optional arguments:
  -h, --help                  show this help message and exit
  -i <file>, --input <file>   CSV file containing a list of domains
  --input-type {txt,csv}      Type of input file to process (txt or csv). (Default=csv)
  --host-ip IP/HOST           CSV field of host or IP. (default=Domain)
  --ns 8.8.8.8 [8.8.8.8 ...]  List of DNS server addresses
  --dmarc                     DMARC record lookup
  --spf                       SPF record lookup
  --mx                        MX record lookup
  -a, --forward               A record lookup
  -x, --reverse               PTR record lookup, ip to host
  -c, --compact               Compact format will add multiple records to single column.
  -o <xlsx>, --output <xlsx>  Output file
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


