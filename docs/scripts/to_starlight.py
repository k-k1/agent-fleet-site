#!/usr/bin/env python3
"""Turn the staged guide (deploy/release/stage-docs.sh output) into Starlight content.

    to_starlight.py <staged-dir> <site-dir> <git-ref>

The guide stays GitHub-shaped in the repository (x.md + x.ja.md, an H1 per page, a
language-switch line, relative .md links); everything Starlight needs is derived here so
the source never has to know a website exists.

It also writes the text for agents into <site-dir>/agent-text/, which build.sh copies into dist/ after the build:
each page's Markdown next to its HTML (/docs/<path>/index.md, links as absolute site URLs, GitHub alerts and code
blocks as in the guide) and /docs/llms.txt, the list of every page with its .md URL (llms_txt below).
"""
import html
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = "/docs"
SITE = "https://agent-fleet.org"
REPO = "https://github.com/k-k1/agent-fleet"
REVERSE = {}

# Where each staged file lives in the repository, for "edit on GitHub" and for relative
# links that point outside the staged tree (runbooks link to their own scripts).
RUNBOOK_SRC = {
    "compose": "deploy/compose/README.md",
    "native": "deploy/native/README.md",
    "wsl": "deploy/local/README-wsl.md",
    "aws-ecs": "deploy/aws/ecs/README.md",
    "aws-ec2-single": "deploy/aws/ec2-single/README.md",
    "kubernetes": "deploy/kubernetes/README.md",
}

LANG_LINE = re.compile(r"^(English \| \[日本語\]\([^)]*\)|\[English\]\([^)]*\) \| 日本語)\s*$")
H1 = re.compile(r"^# (.+?)\s*$")
FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)
LINK = re.compile(r"(!?\[(?:[^\]\\]|\\.)*\])\(([^)\s]+)((?:\s+\"[^\"]*\")?)\)")
NUM = re.compile(r"^(\d+)-")
ALERT = re.compile(r"^> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\n((?:>.*\n?)+)", re.M)
ASIDE = {"NOTE": "note", "TIP": "tip", "IMPORTANT": "note", "WARNING": "caution", "CAUTION": "danger"}


def alert_to_aside(m):
    body = re.sub(r"^> ?", "", m.group(2), flags=re.M).rstrip("\n")
    return f":::{ASIDE[m.group(1)]}\n{body}\n:::\n"



def repo_path(rel: Path) -> str:
    parts = rel.parts
    if parts[:2] == ("operate", "runbooks") and rel.stem in RUNBOOK_SRC:
        return RUNBOOK_SRC[rel.stem]
    if parts[:2] == ("ref", "releases"):
        return "deploy/release/notes/" + "/".join(parts[2:])
    return "guide/" + rel.as_posix()


class LandingError(ValueError):
    """The guide's README no longer has the shape the landing page is built from: the build stops and says where."""


# The cards of the landing page, by the directory their link points into, in this order. Their titles are the topic
# labels (src/topic-labels.json, which astro.config.mjs reads too); "member" is the old shelf of the "user" topic.
LANDING_SHELVES = {"user": "user", "member": "user", "admin": "admin", "operate": "operate"}
LANDING_LINK = re.compile(r"\[((?:[^\]\\]|\\.)*)\]\((/docs/[^)\s]*)\)")


WIDE = r"[^\x00-\x7f]"


def _plain(md: str) -> str:
    """Markdown inline text without its links and emphasis.

    A space that only set a link apart from Japanese text next to it goes with the link: 「[更新履歴](…) は」 becomes
    「更新履歴は」, while 「Console でエージェント」 (no link) keeps its space.
    """
    open_, close = "\x02", "\x03"  # where each link's text starts and ends
    t = re.sub(r"\*\*|`", "", LANDING_LINK.sub(lambda m: open_ + m.group(1) + close, md))
    t = re.sub(f"(?<={WIDE}) {open_}(?={WIDE})", open_, t)
    t = re.sub(f"(?<={WIDE}){close} (?={WIDE})", close, t)
    return t.replace(open_, "").replace(close, "").strip()


# A shelf paragraph opens with its own name as the subject: 「**[リファレンス](…)** は」, "**The [Reference](…)** is".
SUBJECT = {"ja": re.compile(r"\A\*\*[^*]*\]\([^)]*\)[^*]*\*\* ?は"),
           "en": re.compile(r"\A\*\*[^*]*\]\([^)]*\)[^*]*\*\* [a-z]+ ")}


