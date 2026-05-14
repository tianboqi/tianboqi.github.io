#!/usr/bin/env python3
"""Regenerate cv.html from files/CV_website.pdf.

Run locally:  python scripts/generate_cv.py
Or automatically via GitHub Actions when the PDF is pushed.
"""

import re
import sys
from html import escape
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    sys.exit("Install pdfplumber: pip install pdfplumber")

PDF_PATH = Path("files/CV_website.pdf")
OUTPUT   = Path("cv.html")

# ── Section registry ────────────────────────────────────────────────────────

SECTIONS = [
    "EDUCATION",
    "RESEARCH EXPERIENCE",
    "SELECTED PUBLICATIONS",
    "SKILLS",
    "SCHOLARSHIPS AND AWARDS",
    "POSTERS AND TALKS",
    "OTHER EXPERIENCES",
    "REFERENCE CONTACTS",
]

# Match a section by its first distinct word (handles small-caps line-splitting)
SECTION_BY_FIRST_WORD = {
    "EDUCATION":    "EDUCATION",
    "RESEARCH":     "RESEARCH EXPERIENCE",
    "SELECTED":     "SELECTED PUBLICATIONS",
    "SKILLS":       "SKILLS",
    "SCHOLARSHIPS": "SCHOLARSHIPS AND AWARDS",
    "POSTERS":      "POSTERS AND TALKS",
    "OTHER":        "OTHER EXPERIENCES",
    "REFERENCE":    "REFERENCE CONTACTS",
}

SECTION_TITLE = {
    "EDUCATION":               "Education",
    "RESEARCH EXPERIENCE":     "Research Experience",
    "SELECTED PUBLICATIONS":   "Selected Publications",
    "SKILLS":                  "Skills",
    "SCHOLARSHIPS AND AWARDS": "Scholarships and Awards",
    "POSTERS AND TALKS":       "Posters and Talks",
    "OTHER EXPERIENCES":       "Other Experiences",
    "REFERENCE CONTACTS":      "Reference Contacts",
}

# Right-column content is only treated as a date if it matches this pattern
DATE_RE  = re.compile(r'^\d{4}\s*[–—\-]\s*\d{0,4}$')
EMAIL_RE = re.compile(r'[\w.+-]+@[\w.-]+\.[a-z]{2,}', re.I)
DOI_RE   = re.compile(r'doi\.org/[\w./\-]+', re.I)
JOURNAL_RE = re.compile(
    r'\b(Nature Methods|Nature|Cell|Neuron|Science|BioRxiv)\b(?=\s*[\(\d])',
    re.I
)
IN_VIVO_RE = re.compile(r'\bin vivo\b', re.I)

# ── PDF extraction ───────────────────────────────────────────────────────────

def group_words_into_lines(words: list) -> dict:
    """Cluster words into visual lines using a 4pt vertical-gap tolerance.

    This handles small-caps section headers whose characters sit at slightly
    different y positions (e.g. 'AND' at y=191 vs surrounding text at y=189).
    """
    if not words:
        return {}

    sorted_words = sorted(words, key=lambda w: w["top"])
    lines: dict[float, list] = {}
    y_keys: list[float] = []

    for w in sorted_words:
        y = w["top"]
        matched_key = next((k for k in y_keys if abs(y - k) <= 4), None)
        if matched_key is None:
            y_keys.append(y)
            lines[y] = []
            matched_key = y
        lines[matched_key].append(w)

    return lines


def extract_lines(path: Path) -> list[dict]:
    """Return list of {left, right, x0} dicts, one per visual line.

    Only text that looks like a year-range (e.g. '2019 – 2026') is placed in
    the right column; all other text — including wrapped body lines that extend
    past 62% of page width — is kept in the left column.
    """
    rows = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            W = page.width
            words = page.extract_words(x_tolerance=3, y_tolerance=3)
            line_groups = group_words_into_lines(words)

            for y in sorted(line_groups):
                line = sorted(line_groups[y], key=lambda w: w["x0"])
                cut  = W * 0.62

                left_words  = [w for w in line if w["x0"] < cut]
                right_words = [w for w in line if w["x0"] >= cut]

                left  = " ".join(w["text"] for w in left_words).strip()
                right = " ".join(w["text"] for w in right_words).strip()

                # Only keep right column if it looks like a year range.
                # Otherwise it is wrapped body text — merge it into left.
                if right and not DATE_RE.match(right):
                    left  = (left + " " + right).strip()
                    right = ""

                x0 = line[0]["x0"] if line else 0
                if left or right:
                    rows.append({"left": left, "right": right, "x0": x0})
    return rows


def detect_section(left: str) -> "str | None":
    """Return section key if this line is a section header, else None.

    Checks only the first word (upper-cased) so partial matches caused by
    small-caps rendering still work.
    """
    words = left.strip().split()
    if not words:
        return None
    first = words[0].upper()
    # Require the text to be all-uppercase (section headers are small-caps)
    alpha_only = re.sub(r'[^a-zA-Z]', '', left)
    if alpha_only and not alpha_only.isupper():
        return None
    return SECTION_BY_FIRST_WORD.get(first)


