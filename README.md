# Bulk DNS Query Tool

This tool helps identify the top senders based on smart search outbound message exports or CSV data.

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
