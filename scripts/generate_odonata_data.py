#!/usr/bin/env python3
"""Build the data files behind odonatatree.html and odonatalist.html.

  files/odonata_data.js        the newest files/world_odonata_list_<stamp>.csv,
                               embedded verbatim as window.WOL_CSV_TEXT so the
                               pages load it with a <script> tag (works from
                               file:// as well as GitHub Pages)
  files/odonata_phylogeny.json the family-level tree in
                               scripts/odonata_phylogeny_source.py
  files/odonata_phylogeny.js   the same, as window.ODONATA_PHYLOGENY
  files/odonata_china.js       files/odonata_china.csv and odonata_china_taxa.csv
                               as window.ODONATA_CN_CSV / ODONATA_CN_TAXA_CSV
  files/<stem>.js              each English-name region in ENGLISH_REGIONS
                               (North America, Europe, Australia & NZ):
                               files/<stem>.csv and <stem>_taxa.csv as
                               window.<prefix>_CSV / <prefix>_TAXA_CSV

Regional lists (hand-edited; these CSVs are the only copies):

  odonata_china.csv       species recorded in China with their Chinese names,
                          one row per species in CHINA_SOURCE, transcribed from
                          the book's table of contents and its checklist of
                          Chinese species (pp. 62-96) (Source Page). A row
                          with no Source Page was added from elsewhere, and its
                          Note says where; a Note on a book row explains a
                          re-identification. The Chinese Name may be empty.
  odonata_china_taxa.csv  Chinese names of suborders, superfamilies, families
                          and genera (Rank, Scientific Name, Chinese Name,
                          Source Page, Note). Rows with a Source Page are from
                          the same book; the Note says where any other name
                          came from. A genus the list has since sunk keeps its
                          row but labels nothing.
  odonata_north_america.csv, odonata_europe.csv, odonata_australia.csv
                          each region's checklist with English names (the
                          sources are in ENGLISH_REGIONS). Australia also
                          covers New Zealand, with a Country column; a species
                          in both has an Australian row first, so its
                          Australian name leads and the New Zealand one is an
                          alternative.
  <stem>_taxa.csv         English names of higher taxa: North America's
                          families (from the same list), and the suborders.

The species lists have the columns Scientific Name (as in the World Odonata
List when made), a name column, and Name in Source (as printed in the source).
The pages place each row by Scientific Name, else by Name in Source, through
the list's synonyms. A row neither name resolves is reported here as a warning.

The checks are the point, as in generate_phylogeny.py: the tree's tips must be
exactly the checklist's families, and every superfamily must be a clade of the
tree (the page draws one band per superfamily from runs of adjacent families).
Any failure is a hard error.

The World Odonata List CSV is hierarchical: each row fills one of the columns
Suborder, Superfamily, Family, Subfamily, Genus, Species, Synonym, and applies
to the rows below it. files/odonata_lib.js parses it the same way.
"""
import csv
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import odonata_phylogeny_source as P

