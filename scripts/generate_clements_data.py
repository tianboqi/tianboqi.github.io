#!/usr/bin/env python3
"""Embed files/Clements_v2025-October-2025.csv into files/clements_data.js
so birdtree.html can load it via a <script> tag instead of fetch() —
this works identically whether the page is opened via file://, a local
server, or GitHub Pages, sidestepping CORS restrictions on local fetch().
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC  = ROOT / "files" / "Clements_v2025-October-2025.csv"
DST  = ROOT / "files" / "clements_data.js"

def main():
    text = SRC.read_text(encoding="utf-8-sig")
    js = "window.CLEMENTS_CSV_TEXT = " + json.dumps(text) + ";\n"
    DST.write_text(js, encoding="utf-8")
    print(f"Wrote {DST} ({len(js):,} bytes) from {SRC.name}")

if __name__ == "__main__":
    main()
