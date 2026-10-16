"""Build STYLE_GUIDE.html from template.html.

Embeds Instrument Sans and Fragment Mono as base64 woff2, an SVG sprite of the Material Symbols
icons, and the token block from section 17 of STYLE_GUIDE.md. The Markdown file is the
source of every rule's text, the version, and the tables in sections 14.1 and 19; the build
fails when a rule ID is in one file and not in the other.
"""

import base64
import html as htmllib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
ASSETS = HERE
OUT = ROOT / "STYLE_GUIDE.html"

FONT_DIR = HERE / "fonts"
FONTS = [
    ("Instrument Sans", 400, "instrument-sans-latin-400-normal.woff2"),
    ("Instrument Sans", 500, "instrument-sans-latin-500-normal.woff2"),
    ("Instrument Sans", 700, "instrument-sans-latin-700-normal.woff2"),
    ("Fragment Mono", 400, "fragment-mono-latin-400-normal.woff2"),
]


def font_css() -> str:
    rules = []
    for family, weight, name in FONTS:
        data = base64.b64encode((FONT_DIR / name).read_bytes()).decode()
        rules.append(
            f'@font-face {{ font-family: "{family}"; font-style: normal; font-weight: {weight}; '
            f'font-display: swap; src: url(data:font/woff2;base64,{data}) format("woff2"); }}'
        )
    rules.append(
        "/* Instrument Sans and Fragment Mono: SIL Open Font License 1.1. "
        "Icons: Material Symbols Outlined, Apache License 2.0. */"
    )
    return "\n".join(rules)


def icon_sprite(template: str) -> str:
    used = set(re.findall(r'#i-([a-z_]+(?:-fill)?)"', template))
    used |= set(re.findall(r'ic\("([a-z_]+(?:-fill)?)"', template))
    missing = sorted(n for n in used if not (ASSETS / "icons" / f"{n}.svg").exists())
    if missing:
        raise SystemExit(f"icons not found: {missing}")
    symbols = []
    for svg in sorted((ASSETS / "icons").glob("*.svg")):
        if svg.stem not in used:
            continue
        text = svg.read_text()
        paths = re.findall(r'<path d="([^"]+)"', text)
        if not paths:
            raise SystemExit(f"no path in {svg.name}")
        body = "".join(f'<path d="{d}"/>' for d in paths)
        symbols.append(
            f'<symbol id="i-{svg.stem}" viewBox="0 -960 960 960">{body}</symbol>'
        )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">'
        + "".join(symbols)
        + "</svg>"
    )


def token_block() -> str:
    md = (ROOT / "STYLE_GUIDE.md").read_text()
    section = md.split("## 17. Token block", 1)[1]
    block = re.search(r"```css\n(.*?)```", section, re.DOTALL)
    if not block:
        raise SystemExit("token block not found in STYLE_GUIDE.md")
    css = block.group(1)
    if "`" in css or "${" in css:
        raise SystemExit("token block has characters that break a JS template literal")
    return css


MD = ROOT / "STYLE_GUIDE.md"
RULE_ROW = re.compile(r"^\| ([A-Z0-9]+(?:-[A-Z0-9]+)+) \| (.*) \|$", re.MULTILINE)
KEYWORDS = re.compile(r"\b(MUST NOT|MUST|SHOULD|MAY)\b")


def md_inline(text: str) -> str:
    """Markdown cell text to HTML: code spans and RFC 2119 keywords."""
    parts = re.split(r"(`[^`]*`)", text)
    out = []
    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            out.append("<code>" + htmllib.escape(part[1:-1], quote=False) + "</code>")
        else:
            esc = htmllib.escape(part, quote=False)
            esc = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc)
            esc = KEYWORDS.sub(r'<b class="k">\1</b>', esc)
            out.append(esc)
    return "".join(out)


def md_rules(md: str) -> dict:
    rules = {}
    for rid, text in RULE_ROW.findall(md):
        if rid in ("ID",):
            continue
        rules[rid] = text
    return rules


def sync_rules(page: str, rules: dict) -> str:
    row = re.compile(
        r'(<tr><td><span class="rid(?: block)?">)([A-Z0-9-]+)(</span></td>)<td[^>]*>.*?</td>',
        re.DOTALL,
    )
    seen = set()

    def repl(m):
        rid = m.group(2)
        if rid not in rules:
            raise SystemExit(f"rule {rid} is in the page but not in STYLE_GUIDE.md")
        seen.add(rid)
        text = rules[rid]
        return m.group(1) + rid + m.group(3) + "<td>" + md_inline(text) + "</td>"

    page = row.sub(repl, page)
    missing = sorted(set(rules) - seen)
    if missing:
        raise SystemExit(f"rules in STYLE_GUIDE.md but not in the page: {missing}")
    return page