ROOT   = pathlib.Path(__file__).resolve().parent.parent
FILES  = ROOT / "files"
DATA_JS = FILES / "odonata_data.js"
PHY_JSON = FILES / "odonata_phylogeny.json"
PHY_JS   = FILES / "odonata_phylogeny.js"
CN_CSV = FILES / "odonata_china.csv"
CN_TAXA_CSV = FILES / "odonata_china_taxa.csv"
CN_JS  = FILES / "odonata_china.js"
CHINA_SOURCE = "Zhang Haomiao (2019) 中国蜻蜓大图鉴 Dragonflies and Damselflies of China"
# The English-name regions: (label, file stem, JS prefix, source). Each has
# files/<stem>.csv (Scientific Name, English Name, Name in Source, ...) and an
# optional <stem>_taxa.csv (Rank, Scientific Name, English Name), embedded in
# files/<stem>.js as window.<prefix>_CSV / <prefix>_TAXA_CSV / <prefix>_SOURCE.
ENGLISH_REGIONS = [
    # From https://www.pugetsound.edu/north-american-odonata
    ("north america", "odonata_north_america", "ODONATA_NA",
     "North American Odonata, Dragonfly Society of the Americas (updated 18 Feb 2025)"),
    # Species: the IUCN European Red List of Dragonflies & Damselflies (2024),
    # less its four vagrants; names: Dijkstra, Schröter & Lewington (2020) as
    # listed on dragonflypix.com/checklist_en.html (and excluded.html)
    ("europe", "odonata_europe", "ODONATA_EU",
     "Dijkstra, Schröter & Lewington (2020) Field Guide to the Dragonflies of Britain and Europe, "
     "for the species of the IUCN European Red List of Dragonflies & Damselflies (2024)"),
    # From en.wikipedia.org "List of Odonata species of Australia" (rev 1378499913)
    # and "List of Odonata species of New Zealand" (June 2025 version)
    ("australia/nz", "odonata_australia", "ODONATA_AU",
     "Theischinger & Hawking (2021) The Complete Field Guide to Dragonflies of Australia "
     "and the IUCN Red List (New Zealand), as listed on Wikipedia"),
]
NAME_SOURCES_JSON = FILES / "odonata_name_sources.json"
# Where every regional name comes from, written to NAME_SOURCES_JSON (the list
# page links to it). Each row's Note column in the CSVs says which applies.
NAME_SOURCES = [
    {"region": "China", "language": "Chinese", "files": ["odonata_china.csv", "odonata_china_taxa.csv"],
     "main": CHINA_SOURCE + ", species accounts and checklist of Chinese species (pp. 62-96)",
     "also": ["Original descriptions of species described since 2019",
              "china-odonata.top (Odonata Research, Yu Xin)", "iNaturalist (zh-CN names)",
              "Hong Kong dragonfly checklist 2026 (hkdragonflies.blogspot.com)",
              "Liu, Zhang et al. (2025) Biodiversity Science 33: 25348",
              "Names set by the site owner, or formed from the type genus"]},
    {"region": "North America", "language": "English",
     "files": ["odonata_north_america.csv", "odonata_north_america_taxa.csv"],
     "main": "North American Odonata, Dragonfly Society of the Americas (updated 18 Feb 2025), "
             "https://www.pugetsound.edu/north-american-odonata",
     "also": ["Dijkstra (2023) Dragonflies and Damselflies of the World (some family names)"]},
    {"region": "Europe", "language": "English", "files": ["odonata_europe.csv", "odonata_europe_taxa.csv"],
     "main": "Species of the IUCN European Red List of Dragonflies & Damselflies (2024), less its four "
             "vagrants; names of Dijkstra, Schröter & Lewington (2020) Field Guide to the Dragonflies of "
             "Britain and Europe, as listed on dragonflypix.com",
     "also": ["Dijkstra (2023) Dragonflies and Damselflies of the World (some family names)",
              "Wikipedia and the North American list (other family names)"]},
    {"region": "Australia & New Zealand", "language": "English",
     "files": ["odonata_australia.csv", "odonata_australia_taxa.csv"],
     "main": "Wikipedia, List of Odonata species of Australia (after Theischinger & Hawking 2021, "
             "The Complete Field Guide to Dragonflies of Australia) and List of Odonata species of "
             "New Zealand (IUCN Red List names)",
     "also": ["Dijkstra (2023) Dragonflies and Damselflies of the World (some family names)",
              "Wikipedia, the North American list, and the shared ending of species names (other family names)"]},
]
PATTERN = re.compile(r"^world_odonata_list_(\d{14})$")
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def newest_list():
    found = []
    for p in FILES.glob("world_odonata_list_*.csv"):
        m = PATTERN.match(p.stem)
        if m:
            found.append((m.group(1), p))
    if not found:
        sys.exit(f"No world_odonata_list_<yyyymmddhhmmss>.csv found in {FILES}")
    return max(found)


def first_word(s):
    return s.strip().split()[0] if s.strip() else ""


def binomial(s):
    w = re.sub(r"\s+\([A-Z][a-z]+\)\s+", " ", s.replace("?", "")).split()
    if len(w) < 2 or not re.fullmatch(r"[A-Z][a-z]+", w[0]) or not re.fullmatch(r"[a-z][a-z-]*", w[1]):
        return ""
    return f"{w[0]} {w[1]}"


