"""WCAG 2.2 contrast for the Stage UI token pairs, both themes.

Translucent colors are composited over the surface they sit on. Text pairs need 4.5:1
(3:1 for large text, 18.66 px bold or 24 px). Non-text UI parts need 3:1. Disabled text
is exempt and reported for information only.
"""

import re

T = {
    "dark": {
        "base": "#0D0F17",
        "raised": "#171A26",
        "menu": "#1D2130",
        "inverted": "#EDEFF7",
        "inverted-hover": "#D3D7E4",
        "additive": "rgba(255,255,255,.1)",
        "chip-hover": "rgba(255,255,255,.2)",
        "outline": "rgba(255,255,255,.2)",
        "outline-opaque": "#2E3345",
        "text": "#EDEFF7",
        "text-2": "#9AA0B4",
        "text-3": "rgba(255,255,255,.54)",
        "text-dis": "#6B7186",
        "text-inv": "#0D0F17",
        "primary": "#22D3EE",
        "primary-hover": "#67E8F9",
        "primary-inv": "#0E7490",
        "suggested": "#10303B",
        "danger": "#FB923C",
        "danger-bg": "rgba(251,146,60,.16)",
        "needs-input": "#FACC15",
        "green": "#34D399",
        "search-bg": "#0A0C13",
        "search-focus": "#0891B2",
        "tooltip": "rgba(46,51,69,.94)",
    },
    "light": {
        "base": "#F7F8FC",
        "raised": "#FFFFFF",
        "menu": "#FFFFFF",
        "inverted": "#10131C",
        "inverted-hover": "#262A38",
        "additive": "rgba(16,19,28,.05)",
        "chip-hover": "rgba(16,19,28,.1)",
        "outline": "rgba(16,19,28,.12)",
        "outline-opaque": "#E1E4EE",
        "text": "#10131C",
        "text-2": "#5A6072",
        "text-3": "rgba(16,19,28,.6)",
        "text-dis": "#8A90A2",
        "text-inv": "#FFFFFF",
        "primary": "#0E7490",
        "primary-hover": "#155E75",
        "primary-inv": "#22D3EE",
        "suggested": "#DDF6FB",
        "danger": "#B83C0B",
        "danger-bg": "#FFEDE3",
        "needs-input": "#A16207",
        "green": "#047857",
        "search-bg": "#FFFFFF",
        "search-focus": "#0E7490",
        "tooltip": "rgba(46,51,69,.94)",
    },
}
FIXED = {
    "accent": "#8B5CF6",
    "progress": "#8B5CF6",
    "indicator": "#7C3AED",
    "stage": "#07080F",
    "stage-popup": "rgba(22,25,38,.92)",
    "white": "#FFFFFF",
    "dark": "#0D0F17",
    "yellow": "#FACC15",
    "stage-danger": "#FF7A33",
    "stage-select": "#22D3EE",
}


def parse(c):
    c = c.strip()
    if c.startswith("#"):
        h = c[1:]
        return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4)) + (1.0,)
    m = re.match(r"rgba\(([\d.]+),([\d.]+),([\d.]+),([\d.]+)\)", c.replace(" ", ""))
    return tuple(float(m.group(i)) for i in (1, 2, 3)) + (float(m.group(4)),)