def split_sections(lines: list[dict]) -> "list[tuple[str, list]]":
    """Group lines into (section_key, lines) pairs, dropping the header block."""
    sections: "list[tuple[str, list]]" = []
    current_key:  str | None = None
    current: list = []

    for line in lines:
        s = detect_section(line["left"])
        if s:
            if current_key:
                sections.append((current_key, current))
            current_key = s
            current = []
        elif current_key is not None:
            current.append(line)

    if current_key:
        sections.append((current_key, current))
    return sections

# ── Markup helpers ───────────────────────────────────────────────────────────

def linkify_email(text: str) -> str:
    return EMAIL_RE.sub(
        lambda m: f'<a href="mailto:{m.group()}">{m.group()}</a>', text
    )


def linkify_doi(text: str) -> str:
    # Rejoin DOIs split by PDF line breaks: "doi.org/...-  02583" → "doi.org/...-02583"
    text = re.sub(r'(doi\.org/[\w./\-]+-)\s+(\w)', r'\1\2', text)

    def make_link(m: re.Match) -> str:
        doi = m.group().rstrip('.,;)')   # strip trailing punctuation from URL
        tail = m.group()[len(doi):]      # keep any stripped chars as plain text
        return f'<a href="https://{doi}" target="_blank">{doi}</a>{tail}'

    return DOI_RE.sub(make_link, text)


def italicize_journals(text: str) -> str:
    return JOURNAL_RE.sub(lambda m: f'<i>{m.group()}</i>', text)


def italicize_in_vivo(text: str) -> str:
    return IN_VIVO_RE.sub('<i>in vivo</i>', text)


def bold_author(text: str) -> str:
    return re.sub(r'Qi T\*?', lambda m: f'<b>{m.group()}</b>', text)


def fmt(raw: str, *, author=False, doi=False, email=False,
        journals=False, in_vivo=False) -> str:
    """Escape HTML, then selectively apply markup transforms."""
    text = escape(raw)
    if author:   text = bold_author(text)
    if doi:      text = linkify_doi(text)
    if email:    text = linkify_email(text)
    if journals: text = italicize_journals(text)
    if in_vivo:  text = italicize_in_vivo(text)
    return text

# ── Section renderers ────────────────────────────────────────────────────────

INDENT_THRESHOLD = 68   # x0 pt; lines indented past this are sub-items


def render_entries(lines: list[dict]) -> str:
    """Education and Research Experience."""
    entries: list[dict] = []
    current: dict | None = None

    for line in lines:
        left  = line["left"].strip()
        right = line["right"].strip()
        x0    = line["x0"]

        if not left:
            continue

        is_sub = x0 > INDENT_THRESHOLD or left.startswith("•")

        if is_sub:
            text = left.lstrip("•").strip()
            if current is None:
                continue
            if text.lower().startswith("advisor"):
                suffix = escape(text)
                current["inst"] = (
                    current["inst"] + f" &middot; {suffix}"
                ).lstrip(" &middot;")
            else:
                current["bullets"].append(text)
        else:
            role, inst = left.split(" | ", 1) if " | " in left else (left, "")
            role = role.strip()
            inst = inst.strip()
            date = right.strip()

            # Date sometimes gets merged into inst when it falls inside the 62% cutoff;
            # pull it back out if it appears at the end of the inst string.
            if not date:
                m = re.search(r'\s+(\d{4}\s*[–—\-]\s*\d{0,4})\s*$', inst)
                if m:
                    date = m.group(1)
                    inst = inst[:m.start()].strip()

            current = {
                "role":    escape(role),
                "inst":    escape(inst),
                "date":    escape(date),
                "bullets": [],
            }
            entries.append(current)

    parts = []
    for e in entries:
        date_html = f'<span class="cv-date">{e["date"]}</span>' if e["date"] else ""
        parts.append(f'    <div class="cv-entry">\n      <div>\n')
        parts.append(f'        <p class="cv-role">{e["role"]}</p>\n')
        if e["inst"]:
            parts.append(f'        <p class="cv-inst">{e["inst"]}</p>\n')
        if e["bullets"]:
            parts.append('        <ul class="cv-bullets">\n')
            for b in e["bullets"]:
                parts.append(f'          <li>{fmt(b, in_vivo=True)}</li>\n')
            parts.append('        </ul>\n')
        parts.append(f'      </div>\n      {date_html}\n    </div>\n')
    return "".join(parts)


