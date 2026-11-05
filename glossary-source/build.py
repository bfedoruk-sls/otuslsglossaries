#!/usr/bin/env python3
"""Build gen/*.tex for the Linear Algebra Glossary from data/*.yaml.

Each data/sNN.yaml file holds one section:
  num, id, title, mods, blurb, entries: [ {id, term, plain_name?, mod, app?, plain,
  def, ex?, watch?, see?, aka?} ]
Extra files: data/notation.yaml, data/pairs.yaml, data/aliases.yaml, data/howto.tex
Links inside text use \\gl{id}{label}; every id is validated.
"""
import glob, os, re, sys, yaml

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA, GEN = os.path.join(ROOT, "data"), os.path.join(ROOT, "gen")
os.makedirs(GEN, exist_ok=True)

sections = [yaml.safe_load(open(f)) for f in sorted(glob.glob(os.path.join(DATA, "s[0-9][0-9].yaml")))]
entries = {}
errors = []
for s in sections:
    for e in s["entries"]:
        if e["id"] in entries:
            errors.append(f"duplicate id {e['id']}")
        e["_sec"] = s
        entries[e["id"]] = e

def plain(tex):
    """Very small LaTeX -> plain text for bookmarks and sorting."""
    t = tex
    t = re.sub(r"\\mathbb\{R\}\^n|\\mathbb\{R\}\^\{n\}", "Rⁿ", t)
    t = re.sub(r"\\mathbb\{R\}", "R", t)
    t = t.replace(r"\perp", "⊥").replace(r"\times", "×").replace(r"\to", "→")
    t = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", t)
    t = re.sub(r"\\[a-zA-Z]+", "", t)
    t = t.replace("$", "").replace("{", "").replace("}", "").replace("_", "").replace("^", "")
    t = t.replace("~", " ").replace("--", "–")
    return re.sub(r"\s+", " ", t).strip()

def name(e):
    return e.get("plain_name") or plain(e["term"])

def check_links(text, where):
    for tid in re.findall(r"\\glw?\{([^}]+)\}", text or ""):
        if tid not in entries:
            errors.append(f"{where}: unknown link target '{tid}'")

for e in entries.values():
    for k in ("plain", "def", "ex", "watch"):
        check_links(e.get(k), e["id"])
    for t in e.get("see", []) or []:
        if t not in entries:
            errors.append(f"{e['id']}: unknown see-also '{t}'")

def link(tid, label=None):
    if tid not in entries:
        return r"\textcolor{red}{??%s}" % tid
    return r"\gl{%s}{%s}" % (tid, label or entries[tid]["term"])

# ----------------------------------------------------------- body
out = []
for s in sections:
    terms = "".join(r"\glw{%s}{\textcolor{FutureBlue}{%s}}\par " % (e["id"], e["term"]) for e in s["entries"])
    out.append(r"\glsection{%s}{%s}{%s}{%s}{%s}{%d}{%s}" % (
        s["num"], s["id"], s["title"], "", s["blurb"].strip(), len(s["entries"]), terms))
    for e in s["entries"]:
        out.append(r"\begin{glentry}{%s}{%s}{%s}{%s}{%d}" % (
            e["id"], e["term"], name(e), "", 1 if e.get("app") else 0))
        out.append(r"\plainwords{%s}" % e["plain"].strip())
        out.append(r"\definition{%s}" % e["def"].strip())
        if e.get("ex"):
            out.append(r"\example{%s}" % e["ex"].strip())
        if e.get("watch"):
            out.append(r"\watch{%s}" % e["watch"].strip())
        see = ", ".join(link(t) for t in (e.get("see") or []))
        out.append(r"\entryfoot{%s}{%s}" % ((e.get("aka") or "").strip(), see))
        out.append(r"\end{glentry}")
        out.append("")
open(os.path.join(GEN, "body.tex"), "w").write("\n".join(out))

# ----------------------------------------------------------- contents
def colhead(t):
    return (r"{\labelfont\fontsize{7.8}{9}\selectfont\color{FutureBlue}%s}\par\vspace{3pt}"
            r"{\color{FutureBlue}\rule{\linewidth}{1pt}}\par\vspace{12pt}" % t)
c = [r"{\color{white}\noindent\begin{minipage}[t]{2.05in}\raggedright"]
c.append(colhead("START HERE"))
for lbl, txt in [("p:howto", "How to use this glossary"), ("p:notation", "Notation decoder"),
                 ("p:pairs", "Common mix-ups"), ("p:index", "A-Z index")]:
    c.append(r"\hyperref[%s]{\makebox[0.36in][l]{\medium\fontsize{9.5}{11}\selectfont\pageref{%s}}{\labelfont\fontsize{8.6}{11}\selectfont %s}}\par\vspace{11pt}" % (lbl, lbl, txt.upper()))
c.append(r"\end{minipage}\hspace{0.45in}\begin{minipage}[t]{4.2in}\raggedright")
c.append(colhead("THE TERMS"))
for s in sections:
    ttl = s.get("title_caps") or plain(s["title"]).upper()
    c.append(r"\hyperref[s:%s]{\makebox[0.36in][l]{\medium\fontsize{9.5}{11}\selectfont\pageref{s:%s}}\makebox[0.34in][l]{\bfseries\fontsize{16}{11}\selectfont\color{FutureBlue}%s}\parbox[t]{3.4in}{\raggedright{\labelfont\fontsize{8.6}{11}\selectfont %s}\\[1pt]{\light\fontsize{8}{10}\selectfont %d terms}}}\par\vspace{11pt}" % (
        s["id"], s["id"], s["num"], ttl, len(s["entries"])))