def md_section(md: str, heading: str) -> str:
    """The text under a heading, up to the next "## " heading."""
    lines = md.split("\n")
    start = next(i for i, l in enumerate(lines) if l.strip() == heading)
    body = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body).strip("\n")


def md_blocks(text: str) -> str:
    """Paragraphs, "###" headings, "- " lists (one nested level) and "N. " lists, as HTML."""
    out, para, items, kind = [], [], [], None

    def flush_para():
        if para:
            out.append("<p>" + md_inline(" ".join(para)) + "</p>")
            para.clear()

    def flush_list():
        nonlocal kind
        if not items:
            return
        tag = "ol" if kind == "ol" else "ul"
        html = []
        for item, subs in items:
            sub = "".join("<li>" + md_inline(t) + "</li>" for t in subs)
            html.append(
                "<li>" + md_inline(item) + (f"<ul>{sub}</ul>" if sub else "") + "</li>"
            )
        out.append(f"<{tag}>" + "".join(html) + f"</{tag}>")
        items.clear()
        kind = None

    for raw in text.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            flush_para()
            continue
        if line.startswith("### "):
            flush_para()
            flush_list()
            out.append("<h3>" + md_inline(line[4:]) + "</h3>")
        elif re.match(r"^- ", line):
            flush_para()
            if kind == "ol":
                flush_list()
            kind = "ul"
            items.append([line[2:], []])
        elif re.match(r"^\d+\. ", line):
            flush_para()
            if kind == "ul":
                flush_list()
            kind = "ol"
            items.append([re.sub(r"^\d+\. ", "", line), []])
        elif re.match(r"^  +- ", line) and items:
            items[-1][1].append(line.strip()[2:])
        elif line.startswith("  ") and items:
            if items[-1][1]:
                items[-1][1][-1] += " " + line.strip()
            else:
                items[-1][0] += " " + line.strip()
        else:
            flush_list()
            para.append(line.strip())
    flush_para()
    flush_list()
    return "\n".join(out)


def md_intro(md: str) -> str:
    """The text between the version paragraph and "## 1.": the guide's opening description."""
    lines = md.split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("Version "))
    while start < len(lines) and lines[start].strip():
        start += 1
    end = next(i for i, l in enumerate(lines) if l.startswith("## 1. "))
    return "\n".join(lines[start:end]).strip("\n")


def principles(md: str) -> str:
    """Section 1 as a lead paragraph and one card per numbered principle."""
    body = md_section(md, "## 1. Principles")
    lead, cards, cur = [], [], None
    for line in body.split("\n"):
        m = re.match(r"^(\d+)\. \*\*(.+?)\*\*\s*(.*)$", line)
        if m:
            cur = [m.group(1), m.group(2).rstrip("."), m.group(3)]
            cards.append(cur)
        elif line.startswith("   ") and cur:
            cur[2] += " " + line.strip()
        elif line.strip() and not cards:
            lead.append(line.strip())
    html = '<p class="lead">' + md_inline(" ".join(lead)) + "</p>" if lead else ""
    html += (
        '<div class="grid g3" style="margin-top:16px">'
        + "".join(
            f'<div class="pr"><p class="pn">{n}</p><h4>{md_inline(t)}</h4><p>{md_inline(x)}</p></div>'
            for n, t, x in cards
        )
        + "</div>"
    )
    return html


def table_rows(md: str, heading: str) -> list:
    """Cells of the first Markdown table after a heading, header and divider removed."""
    after = md.split(heading, 1)[1]
    rows = []
    for line in after.splitlines():
        if line.startswith("|"):
            rows.append([c.strip() for c in line.strip("|").split("|")])
        elif rows:
            break
    return rows[2:]


def plain(cell: str) -> str:
    return cell.replace("`", "")


def swatch_color(value: str) -> str:
    """A CSS color for a stage palette value written in words."""
    v = plain(value)
    grad = re.match(r"^(#[0-9A-Fa-f]{6}) to (#[0-9A-Fa-f]{6})", v)
    if grad:
        return f"linear-gradient(90deg,{grad.group(1)} 70%,{grad.group(2)})"
    m = re.search(r"#[0-9A-Fa-f]{6}|rgba\([^)]*\)", v)
    if m:
        return m.group(0)
    m = re.match(r"white at (\d+)%", v)
    if m:
        return f"rgba(255,255,255,{int(m.group(1)) / 100})"
    raise SystemExit(f"no color in stage palette value: {value}")


