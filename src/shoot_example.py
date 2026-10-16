"""Take the README screenshots of examples/dispatch.html.

Run from the repo root:
    uv run --offline --no-project --with playwright python src/shoot_example.py [--chromium PATH]

Writes docs/images/example.png: the same screen in the dark theme (left) and
the light theme (right), split by a violet line that leans like a slash through the center.
"""
import argparse
import base64
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "examples" / "dispatch.html").as_uri()
OUT = ROOT / "docs" / "images" / "example.png"
W, H = 1440, 900

COMPOSITE = """<!doctype html><meta charset="utf-8">
<style>
html, body { margin: 0; background: #0D0F17; }
.wrap { position: relative; width: %(w)dpx; height: %(h)dpx; overflow: hidden; }
.wrap img { position: absolute; inset: 0; width: 100%%; height: 100%%; display: block; }
.light { clip-path: polygon(815.7px 0, 100%% 0, 100%% 100%%, 624.3px 100%%); }
.line { position: absolute; inset: 0; width: 100%%; height: 100%%; }
</style>
<div class="wrap">
<img src="%(dark)s" alt="">
<img class="light" src="%(light)s" alt="">
<svg class="line" viewBox="0 0 %(w)d %(h)d"><line x1="815.7" y1="0" x2="624.3" y2="900" stroke="#8B5CF6" stroke-width="2"/></svg>
</div>"""


def uri(png: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(png).decode()


def shot(browser, scheme: str, theme: str) -> bytes:
    ctx = browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=2, color_scheme=scheme)
    page = ctx.new_page()
    page.goto(f"{PAGE}?theme={theme}")
    page.evaluate("document.fonts.ready")
    page.wait_for_function("window.__stageDrawn === true")
    # A theme label in the badge style, beside the split line, which leans 12 degrees and crosses the center.
    page.evaluate(
        """([text, side]) => {
          const b = document.createElement("span");
          b.className = "sbadge"; b.textContent = text;
          b.style.cssText = "position:fixed;top:66px;z-index:99;" + (side === "left" ? "right:651px" : "left:809px");
          document.body.appendChild(b);
        }""",
        ["Dark", "left"] if theme == "dark" else ["Light", "right"],
    )
    page.wait_for_timeout(300)
    png = page.screenshot(animations="disabled")
    ctx.close()
    return png


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chromium", help="path to a Chromium executable (default: Playwright's own)")
    args = ap.parse_args()
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.chromium) if args.chromium else p.chromium.launch()
        dark = shot(browser, "dark", "dark")
        light = shot(browser, "light", "light")
        ctx = browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=2)
        page = ctx.new_page()
        page.set_content(COMPOSITE % {"w": W, "h": H, "dark": uri(dark), "light": uri(light)})
        page.wait_for_function("Array.from(document.images).every(i => i.complete)")
        OUT.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(OUT), animations="disabled")
        browser.close()
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
