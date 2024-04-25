import argparse
import csv
from pathlib import Path
from pprint import pprint
from typing import Iterable, List

import requests

URLS = [
    "https://adaway.org/hosts.txt",
    "https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt",
    "https://raw.githubusercontent.com/bigdargon/hostsVN/master/hosts",
    "https://raw.githubusercontent.com/jdlingyu/ad-wars/master/hosts",
    "https://s3.amazonaws.com/lists.disconnect.me/simple_ad.txt",
    "https://v.firebog.net/hosts/AdguardDNS.txt",
    "https://www.github.developerdan.com/hosts/lists/ads-and-tracking-extended.txt",
]


def main(opts: argparse.Namespace):
    lines = [line for url in URLS for line in download_file(url).splitlines()]
    domains = [domain for raw_line in lines for domain in extract_domain(raw_line.decode())]
    lines = clean_list(domains)

    pprint(lines)
    print(len(lines))

    write_csv_file(opts.file, lines)


def download_file(url: str, ):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    return r.content


def extract_domain(line: str) -> Iterable[str]:
    if not line.startswith("#"):
        yield line.split(" ").pop()


def clean_list(lines) -> List[str]:
    remove_entries = {
        '',
        "",
        "localhost",
    }
    for line in lines:
        if line.count(".") == 0:
            remove_entries.add(line)
        if len(line) < 3:
            remove_entries.add(line)

    lines = set(lines)
    for entry in remove_entries:
        if entry in lines:
            lines.remove(entry)
    return sorted(lines)


def write_csv_file(file_name: Path, lines: List[str]):
    with file_name.open("w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["ad_domain"])

        writer.writeheader()
        for line in lines:
            writer.writerow({'ad_domain': line})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=Path, default=Path("adlist.csv"), help="Output CSV file")
    return parser.parse_args()


if __name__ == '__main__':
    opts = parse_args()
    main(opts)