def token_arrays(md: str) -> dict:
    page = [
        [plain(r[0]), plain(r[1]), plain(r[2]), r[3]]
        for r in table_rows(md, "### 3.2 Page tokens")
    ]
    fixed = [
        [plain(r[0]), plain(r[1]), r[2]] for r in table_rows(md, "### 3.3 Fixed tokens")
    ]
    stage = [
        [r[0], plain(r[1]), swatch_color(r[1])]
        for r in table_rows(md, "### 3.4 Stage palette")
    ]
    return {
        "/*@PAGE@*/[]": json.dumps(page),
        "/*@FIXED@*/[]": json.dumps(fixed),
        "/*@STAGEPAL@*/[]": json.dumps(stage),
    }


def md_table(md: str, heading: str) -> str:
    """The first Markdown table after a heading, as an HTML table."""
    after = md.split(heading, 1)[1]
    lines = []
    for line in after.splitlines():
        if line.startswith("|"):
            lines.append(line)
        elif lines:
            break
    head = [c.strip() for c in lines[0].strip("|").split("|")]
    body = [[c.strip() for c in l.strip("|").split("|")] for l in lines[2:]]
    th = "".join(f"<th>{htmllib.escape(c)}</th>" for c in head)
    tr = "".join(
        "<tr>" + "".join(f'<td class="num">{md_inline(c)}</td>' for c in r) + "</tr>"
        for r in body
    )
    return f'<div class="tbl-wrap"><table class="tbl"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def main() -> None:
    html = (HERE / "template.html").read_text()
    md = MD.read_text()
    m = re.search(r"^Version (\d+\.\d+), (\d{4}-\d{2}-\d{2})\.", md, re.MULTILINE)
    version, date = m.group(1), m.group(2)
    html = html.replace("@VERSION@", version).replace("@DATE@", date)
    html = sync_rules(html, md_rules(md))
    for marker, value in (
        ("<!--@GOAL@-->", md_blocks(md_intro(md))),
        ("<!--@SEC1@-->", md_blocks(md_section(md, "## 2. How to use this guide"))),
        ("<!--@PRINCIPLES@-->", principles(md)),
    ):
        if html.count(marker) != 1:
            raise SystemExit(f"marker {marker} must appear exactly once")
        html = html.replace(marker, value)
    i = md.index("## 17. Token block")
    css = (
        md[
            md.index("```css\n", i) + 7 : md.index("@media (prefers-reduced-motion", i)
        ].rstrip()
        + "\n"
    )
    if html.count("/*@TOKENS_CSS@*/") != 1:
        raise SystemExit("marker /*@TOKENS_CSS@*/ must appear exactly once")
    html = html.replace("/*@TOKENS_CSS@*/", css)
    for marker, value in token_arrays(md).items():
        if html.count(marker) != 1:
            raise SystemExit(f"marker {marker} must appear exactly once")
        html = html.replace(marker, value)
    for marker, heading in (
        ("<!--@CONTRAST@-->", "### 14.1 Measured contrast"),
        ("<!--@CHANGES@-->", "## 19. Changes"),
    ):
        if html.count(marker) != 1:
            raise SystemExit(f"marker {marker} must appear exactly once")
        html = html.replace(marker, md_table(md, heading))
    for marker, value in (
        ("/*@FONTS@*/", font_css()),
        ("<!--@ICONS@-->", icon_sprite(html)),
        ("/*@TOKENS@*/", token_block()),
    ):
        if html.count(marker) != 1:
            raise SystemExit(f"marker {marker} must appear exactly once")
        html = html.replace(marker, value)
    # Optional local word list: src/.denylist is untracked, one regex per line, "#" starts a
    # comment. When it exists, the build fails if any pattern matches the guide or the page.
    denylist = HERE / ".denylist"
    if denylist.exists():
        for line in denylist.read_text().splitlines():
            pattern = line.strip()
            if not pattern or pattern.startswith("#"):
                continue
            rx = re.compile(pattern, re.IGNORECASE)
            if rx.search(md) or rx.search(html):
                raise SystemExit(f"a word from src/.denylist is in the guide or the page: {pattern}")
    OUT.write_text(html)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