def read_checklist(path):
    """Return (families {name: (superfamily, suborder)} in list order, species count,
    set of every binomial the list knows: accepted names, synonyms, original names,
    set of accepted genera)."""
    fams, n, known, genera = {}, 0, set(), set()
    sub = sup = fam = ""
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["Suborder"].strip():
                sub, sup, fam = first_word(r["Suborder"]), "", ""
            if r["Superfamily"].strip():
                sup, fam = first_word(r["Superfamily"]), ""
            if r["Family"].strip():
                fam = first_word(r["Family"])
                if fam.upper() == "INCERTAE":
                    fam = f"{sup} incertae sedis"
                fams.setdefault(fam, (sup, sub))
            if r["Species"].strip():
                if not fam:
                    sys.exit(f"Species row outside any family: {r['Species']}")
                n += 1
                full = r["Species"].strip()
                known.add(binomial(full))
                if binomial(full):
                    genera.add(binomial(full).split()[0])
                orig = re.search(r"\[([A-Z][a-z]+)\]", full)
                if orig and binomial(full):
                    known.add(f"{orig.group(1)} {binomial(full).split()[1]}")
            if r["Synonym"].strip():
                known.add(binomial(re.sub(r"^Syn\s+", "", r["Synonym"].strip(), flags=re.I)))
    known.discard("")
    return fams, n, known, genera


