#!/usr/bin/env python3
"""Keep the old URLs of moved guide pages working: redirect stubs, written into a built site.

    redirect_stubs.py <agent-fleet checkout> <ref> <dist dir>

Reads guide/_redirects.tsv at <ref> (`old<TAB>new`, English paths relative to guide/; `page.md#anchor` on the left
is a section that moved out of a page) and runs after `astro build`, so nothing written here reaches Pagefind or
the sitemap.

- An old page that this build does not have gets a stub at its URL, in English and in Japanese: a script that sends
  the reader to the row of `location.hash`, or to the page-level target when no row matches; a meta refresh to the
  page-level target for readers without JavaScript; a canonical link; noindex; a plain link.
- The page-level target is the page's own row (`old.md<TAB>new.md`). A page without one goes where its first moved
  section went: the first of its anchor rows in the heading order of the last release that had the page (or in
  file order, when no release in the checkout has it).
- An old page that is still built, but lost sections, gets a small map instead: when the hash names no element on
  the page and the map has it, the reader goes to the section's new place.

Japanese: the anchors in the file are English heading slugs, and a Japanese page has Japanese ones. A heading is
paired with the one at the same position in the other language, from the newest release (merged into <ref>) whose
two versions of the old page have the same heading levels and contain the anchor, and for the target from the
built pages. Position alone is not trusted: the pair is kept only when the two sections' bodies agree (see
`paired`), so two same-level sections in a different order are not mistaken for each other. An anchor that cannot
be paired falls back to the Japanese page-level target (or to the top of the target page). scripts/check_dist.py
checks every target that is written here.
"""
import html
import json
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path

BASE = "/docs"
SITE = "https://agent-fleet.org"
STUB_MARK = 'id="redirect-map"'
SECTION_MARK = 'id="section-redirects"'
HEADING_ID = re.compile(r'<h([1-6])\b[^>]*\sid="([^"]+)"')
MD_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
# What a section and its translation share: ASCII words (names, commands, code) and numbers.
TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9_.+/-]*[A-Za-z0-9]|\d+")
SHAPE = ("fence", "row", "item", "quote")

STUB_JS = ("(()=>{const m=JSON.parse(document.getElementById('redirect-map').textContent);"
           "let h='';try{h=decodeURIComponent(location.hash.slice(1))}catch(e){}"
           "location.replace(m[h]||m[''])})()")
SECTION_BLOCK = re.compile(r'<script type="application/json" id="section-redirects">.*?</script><script>.*?</script>',
                           re.S)
SECTION_JS = ("(()=>{const m=JSON.parse(document.getElementById('section-redirects').textContent);"
              "const go=()=>{let h='';try{h=decodeURIComponent(location.hash.slice(1))}catch(e){}"
              "if(h&&m[h]&&!document.getElementById(h))location.replace(m[h])};"
              "addEventListener('DOMContentLoaded',go);addEventListener('hashchange',go)})()")


def git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout if r.returncode == 0 else None


# --- URLs ---------------------------------------------------------------------------------------------------------

def slug(page: str) -> str:
    """member/03-x.md -> member/03-x; admin/README.md -> admin; README.md -> ''."""
    s = page[: -len(".md")]
    if s == "README" or s.endswith("/README"):
        s = s[: -len("README")].rstrip("/")
    return s.lower()


def url(lang: str, page: str, anchor: str = "") -> str:
    s = slug(page)
    u = BASE + ("/ja" if lang == "ja" else "") + (f"/{s}/" if s else "/")
    return u + (f"#{anchor}" if anchor else "")


def dist_file(dist: Path, lang: str, page: str) -> Path:
    s = slug(page)
    return dist / ("ja" if lang == "ja" else "") / s / "index.html"


# --- heading slugs (src/console-slug.mjs) --------------------------------------------------------------------------

def console_slug(t: str) -> str:
    t = "".join(c for c in t.lower().strip() if unicodedata.category(c)[0] in "LN" or c in " -")
    return re.sub(r"\s+", "-", t)


def github_slug(t: str) -> str:
    t = "".join(c for c in t.lower().strip()
                if unicodedata.category(c)[0] in "LMN" or unicodedata.category(c) == "Pc" or c in " -")
    return t.replace(" ", "-")


def heading_text(md: str) -> str:
    """The text a rendered heading has: no link targets, images, code ticks or tags."""
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", md)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\\(.)", r"\1", t)
    return html.unescape(t.replace("`", ""))


def evidence(tokens: set, shape: dict, links) -> frozenset:
    """A section's language-neutral content: its ASCII words and numbers, how many code blocks, table rows, list items
    and quotes it has, and where its links and images point (`link`)."""
    return frozenset(tokens | {f"#{k}:{v}" for k, v in shape.items() if v} | {"@" + link(u) for u in links})


