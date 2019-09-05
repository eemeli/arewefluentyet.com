from data import Aggregator
import os
from collections import defaultdict
from datetime import date, timedelta
from functools import partial
import re

from helper import read_progress_data, parse_date, \
    pick_next_revision, get_current_revision, get_revision_date, \
    switch_to_revision, write_data, is_file_writable, is_dir_readable, \
    run_app

PARAMS = {
    "start_date": date(2019, 7, 1),
    "milestone": "M1",
    "frequency": timedelta(days=7),
    "main_file": "./browser/base/content/browser.xhtml"
}


def load_include(path, match=None):
    if match is not None:
        path = os.path.join(path, match[1])
    raw_data = open(path).read()

    new_dir = os.path.dirname(path)

    raw_data = re.sub('#include (.*)', partial(load_include, new_dir),
                      raw_data)
    return raw_data


def matches_in_file(path, entries, mc_path):
    full_path = os.path.join(mc_path, path)
    raw_data = load_include(full_path)

    re_dtd = re.compile("&([a-zA-Z][^;]+);")
    matches = re_dtd.findall(raw_data)
    for match in matches:
        entries.append({"type": "dtd", "id": match})

    re_ftl = re.compile("data-l10n-id=\"([^\"]+)\"")
    matches = re_ftl.findall(raw_data)
    entries.extend(({"type": "ftl", "id": match} for match in matches))


def get_data(mc_path, next_date, next_revision):
    entries = []
    matches_in_file(PARAMS["main_file"], entries, mc_path)

    snapshot = {"date": str(next_date), "revision": next_revision, "data": entries}

    progress = defaultdict(int)

    for entry in entries:
        progress[entry["type"]] += 1

    return (entries, progress)


if __name__ == "__main__":
    run_app(PARAMS, get_data)