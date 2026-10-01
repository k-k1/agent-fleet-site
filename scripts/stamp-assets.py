#!/usr/bin/env python3
"""Stamp every page's stylesheet and script URL with a hash of the file's content.

    scripts/stamp-assets.py      # after editing site/assets/site.css or lightbox.js

/assets/* is cached for a day, at Cloudflare's edge and in browsers, and the file names
carry no hash. Without a new URL, a deploy that changes the stylesheet serves new HTML
against yesterday's CSS until the cache expires (measured: the features page shipped
unstyled on agent-fleet.org while the pull-request preview looked right). scripts/check.py
fails when a stamp does not match the file, so a forgotten run is caught before merge.
"""
import hashlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
STAMPED = ("assets/site.css", "assets/lightbox.js")


def stamp(rel: str) -> str:
    return hashlib.sha256((SITE / rel).read_bytes()).hexdigest()[:10]


def main() -> None:
    for page in sorted(SITE.rglob("*.html")):
        text = page.read_text(encoding="utf-8")
        new = text
        for rel in STAMPED:
            new = re.sub(rf'"/{re.escape(rel)}(\?v=[0-9a-f]*)?"', f'"/{rel}?v={stamp(rel)}"', new)
        if new != text:
            page.write_text(new, encoding="utf-8")
            print(f"stamped {page.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
