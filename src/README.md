# Style guide page source

`STYLE_GUIDE.html` is built from these files. `STYLE_GUIDE.md` is its text twin.
Change the two guide files together.

| File | What it does |
|---|---|
| `template.html` | The page: styles, markup, samples and scripts. Its rule rows, token tables and token block are placeholders that the build fills in. |
| `build.py` | Takes from `STYLE_GUIDE.md` every rule's text, the version and date, the opening description, sections 1 and 2, the token tables (3.2 to 3.4), the token block (17) and the tables in 14.1 and 19. Embeds the fonts from `fonts/` and the used icons from `icons/`. Writes `STYLE_GUIDE.html`. Fails if a rule ID is in one file and not the other. It also fails if a pattern from an optional local, untracked word list, `src/.denylist` (one regex per line), matches the guide or the page; without that file it skips the check. |
| `contrast.py` | Measures WCAG 2.2 contrast for the token pairs in both themes and lists any pair below the required ratio. With `--md` it prints the table for section 14.1. |
| `check_values.py` | After a wording change, compares each rule's numbers, tokens, cross-references and MUST/SHOULD/MAY words with a git revision (default HEAD), and lists every difference. |
| `shoot_example.py` | Takes the README picture of `examples/dispatch.html` in both themes with Playwright and writes `docs/images/example.png`. Run it with `uv run --offline --no-project --with playwright python src/shoot_example.py`; add `--chromium <path>` to use your own browser. |
| `icons/` | Material Symbols Outlined (weight 400) as SVG files, with their Apache 2.0 license text. `icons/SOURCES.md` records where they came from. |
| `fonts/` | Instrument Sans (400, 500, 700) and Fragment Mono (400), Latin woff2, with their SIL OFL texts. `fonts/SOURCES.md` records where they came from. |

```bash
uv run --no-project python src/build.py
uv run --no-project python src/contrast.py
uv run --no-project python src/check_values.py
```

The built page is self-contained. You can also edit it directly, but then the next build
overwrites the edit. Edit `template.html` instead.