# The two sentences that become the hero's buttons keep only their link: the rest of the sentence has to be exactly
# one of these, or the build fails, so no wording added around the link is lost. {link} is the link, any text and
# target. 「端末を」 is the wording of releases up to v0.44.0.
BUTTON_SENTENCES = {
    "first-time": {"ja": ["はじめて使うなら {link} から読み始めてください。"],
                   "en": ["If you are new, start with {link}."]},
    "no-terminal": {"ja": ["ターミナルを一度も開かずに使いたい方は、{link} が近道です。",
                           "端末を一度も開かずに使いたい方は、{link} が近道です。"],
                    "en": ["If you would rather never open a terminal, {link} is the short way round."]},
}


def _is_button_sentence(kind: str, lang: str, sentence: str) -> bool:
    return any(re.fullmatch(re.escape(t).replace(re.escape("{link}"), LANDING_LINK.pattern), sentence.strip())
               for t in BUTTON_SENTENCES[kind][lang])


def _predicate(md: str, lang: str):
    """The paragraph without its opening subject, so a card does not repeat its own title; None if it has none."""
    m = SUBJECT[lang].match(md)
    if not m:
        return None
    rest = md[m.end():].lstrip()
    return rest[:1].upper() + rest[1:]


def _sentences(text: str, lang: str):
    return [x for x in re.split(r"(?<=。)" if lang == "ja" else r"(?<=\.)\s+", text) if x.strip()]


def _attr(s: str) -> str:
    return "{" + json.dumps(s, ensure_ascii=False) + "}"


