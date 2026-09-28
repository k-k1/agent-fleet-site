#!/usr/bin/env python3
"""Static checks for site/: run before every push.

    scripts/check.py            # offline: local links, images, hreflang, security.txt
    scripts/check.py --online   # also fetch every external link and GitHub heading anchor

Exits 1 when anything is wrong. Standard library only, so CI needs no install step.
"""
import datetime
import html.parser
import pathlib
import re
import struct
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
ORIGIN = "https://agent-fleet.org"
HREFLANGS = {"en", "ja", "x-default"}

errors: list[str] = []


def err(where: str, msg: str) -> None:
    errors.append(f"{where}: {msg}")


class Page(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.ids: set[str] = set()
        self.links: list[tuple[str, str]] = []  # (tag, url)
        self.imgs: list[dict] = []
        self.alternates: dict[str, str] = {}
        self.canonical = None
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "href" in a:
            self.links.append((tag, a["href"]))
        if tag == "link":
            rel = a.get("rel", "")
            if rel == "alternate" and "hreflang" in a:
                self.alternates[a["hreflang"]] = a.get("href", "")
            elif rel == "canonical":
                self.canonical = a.get("href")
            elif "href" in a:
                self.links.append((tag, a["href"]))
        if tag == "script" and "src" in a:
            self.links.append((tag, a["src"]))
        if tag == "img":
            self.imgs.append(a)
            self.links.append((tag, a.get("src", "")))
        if tag == "meta" and "content" in a:
            key = a.get("property") or a.get("name")
            if key:
                self.meta[key] = a["content"]


def image_size(path: pathlib.Path) -> tuple[int, int] | None:
    b = path.read_bytes()[:64]
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", b[16:24])
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        kind = b[12:16]
        if kind == b"VP8X":
            w = int.from_bytes(b[24:27], "little") + 1
            h = int.from_bytes(b[27:30], "little") + 1
            return w, h
        if kind == b"VP8 ":
            w, h = struct.unpack("<HH", b[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if kind == b"VP8L":
            bits = int.from_bytes(b[21:25], "little")
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    return None


def resolve_local(url: str) -> pathlib.Path | None:
    """Map a site-absolute or origin URL to the file Cloudflare Pages would serve."""
    if url.startswith(ORIGIN):
        url = url[len(ORIGIN):] or "/"
    path = urllib.parse.unquote(urllib.parse.urlsplit(url).path)
    target = SITE / path.lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    return target if target.is_file() else None


def is_local(url: str) -> bool:
    return url.startswith("/") or url.startswith(ORIGIN)


def check_page(path: pathlib.Path, pages: dict[pathlib.Path, Page], external: dict[str, set[str]]) -> None:
    rel = path.relative_to(SITE).as_posix()
    p = pages[path]
    if not p.lang:
        err(rel, "<html> has no lang")
    for tag, url in p.links:
        if not url:
            err(rel, f"<{tag}> with an empty URL")
            continue
        if url.startswith("#"):
            if url[1:] not in p.ids:
                err(rel, f"in-page anchor {url} has no matching id")
            continue
        if url.startswith("mailto:"):
            continue
        if url.startswith("http://"):
            err(rel, f"plain-http link {url}")
            continue
        if is_local(url):
            target = resolve_local(url)
            if target is None:
                err(rel, f"<{tag}> {url} does not resolve to a file under site/")
                continue
            frag = urllib.parse.urlsplit(url).fragment
            if frag and target in pages and frag not in pages[target].ids:
                err(rel, f"{url}: no id {frag!r} on the target page")
            continue
        external.setdefault(url, set()).add(rel)

    for img in p.imgs:
        src = img.get("src", "")
        if "alt" not in img:
            err(rel, f"<img {src}> has no alt attribute")
        if "width" not in img or "height" not in img:
            err(rel, f"<img {src}> lacks width/height (layout shift while it loads)")
            continue
        target = resolve_local(src) if is_local(src) else None
        size = image_size(target) if target else None
        if size:
            declared = int(img["width"]) / int(img["height"])
            actual = size[0] / size[1]
            if abs(declared - actual) / actual > 0.01:
                err(rel, f"<img {src}> declares {img['width']}x{img['height']}, file is {size[0]}x{size[1]}")

    if rel == "404.html":
        return
    if not p.canonical:
        err(rel, "no canonical link")
    if set(p.alternates) != HREFLANGS:
        err(rel, f"hreflang set is {sorted(p.alternates)}, want {sorted(HREFLANGS)}")
    for lang, href in p.alternates.items():
        if not href.startswith(ORIGIN) or resolve_local(href) is None:
            err(rel, f"hreflang={lang} {href} is not a page on {ORIGIN}")
    if p.canonical and p.canonical not in p.alternates.values():
        err(rel, f"canonical {p.canonical} is not one of the hreflang alternates")
    if p.canonical and p.lang and p.alternates.get(p.lang) != p.canonical:
        err(rel, f"lang={p.lang} but hreflang={p.lang} points at {p.alternates.get(p.lang)}, not the canonical")
    og = p.meta.get("og:image")
    if not og or resolve_local(og) is None:
        err(rel, f"og:image {og!r} does not resolve to a file under site/")
    elif image_size(resolve_local(og)) != (int(p.meta.get("og:image:width", 0)), int(p.meta.get("og:image:height", 0))):
        err(rel, f"og:image {og} size differs from og:image:width/height")


def check_security_txt() -> None:
    path = SITE / ".well-known/security.txt"
    text = path.read_text()
    m = re.search(r"^Expires:\s*(\S+)", text, re.M)
    if not m:
        err("security.txt", "no Expires field (RFC 9116 requires one)")
        return
    expires = datetime.datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
    left = expires - datetime.datetime.now(datetime.timezone.utc)
    if left.days < 30:
        err("security.txt", f"Expires {m.group(1)} is {left.days} days away; move it forward (at most a year)")
    if left.days > 366:
        err("security.txt", f"Expires {m.group(1)} is more than a year away (RFC 9116 recommends less)")
    if not re.search(r"^Contact:", text, re.M):
        err("security.txt", "no Contact field")


def check_sitemap(pages: dict[pathlib.Path, Page]) -> None:
    text = (SITE / "sitemap.xml").read_text()
    locs = re.findall(r"<loc>([^<]+)</loc>", text)
    served = {resolve_local(u) for u in locs}
    want = {p for p in pages if p.name != "404.html"}
    if served != want:
        err("sitemap.xml", f"lists {sorted(str(x) for x in served)}, pages are {sorted(str(x) for x in want)}")


def fetch(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "agent-fleet-site-check"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""


def check_online(external: dict[str, set[str]]) -> None:
    bodies: dict[str, tuple[int, str]] = {}
    for url, where in sorted(external.items()):
        base, _, frag = url.partition("#")
        if base not in bodies:
            bodies[base] = fetch(base)
        status, body = bodies[base]
        if status != 200:
            err(", ".join(sorted(where)), f"{base} answered {status}")
            continue
        # GitHub renders heading ids as user-content-<slug>, percent-encoded for non-ASCII.
        if frag and "github.com" in base:
            ids = {urllib.parse.unquote(i) for i in re.findall(r'id="user-content-([^"]+)"', body)}
            if frag not in ids:
                err(", ".join(sorted(where)), f"{url}: GitHub renders no heading #{frag}")
    print(f"online: {len(external)} external links, {len(bodies)} distinct pages fetched")


def main() -> int:
    online = "--online" in sys.argv[1:]
    files = sorted(SITE.rglob("*.html"))
    pages = {}
    for f in files:
        p = Page()
        p.feed(f.read_text(encoding="utf-8"))
        pages[f] = p
    external: dict[str, set[str]] = {}
    for f in files:
        check_page(f, pages, external)
    check_security_txt()
    check_sitemap(pages)
    if online:
        check_online(external)
    n_links = sum(len(p.links) for p in pages.values())
    n_imgs = sum(len(p.imgs) for p in pages.values())
    print(f"checked {len(files)} pages, {n_links} links, {n_imgs} images; {len(errors)} errors")
    for e in errors:
        print("  " + e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
