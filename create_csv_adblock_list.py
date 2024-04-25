import argparse
import csv
from pathlib import Path
from pprint import pprint
from typing import Iterable, List

import requests

URLS = [
    "https://adaway.org/hosts.txt",
    "https://v.firebog.net/hosts/AdguardDNS.txt",
    "https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt",
    "https://s3.amazonaws.com/lists.disconnect.me/simple_ad.txt"
]


def main(opts: argparse.Namespace):
    lines = [line for url in URLS for line in download_file(url).splitlines()]
    lines = sorted(set(l for line in lines for l in extract_domain(line.decode())))
    lines.remove("")

    pprint(lines)
    print(len(lines))

    write_csv_file(opts.file, lines)


def download_file(url: str, ):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    return r.content


def extract_domain(line: str) -> Iterable[str]:
    pprint(line)
    if not line.startswith("#"):
        yield line.split(" ").pop()


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
