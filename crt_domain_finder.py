#!/usr/bin/env python
import re
import argparse

import requests

TARGET_URL = 'https://crt.sh/?q='
DOMAIN_REGEXP = r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}'


def remove_html_tags(text: str) -> str:
    clean = re.compile('<.*?>')
    return re.sub(clean, ' ', text)


def write_list_in_file(write_list: list, output_file: str) -> None:
    with open(f'{output_file}', 'w+') as file:
        file.write('\n'.join(write_list))


def crt_get_subdomains(target_url: str) -> list:
    subdomains = []
    target_response = requests.get(target_url)
    if target_response.status_code == 200:
        subdomains = re.findall(DOMAIN_REGEXP, remove_html_tags(str(target_response.content)))
    return subdomains


def clear_subdomain(dirty_subdomains: list, target_word: str) -> list:
    clear_subdomains = [subdomains for subdomains in dirty_subdomains if target_word in subdomains]
    clear_subdomains = list(dict.fromkeys(clear_subdomains))
    return clear_subdomains


def get_subdomains(target_domain: str, search_keyword: bool = True) -> list:
    target_word = target_domain.rsplit(".", 1)[0]

    target_domain_url = f'{TARGET_URL}%25.{target_domain}'
    target_word_url = f'{TARGET_URL}{target_word}.%25'

    all_subdomains = crt_get_subdomains(target_domain_url)
    if search_keyword:
        all_subdomains += crt_get_subdomains(target_word_url)
    all_subdomains = clear_subdomain(all_subdomains, target_word)

    return all_subdomains


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Extract all domains with second level word from domain from crt.sh website.'
    )
    parser.add_argument(
        'target_domain',
        type=str,
        help='Target domain (google.com, microsoft.com)'
    )
    parser.add_argument(
        '-o',
        '--output',
        help='Save the results to text file'
    )
    parser.add_argument(
        '-w',
        '--without_keyword',
        action='store_true',
        help='Searches only subdomains',
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    savefile = args.output

    found_subdomains = get_subdomains(args.target_domain, not args.without_keyword)

    print(f"Founded: {len(found_subdomains)} domains related to {args.target_domain}")
    if not len(found_subdomains):
        print("=(")
        exit(-1)
    elif savefile:
        write_list_in_file(found_subdomains, savefile)
        print(f"Output file name: {savefile}")
    else:
        for line in found_subdomains:
            print(line)