def read_rows(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def check_species(path, rows, known, label):
    """Warn about species rows the list cannot place; return a summary line."""
    lost = [r for r in rows if r["Scientific Name"] not in known and r["Name in Source"] not in known]
    for r in lost:
        print(f"warning       : {path.name}: not in the list: {r['Scientific Name']} / "
              f"{r['Name in Source']}", file=sys.stderr)
    n_sp = len({r["Scientific Name"] for r in rows})
    return f"{label:14}: {len(rows)} rows, {n_sp} species, {len(lost)} not in the list"


def embed(js_path, variables):
    js_path.write_text("".join(f"window.{k} = {json.dumps(v, ensure_ascii=False)};\n"
                               for k, v in variables), encoding="utf-8")


def write_regional(known, fams, genera):
    """Embed the regional lists (see the docstring). Missing files are skipped."""
    out = []
    if CN_CSV.exists() and CN_TAXA_CSV.exists():
        out.append(check_species(CN_CSV, read_rows(CN_CSV), known, "china"))
        taxa = read_rows(CN_TAXA_CSV)
        used = [r for r in taxa if (r["Rank"] == "family" and r["Scientific Name"] in fams)
                or (r["Rank"] == "genus" and r["Scientific Name"] in genera)
                or (r["Rank"] == "superfamily" and r["Scientific Name"] in {v[0] for v in fams.values()})
                or r["Rank"] == "suborder"]
        out.append(f"china taxa    : {len(taxa)} rows, {len(used)} name a taxon in the list")
        embed(CN_JS, [("ODONATA_CN_SOURCE", CHINA_SOURCE),
                      ("ODONATA_CN_CSV", CN_CSV.read_text(encoding="utf-8-sig")),
                      ("ODONATA_CN_TAXA_CSV", CN_TAXA_CSV.read_text(encoding="utf-8-sig"))])
    else:
        print("warning       : odonata_china*.csv not found; no Chinese names", file=sys.stderr)
    for label, stem, prefix, source in ENGLISH_REGIONS:
        path, taxa = FILES / f"{stem}.csv", FILES / f"{stem}_taxa.csv"
        if not path.exists() or not source:
            print(f"warning       : {path.name} not found or no source; skipped", file=sys.stderr)
            continue
        out.append(check_species(path, read_rows(path), known, label))
        variables = [(f"{prefix}_SOURCE", source), (f"{prefix}_CSV", path.read_text(encoding="utf-8-sig"))]
        if taxa.exists():
            variables.append((f"{prefix}_TAXA_CSV", taxa.read_text(encoding="utf-8-sig")))
        embed(FILES / f"{stem}.js", variables)
    return out


def tips(node):
    if isinstance(node, str):
        return [node]
    return [t for c in node[1] for t in tips(c)]


def stats(node):
    """(internal node count, max depth, polytomy count)"""
    if isinstance(node, str):
        return 0, 1, 0
    n, d, poly = 1, 0, 1 if len(node[1]) > 2 else 0
    for c in node[1]:
        cn, cd, cp = stats(c)
        n += cn; poly += cp; d = max(d, cd)
    return n, d + 1, poly


def clades(node, out):
    """Collect the tip set of every internal node."""
    if isinstance(node, str):
        return {node}
    s = set()
    for c in node[1]:
        s |= clades(c, out)
    out.append(s)
    return s


def to_json(node, fams):
    if isinstance(node, str):
        sup, sub = fams[node]
        return {"name": node, "rank": "family", "superfamily": sup, "suborder": sub}
    name, children = node
    out = {"rank": "clade", "children": [to_json(c, fams) for c in children]}
    if name:
        out["name"] = name
    return out


def parse_sources(doc):
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
    stamp, src = newest_list()
    date_label = f"{int(stamp[6:8])} {MONTHS[int(stamp[4:6]) - 1]} {stamp[:4]}"
    label = f"World Odonata List ({date_label})"
    fams, n_species, known, genera = read_checklist(src)

    tree = P.TREE
    t = tips(tree)
    ok = True
    dupes = sorted({x for x in t if t.count(x) > 1})
    missing = [f for f in fams if f not in set(t)]
    extra = sorted(set(t) - set(fams))
    if dupes:
        print(f"ERROR: tips appear more than once: {dupes}", file=sys.stderr); ok = False
    if missing:
        print("ERROR: checklist families missing from the phylogeny:", file=sys.stderr)
        for f in missing:
            print(f"    {f:32} ({fams[f][0]})", file=sys.stderr)
        ok = False
    if extra:
        print(f"ERROR: phylogeny tips that are not checklist families: {extra}", file=sys.stderr)
        ok = False
    if ok:
        all_clades = []
        clades(tree, all_clades)
        by_sup = {}
        for f, (sup, _) in fams.items():
            by_sup.setdefault(sup, set()).add(f)
        for sup, members in by_sup.items():
            if len(members) > 1 and members not in all_clades:
                print(f"ERROR: superfamily {sup} is not a clade of the tree: "
                      f"{sorted(members)}", file=sys.stderr)
                ok = False
    if not ok:
        sys.exit(1)

    nodes, depth, poly = stats(tree)
    sources = parse_sources(P.__doc__)
    doc = {
        "meta": {
            "title": "Family-level phylogeny of Odonata",
            "basis": label,
            "families": len(t),
            "internalNodes": nodes,
            "maxDepth": depth,
            "polytomies": poly,
            "sources": sources,
            "sourceCount": len(sources),
            "limitation": " ".join(P.__doc__.split("KNOWN LIMITATION")[1]
                                   .strip().lstrip("-").split()),
            "generator": "scripts/generate_odonata_data.py from scripts/odonata_phylogeny_source.py",
        },
        "tree": to_json(tree, fams),
    }
    PHY_JSON.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    PHY_JS.write_text("window.ODONATA_PHYLOGENY = "
                      + json.dumps(doc, separators=(",", ":"), ensure_ascii=False) + ";\n",
                      encoding="utf-8")

    text = src.read_text(encoding="utf-8-sig")
    DATA_JS.write_text(
        f"window.WOL_VERSION = {json.dumps(stamp)};\n"
        f"window.WOL_LABEL = {json.dumps(label)};\n"
        f"window.WOL_CSV_TEXT = {json.dumps(text, ensure_ascii=False)};\n",
        encoding="utf-8")

    regional = write_regional(known, fams, genera)
    NAME_SOURCES_JSON.write_text(json.dumps({"sources": NAME_SOURCES}, ensure_ascii=False, indent=1) + "\n",
                                 encoding="utf-8")

    print(f"source        : {src.name}  ->  {label}")
    for line in regional:
        print(line)
    print(f"species       : {n_species:,} in {len(fams)} families")
    print(f"phylogeny     : {len(t)} tips (match checklist exactly), "
          f"{nodes} internal nodes, max depth {depth}, {poly} polytomies")
    english = [FILES / f"{stem}.js" for _, stem, _, src in ENGLISH_REGIONS if src]
    for p in [DATA_JS, PHY_JSON, PHY_JS, CN_JS, *english, NAME_SOURCES_JSON]:
        if p.exists(): print(f"wrote         : {p.relative_to(ROOT)} ({p.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