def landing(lang: str, title: str, body: str, labels: dict) -> str:
    """The root page as a Starlight splash page, built from the guide's README (already link-converted).

    The README stays plain Markdown for the containers and GitHub; this reads its parts and fails on anything it
    does not recognise, rather than dropping it: a lead paragraph that links the first-time page, a three-column
    table with one row per reader and a link to their shelf, then one paragraph each for the reference, the release
    history, the no-terminal entry, and the closing note on the Console.

    Nothing is dropped silently. The sentence pointing at the first-time page and the no-terminal sentence become
    the hero's buttons (each must be one sentence with one link), the table's shelf link becomes a card titled with
    the topic label, a shelf paragraph loses only its subject (its own name, which is the card's title), and every
    other sentence is a card's description or text below the cards. Anything that does not fit fails the build.
    """
    sep = " " if lang == "en" else ""
    blocks = [b.strip("\n") for b in re.split(r"\n\s*\n", body.strip()) if b.strip()]

    def fail(why):
        raise LandingError(f"guide/README{'.ja' if lang == 'ja' else ''}.md: {why}; update landing() in "
                           "scripts/to_starlight.py to the README's new shape")

    def one_link(block, what):
        links = LANDING_LINK.findall(block)
        if not links:
            fail(f"the {what} has no link into the guide")
        return links

    def url_lang(url):
        return url[len(BASE) + 4:] if lang == "ja" and url.startswith(BASE + "/ja/") else url[len(BASE) + 1:]

    if len(blocks) < 2:
        fail("expected a lead paragraph and a table")
    lead, table, rest = blocks[0], blocks[1], blocks[2:]
    if lead.startswith("|") or not table.startswith("|"):
        fail("expected the lead paragraph, then the readers' table")
    first = one_link(lead, "lead paragraph")[0]
    if not url_lang(first[1]).startswith("user/start/"):
        fail(f"the lead paragraph's link {first[1]} is not a first-time page under user/start/")
    if len(LANDING_LINK.findall(lead)) != 1:
        fail("the lead paragraph has more than one link; only the first-time page can become its button")
    rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in table.splitlines()]
    if len(rows) < 3 or any(len(r) != 3 for r in rows) or not all(re.fullmatch(r":?-+:?", c) for c in rows[1]):
        fail("the readers' table is not a header, a separator and rows of three columns")
    cards = []
    for reader, read, answers in rows[2:]:
        links = LANDING_LINK.findall(read)
        if len(links) != 1 or LANDING_LINK.sub("", read).strip():
            fail(f"the table row for {reader!r} does not link one shelf and nothing else")
        if LANDING_LINK.search(reader) or LANDING_LINK.search(answers):
            fail(f"the table row for {reader!r} has a link outside its shelf column; a card cannot carry it")
        shelf = url_lang(links[0][1]).split("/", 1)[0]
        if shelf not in LANDING_SHELVES:
            fail(f"the table row for {reader!r} links {links[0][1]}, which is not a known shelf")
        sep_r = "：" if lang == "ja" else ": "
        cards.append((LANDING_SHELVES[shelf], links[0][1], f"{_plain(reader)}{sep_r}{_plain(answers)}"))
    if [c[0] for c in cards] != ["user", "admin", "operate"]:
        fail(f"the readers' table links {[c[0] for c in cards]}, not user, admin and operate in that order")

    ref = releases = no_term = None
    notes = []
    for b in rest:
        if b.startswith("|") or b.startswith("#") or b.startswith(":::") or b.startswith("<"):
            fail(f"unexpected block after the table: {b.splitlines()[0]!r}")
        links = LANDING_LINK.findall(b)
        targets = [url_lang(u) for _, u in links]
        if targets and targets[0] == "ref/" and ref is None:
            ref = b
        elif targets and targets[0].startswith("ref/releases/") and releases is None:
            releases = b
        elif targets and targets[0].startswith("user/start/") and no_term is None:
            # The whole paragraph becomes a button: one sentence, one link, nothing else to lose.
            sentence = sep.join(l.strip() for l in b.splitlines())
            if not _is_button_sentence("no-terminal", lang, sentence):
                fail(f"the no-terminal sentence {sentence!r} is not one of BUTTON_SENTENCES['no-terminal']")
            no_term = links[0]
        elif not links and not notes:
            notes.append(b)
        else:
            fail(f"unexpected paragraph after the table: {b.splitlines()[0]!r}")
    if not (ref and releases and no_term and notes):
        fail("expected one paragraph each for the reference, the release history, the no-terminal entry and the "
             "Console")

    # The reference's own sentences describe its card; one that links elsewhere (the glossary) stays as text.
    ref_text = sep.join(l.strip() for l in ref.splitlines())
    own, other = [], []
    for x in _sentences(ref_text, lang):
        (other if [u for _, u in LANDING_LINK.findall(x) if url_lang(u) != "ref/"] else own).append(x)
    ref_desc = _predicate(sep.join(own), lang) if own else None
    if not ref_desc:
        fail("the reference paragraph does not open with its own name as the subject")
    ref_url = LANDING_LINK.findall(ref)[0][1]
    cards.append(("ref", ref_url, _plain(ref_desc)))
    rel_text = sep.join(l.strip() for l in releases.splitlines())
    rel_desc = _predicate(rel_text, lang)
    if not rel_desc:
        fail("the release-history paragraph does not open with its own name as the subject")
    if len(LANDING_LINK.findall(releases)) != 1:
        fail("the release-history paragraph has more than one link; its card can carry only its own")
    rel_url = LANDING_LINK.findall(releases)[0][1]

    # The tagline leaves out the sentence that points at the first-time page: the primary button says it.
    lead_sents = _sentences(sep.join(l.strip() for l in lead.splitlines()), lang)
    lead_rest = [x for x in lead_sents if first[1] not in x]
    pointer = [x for x in lead_sents if first[1] in x]
    if len(pointer) != 1 or not _is_button_sentence("first-time", lang, pointer[0]):
        fail(f"the first-time sentence {pointer!r} is not one of BUTTON_SENTENCES['first-time']")
    # 「それ以外は、」/ "Otherwise," answers the pointer, which the tagline leaves to the button.
    otherwise = {"ja": "それ以外は、", "en": "Otherwise, "}[lang]
    if not lead_rest[0].startswith(otherwise):
        fail(f"the lead's sentence after the first-time pointer does not start with {otherwise.strip()!r}")
    rest0 = lead_rest[0][len(otherwise):]
    lead_rest = [rest0[:1].upper() + rest0[1:], *lead_rest[1:]]
    if not lead_rest:
        fail("the lead paragraph has nothing besides the pointer to the first-time page")

    tail = [sep.join(other).strip()] if other else []
    tail += [sep.join(l.strip() for l in n.splitlines()) for n in notes]
    for t in tail:
        if re.search(r"[{}<>]", t):
            fail(f"the text {t!r} has characters MDX would read as code")

    def card(topic, href, desc):
        return f"  <LinkCard title={_attr(labels[topic][lang])} href={_attr(href)} description={_attr(desc)} />"

    fm = [
        f"title: {yaml_str(title)}",
        "template: splash",
        "hero:",
        f"  tagline: {yaml_str(html.escape(_plain(sep.join(lead_rest))))}",
        "  actions:",
        f"    - text: {yaml_str(_plain(first[0]))}",
        f"      link: {yaml_str(first[1])}",
        "      icon: right-arrow",
        f"    - text: {yaml_str(_plain(no_term[0]))}",
        f"      link: {yaml_str(no_term[1])}",
        "      icon: right-arrow",
        "      variant: minimal",
    ]
    out = [
        "import { CardGrid, LinkCard } from '@astrojs/starlight/components';",
        "",
        "<CardGrid>",
        *[card(*c) for c in cards],
        "</CardGrid>",
        "",
        card("releases", rel_url, _plain(rel_desc)).strip(),
        "",
        *[t + "\n" for t in tail],
    ]
    return "---\n" + "\n".join(fm) + "\n---\n\n" + "\n".join(out)