def over(fg, bg):
    r, g, b, a = fg
    R, G, B, _ = bg
    return (r * a + R * (1 - a), g * a + G * (1 - a), b * a + B * (1 - a), 1.0)


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def ratio(fg, bg):
    a, b = lum(fg), lum(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def surface(theme, *layers):
    """Composite layers bottom to top. Each layer is a token or fixed name."""
    c = None
    for name in layers:
        v = parse(T[theme].get(name) or FIXED[name])
        c = v if c is None else over(v, c)
    return c


# (label, foreground, surface layers bottom to top, need, kind)
PAIRS = [
    ("Body text on page", "text", ("base",), 4.5, "text"),
    ("Body text on menu", "text", ("menu",), 4.5, "text"),
    ("Body text on tonal fill", "text", ("base", "additive"), 4.5, "text"),
    ("Body text on hover fill", "text", ("base", "chip-hover"), 4.5, "text"),
    ("Body text on highlighted row", "text", ("base", "suggested"), 4.5, "text"),
    ("Body text on card over menu", "text", ("menu", "additive"), 4.5, "text"),
    ("Secondary text on page", "text-2", ("base",), 4.5, "text"),
    ("Secondary text on menu", "text-2", ("menu",), 4.5, "text"),
    ("Secondary text on raised", "text-2", ("raised",), 4.5, "text"),
    ("Secondary text on card", "text-2", ("base", "additive"), 4.5, "text"),
    ("Secondary text on highlighted row", "text-2", ("base", "suggested"), 4.5, "text"),
    ("Feed timestamp (text-3) on page", "text-3", ("base",), 4.5, "text"),
    (
        "Feed timestamp on highlighted row (text-2)",
        "text-2",
        ("base", "suggested"),
        4.5,
        "text",
    ),
    ("Filled button / active chip text", "text-inv", ("inverted",), 4.5, "text"),
    ("Filled button text, hover", "text-inv", ("inverted-hover",), 4.5, "text"),
    ("Primary button text", "text-inv", ("primary",), 4.5, "text"),
    ("Primary button text, hover", "text-inv", ("primary-hover",), 4.5, "text"),
    ("Text-primary button on page", "primary", ("base",), 4.5, "text"),
    ("Text-primary button on menu", "primary", ("menu",), 4.5, "text"),
    ("Snackbar text", "text-inv", ("inverted",), 4.5, "text"),
    ("Snackbar action (primary-inv)", "primary-inv", ("inverted",), 4.5, "text"),
    ("Danger text (form error) on page", "danger", ("base",), 4.5, "text"),
    ("Danger badge text", "danger", ("base", "danger-bg"), 4.5, "text"),
    ("Confirm prompt (danger) on card", "danger", ("base", "additive"), 4.5, "text"),
    (
        "OK badge text (green) on neutral badge",
        "green",
        ("base", "additive"),
        4.5,
        "text",
    ),
    ("Healthy state text (green) on menu", "green", ("menu",), 4.5, "text"),
    ("Degraded state text (danger) on menu", "danger", ("menu",), 4.5, "text"),
    ("Search placeholder (text-2)", "text-2", ("search-bg",), 4.5, "text"),
    ("Tooltip text", "white", ("base", "tooltip"), 4.5, "text"),
    (
        "User name chip and avatar (text-inv on inverted)",
        "text-inv",
        ("inverted",),
        4.5,
        "text",
    ),
    ("Count badge text", "white", ("indicator",), 4.5, "text"),
    ("Live status badge text", "white", ("indicator",), 4.5, "text"),
    ("Live dot and scrubber knob (accent) on page", "accent", ("base",), 3.0, "ui"),
    ("Disabled text on page (exempt)", "text-dis", ("base",), 0, "info"),
    ("Needs-input dot on page", "needs-input", ("base",), 3.0, "ui"),
    ("Danger dot, icon, underline on page", "danger", ("base",), 3.0, "ui"),
    ("Selection ring / new dot (primary) on page", "primary", ("base",), 3.0, "ui"),
    ("Healthy dot (green) on page", "green", ("base",), 3.0, "ui"),
    ("Working dot (text-2) on page", "text-2", ("base",), 3.0, "ui"),
    ("Search focus border on search fill", "search-focus", ("search-bg",), 3.0, "ui"),
    ("Focus ring (text) on page", "text", ("base",), 3.0, "ui"),
    ("Slider and switch (primary) on menu", "primary", ("menu",), 3.0, "ui"),
    ("Panel border (outline) on page (decorative)", "outline", ("base",), 0, "info"),
]
STAGE = [
    ("Stage label, white 88%", "rgba(255,255,255,.88)", 4.5),
    ("Stage sub-label, white 62%", "rgba(255,255,255,.62)", 4.5),
    ("Stage group label, white 55%", "rgba(255,255,255,.55)", 4.5),
    ("Stage overlay meta, white 70%", "rgba(255,255,255,.7)", 4.5),
    ("Count pill text on yellow", "dark-on-yellow", 4.5),
    ("Rich tooltip label, white 70% on popup", "popup", 4.5),
    ("Selection ring (cyan) on the stage", FIXED["stage-select"], 3.0),
    ("Needs-input yellow on the stage", FIXED["yellow"], 3.0),
    ("Stage danger orange on the stage", FIXED["stage-danger"], 3.0),
    ("Error icon, dark on stage danger pill", "dark-on-danger", 3.0),
    ("Progress fill (violet) on the stage", FIXED["progress"], 3.0),
    ("Scrubber knob and live dot (accent) on the stage", FIXED["accent"], 3.0),
    ("Item dot, cool gray 58%, on the stage", "rgba(160,166,186,.58)", 3.0),
]


def markdown():
    """Print the measured pairs as the Markdown table for section 14.1 of the guide."""
    print("| Pair | Dark | Light | Needs |")
    print("|---|---|---|---|")
    for label, fg, layers, need, kind in PAIRS:
        vals = []
        for th in ("dark", "light"):
            bg = surface(th, *layers)
            f = parse(T[th].get(fg) or FIXED[fg])
            vals.append(ratio(over(f, bg) if f[3] < 1 else f, bg))
        req = "exempt" if kind == "info" else f"{need}:1"
        print(f"| {label} | {vals[0]:.2f} | {vals[1]:.2f} | {req} |")
    black = parse(FIXED["stage"])
    for label, fg, need in STAGE:
        if fg == "dark-on-yellow":
            r = ratio(parse(FIXED["dark"]), parse(FIXED["yellow"]))
        elif fg == "dark-on-danger":
            r = ratio(parse(FIXED["dark"]), parse(FIXED["stage-danger"]))
        elif fg == "popup":
            bg = over(parse(FIXED["stage-popup"]), black)
            r = ratio(over(parse("rgba(255,255,255,.7)"), bg), bg)
        else:
            f = parse(fg)
            r = ratio(over(f, black) if f[3] < 1 else f, black)
        print(f"| Stage: {label} | {r:.2f} | {r:.2f} | {need}:1 |")


def main():
    fails = []
    print(f"{'Pair':50} {'dark':>7} {'light':>7}  need")
    for label, fg, layers, need, kind in PAIRS:
        row = []
        for th in ("dark", "light"):
            bg = surface(th, *layers)
            f = parse(T[th].get(fg) or FIXED[fg])
            if f[3] < 1:
                f = over(f, bg)
            r = ratio(f, bg)
            row.append(r)
            if need and r < need:
                fails.append((label, th, r, need))
        tag = "info" if kind == "info" else f"{need}:1"
        print(f"{label:50} {row[0]:7.2f} {row[1]:7.2f}  {tag}")
    print("\nStage (theme-independent, on the stage color)")
    black = parse(FIXED["stage"])
    for label, fg, need in STAGE:
        if fg == "dark-on-yellow":
            r = ratio(parse(FIXED["dark"]), parse(FIXED["yellow"]))
        elif fg == "dark-on-danger":
            r = ratio(parse(FIXED["dark"]), parse(FIXED["stage-danger"]))
        elif fg == "popup":
            bg = over(parse(FIXED["stage-popup"]), black)
            r = ratio(over(parse("rgba(255,255,255,.7)"), bg), bg)
        else:
            f = parse(fg)
            r = ratio(over(f, black) if f[3] < 1 else f, black)
        if r < need:
            fails.append((label, "stage", r, need))
        print(f"{label:50} {r:7.2f}          {need}:1")
    print("\nBelow the required ratio:")
    for label, th, r, need in fails:
        print(f"  {label} [{th}]: {r:.2f} < {need}")
    if not fails:
        print("  none")


if __name__ == "__main__":
    import sys

    markdown() if "--md" in sys.argv else main()