c.append(r"\end{minipage}}")
open(os.path.join(GEN, "contents.tex"), "w").write("\n".join(c))

# ----------------------------------------------------------- notation
nota = yaml.safe_load(open(os.path.join(DATA, "notation.yaml")))
n = [r"{\fontsize{9.2}{12.2}\selectfont"]
for grp in nota:
    n.append(r"\par\ifdim\dimexpr\pagegoal-\pagetotal\relax<1.1in\relax\ifdim\pagegoal<\maxdimen\newpage\fi\fi\vspace{10pt}\lbl[SimcoeBlue]{%s}\par\vspace{3pt}{\color{FutureBlue}\rule{\linewidth}{0.8pt}}\par\nopagebreak\vspace{2pt}" % grp["group"])
    for r in grp["rows"]:
        check_links(r.get("link", ""), "notation")
        n.append(r"\noindent\begin{tabularx}{\linewidth}{@{}>{\raggedright\arraybackslash}p{1.45in}>{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}p{1.55in}@{}}%s & %s & %s\end{tabularx}\par\vspace{2.5pt}" % (r["sym"], r["read"], r.get("link", "")))
n.append("}")
open(os.path.join(GEN, "notation.tex"), "w").write("\n".join(n))

# ----------------------------------------------------------- pairs
pairs = yaml.safe_load(open(os.path.join(DATA, "pairs.yaml")))
p = [r"\begin{multicols}{2}\raggedcolumns"]
for pr in pairs:
    a, b = pr["a"], pr["b"]
    for t in (a, b):
        if t not in entries:
            errors.append(f"pairs: unknown {t}")
    check_links(pr["text"], "pairs")
    p.append(r"""\begin{tcolorbox}[enhanced,breakable=false,colback=white,colframe=white,boxrule=0pt,arc=0pt,
 left=8pt,right=4pt,top=1pt,bottom=2pt,borderline west={3pt}{0pt}{SimcoeBlue},before skip=0pt,after skip=9pt]
{\bfseries\fontsize{10.8}{13}\selectfont\glw{%s}{\textcolor{FutureBlue}{%s}}\ {\color{Tangerine}\medium vs.}\ \glw{%s}{\textcolor{FutureBlue}{%s}}\par}
\vspace{3pt}{\fontsize{8.8}{12}\selectfont %s\par}
\end{tcolorbox}""" % (a, entries[a]["term"], b, entries[b]["term"], pr["text"].strip()))
p.append(r"\end{multicols}")
open(os.path.join(GEN, "pairs.tex"), "w").write("\n".join(p))

# ----------------------------------------------------------- index
aliases = yaml.safe_load(open(os.path.join(DATA, "aliases.yaml"))) or []
items = [(name(e), e["id"], None) for e in entries.values()]
for a in aliases:
    if a["to"] not in entries:
        errors.append(f"alias {a['name']}: unknown {a['to']}")
    items.append((a["name"], a["to"], a["name"]))
def sortkey(t):
    k = re.sub(r"^[^A-Za-z0-9]+", "", t[0]).lower()
    return k.replace("–", " ").replace("-", " ")
items.sort(key=sortkey)
ix = [r"{\fontsize{8.6}{11.6}\selectfont\begin{multicols}{3}\raggedright"]
cur = None
for nm, tid, alias in items:
    first = re.sub(r"^[^A-Za-z0-9]+", "", nm)[0].upper()
    if first.isdigit():
        first = r"\#"
    if first != cur:
        cur = first
        ix.append(r"\needspace{3\baselineskip}\vspace{8pt}{\bfseries\fontsize{18}{20}\selectfont\color{Tangerine}%s}\par\vspace{3pt}" % first)
    disp = entries[tid]["term"] if alias is None else nm
    if alias is None:
        ix.append(r"\glw{%s}{%s}\dotfill\glw{%s}{\textcolor{SimcoeBlue}{\medium\pageref{g:%s}}}\par" % (tid, disp, tid, tid))
    else:
        ix.append(r"{\itshape %s}, \textit{see} \gl{%s}{%s}\par" % (disp, tid, entries[tid]["term"]))
ix.append(r"\end{multicols}}")
open(os.path.join(GEN, "index.tex"), "w").write("\n".join(ix))

# ----------------------------------------------------------- how-to (static)
open(os.path.join(GEN, "howto.tex"), "w").write(open(os.path.join(DATA, "howto.tex")).read())

# ----------------------------------------------------------- csv export (source of truth for staff)
import csv
with open(os.path.join(ROOT, "glossary_terms.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["section", "id", "term", "application", "plain_words", "definition", "example", "dont_confuse_with", "see_also", "also_called"])
    for s in sections:
        for e in s["entries"]:
            w.writerow([plain(s["title"]), e["id"], name(e), "yes" if e.get("app") else "",
                        e["plain"].strip(), e["def"].strip(), (e.get("ex") or "").strip(),
                        (e.get("watch") or "").strip(), "; ".join(e.get("see") or []), (e.get("aka") or "").strip()])

print(f"{len(sections)} sections, {len(entries)} entries, {len(aliases)} aliases")
if errors:
    print("ERRORS:"); print("\n".join(errors)); sys.exit(1)
