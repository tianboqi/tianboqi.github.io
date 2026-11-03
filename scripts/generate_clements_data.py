#!/usr/bin/env python3
"""Embed the newest files/Clements_v*.csv into files/clements_data.js so
birdtree.html can load it via a <script> tag instead of fetch() — this works
identically whether the page is opened via file://, a local server, or GitHub
Pages, sidestepping CORS restrictions on local fetch().

The checklist is picked automatically: the highest vYYYY among
files/Clements_v<year>-<Month>-<year>.csv. The version label is derived from
that filename, so birdtree.html never hard-codes a year.

The CSV is embedded verbatim. Anything wrong with the data is fixed in the CSV
itself, not here, so that a checklist dropped onto the page by hand behaves
exactly like the bundled one. This script only sanity-checks the file and warns
— note that the v2026 release as published shipped three species rows
(brcfly1, orhthr1, pubsun4) with truncated range text and blank order/family;
those are corrected in the committed copy and will need correcting again if the
file is re-downloaded.
"""
import csv
import json
import pathlib
import re
import sys

ROOT  = pathlib.Path(__file__).resolve().parent.parent
FILES = ROOT / "files"
DST   = FILES / "clements_data.js"

PATTERN = re.compile(r"^Clements_v(\d{4})-([A-Za-z]+)-\d{4}$")
MONTH_ABBR = {
    'january': 'Jan', 'february': 'Feb', 'march': 'Mar', 'april': 'Apr',
    'may': 'May', 'june': 'Jun', 'july': 'Jul', 'august': 'Aug',
    'september': 'Sep', 'october': 'Oct', 'november': 'Nov', 'december': 'Dec',
}


def newest_checklist():
    """Return (path, year, month) for the highest-version Clements CSV."""
    found = []
    for p in FILES.glob("Clements_v*.csv"):
        m = PATTERN.match(p.stem)
        if m:
            found.append((int(m.group(1)), m.group(2), p))
    if not found:
        sys.exit(f"No Clements_v<year>-<Month>-<year>.csv found in {FILES}")
    year, month, path = max(found, key=lambda t: t[0])
    return path, year, month


def check(path):
    """Warn about rows birdtree.html would silently drop. Returns species count."""
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    species = [r for r in rows if (r.get('category') or '').strip().lower() == 'species']
    blank = [r for r in species
             if not (r.get('order') or '').strip() or not (r.get('family') or '').strip()]
    for r in blank:
        print(f"  !! blank order/family: {r.get('scientific name','?')} "
              f"({r.get('species_code','?')}) — the page will drop this row",
              file=sys.stderr)
    return len(species), len(blank)


def main():
    src, year, month = newest_checklist()
    text  = src.read_text(encoding="utf-8-sig")
    label = f"Clements {MONTH_ABBR.get(month.lower(), month)} {year}"
    total, blank = check(src)

    js = (
        f"window.CLEMENTS_VERSION = {json.dumps(f'v{year}')};\n"
        f"window.CLEMENTS_LABEL = {json.dumps(label)};\n"
        f"window.CLEMENTS_CSV_TEXT = {json.dumps(text)};\n"
    )
    DST.write_text(js, encoding="utf-8")

    print(f"source  : {src.name}  ->  {label}")
    print(f"species : {total:,}" + (f"  ({blank} unusable)" if blank else ""))
    print(f"wrote   : {DST} ({len(js):,} bytes)")


if __name__ == "__main__":
    main()
