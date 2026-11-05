# Linear Algebra Glossary (MATH 1850U): source files

## What's here

| Path | What it is |
|---|---|
| `data/s01.yaml` … `data/s11.yaml` | The glossary content, one file per section. **Edit terms here.** |
| `data/pairs.yaml` | The cards on the "Common mix-ups" page |
| `data/notation.yaml` | The rows in the notation decoder |
| `data/aliases.yaml` | Index-only names that point to an entry (for example, "Pivot" points to "Leading 1") |
| `data/howto.tex` | The "How to use this glossary" page |
| `build.py` | Turns the YAML into LaTeX in `gen/`, checks every link, and writes `glossary_terms.csv` |
| `gen/` | Generated LaTeX. Don't edit this folder, because `build.py` overwrites it |
| `glossary.tex` | The main document: page design, colours, fonts, section openers, entry layout, back cover |
| `cover/cover.html` | The cover design (HTML), rendered to `cover/cover.pdf` |
| `cover/render_cover.js` | Renders the cover HTML to PDF and PNG with Playwright |
| `logo/brand.pdf` | The Ontario Tech Brand Guidelines QRG. The logos are clipped from it as vector art |
| `logo/logo_white_clean.svg` | The white logo used on the cover |
| `fonts/` | Ubuntu (Ubuntu Font Licence) and Fira Math (SIL OFL) |
| `glossary_terms.csv` | Every entry in one spreadsheet, for review |

## Rebuilding the PDF

You need Python 3 with PyYAML (`pip install pyyaml`) and a TeX installation with XeLaTeX (TeX Live or MacTeX).

```bash
python3 build.py                 # regenerate gen/*.tex and check every link
xelatex glossary.tex             # run three times so page numbers and links settle
xelatex glossary.tex
xelatex glossary.tex
```

`build.py` stops with a list of errors if any `\gl{...}` link, "see also" ID, mix-up pair or alias points to a term ID that doesn't exist.

## Rebuilding the cover

The glossary includes `cover/cover.pdf` as page 1. If you change `cover.html`, re-render it. This needs Node and Playwright (`npm install playwright`, then `npx playwright install chromium`):

```bash
node cover/render_cover.js "$(pwd)/cover"
```

Then run XeLaTeX again to pick up the new cover.

## Writing an entry

Each entry in a section file looks like this:

```yaml
- id: span                      # unique ID used for links
  term: Span                    # the heading (LaTeX allowed)
  plain_name: Span              # optional: plain-text name for bookmarks and the index
  mod: 7a                       # module tag
  app: true                     # optional: shows the APPLICATION badge
  plain: >-                     # "In plain words" line
    Everything you can build ...
  def: >-                       # definition
    ...
  ex: >-                        # optional example
    ...
  watch: >-                     # optional "Don't confuse with"
    \gl{basis}{Basis}. A spanning set ...
  see: [spanning-set, basis]    # "See also" links, by ID
  aka: other name               # optional "Also called"
```

Link to another entry anywhere in the text with `\gl{id}{label}`. Use `>-` for any field that contains a colon, so YAML doesn't misread it.

## Brand notes

- Colours: Future Blue `#003C71`, Simcoe Blue `#0077CA`, Tech Tangerine `#E75D2A` (graphics and type of 16 pt or more only), Spirit Navy `#00283C`, and tints of Cool Grey.
- Type: Ubuntu throughout. Maths is set in Fira Math to match.
- The guide asks staff to contact brand@ontariotechu.ca before using the logo.
