import argparse
import csv
import ipaddress
import os
import re
import sys
from typing import Union, Optional

import dns
import xlsxwriter
from dns import rdatatype, resolver, reversename
from dns.name import Name
from dns.rdatatype import RdataType
from dns.resolver import Answer

DATA_TYPE_DMARC = 'DMARC Data'
DATA_TYPE_SPF = 'SPF Data'
DATA_TYPE_MX = 'MX Data'
DATA_TYPE_PTR = 'PTR Data'
DATA_TYPE_A = 'A Data'

# Initialize a custom resolver
custom_resolver = resolver.Resolver()

# Pattern to match SPF record
spf_pattern = re.compile(r'^v=spf', re.IGNORECASE)

def is_ip(ip_or_host :str) -> bool:
    try:
        ipaddress.ip_address(ip_or_host)
        return True
    except ValueError:
        return  False

def validate_file_path(file_path: str) -> str:
    """Validate if the file path exists."""
    if not os.path.exists(file_path):
        raise argparse.ArgumentTypeError(f"File '{file_path}' does not exist.")
    return file_path


def validate_xlsx_file(file_path: str) -> str:
    """Validate if the file has a .xlsx extension."""
    if not file_path.lower().endswith('.xlsx'):
        raise argparse.ArgumentTypeError("File must have a .xlsx extension.")
    return file_path


def parse_ip_list(ip: str) -> str:
    """Validate if the IP address is valid."""
    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid IP address: {e}")


def dns_lookup(qname: Union[str, Name], rdtype: Union[RdataType, str], pattern: Optional[re.Pattern] = None) -> list:
    """Perform DNS lookup and return records."""
    try:
        answers = custom_resolver.resolve(qname, rdtype)
        records = []
        for rdata in answers:
            record_text = get_record_text(rdata)
            if pattern is None or pattern.match(record_text):
                records.append(record_text)
        return records
    except dns.resolver.NXDOMAIN:
        return ["No such domain"]
    except dns.resolver.Timeout:
        return ["Query timed out"]
    except dns.resolver.NoAnswer:
        return ["No answer from DNS server"]
    except dns.resolver.NoNameservers:
        return ["No nameservers available"]
    except Exception as e:
        return [f"Unexpected error: {str(e)}"]


def get_record_text(rdata: Answer) -> str:
    """Get text representation of DNS record."""
    if rdata.rdtype in [rdatatype.A, rdatatype.CNAME, rdatatype.PTR]:
        return rdata.to_text().strip('.')
    elif rdata.rdtype == rdatatype.TXT:
        return ''.join(chunk.decode('utf-8') for chunk in rdata.strings)
    elif rdata.rdtype == rdatatype.MX:
        return rdata.exchange.to_text().strip('.')
    else:
        return rdata.to_text().strip('.')


def process_dns_record(ip_or_host: str, dns_data: dict, record_type: str, key: str, data_func) -> None:
    """Generic function to process DNS records."""
    dns_data.setdefault(key, {'max_cols': 0, 'data': []})
    data = data_func()
    dns_data[key]['max_cols'] = max(len(data), dns_data[key]['max_cols'])
    dns_data[key]['data'].append([ip_or_host] + data)


def process_dmarc(host: str, dns_data: dict) -> None:
    """Process DMARC lookup for a domain."""
    process_dns_record(host, dns_data, 'TXT', DATA_TYPE_DMARC, lambda: dns_lookup(f'_dmarc.{host}', 'TXT'))


def process_spf(host: str, dns_data: dict) -> None:
    """Process SPF lookup for a domain."""
    process_dns_record(host, dns_data, 'TXT', DATA_TYPE_SPF, lambda: dns_lookup(host, 'TXT', spf_pattern))


def process_mx(host: str, dns_data: dict) -> None:
    """Process MX lookup for a domain."""
    process_dns_record(host, dns_data, 'MX', DATA_TYPE_MX, lambda: dns_lookup(host, 'MX'))


def process_a(host: str, dns_data: dict) -> None:
    """Process A record lookup for a domain."""
    process_dns_record(host, dns_data, 'A', DATA_TYPE_A, lambda: dns_lookup(host, 'A'))


def process_reverse(ip: str, dns_data: dict) -> None:
    """Process reverse DNS lookup for a domain."""
    reversed_ip = reversename.from_address(ip)
    process_dns_record(ip, dns_data, 'PTR', DATA_TYPE_PTR, lambda: dns_lookup(reversed_ip, 'PTR'))


