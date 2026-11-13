#!/usr/bin/env python3
"""Fail when a built page links to a /docs/ path that was not built, a redirect points nowhere, or an image has no size.

    docs/scripts/check_dist.py <dist dir>

starlight-links-validator checks the links inside the Markdown, not the ones Starlight writes itself from the
sidebar and topic config, so a topic whose landing page was left out of the build (the pilot pages, DOCS_PILOT=0)
renders a dead link in every page's top bar and the build stays green.

The redirects that scripts/redirect_stubs.py writes after the build are checked here too: every target of a stub or
of a page's section map is a built page (not another stub), its #anchor is an id on that page, and no stub sits at
a URL the sitemap lists as a page.

Every <img> in a page's content (.sl-markdown-content) must carry a width and a height, or an aspect-ratio in its
style, so that the browser reserves its box before it loads: a lazy screenshot without one grows the page when it
arrives, and a page opened at #anchor drifts away from the heading. scripts/to_starlight.py writes both from the
image file. The site's own chrome (the logo) is left out: its size can come from CSS.
"""
import json
import math
import pathlib
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote

# Elements without an end tag, which must not open a level of nesting.
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}


NUM = r'(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]+)?'
RATIO = re.compile(rf'({NUM})\s*(?:/\s*({NUM}))?')


def _number(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return False
    return math.isfinite(f) and f > 0


def _ratio(value):
    """True for an aspect-ratio value that fixes the box: a positive number or n / m, optionally with 'auto'."""
    v = re.sub(r'\s*!important\s*$', '', value.strip(), flags=re.I)
    parts = v.split()
    if 'auto' in (p.lower() for p in parts):
        # "auto 16 / 9" or "16 / 9 auto": the ratio holds until the image loads. Plain "auto" does not.
        v = ' '.join(p for p in parts if p.lower() != 'auto')
    m = RATIO.fullmatch(v)
    return bool(m) and _number(m.group(1)) and (m.group(2) is None or _number(m.group(2)))


def has_box(attrs):
    """An <img> whose box is known before it loads: width and height, or a valid aspect-ratio in its style.

    Only the last aspect-ratio declaration counts, as in CSS: "aspect-ratio: 2; aspect-ratio: auto" is not sized.
    """
    a = dict(attrs)
    if _number(a.get('width')) and _number(a.get('height')):
        return True
    last = None
    for decl in (a.get('style') or '').split(';'):
        prop, _, value = decl.partition(':')
        if prop.strip().lower() == 'aspect-ratio':
            last = value
    return last is not None and _ratio(last)


class ContentImages(HTMLParser):
    """Collects the <img> tags inside .sl-markdown-content that have no box. Comments are never seen as tags."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0  # > 0 while inside the content area
        self.unsized = []

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            if self.depth and not has_box(attrs):
                self.unsized.append(self.get_starttag_text())
            return
        if tag in VOID:
            return
        if self.depth:
            self.depth += 1
        elif 'sl-markdown-content' in (dict(attrs).get('class') or '').split():
            self.depth = 1

    def handle_startendtag(self, tag, attrs):
        if tag == 'img':
            self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if self.depth and tag not in VOID:
            self.depth -= 1


def unsized_images(text):
    """The start tags of the content images in a page that have neither width and height nor an aspect-ratio."""
    p = ContentImages()
    p.feed(text)
    p.close()
    return p.unsized


def main():
    dist = pathlib.Path(sys.argv[1])
    href = re.compile(r'href="/docs/([^"#?]*)')
    maps = re.compile(r'<script type="application/json" id="(redirect-map|section-redirects)">(.*?)</script>', re.S)
    ids = re.compile(r'\sid="([^"]+)"')
    dead, bad, unsized = {}, [], []
    pages, stubs, sections = [], [], 0
    html = {}
    for page in sorted(dist.rglob('*.html')):
        html[page] = page.read_text(encoding='utf-8')
        (stubs if 'id="redirect-map"' in html[page] else pages).append(page)

    def built(target):
        """The built file a /docs/ URL names, or None."""
        p = dist / unquote(target)
        f = p if p.is_file() else p / 'index.html'
        return f if f.is_file() else None

    for page in pages + stubs:
        for target in href.findall(html[page]):
            if not (target == '' or built(target)):
                dead.setdefault('/docs/' + target, page.relative_to(dist).as_posix())
        for kind, blob in maps.findall(html[page]):
            sections += kind == 'section-redirects'
            for key, to in json.loads(blob).items():
                where = f"{page.relative_to(dist).as_posix()} #{key}"
                path, _, anchor = to.partition('#')
                f = built(path[len('/docs/'):]) if path.startswith('/docs/') else None
                if f is None or f not in html:
                    bad.append(f'{where}: target {to} is not a built page')
                elif f in stubs:
                    bad.append(f'{where}: target {to} is itself a redirect stub')
                elif anchor and anchor not in ids.findall(html[f]):
                    bad.append(f'{where}: target {to} has no element with the id "{anchor}"')

    for page in pages:
        for tag in unsized_images(html[page]):
            shown = re.sub(r''' alt=("[^"]*"|'[^']*')''', '', tag)
            unsized.append(f'{page.relative_to(dist).as_posix()}: {shown}')

    listed = set()
    for sm in dist.glob('sitemap-*.xml'):
        listed |= set(re.findall(r'<loc>[^<]*?/docs/([^<]*)</loc>', sm.read_text(encoding='utf-8')))
    listed = {unquote(u) for u in listed}
    for stub in stubs:
        if unquote(stub.parent.relative_to(dist).as_posix() + '/') in listed:
            bad.append(f'{stub.relative_to(dist).as_posix()}: a redirect stub where the sitemap lists a page')

    for target, page in sorted(dead.items()):
        print(f'dead link {target} (first seen in {page})', file=sys.stderr)
    for b in bad:
        print(f'bad redirect: {b}', file=sys.stderr)
    for u in unsized:
        print(f'image without height or aspect-ratio: {u}', file=sys.stderr)
    print(f'check_dist: {len(pages)} pages, {len(dead)} dead /docs/ links; '
          f'{len(stubs)} redirect stubs and {sections} pages with section redirects, {len(bad)} bad redirects; {len(unsized)} images without a size')
    return 1 if dead or bad or unsized else 0


if __name__ == '__main__':
    sys.exit(main())