def link(u: str) -> str:
    """A link or image destination with the language taken out: `x.ja.md` and `/docs/ja/x/` are `x.md` and `/docs/x/`,
    a screenshot `x-ja-light.webp` is `x-en-light.webp`, and the #fragment (a heading id) is dropped."""
    u = html.unescape(u).split("#", 1)[0]
    u = re.sub(r"\.ja\.md$", ".md", u)
    u = re.sub(r"^/docs/ja/", "/docs/", u)
    return u.replace("-ja-", "-en-")


def nest(heads):
    """A section's evidence includes its sub-sections: a heading followed directly by sub-headings has no body."""
    out = []
    for n, (lv, i, ev) in enumerate(heads):
        k = n + 1
        while k < len(heads) and heads[k][0] > lv:
            ev |= heads[k][2]
            k += 1
        out.append((lv, i, ev))
    return out


def md_headings(text: str):
    """[(level, (Console id, GitHub id), evidence)] of a guide page; the first H1 is the page title and has no id.

    The site and the Console give a guide heading the Console's id, but a row may have been written with GitHub's
    (`a → b` is `a-b` in one and `a--b` in the other), so both are kept and either one matches.
    """
    out, seen, fence, title = [], ({}, {}), False, False
    tokens, shape = None, None
    for line in text.split("\n"):
        st = line.lstrip()
        if st.startswith("```"):
            fence = not fence
            if fence and shape is not None:
                shape["fence"] += 1
            continue
        m = None if fence else MD_HEADING.match(line)
        if m and not (len(m.group(1)) == 1 and not title):
            ids = []
            for rule, used in zip((console_slug, github_slug), seen):
                i = rule(heading_text(m.group(2)))
                k = used.get(i, 0)
                used[i] = k + 1
                ids.append(f"{i}-{k}" if k else i)
            tokens, shape, links = set(), dict.fromkeys(SHAPE, 0), []
            out.append((len(m.group(1)), tuple(ids), tokens, shape, links))
        elif m:
            title = True
            continue
        if tokens is None:
            continue
        if not fence:
            if st.startswith("|"):
                shape["row"] += 1
            elif re.match(r"([-*+]|\d+\.)\s", st):
                shape["item"] += 1
            elif st.startswith(">"):
                shape["quote"] += 1
            links += re.findall(r"\]\(([^)\s]+)", line)
        line = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", line)  # link targets differ by language
        tokens |= {t.lower() for t in TOKEN.findall(line)}
    return nest([(lv, ids, evidence(t, sh, ln)) for lv, ids, t, sh, ln in out])


def html_headings(doc: str):
    """[(level, id, evidence)] of the headings in a built page's content."""
    start = doc.find('class="sl-markdown-content"')
    if start < 0:
        return []
    end = doc.find("<footer", start)
    body = doc[start:end if end > 0 else len(doc)]
    body = re.sub(r'<a class="sl-anchor-link".*?</a>|<svg.*?</svg>', "", body, flags=re.S)
    parts = re.split(r'<h([2-6])\b[^>]*\sid="([^"]+)"[^>]*>', body)
    out = []
    for n in range(1, len(parts) - 2, 3):
        chunk = parts[n + 2]
        shape = {"fence": chunk.count("<pre"), "row": len(re.findall(r"<tr\b", chunk)),
                 "item": len(re.findall(r"<li\b", chunk)), "quote": len(re.findall(r"<aside\b|<blockquote\b", chunk))}
        links = re.findall(r'<(?:a\b[^>]*\shref|img\b[^>]*\ssrc)="([^"]+)"', chunk)
        text = html.unescape(re.sub(r"<[^>]+>", " ", chunk))
        out.append((int(parts[n]), parts[n + 1], evidence({t.lower() for t in TOKEN.findall(text)}, shape, links)))
    return nest(out)


# The least shared weight that tells a section apart from its siblings: one token that at most one other section
# of the level also has (a token weighs 1 / the number of same-level sections that have it).
DISTINCT = 0.5


def paired(en, ja, n) -> bool:
    """Whether heading n of `en` and heading n of `ja` are the same section.

    The two versions must have the same heading levels, and section n must fit its counterpart strictly better than
    it would swapped with any other section of the same level: a pair of same-level sections in a different order
    fits better swapped, and a tie (sections with the same content) is not trusted. Content counts only where the
    other language could have it (English words that appear nowhere on the Japanese page are prose), and the more
    same-level sections share a token, the less it weighs: boilerplate tells sections apart no better than nothing.
    The two sections must also share at least DISTINCT of weight that not every section of the level has."""
    if not en or [h[0] for h in en] != [h[0] for h in ja]:
        return False
    same = [m for m in range(len(en)) if en[m][0] == en[n][0]]
    shared = frozenset().union(*(h[2] for h in ja))
    e = {m: en[m][2] & shared for m in same}
    j = {m: ja[m][2] for m in same}
    spread = Counter(t for m in same for t in e[m] | j[m])

    def sim(a, b):
        union = sum(1 / spread[t] for t in a | b)
        return sum(1 / spread[t] for t in a & b) / union if union else 0.0

    here = sim(e[n], j[n])
    distinct = sum(1 / spread[t] for t in e[n] & j[n] if spread[t] < len(same))
    if here == 0 or (len(same) > 1 and distinct < DISTINCT):
        return False
    return all(here + sim(e[m], j[m]) > sim(e[n], j[m]) + sim(e[m], j[n]) for m in same if m != n)


