#!/usr/bin/env python3
"""Fail when a built page links to a /docs/ path that was not built, a redirect points nowhere, or an image has no size.

    docs/scripts/check_dist.py <dist dir>

starlight-links-validator checks the links inside the Markdown, not the ones Starlight writes itself from the
sidebar and topic config, so a topic whose landing page was left out of the build (the pilot pages, DOCS_PILOT=0)
renders a dead link in every page's top bar and the build stays green.

The redirects that scripts/redirect_stubs.py writes after the build are checked here too: every target of a stub or
of a page's section map is a built page (not another stub), its #anchor is an id on that page, and no stub sits at
a URL the sitemap lists as a page.

Every <img> must carry a height (with its width) or an aspect-ratio, so that the browser reserves its box before it
loads: a lazy screenshot without one grows the page when it arrives, and a page opened at #anchor drifts away from the
heading. scripts/to_starlight.py writes both from the image file.
"""
import json
import pathlib
import re
import sys
from urllib.parse import unquote

dist = pathlib.Path(sys.argv[1])
href = re.compile(r'href="/docs/([^"#?]*)')
maps = re.compile(r'<script type="application/json" id="(redirect-map|section-redirects)">(.*?)</script>', re.S)
ids = re.compile(r'\sid="([^"]+)"')
# Quoted values may hold a bare '>' (an alt text like "Settings > Agents").
img = re.compile(r'''<img\b(?:[^>"']|"[^"]*"|'[^']*')*>''', re.I)
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


def sized(tag):
    """An <img> whose box is known before it loads: width and height attributes, or an aspect-ratio in its style."""
    has = lambda a: re.search(rf'\s{a}\s*=\s*"?[0-9]', tag, re.I)
    return bool(has('width') and has('height')) or bool(re.search(r'aspect-ratio\s*:', tag, re.I))


for page in pages:
    for tag in img.findall(html[page]):
        if not sized(tag):
            shown = re.sub(r' alt="[^"]*"', '', tag)
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
sys.exit(1 if dead or bad or unsized else 0)