def process_domain(host: str, args: argparse.Namespace, dns_data: dict) -> None:
    """Process DNS lookup for a single domain."""
    if args.dmarc_flag:
        if not is_ip(host):
            process_dmarc(host, dns_data)

    if args.spf_flag:
        if not is_ip(host):
            process_spf(host, dns_data)

    if args.mx_flag:
        if not is_ip(host):
            process_mx(host, dns_data)

    if args.a_flag:
        if not is_ip(host):
            process_a(host, dns_data)

    if args.reverse_flag:
        if is_ip(host):
            process_reverse(host, dns_data)


def write_to_excel(dns_data: dict, output_file: str, compact: bool = False) -> None:
    """Write DNS data to an Excel file. Compact mode combines data columns."""
    workbook = xlsxwriter.Workbook(output_file)
    header_field = workbook.add_format()
    header_field.set_bold()
    dns_sheets = {}

    for name, meta in dns_data.items():
        header_name = name.upper().replace(' ', '_')
        dns_sheets[name] = workbook.add_worksheet(name)
        dns_sheets[name].write(0, 0, "Host/IP", header_field)

        if compact:
            dns_sheets[name].write(0, 1, header_name, header_field)
        else:
            col = 1
            for i in range(meta['max_cols']):
                dns_sheets[name].write(0, col, f"{header_name}_{i}", header_field)
                col += 1

    for name, meta in dns_data.items():
        row = 1
        for row_data in meta['data']:
            dns_sheets[name].write(row, 0, row_data[0])

            if compact:
                cell_format = workbook.add_format({'text_wrap': True})
                cell_value = '\n'.join(row_data[1:])
                dns_sheets[name].write(row, 1, cell_value, cell_format)
            else:
                col = 1
                for col_data in row_data[1:]:
                    dns_sheets[name].write(row, col, col_data)
                    col += 1

            row += 1
        dns_sheets[name].autofit()

    workbook.close()


def main():
    # Argument parsing
    parser = argparse.ArgumentParser(prog="dnscheck", description="Bulk DNS Lookup Tool",
                                     formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=80))
    parser.add_argument('-i', '--input', metavar='<file>', dest="input_file", type=validate_file_path,
                        required=True, help='CSV file containing a list of domains')
    parser.add_argument("--input-type", choices=['txt', 'csv'], default='csv', dest="input_type",
                        help="Type of input file to process (txt or csv). (Default=csv)")
    parser.add_argument('--host-ip', metavar='IP/HOST', dest="host_field", type=str, required=False,
                        help='CSV field of host or IP. (default=Host)')
    parser.add_argument("--ns", metavar='8.8.8.8', dest="ns", nargs='+', type=parse_ip_list,
                        help="List of DNS server addresses")
    parser.add_argument('--dmarc', action="store_true", dest="dmarc_flag", help='DMARC record lookup')
    parser.add_argument('--spf', action="store_true", dest="spf_flag", help='SPF record lookup')
    parser.add_argument('--mx', action="store_true", dest="mx_flag", help='MX record lookup')
    parser.add_argument('-a', '--forward', action="store_true", dest="a_flag", help='A record lookup')
    parser.add_argument('-x', '--reverse', action="store_true", dest="reverse_flag",
                        help='PTR record lookup, ip to host')
    parser.add_argument('-c', '--compact', action="store_true", dest="compact_flag",
                        help='Compact format will add multiple records to single column.')
    parser.add_argument('-o', '--output', metavar='<xlsx>', dest="output_file", type=validate_xlsx_file,
                        required=True, help='Output file')

    if len(sys.argv) == 1:
        parser.print_usage()  # Print usage information if no arguments are passed
        sys.exit(1)

    args = parser.parse_args()

    if args.input_type == 'csv' and not args.host_field:
        args.host_field = 'Host'

    if args.input_type != 'csv' and args.host_field:
        parser.error("--host-ip can not be used with type '{}'".format(args.input_type))

    if args.input_file:
        print("Input file:", args.input_file)

    if args.ns:
        custom_resolver.nameservers = args.ns

    print("Nameserver(s):", custom_resolver.nameservers)

    dns_data = {}

    with open(args.input_file, 'r', encoding='utf-8-sig') as input_file:
        reader = csv.DictReader(input_file) if args.input_type == 'csv' else input_file
        for line in reader:
            host = line[args.host_field].strip() if args.input_type == 'csv' else line.strip()
            if not host:
                continue
            print("Processing:", host)
            process_domain(host, args, dns_data)

    write_to_excel(dns_data, args.output_file, args.compact_flag)

    print("Please see report: {}".format(args.output_file))


if __name__ == '__main__':
    main()
