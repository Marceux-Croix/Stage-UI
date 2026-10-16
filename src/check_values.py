"""Check that a wording change to STYLE_GUIDE.md kept every value.

Compares the working file with a git revision (default HEAD). For each rule ID it compares
the numbers, the backtick tokens, the RFC 2119 keywords and the rule ID references.
For each data table row outside the rule tables it
compares the numbers and the backtick tokens. Prints every difference; exits 1 if any.

    uv run --no-project python src/check_values.py [REV]
"""

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REL = "STYLE_GUIDE.md"
RULE = re.compile(r"^\| ([A-Z0-9]+(?:-[A-Z0-9]+)+) \| (.*) \|$", re.MULTILINE)
NUM = re.compile(r"(?<![\w-])\d+(?:\.\d+)?")
CODE = re.compile(r"`([^`]*)`")
KEY = re.compile(r"\b(MUST NOT|MUST|SHOULD NOT|SHOULD|MAY)\b")
REF = re.compile(r"\b(?:[A-Z0-9]+-)+[0-9]+\b")


def facts(text: str) -> dict:
    codes = CODE.findall(text)
    plain = CODE.sub(" ", text)
    return {
        "numbers": Counter(NUM.findall(plain)),
        "tokens": Counter(codes),
        "keywords": Counter(KEY.findall(plain)),
        "refs": Counter(REF.findall(plain)),
    }


def rules(md: str) -> dict:
    return dict(RULE.findall(md))


def data_rows(md: str) -> dict:
    """Non-rule table rows, keyed by section heading and first cell."""
    out, heading = {}, ""
    for line in md.splitlines():
        if line.startswith("#"):
            heading = line.strip()
        elif (
            line.startswith("|")
            and not RULE.match(line)
            and not re.match(r"^\|[-| ]+\|$", line)
        ):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells[0] in (
                "ID",
                "Token",
                "Role",
                "Radius",
                "Change",
                "Variant",
                "Asset",
                "Pair",
                "Version",
            ):
                continue
            key = (heading, cells[0])
            out[key] = " ".join(cells[1:])
    return out


def diff(a: dict, b: dict) -> list:
    msgs = []
    for k, before in a.items():
        after = b[k]
        lost, gained = before - after, after - before
        if lost:
            msgs.append(f"{k} lost {dict(lost)}")
        if gained:
            msgs.append(f"{k} gained {dict(gained)}")
    return msgs


def main() -> int:
    rev = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    shown = subprocess.run(
        ["git", "show", f"{rev}:{REL}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if shown.returncode != 0:
        print(f"no committed {REL} at {rev}: commit it once, then compare against that revision")
        return 1
    old = shown.stdout
    new = (ROOT / REL).read_text()
    problems = 0
    ro, rn = rules(old), rules(new)
    if list(ro) != list(rn):
        print("RULE IDS OR ORDER CHANGED")
        print("  only before:", sorted(set(ro) - set(rn)))
        print("  only after:", sorted(set(rn) - set(ro)))
        problems += 1
    for rid in ro:
        if rid not in rn:
            continue
        d = diff(facts(ro[rid]), facts(rn[rid]))
        if d:
            problems += 1
            print(f"{rid}: " + "; ".join(d))
    do, dn = data_rows(old), data_rows(new)
    for key in do:
        if key not in dn:
            print(f"TABLE ROW GONE {key[0]} / {key[1]}")
            problems += 1
            continue
        d = diff(facts(do[key]), facts(dn[key]))
        d = [m for m in d if not m.startswith(("keywords", "refs"))]
        if d:
            problems += 1
            print(f"TABLE {key[0]} / {key[1]}: " + "; ".join(d))
    changed = sum(1 for rid in ro if rid in rn and ro[rid] != rn[rid])
    print(
        f"\n{len(ro)} rules before, {len(rn)} after; {changed} reworded; {problems} with a value difference."
    )
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
