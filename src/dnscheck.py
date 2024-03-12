import argparse
import csv
import os
import re
import sys
from glob import glob
from typing import Union, Optional
from dns import rdatatype, resolver, reversename
from dns.name import Name
from dns.rdatatype import RdataType
import xlsxwriter

DATA_TYPE_DMARC = 'DMARC Data'
DATA_TYPE_SPF = 'SPF Data'
DATA_TYPE_MX = 'MX Data'
DATA_TYPE_RDNS = 'RDNS Data'

custom_dns_server = '8.8.8.8'
custom_resolver = resolver.Resolver()
custom_resolver.nameservers = [custom_dns_server]


def validate_xlsx_file(file_path):
    if not file_path.lower().endswith('.xlsx'):
        raise argparse.ArgumentTypeError("File must have a .xlsx extension.")
    return file_path


def dns_lookup(qname: Union[Name, str], rdtype: Union[RdataType, str], pattern: Optional[re.Pattern] = None):
    records = []
    try:
        answers = custom_resolver.resolve(qname, rdtype)
        for rdata in answers:
            if rdata.rdtype in [rdatatype.A, rdatatype.CNAME, rdatatype.PTR]:
                record_text = rdata.to_text().strip('.')
            elif rdata.rdtype == rdatatype.TXT:
                record_text = ''.join(chunk.decode('utf-8') for chunk in rdata.strings)
            elif rdata.rdtype == rdatatype.MX:
                record_text = rdata.exchange.to_text().strip('.')
            else:
                record_text = rdata.to_text().strip('.')

            if pattern is None or pattern.match(record_text):
                records.append(record_text)
    except Exception as e:
        records.append(str(e))
    return records


def main():
    if len(sys.argv) == 1:
        print("""usage: dnscheck [-h]""")
        exit(1)

    parser = argparse.ArgumentParser(prog="dnscheck",
                                     description="""Bulk DNS Lookup Tool.""",
                                     formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=80))

    parser.add_argument('-i', '--input', metavar='<file>', dest="input_files",
                        nargs='+', type=str, required=True,
                        help='CSV file containing a list of domains')

    parser.add_argument('--dmarc', action="store_true", dest="dmarc_flag",
                        help='DMARC record lookup')

    parser.add_argument('--spf', action="store_true", dest="spf_flag",
                        help='SPF record lookup')

    parser.add_argument('--mx', action="store_true", dest="mx_flag",
                        help='MX record lookup')

    parser.add_argument('--rdns', action="store_true", dest="reverse_flag",
                        help='PTR record lookup, ip to host')

    parser.add_argument('-o', '--output', metavar='<xlsx>', dest="output_file", type=validate_xlsx_file, required=True,
                        help='Output file')

    args = parser.parse_args()

    file_names = [file for pattern in args.input_files for file in glob(pattern) if os.path.isfile(file)]

    print("Files to be processed:")
    for files in file_names:
        print(files)
    print()

    dns_data = {}

    dmarc_pattern = re.compile(r'.', re.IGNORECASE)
    spf_pattern = re.compile(r'^v=spf', re.IGNORECASE)
    mx_pattern = re.compile(r'.', re.IGNORECASE)

    for f in file_names:
        with open(f, 'r', encoding='utf-8-sig') as input_file:
            reader = csv.DictReader(input_file)
            for line in reader:
                host = line['Domain'].strip()

                if args.dmarc_flag:
                    dns_data.setdefault(DATA_TYPE_DMARC, {'max_cols': 0, 'data': []})
                    data = dns_lookup('_dmarc.{}'.format(host), 'TXT')
                    dns_data[DATA_TYPE_DMARC]['max_cols'] = max(len(data), dns_data[DATA_TYPE_DMARC]['max_cols'])
                    dns_data[DATA_TYPE_DMARC]['data'].append([host] + data)

                if args.spf_flag:
                    dns_data.setdefault(DATA_TYPE_SPF, {'max_cols': 0, 'data': []})
                    data = dns_lookup(host, 'TXT', spf_pattern)
                    dns_data[DATA_TYPE_SPF]['max_cols'] = max(len(data), dns_data[DATA_TYPE_SPF]['max_cols'])
                    dns_data[DATA_TYPE_SPF]['data'].append([host] + data)

                if args.mx_flag:
                    dns_data.setdefault(DATA_TYPE_MX, {'max_cols': 0, 'data': []})
                    data = dns_lookup(host, 'MX')
                    dns_data[DATA_TYPE_MX]['max_cols'] = max(len(data), dns_data[DATA_TYPE_MX]['max_cols'])
                    dns_data[DATA_TYPE_MX]['data'].append([host] + data)

                if args.reverse_flag:
                    dns_data.setdefault(DATA_TYPE_RDNS, {'max_cols': 0, 'data': []})
                    reversed_ip = reversename.from_address(host)
                    data = dns_lookup(reversed_ip, 'PTR')
                    dns_data[DATA_TYPE_RDNS]['max_cols'] = max(len(data), dns_data[DATA_TYPE_RDNS]['max_cols'])
                    dns_data[DATA_TYPE_RDNS]['data'].append([host] + data)

    workbook = xlsxwriter.Workbook(args.output_file)

    header_field = workbook.add_format()
    header_field.set_bold()

    dns_sheets = {}
    for name, meta in dns_data.items():
        header_name = name.upper().replace(' ', '_')
        dns_sheets[name] = workbook.add_worksheet(name)
        dns_sheets[name].write(0, 0, "Host/IP", header_field)
        col = 1
        for i in range(meta['max_cols']):
            dns_sheets[name].write(0, col, "{}_{}".format(header_name, i), header_field)
            col += 1

    for name, meta in dns_data.items():
        row = 1
        for row_data in meta['data']:
            col = 0
            for col_data in row_data:
                dns_sheets[name].write(row, col, col_data)
                col += 1
            row += 1

    workbook.close()
    print("Please see report: {}".format(args.output_file))


if __name__ == '__main__':
    main()
