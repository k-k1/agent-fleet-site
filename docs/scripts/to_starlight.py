#!/usr/bin/env python3
"""Turn the staged guide (deploy/release/stage-docs.sh output) into Starlight content.

    to_starlight.py <staged-dir> <site-dir> <git-ref>

The guide stays GitHub-shaped in the repository (x.md + x.ja.md, an H1 per page, a
language-switch line, relative .md links); everything Starlight needs is derived here so
the source never has to know a website exists.
"""
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = "/docs"
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
    for d in (out, pub / "assets"):
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

        def fix(mt):
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
                return f"{label}({url_of(tl, ts)}{frag}{ttl})"
            if tgt.parts and tgt.parts[0] == "assets" and (staged / tgt).is_file():
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
                return f"{label}({url_of(tl, ts)}{frag}{ttl})"
            kind = "tree" if path.endswith("/") or "." not in Path(path).name else "blob"
            unresolved.append(f"{rel}: {target}")
            return f"{label}({REPO}/{kind}/{ref}/{'/'.join(norm)}{frag}{ttl})"

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
                lambda mt: mt.group(0) if any(a0 <= mt.start() < b0 for a0, b0 in spans) else fix(mt),
                line))
        body_text = ALERT.sub(alert_to_aside, "\n".join(res)).lstrip("\n")

        fm = [f"title: {yaml_str(title)}"]
        if not slug_of(stem):  # the home pages sit in the user-guide topic
            fm.append("topic: user")
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
    print(f"converted; {len(unresolved)} links sent to GitHub:")
    for u in unresolved:
        print("  " + u)


if __name__ == "__main__":
    try:
        main()
    except ImageSizeError as e:
        sys.exit(f"to_starlight: {e}")