def render_publications(lines: list[dict]) -> str:
    """Bullet list of publications; merge continuation lines per entry."""
    pubs: list[str] = []
    buf:  list[str] = []

    for line in lines:
        text = line["left"].strip()
        if not text:
            continue
        if text.startswith("•"):
            if buf:
                pubs.append(" ".join(buf))
            buf = [text.lstrip("•").strip()]
        else:
            buf.append(text)

    if buf:
        pubs.append(" ".join(buf))

    parts = ['    <ul class="cv-pub-list">\n']
    for pub in pubs:
        h = fmt(pub, author=True, doi=True, journals=True)
        # Wrap status parentheticals in italic span
        h = re.sub(
            r'\((BioRxiv|in prep\.?|under revision[^)]*)\)',
            lambda m: f'<span class="pub-status">({m.group(1)})</span>',
            h
        )
        parts.append(f'      <li>{h}</li>\n')
    parts.append('    </ul>\n')
    return "".join(parts)


def render_skills(lines: list[dict]) -> str:
    """Category: content rows, merging wrapped continuation lines."""
    # A line starts a new skill if it has a single-word label before ":"
    def is_skill_start(text: str) -> bool:
        if ":" not in text:
            return False
        label = text.split(":", 1)[0].strip()
        return " " not in label and len(label) < 20

    merged: list[str] = []
    for line in lines:
        text = line["left"].strip()
        if not text:
            continue
        if is_skill_start(text) or not merged:
            merged.append(text)
        else:
            merged[-1] += " " + text   # continuation of previous wrapped line

    parts = []
    for text in merged:
        if is_skill_start(text):
            label, content = text.split(":", 1)
            parts.append(
                f'    <div class="cv-skill">'
                f'<span class="cv-skill-label">{escape(label.strip())}: </span>'
                f'{escape(content.strip())}'
                f'</div>\n'
            )
        else:
            parts.append(f'    <div class="cv-skill">{escape(text)}</div>\n')
    return "".join(parts)


def render_list(lines: list[dict]) -> str:
    """Generic bullet / plain list (awards, talks, other, references)."""
    items: list[str] = []
    buf:   list[str] = []

    for line in lines:
        text = line["left"].strip()
        if not text:
            continue
        if text.startswith("•"):
            if buf:
                items.append(" ".join(buf))
            buf = [text.lstrip("•").strip()]
        elif buf:
            buf.append(text)   # continuation of previous bullet
        else:
            items.append(text) # non-bullet line (e.g. Other Experiences)

    if buf:
        items.append(" ".join(buf))

    parts = ['    <ul class="cv-list">\n']
    for item in items:
        parts.append(f'      <li>{fmt(item, email=True)}</li>\n')
    parts.append('    </ul>\n')
    return "".join(parts)


RENDERERS = {
    "EDUCATION":               render_entries,
    "RESEARCH EXPERIENCE":     render_entries,
    "SELECTED PUBLICATIONS":   render_publications,
    "SKILLS":                  render_skills,
    "SCHOLARSHIPS AND AWARDS": render_list,
    "POSTERS AND TALKS":       render_list,
    "OTHER EXPERIENCES":       render_list,
    "REFERENCE CONTACTS":      render_list,
}

# ── HTML template ────────────────────────────────────────────────────────────

HTML_HEAD = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CV — Tianbo Qi</title>
  <link rel="icon" type="image/x-icon" href="/images/favicon.ico">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Lora:ital,wght@0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <link rel="stylesheet" href="css/style.css">
</head>

<body>

<header class="banner">
  <div class="banner-inner">
    <div class="banner-text">
      <h1 class="banner-name">Curriculum Vitae</h1>
      <p class="banner-sub"><a href="index.html">← Tianbo Qi</a></p>
    </div>
    <div class="banner-socials">
      <a href="files/CV_website.pdf" download class="cv-download">
        <i class="fa-solid fa-download"></i> PDF
      </a>
    </div>
  </div>
</header>

<main>

"""

HTML_FOOT = """\
</main>

<footer class="site-footer">
  <div class="footer-inner">
    <p>&copy; 2026 Tianbo Qi. All rights reserved.</p>
  </div>
</footer>

</body>
</html>
"""

# ── Main ─────────────────────────────────────────────────────────────────────

def build_section(key: str, lines: list[dict]) -> str:
    title = SECTION_TITLE[key]
    sub   = ' <span class="section-sub">(*co-first authors)</span>' \
            if key == "SELECTED PUBLICATIONS" else ""
    body  = RENDERERS[key](lines)
    return f'  <section>\n    <h2>{title}{sub}</h2>\n{body}  </section>\n\n'


def main() -> None:
    if not PDF_PATH.exists():
        sys.exit(f"PDF not found: {PDF_PATH}")

    print(f"Parsing {PDF_PATH} …")
    lines    = extract_lines(PDF_PATH)
    sections = split_sections(lines)

    found   = [k for k, _ in sections]
    missing = [s for s in SECTIONS if s not in found]
    if missing:
        print(f"WARNING: sections not detected: {missing}", file=sys.stderr)

    html = [HTML_HEAD]
    for key, sec_lines in sections:
        html.append(build_section(key, sec_lines))
    html.append(HTML_FOOT)

    OUTPUT.write_text("".join(html), encoding="utf-8")
    print(f"Written → {OUTPUT}")


if __name__ == "__main__":
    main()
