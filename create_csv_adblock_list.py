import argparse
import csv
from pathlib import Path
from pprint import pprint
from typing import Iterable, List
from zipfile import ZipFile

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

UMBRELLA_URL = "http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip"


def main(opts: argparse.Namespace):
    cache_zip_file = Path("/tmp/umbrella_top-1m.csv.zip")
    cache_zip_file.unlink(missing_ok=True)
    cache_zip_file.write_bytes(download_file(UMBRELLA_URL))

    umbrella_lines = [line.split(",")[1] for line in unzip_and_read_lines(cache_zip_file)]

    add_lines = [line for url in URLS for line in download_file(url).splitlines()]
    add_domains = [domain for raw_line in add_lines for domain in extract_domain(raw_line.decode())]

    add_lines = clean_list(add_domains + umbrella_lines)
    pprint(add_lines)
    print(len(add_lines))

    write_csv_file(opts.file, add_lines)


def download_file(url: str, ):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    return r.content


def unzip_and_read_lines(cache_zip_file: Path) -> Iterable[str]:
    with ZipFile(cache_zip_file.absolute()) as myzip:
        with myzip.open('top-1m.csv') as myfile:
            for line in myfile.read().decode().splitlines():
                yield line


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
