#!/usr/bin/env python3
"""Fail when a built page links to a /docs/ path that was not built.

    docs/scripts/check_dist.py <dist dir>

starlight-links-validator checks the links inside the Markdown, not the ones Starlight writes itself from the
sidebar and topic config, so a topic whose landing page was left out of the build (the pilot pages, DOCS_PILOT=0)
renders a dead link in every page's top bar and the build stays green.
"""
import pathlib
import re
import sys

dist = pathlib.Path(sys.argv[1])
href = re.compile(r'href="/docs/([^"#?]*)')
dead = {}
pages = sorted(dist.rglob('*.html'))
for page in pages:
    for target in href.findall(page.read_text(encoding='utf-8')):
        path = dist / target
        if not (target == '' or path.is_file() or (path / 'index.html').is_file()):
            dead.setdefault('/docs/' + target, page.relative_to(dist).as_posix())
for target, page in sorted(dead.items()):
    print(f'dead link {target} (first seen in {page})', file=sys.stderr)
print(f'check_dist: {len(pages)} pages, {len(dead)} dead /docs/ links')
sys.exit(1 if dead else 0)