# --- the old pages, from the checkout's history ---------------------------------------------------------------------

class History:
    """English and Japanese headings of a guide page in the releases merged into <ref>, newest first."""

    def __init__(self, repo, ref):
        self.repo = repo
        tags = git(repo, "tag", "--list", "v*", "--merged", ref, "--sort=-v:refname", check=False) or ""
        self.tags = tags.split()
        self.trees = {}
        self.partial = (git(repo, "config", "--get", "remote.origin.promisor", check=False) or "").strip() == "true"

    def blobs(self, tag):
        if tag not in self.trees:
            out = git(self.repo, "ls-tree", "-r", tag, "--", "guide", check=False) or ""
            self.trees[tag] = {l.split("\t", 1)[1]: l.split()[2] for l in out.splitlines()}
        return self.trees[tag]

    def versions(self, page):
        """[(tag, en blob, ja blob)] for every release that has both languages of the page."""
        ja = page[: -len(".md")] + ".ja.md"
        out = []
        for t in self.tags:
            b = self.blobs(t)
            if "guide/" + page in b and "guide/" + ja in b:
                out.append((t, b["guide/" + page], b["guide/" + ja]))
        return out

    def prefetch(self, oids):
        """A blobless clone fetches each missing blob on its own; ask for all of them at once instead."""
        if not self.partial or not oids:
            return
        subprocess.run(["git", "-C", str(self.repo), "-c", "fetch.negotiationAlgorithm=noop", "fetch", "-q",
                        "--no-tags", "--no-write-fetch-head", "--filter=blob:none", "origin", *sorted(oids)],
                       capture_output=True)

    def texts(self, oids):
        """{oid: text}, read in one `git cat-file --batch`."""
        oids = sorted(oids)
        r = subprocess.run(["git", "-C", str(self.repo), "cat-file", "--batch"], input=("\n".join(oids) + "\n").encode(),
                           capture_output=True, check=True)
        out, pos = {}, 0
        for o in oids:
            end = r.stdout.index(b"\n", pos)
            head = r.stdout[pos:end].split()
            pos = end + 1
            if len(head) == 3:
                n = int(head[2])
                out[o] = r.stdout[pos:pos + n].decode("utf-8", "replace")
                pos += n + 1
        return out


def old_headings(hist, pages):
    """{page: [(tag, en headings, ja headings)]} for the old pages, newest release first."""
    vers = {p: hist.versions(p) for p in pages}
    oids = {o for v in vers.values() for _, e, j in v for o in (e, j)}
    hist.prefetch(oids)
    text = hist.texts(oids)
    return {p: [(t, md_headings(text.get(e, "")), md_headings(text.get(j, ""))) for t, e, j in v]
            for p, v in vers.items()}


# --- main -----------------------------------------------------------------------------------------------------------