class ImageSizeError(ValueError):
    """An image whose size cannot be read: the build stops and names the file."""


# CSS absolute units in px (CSS Values 4: 1in = 96px).
SVG_UNITS = {"": 1.0, "px": 1.0, "in": 96.0, "cm": 96 / 2.54, "mm": 96 / 25.4, "pt": 96 / 72, "pc": 16.0}


def image_size(path: Path):
    """Intrinsic (width, height) in px of a WebP, PNG or SVG; None for any other kind of file.

    A file of one of those kinds whose size cannot be read raises ImageSizeError: a truncated or malformed header
    would otherwise come out as a 1x1 or 0x0 box.
    """
    suffix = path.suffix.lower()
    if suffix == ".svg":
        return svg_size(path)
    if suffix == ".png":
        return png_size(path)
    if suffix == ".webp":
        return webp_size(path)
    return None


def _positive(path: Path, what: str, w, h):
    if w <= 0 or h <= 0:
        raise ImageSizeError(f"{path}: {what} gives a size of {w}x{h}")
    return w, h


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
# Minimum payload of each WebP first chunk that carries the canvas size.
WEBP_MIN_CHUNK = {b"VP8X": 10, b"VP8 ": 10, b"VP8L": 5}


def png_size(path: Path):
    """IHDR's size. The first 33 bytes must be whole: the signature, IHDR's length (13) and type, its 13 bytes, its CRC."""
    b = path.read_bytes()[:33]
    if len(b) < 33 or b[:8] != PNG_SIGNATURE or b[8:12] != (13).to_bytes(4, "big") or b[12:16] != b"IHDR":
        raise ImageSizeError(f"{path}: not a PNG with a complete IHDR chunk (truncated or malformed header)")
    return _positive(path, "IHDR", int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big"))


def webp_size(path: Path):
    """The canvas size from the first chunk, after checking the RIFF size and that chunk's declared length."""
    data = path.read_bytes()
    b = data[:30]
    if len(b) < 20 or b[:4] != b"RIFF" or b[8:12] != b"WEBP":
        raise ImageSizeError(f"{path}: not a RIFF WEBP file (truncated or malformed header)")
    riff_size = int.from_bytes(b[4:8], "little")
    if riff_size + 8 > len(data):
        raise ImageSizeError(f"{path}: RIFF size {riff_size} runs past the end of the file ({len(data)} bytes)")
    kind, length = b[12:16], int.from_bytes(b[16:20], "little")
    if kind not in WEBP_MIN_CHUNK:
        raise ImageSizeError(f"{path}: unknown WebP chunk {kind!r}")
    if length < WEBP_MIN_CHUNK[kind] or 20 + length > riff_size + 8:
        raise ImageSizeError(f"{path}: {kind.decode().strip()} chunk length {length} is below its minimum "
                             f"({WEBP_MIN_CHUNK[kind]}) or runs past the RIFF size {riff_size}")
    if kind == b"VP8X":
        return 1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little")
    if kind == b"VP8 ":
        # Frame tag (3 bytes), start code 9d 01 2a, then 14-bit width and height.
        if b[23:26] != b"\x9d\x01\x2a":
            raise ImageSizeError(f"{path}: VP8 frame header without its start code")
        w, h = int.from_bytes(b[26:28], "little") & 0x3FFF, int.from_bytes(b[28:30], "little") & 0x3FFF
        return _positive(path, "the VP8 frame header", w, h)
    if b[20] != 0x2F:
        raise ImageSizeError(f"{path}: VP8L header without its signature byte")
    v = int.from_bytes(b[21:25], "little")
    return 1 + (v & 0x3FFF), 1 + ((v >> 14) & 0x3FFF)


def svg_size(path: Path):
    """Size of the root <svg> in px.

    width and height in an absolute unit are converted to px. A missing or percentage dimension is derived from the
    viewBox (its aspect ratio when the other dimension is known, its size when neither is). Relative units (em, ex,
    ...) cannot be resolved at build time and raise ImageSizeError, as does an SVG with nothing to size it by.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    # No entity declarations and no internal DTD subset (the defusedxml rules); expat never fetches an external DTD,
    # so a plain <!DOCTYPE svg PUBLIC ...> line is allowed.
    if re.search(r"<!ENTITY", text) or re.search(r"<!DOCTYPE[^>\[]*\[", text):
        raise ImageSizeError(f"{path}: SVG declares entities or an internal DTD subset; refusing to parse it")
    try:
        # The real root element: comments, CDATA, the prolog and processing instructions are not elements.
        root = ET.fromstring(path.read_bytes())
    except ET.ParseError as e:
        raise ImageSizeError(f"{path}: not well-formed XML ({e})") from None
    if root.tag.rpartition("}")[2] != "svg":
        raise ImageSizeError(f"{path}: the root element is <{root.tag}>, not <svg>")

    def attr(name):
        v = root.get(name)
        return v.strip() if v is not None else None

    def length(name):
        """px for an absolute length, None for a missing or percentage one."""
        v = attr(name)
        if v is None or v == "" or v.endswith("%"):
            return None
        n = re.fullmatch(r"([0-9]*\.?[0-9]+(?:[eE][+-]?[0-9]+)?)\s*([a-zA-Z]*)", v)
        if not n or n.group(2).lower() not in SVG_UNITS:
            raise ImageSizeError(f"{path}: <svg {name}=\"{v}\"> is not a length that can be resolved at build time")
        return float(n.group(1)) * SVG_UNITS[n.group(2).lower()]

    w, h = length("width"), length("height")
    if w is None or h is None:
        box = (attr("viewBox") or "").replace(",", " ").split()
        try:
            bw, bh = (float(box[2]), float(box[3])) if len(box) == 4 else (0.0, 0.0)
        except ValueError:
            bw = bh = 0.0
        if bw <= 0 or bh <= 0:
            raise ImageSizeError(f"{path}: <svg> has no absolute width and height and no usable viewBox")
        if w is None and h is None:
            w, h = bw, bh
        elif h is None:
            h = w * bh / bw
        else:
            w = h * bw / bh
    # A box smaller than a pixel still gets one, rather than collapsing to 0.
    return _positive(path, "<svg>", max(1, round(w)), max(1, round(h)))


def split_lang(rel: Path):
    """member/01-x.ja.md -> ('ja', member/01-x)."""
    name = rel.name
    if name.endswith(".ja.md"):
        return "ja", rel.with_name(name[: -len(".ja.md")])
    return "en", rel.with_name(name[: -len(".md")])


def slug_of(stem: Path) -> str:
    s = stem.as_posix()
    if stem.name == "README":
        s = stem.parent.as_posix()
        s = "" if s == "." else s
    return s.lower()


def url_of(lang: str, stem: Path) -> str:
    s = slug_of(stem)
    prefix = BASE + ("/ja" if lang == "ja" else "")
    return f"{prefix}/{s}/" if s else f"{prefix}/"


def yaml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)  # JSON strings are valid YAML scalars


PAGE_ORDER: dict = {}


def agent_url(url: str) -> str:
    """/docs/ja/user/x/ -> https://agent-fleet.org/docs/ja/user/x/index.md, the page's Markdown for agents."""
    return f"{SITE}{url}index.md"


# The sections of llms.txt, in this order: the topics of the site (astro.config.mjs), by the page's directory.
LLMS_TOPICS = ["user", "admin", "operate", "ref", "releases"]


def topic_of(stem: Path) -> str:
    parts = slug_of(stem).split("/")
    if parts[:2] == ["ref", "releases"]:
        return "releases"
    return parts[0] if parts[0] in LLMS_TOPICS else "user"  # the home page and the old member/ shelf


def _release_key(stem: str):
    v = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", stem.rsplit("/", 1)[-1])
    return tuple(-int(x) for x in v.groups()) if v else (1,)  # newest first, SUMMARY and others after


def llms_txt(pages, labels) -> str:
    """/docs/llms.txt (llmstxt.org): every page with its title, its audience and its index.md URL.

    One file for both languages: a section per topic in English, then the same sections in Japanese. Within a topic
    the home page comes first, then the pages in the reading order of research/page-titles.tsv, then the rest by path
    (release notes newest first).
    """
    out = [
        "# Agent Fleet",
        "",
        "> The user guide of Agent Fleet, which runs coding agents such as Claude Code and Codex from the Console in "
        "your browser, each user in their own workspace. Agent Fleet の利用ガイド（日本語のページは後半の「(日本語)」の節）。",
        "",
        "Every page of https://agent-fleet.org/docs/ is published as Markdown next to its HTML: add `index.md` to the "
        "page's URL. The links below point at those files; the links inside them are absolute URLs too. Each entry "
        "says who the page is for. The pages exist in English and in Japanese (/docs/ja/); the Japanese sections "
        "follow the English ones.",
    ]
    for lang in ("en", "ja"):
        for topic in LLMS_TOPICS:
            items = [p for p in pages if p["lang"] == lang and p["topic"] == topic]
            if not items:
                continue
            items.sort(key=lambda p: (p["order"] >= 0, p["order"] or 10**9,
                                      _release_key(p["stem"]) if topic == "releases" else (), p["url"]))
            head = labels[topic][lang] + (" (日本語)" if lang == "ja" else "")
            out += ["", f"## {head}", ""]
            for p in items:
                desc = f": {p['description']}" if p["description"] else ""
                out.append(f"- [{p['title']}]({agent_url(p['url'])}){desc}")
    return "\n".join(out) + "\n"


def write_subgroups(rows, out: Path, site: Path):
    """Write src/sidebar-subgroups.json for the groups whose pages carry a sub-heading in page-titles.tsv.

    A group named there is listed page by page instead of autogenerated: {"user/integrations": [{"en": …, "ja": …,
    "items": [slug, …]}, …]}. Only pages this build has in English are listed (an explicit sidebar entry has to
    exist in the default locale); a group without sub-headings keeps autogenerate (astro.config.mjs).
    """
    groups: dict = {}
    for r in rows:
        if len(r) < 4 or not r[3].strip():
            continue
        page = r[0]
        if not (out / f"{page}.md").exists():
            continue
        ja, _, en = r[3].partition("|")
        subs = groups.setdefault(page.rsplit("/", 1)[0], [])
        if not subs or subs[-1]["ja"] != ja:
            subs.append({"ja": ja, "en": en or ja, "items": []})
        subs[-1]["items"].append(page)
    (site / "src/sidebar-subgroups.json").write_text(json.dumps(groups, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    staged, site, ref = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    out = site / "src/content/docs"
    pub = site / "public"
    agent_out = site / "agent-text"
    listing = []
    for d in (out, pub / "assets", agent_out):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    for a in (staged / "assets").iterdir():
        shutil.copy2(a, pub / "assets" / a.name)

    unresolved = []
    global PAGE_ORDER
    titles = site / "research/page-titles.tsv"
    rows = []
    if titles.exists():
        rows = [l.split("\t") for l in titles.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
        PAGE_ORDER = {r[0]: n + 1 for n, r in enumerate(rows)}
    global REVERSE
    REVERSE = {repo_path(p.relative_to(staged)): p.relative_to(staged) for p in staged.rglob("*.md")}
    for src in sorted(staged.rglob("*.md")):
        rel = src.relative_to(staged)
        lang, stem = split_lang(rel)
        text = src.read_text(encoding="utf-8")

        meta = {}
        m = FRONT.match(text)
        if m:
            for line in m.group(1).splitlines():
                k, _, v = line.partition(":")
                meta[k.strip()] = v.strip().strip('"')
            text = text[m.end():]

        lines = text.split("\n")
        title = None
        body = []
        in_fence = False
        for line in lines:
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
            if not in_fence:
                if LANG_LINE.match(line):
                    continue
                if title is None:
                    h = H1.match(line)
                    if h:
                        title = h.group(1)
                        continue
            body.append(line)
        if title is None:  # release notes have no H1
            title = ("v" + stem.name) if stem.parent.name == "releases" else stem.name

        def fix(mt, agent=False):
            """One link, for the Starlight page; agent=True: for the Markdown agents read, where every link is an
            absolute site URL (a page's index.md, an asset's file) and an image stays a Markdown image."""
            label, target, ttl = mt.groups()
            if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                return mt.group(0)
            path, _, frag = target.partition("#")
            frag = "#" + frag if frag else ""
            tgt = (rel.parent / path)
            # normalise ../ without touching the filesystem
            parts = []
            for p in tgt.parts:
                if p == "..":
                    if parts:
                        parts.pop()
                    else:
                        parts.append(p)
                elif p != ".":
                    parts.append(p)
            tgt = Path(*parts) if parts else Path(".")
            if path.endswith(".md") and (staged / tgt).is_file():
                tl, ts = split_lang(tgt)
                return f"{label}({agent_url(url_of(tl, ts)) if agent else url_of(tl, ts)}{frag}{ttl})"
            if tgt.parts and tgt.parts[0] == "assets" and (staged / tgt).is_file():
                if agent:
                    return f"{label}({SITE}{BASE}/{tgt.as_posix()}{ttl})"
                size = image_size(staged / tgt) if label.startswith("!") else None
                if size:
                    w, h = size
                    if tgt.suffix.lower() == ".webp":
                        # Screenshots (the WebPs) are taken at 2x: show them at their CSS size, never stretched.
                        # Other images are shown at their own size, as they were before they carried one.
                        w, h = max(1, w // 2), max(1, h // 2)
                    # width and height both: the browser reserves the box (CSS keeps height: auto, max-width: 100%,
                    # so it still scales) and a lazy image that loads later does not push the page down under an
                    # #anchor.
                    alt = label[2:-1].replace('"', "&quot;")
                    return (f'<img src="{BASE}/{tgt.as_posix()}" alt="{alt}" width="{w}" height="{h}"'
                            ' loading="lazy" />')
                return f"{label}({BASE}/{tgt.as_posix()}{ttl})"
            # Outside the staged tree: point at the repository at the same ref.
            origin = Path(repo_path(rel)).parent / path
            norm = []
            for p in origin.parts:
                if p == "..":
                    norm and norm.pop()
                elif p != ".":
                    norm.append(p)
            back = REVERSE.get("/".join(norm))
            if back is not None:
                tl, ts = split_lang(back)
                return f"{label}({agent_url(url_of(tl, ts)) if agent else url_of(tl, ts)}{frag}{ttl})"
            kind = "tree" if path.endswith("/") or "." not in Path(path).name else "blob"
            if not agent:
                unresolved.append(f"{rel}: {target}")
            return f"{label}({REPO}/{kind}/{ref}/{'/'.join(norm)}{frag}{ttl})"

        def links(agent):
            res, in_fence = [], False
            for line in body:
                if line.lstrip().startswith("```"):
                    in_fence = not in_fence
                if in_fence:
                    res.append(line)
                    continue
                # Leave inline code alone: `[text](src/app.ts)` is an example, not a link.
                # (A link whose label is code, [`x`](y), starts outside the span and is kept.)
                spans = [m2.span() for m2 in re.finditer(r"(`+).*?\1", line)]
                res.append(LINK.sub(
                    lambda mt: mt.group(0) if any(a0 <= mt.start() < b0 for a0, b0 in spans) else fix(mt, agent),
                    line))
            return "\n".join(res)

        body_text = ALERT.sub(alert_to_aside, links(False)).lstrip("\n")
        # The agents' copy: the guide's own Markdown with absolute links, its H1 back on top; no front matter,
        # language line or Starlight syntax (asides, <img>, MDX).
        url = url_of(lang, stem)
        dst_md = agent_out / url[len(BASE) + 1:] / "index.md"
        dst_md.parent.mkdir(parents=True, exist_ok=True)
        dst_md.write_text(f"# {title}\n\n" + links(True).strip("\n") + "\n", encoding="utf-8")
        listing.append({"lang": lang, "url": url, "title": title, "description": meta.get("audience", ""),
                        "topic": topic_of(stem), "order": PAGE_ORDER.get(stem.as_posix(), 0) if slug_of(stem) else -1,
                        "stem": stem.as_posix()})

        if not slug_of(stem):
            # The two home pages are a splash landing (no sidebar, so in no topic), as MDX for its cards.
            labels = json.loads((site / "src/topic-labels.json").read_text(encoding="utf-8"))
            dst = out / ("ja/" if lang == "ja" else "") / "index.mdx"
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(landing(lang, title, body_text, labels), encoding="utf-8")
            continue

        fm = [f"title: {yaml_str(title)}"]
        if slug_of(stem):  # the two home pages take their id from index.md
            fm.append(f"slug: {yaml_str(('ja/' if lang == 'ja' else '') + slug_of(stem))}")
        if meta.get("audience"):
            fm.append(f"description: {yaml_str(meta['audience'])}")
        n = NUM.match(stem.name)
        sb = []
        short = re.sub(r"^\d+\.\s+", "", title)
        if short != title:
            sb.append(f"  label: {yaml_str(short)}")
        v = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", stem.name)
        if v:  # newest release first
            a, b, c = map(int, v.groups())
            sb.append(f"  order: {-(a * 1000000 + b * 1000 + c)}")
        elif stem.name == "SUMMARY":
            sb.append("  order: -999999999")
        if meta.get("order"):
            sb.append(f"  order: {int(meta['order'])}")
        elif stem.as_posix() in PAGE_ORDER:
            # A task page takes its place in research/page-titles.tsv, which lists each group's pages in reading
            # order (related pages together); autogenerate would sort them by file name.
            sb.append(f"  order: {PAGE_ORDER[stem.as_posix()]}")
        elif n:
            sb.append(f"  order: {int(n.group(1))}")
        elif stem.name == "README":
            sb.append("  order: 0")
        if rel.parent.as_posix() == "user" and stem.name == "README":
            # The task shelf's index: its pages are listed in the user topic's groups, so the index itself is
            # hidden, and a hidden page names its topic (see the runbooks below).
            sb.append("  hidden: true")
            fm.append("topic: user")
        if rel.parent.as_posix() == "operate/runbooks":
            # Autogenerate would put these in a group named after the directory ("runbooks", with the index
            # page "Runbooks" right under it). astro.config.mjs lists them in a "Runbooks" group instead.
            sb.append("  hidden: true")
            # A page hidden from the sidebar is in no topic's list, so the topic is named.
            fm.append("topic: operate")
        if sb:
            fm.append("sidebar:\n" + "\n".join(sb))
        fm.append(f"editUrl: {yaml_str(f'{REPO}/edit/main/{repo_path(rel)}')}")

        dst = out / (("ja/" if lang == "ja" else "") + rel.parent.as_posix()) / (
            ("index" if stem.name == "README" else stem.name) + ".md")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text("---\n" + "\n".join(fm) + "\n---\n\n" + body_text, encoding="utf-8")

    write_subgroups(rows, out, site)
    # A page the guide has only in English is built at its Japanese URL too (Starlight's fallback, the English text
    # under a notice): its Markdown goes there as well, and llms.txt lists it in the Japanese sections, marked.
    have_ja = {p["url"] for p in listing if p["lang"] == "ja"}
    for p in [p for p in listing if p["lang"] == "en"]:
        ja_url = BASE + "/ja" + p["url"][len(BASE):]
        if ja_url not in have_ja:
            dst_md = agent_out / ja_url[len(BASE) + 1:] / "index.md"
            dst_md.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(agent_out / p["url"][len(BASE) + 1:] / "index.md", dst_md)
            listing.append({**p, "lang": "ja", "url": ja_url, "title": p["title"] + "（英語のみ）"})
    labels = json.loads((site / "src/topic-labels.json").read_text(encoding="utf-8"))
    (agent_out / "llms.txt").write_text(llms_txt(listing, labels), encoding="utf-8")
    print(f"converted; {len(unresolved)} links sent to GitHub:")
    for u in unresolved:
        print("  " + u)


if __name__ == "__main__":
    try:
        main()
    except (ImageSizeError, LandingError) as e:
        sys.exit(f"to_starlight: {e}")
