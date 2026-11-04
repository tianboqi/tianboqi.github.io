#!/usr/bin/env python3
"""Turn scripts/phylogeny_source.py into files/bird_phylogeny.json and check it
against the family list of the newest Clements checklist.

The check is the point of this script. A family-level phylogeny is only usable
by birdtree.html if its tip set is exactly the checklist's family set — a
missing family would silently vanish from the drawing, an extra one would
dangle. Both are hard errors here.
"""
import csv
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import phylogeny_source as P

ROOT  = pathlib.Path(__file__).resolve().parent.parent
FILES = ROOT / "files"
DST   = FILES / "bird_phylogeny.json"
DST_JS = FILES / "bird_phylogeny.js"
PATTERN = re.compile(r"^Clements_v(\d{4})-([A-Za-z]+)-\d{4}$")


def splice(node, token, subtree):
    """Replace the string `token` wherever it appears with `subtree`."""
    if isinstance(node, str):
        return subtree if node == token else node
    name, children = node
    return (name, [splice(c, token, subtree) for c in children])


def tips(node):
    if isinstance(node, str):
        return [node]
    return [t for c in node[1] for t in tips(c)]


def to_json(node):
    if isinstance(node, str):
        return {"name": node, "rank": "family"}
    name, children = node
    out = {"rank": "clade", "children": [to_json(c) for c in children]}
    if name:
        out["name"] = name
    return out


def checklist_families():
    found = []
    for p in FILES.glob("Clements_v*.csv"):
        m = PATTERN.match(p.stem)
        if m:
            found.append((int(m.group(1)), p))
    if not found:
        sys.exit("No Clements checklist found")
    year, path = max(found)
    fams, order_of = {}, {}
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            if (r.get('category') or '').strip().lower() != 'species':
                continue
            full = (r.get('family') or '').strip()
            if not full:
                continue
            sci = full.split(' (')[0]
            com = full[len(sci) + 2:-1] if ' (' in full else ''
            fams.setdefault(sci, com)
            order_of.setdefault(sci, (r.get('order') or '').strip())
    return year, fams, order_of


def stats(node):
    """(internal node count, max depth, polytomy count)"""
    if isinstance(node, str):
        return 0, 1, 0
    n, d, poly = 1, 0, 1 if len(node[1]) > 2 else 0
    for c in node[1]:
        cn, cd, cp = stats(c)
        n += cn; poly += cp; d = max(d, cd)
    return n, d + 1, poly


def parse_sources(doc):
    """Citations from the module docstring: one per line, '#' lines are headers."""
    block = doc.split("PRIMARY SOURCES")[1].split("KNOWN LIMITATION")[0]
    out = []
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or set(line) <= {"-"}:
            continue
        if line.startswith("One citation per line") or line.startswith("source."):
            continue
        out.append(line)
    return out


def main():
    tree = splice(P.TREE, "__PASSERIDES__", P.PASSERIDES)
    t = tips(tree)
    year, fams, order_of = checklist_families()

    dupes  = sorted({x for x in t if t.count(x) > 1})
    missing = sorted(set(fams) - set(t))
    extra   = sorted(set(t) - set(fams))
    ok = True
    if dupes:
        print(f"ERROR: {len(dupes)} family appears more than once: {dupes}", file=sys.stderr); ok = False
    if missing:
        print(f"ERROR: {len(missing)} checklist families missing from the phylogeny:", file=sys.stderr)
        for f in missing:
            print(f"    {f:22} ({order_of.get(f,'?')})", file=sys.stderr)
        ok = False
    if extra:
        print(f"ERROR: {len(extra)} phylogeny tips are not checklist families:", file=sys.stderr)
        for f in extra:
            print(f"    {f}", file=sys.stderr)
        ok = False
    if not ok:
        sys.exit(1)

    # attach English names to tips
    def decorate(n):
        if n.get("rank") == "family":
            com = fams.get(n["name"])
            if com:
                n["comName"] = com
            n["order"] = order_of.get(n["name"], "")
        for c in n.get("children", []):
            decorate(c)
        return n

    nodes, depth, poly = stats(tree)
    sources = parse_sources(P.__doc__)
    doc = {
        "meta": {
            "title": "Family-level phylogeny of birds",
            "basis": f"eBird/Clements checklist v{year}",
            "families": len(t),
            "internalNodes": nodes,
            "maxDepth": depth,
            "polytomies": poly,
            "sources": sources,
            "sourceCount": len(sources),
            "limitation": " ".join(P.__doc__.split("KNOWN LIMITATION")[1]
                                   .strip().lstrip("-").split()),
            "generator": "scripts/generate_phylogeny.py from scripts/phylogeny_source.py",
        },
        "tree": decorate(to_json(tree)),
    }
    DST.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    # birdtree.html loads the tree through a <script> tag rather than fetch(),
    # for the same file:// reason as the checklist itself. Both files are
    # written from the same dict in the same run, so they cannot drift.
    DST_JS.write_text(
        "window.BIRD_PHYLOGENY = "
        + json.dumps(doc, separators=(",", ":"), ensure_ascii=False) + ";\n",
        encoding="utf-8")
    print(f"families      : {len(t)}  (matches checklist v{year} exactly)")
    print(f"internal nodes: {nodes}   max depth: {depth}   polytomies: {poly}")
    print(f"sources       : {len(sources)}")
    print(f"wrote         : {DST} ({DST.stat().st_size:,} bytes)")
    print(f"wrote         : {DST_JS} ({DST_JS.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