def main():
    repo, ref, dist = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    tsv = git(repo, "show", f"{ref}:guide/_redirects.tsv", check=False)
    if tsv is None:
        print("redirect_stubs: no guide/_redirects.tsv at this ref; nothing to do")
        return
    rows = []
    for line in tsv.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        old, _, new = line.partition("\t")
        op, _, oa = old.strip().partition("#")
        np_, _, na = new.strip().partition("#")
        rows.append((op, oa, np_, na))

    docs = {}

    def doc(lang, page):
        """The HTML of a built page, or None (a stub from an earlier run does not count as built)."""
        k = (lang, page)
        if k not in docs:
            f = dist_file(dist, lang, page)
            d = f.read_text(encoding="utf-8") if f.is_file() else None
            docs[k] = None if d is None or STUB_MARK in d else d
        return docs[k]

    old_pages = list(dict.fromkeys(r[0] for r in rows))
    hist = History(repo, ref)
    olds = old_headings(hist, [p for p in old_pages if any(r[0] == p and r[1] for r in rows)])

    def old_ids(page, anchor):
        """The ids the old page's section had: ({English ids}, {Japanese ids}). The Japanese ones come from the
        newest release where the two versions' sections pair (`paired`)."""
        en_ids = {anchor}
        for _, en, ja in olds.get(page, []):
            n = next((n for n, h in enumerate(en) if anchor in h[1]), None)
            if n is None:
                continue
            en_ids |= set(en[n][1])
            if paired(en, ja, n):
                return en_ids, set(ja[n][1])
        return en_ids, set()

    dropped = set()

    def target(lang, page, anchor):
        """The URL a row sends a reader of `lang` to. A Japanese reader goes to the Japanese page when there is one."""
        if lang == "en" or doc("ja", page) is None:
            return url("en", page, anchor)
        if not anchor:
            return url("ja", page)
        en, ja = doc("en", page), doc("ja", page)
        if f'id="{anchor}"' in ja:
            return url("ja", page, anchor)
        he, hj = html_headings(en or ""), html_headings(ja)
        n = next((n for n, h in enumerate(he) if h[1] == anchor), None)
        j = hj[n][1] if n is not None and paired(he, hj, n) else None
        if j is None:
            dropped.add(f"{page}#{anchor}")
        return url("ja", page, j or "")

    stats = dict.fromkeys(("stubs", "stub_rows", "ja_paired", "ja_unpaired", "kept_rows", "section_rows",
                           "section_pages"), 0)
    for page in old_pages:
        prow = [r for r in rows if r[0] == page and not r[1]]
        arows = [r for r in rows if r[0] == page and r[1]]
        ids = {r[1]: old_ids(page, r[1]) for r in arows}
        if prow:
            first = prow[0]
        else:
            heads = next((en for _, en, _ in olds.get(page, []) if en), [])
            order = {i: n for n, h in enumerate(heads) for i in h[1]}
            first = min(arows, key=lambda r: (order.get(r[1], len(heads)), arows.index(r)))
        for lang in ("en", "ja"):
            built = doc(lang, page)
            keys = {oa: ids[oa][0] | (ids[oa][1] if lang == "ja" else set()) for _, oa, _, _ in arows}
            if built is not None:
                # The page is still here: only the sections that are gone from it are redirected.
                m = {}
                for _, oa, np_, na in arows:
                    if any(f'id="{k}"' in built for k in keys[oa]):
                        continue
                    for k in keys[oa]:
                        m[k] = target(lang, np_, na)
                    stats["section_rows"] += 1
                stats["kept_rows"] += len(arows) if lang == "en" else 0
                if m:
                    blob = json.dumps(m, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
                    tag = f'<script type="application/json" {SECTION_MARK}>{blob}</script><script>{SECTION_JS}</script>'
                    built = re.sub(SECTION_BLOCK, "", built)
                    dist_file(dist, lang, page).write_text(built.replace("</head>", tag + "</head>", 1),
                                                           encoding="utf-8")
                    stats["section_pages"] += 1
                continue
            top = target(lang, first[2], first[3])
            m = {"": top}
            for _, oa, np_, na in arows:
                for k in keys[oa]:
                    m[k] = target(lang, np_, na)
                if lang == "ja":
                    stats["ja_paired" if ids[oa][1] else "ja_unpaired"] += 1
            write_stub(dist_file(dist, lang, page), lang, top, m)
            stats["stubs"] += 1
            stats["stub_rows"] += len(arows)
    print(f"redirect_stubs: {len(rows)} rows. {stats['stubs']} stubs (en + ja) carrying {stats['stub_rows']} "
          f"section rows; Japanese old anchors paired for {stats['ja_paired']} of them, not for "
          f"{stats['ja_unpaired']}. {stats['kept_rows']} rows are sections of pages this build still has; "
          f"{stats['section_rows']} (en + ja) are gone from their page and redirected by a map on "
          f"{stats['section_pages']} pages. Japanese target anchors not paired: {len(dropped)}"
          + "".join(f"\n  {d}" for d in sorted(dropped)))


def write_stub(path: Path, lang: str, top: str, m: dict):
    if path.exists() and STUB_MARK not in path.read_text(encoding="utf-8"):
        raise SystemExit(f"redirect_stubs: refusing to overwrite the built page {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(m, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    t = html.escape(top)
    ja = lang == "ja"
    path.write_text(
        f'<!doctype html>\n<html lang="{lang}">\n<head>\n<meta charset="utf-8">\n'
        f"<title>{'移動しました' if ja else 'Moved'}</title>\n"
        '<meta name="robots" content="noindex">\n'
        f'<link rel="canonical" href="{SITE}{t}">\n'
        f'<script type="application/json" {STUB_MARK}>{blob}</script>\n'
        f"<script>{STUB_JS}</script>\n"
        f'<meta http-equiv="refresh" content="0; url={t}">\n'
        "</head>\n<body>\n"
        f"<p>{'このページは移動しました:' if ja else 'This page has moved:'} <a href=\"{t}\">{t}</a></p>\n"
        "</body>\n</html>\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
