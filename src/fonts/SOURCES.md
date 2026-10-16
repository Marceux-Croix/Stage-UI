# Font sources

The style guide's typefaces. `build.py` embeds these files in `STYLE_GUIDE.html`.

| File | Family, weight | Source | License |
|---|---|---|---|
| `instrument-sans-latin-400-normal.woff2` | Instrument Sans 400 | npm `@fontsource/instrument-sans@5.3.0`, `files/` | SIL OFL 1.1, `InstrumentSans-OFL.txt` |
| `instrument-sans-latin-500-normal.woff2` | Instrument Sans 500 | same | same |
| `instrument-sans-latin-700-normal.woff2` | Instrument Sans 700 | same | same |
| `fragment-mono-latin-400-normal.woff2` | Fragment Mono 400 | npm `@fontsource/fragment-mono@5.3.0`, `files/` | SIL OFL 1.1, `FragmentMono-OFL.txt` |

Downloaded from jsDelivr on 2026-09-27. Latin subset, as Fontsource ships it.

- Instrument Sans: Copyright 2022 The Instrument Sans Project Authors,
  https://github.com/Instrument/instrument-sans
- Fragment Mono: Copyright 2022 The Fragment-Mono Project Authors,
  https://github.com/weiweihuanghuang/fragment-mono

Neither license declares a Reserved Font Name, so a subset or converted copy may keep the
family's real name. This guide keeps the real names.

Checked with fontTools: Instrument Sans has the `tnum` feature (tabular numerals, rule
TYP-2); Fragment Mono is monospaced (every digit is 618 units wide).
