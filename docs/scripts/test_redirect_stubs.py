#!/usr/bin/env python3
"""Tests for redirect_stubs.py: python3 -m unittest discover -s docs/scripts -p 'test_*.py'"""
import unittest

import redirect_stubs as R

EN = """# Page

## Install the CLI

Run `af-install --user` and open [the settings](settings.md).

```bash
af-install --user
```

## Rotate a token

| Column | Value |
|---|---|
| `token` | 30 days |
| `expiry` | 90 days |

## Read the log

See `journalctl -u af` for the last 200 lines.
"""

JA_SAME = """# ページ

## CLI を入れる

`af-install --user` を実行し、[設定](settings.ja.md)を開きます。

```bash
af-install --user
```

## トークンを入れ替える

| 列 | 値 |
|---|---|
| `token` | 30 日 |
| `expiry` | 90 日 |

## ログを読む

直近 200 行は `journalctl -u af` で見ます。
"""

# The same translation with its first two sections in the other order: the levels still match.
JA_SWAPPED = JA_SAME.replace(
    JA_SAME[JA_SAME.index("## CLI"):JA_SAME.index("## ログ")],
    JA_SAME[JA_SAME.index("## トークン"):JA_SAME.index("## ログ")]
    + JA_SAME[JA_SAME.index("## CLI"):JA_SAME.index("## トークン")])


def html(heads):
    """A built Starlight page with the given (level, id, body) sections."""
    body = "".join(f'<div class="sl-heading-wrapper level-h{lv}"><h{lv} id="{i}">{i}</h{lv}>'
                   f'<a class="sl-anchor-link" href="#{i}"><svg><path d="m12 15 3 8"/></svg></a></div>{b}'
                   for lv, i, b in heads)
    return f'<main><div class="sl-markdown-content">{body}</div></main><footer></footer>'


class Pairing(unittest.TestCase):
    def test_translation_in_the_same_order_pairs(self):
        en, ja = R.md_headings(EN), R.md_headings(JA_SAME)
        self.assertEqual([R.paired(en, ja, n) for n in range(3)], [True, True, True])
        self.assertEqual(ja[1][1][0], "トークンを入れ替える")

    def test_reordered_same_level_headings_do_not_pair(self):
        en, ja = R.md_headings(EN), R.md_headings(JA_SWAPPED)
        self.assertEqual([h[0] for h in en], [h[0] for h in ja])  # a level check alone would accept this
        self.assertFalse(R.paired(en, ja, 0))
        self.assertFalse(R.paired(en, ja, 1))
        self.assertTrue(R.paired(en, ja, 2))

    def test_different_levels_do_not_pair(self):
        en = R.md_headings(EN)
        ja = R.md_headings(JA_SAME.replace("## ログを読む", "### ログを読む"))
        self.assertFalse(any(R.paired(en, ja, n) for n in range(3)))

    def test_section_without_content_does_not_pair(self):
        en = R.md_headings("# P\n\n## Overview\n\nPlain words only.\n\n## Rotate\n\nUse `af-rotate`.\n")
        ja = R.md_headings("# P\n\n## 概要\n\n言葉だけ。\n\n## 入れ替え\n\n`af-rotate` を使う。\n")
        self.assertFalse(R.paired(en, ja, 0))
        self.assertTrue(R.paired(en, ja, 1))

    def test_parent_heading_takes_its_subsections(self):
        en = R.md_headings("# P\n\n## Setup\n\n### Step one\n\nRun `af-a`.\n\n## Other\n\nRun `af-b`.\n")
        ja = R.md_headings("# P\n\n## 準備\n\n### 手順 1\n\n`af-a` を実行。\n\n## その他\n\n`af-b` を実行。\n")
        self.assertTrue(R.paired(en, ja, 0))

    def test_built_pages_reordered(self):
        a = (2, "a", "<p>Run <code>af-install --user</code></p><pre>x</pre>")
        b = (2, "b", "<table><tr><td>token</td><td>30</td></tr><tr><td>expiry</td><td>90</td></tr></table>")
        en = R.html_headings(html([a, b]))
        same = R.html_headings(html([(2, "あ", a[2]), (2, "い", b[2])]))
        swapped = R.html_headings(html([(2, "い", b[2]), (2, "あ", a[2])]))
        self.assertTrue(R.paired(en, same, 0))
        self.assertFalse(R.paired(en, swapped, 0))
        self.assertNotIn("15", en[0][2])  # the anchor icon's SVG is not content


class Boilerplate(unittest.TestCase):
    """Two same-level sections whose only shared content is identical: nothing tells them apart."""
    BLOCK = "```bash\ncommon --help\n```\n"

    def test_markdown_identical_sections_swapped(self):
        en = R.md_headings(f"# P\n\n## First\n\n{self.BLOCK}\n## Second\n\n{self.BLOCK}")
        ja = R.md_headings(f"# P\n\n## 二つめ\n\n{self.BLOCK}\n## 一つめ\n\n{self.BLOCK}")
        self.assertFalse(R.paired(en, ja, 0))
        self.assertFalse(R.paired(en, ja, 1))

    def test_markdown_boilerplate_does_not_outweigh_the_rest(self):
        en = R.md_headings(f"# P\n\n## First\n\n{self.BLOCK}Use `af-one`.\n\n## Second\n\n{self.BLOCK}Use `af-two`.\n")
        ja = R.md_headings(f"# P\n\n## 一つめ\n\n{self.BLOCK}`af-one` を使う。\n\n## 二つめ\n\n{self.BLOCK}`af-two` を使う。\n")
        swapped = R.md_headings(f"# P\n\n## 二つめ\n\n{self.BLOCK}`af-two` を使う。\n\n## 一つめ\n\n{self.BLOCK}`af-one` を使う。\n")
        self.assertTrue(R.paired(en, ja, 0))
        self.assertFalse(R.paired(en, swapped, 0))

    def test_html_identical_sections_swapped(self):
        body = "<pre><code>common --help</code></pre>"
        en = R.html_headings(html([(2, "first", body), (2, "second", body)]))
        ja = R.html_headings(html([(2, "二つめ", body), (2, "一つめ", body)]))
        self.assertFalse(R.paired(en, ja, 0))
        self.assertFalse(R.paired(en, ja, 1))


class LinkDestinations(unittest.TestCase):
    """Swapped sections that share boilerplate and differ only in where their links point."""
    BLOCK = "```bash\ncommon --help\n```\n"

    def test_markdown_swapped_links(self):
        en = R.md_headings("# P\n## Alpha\n" + self.BLOCK + "[Guide](alpha.md)\n## Beta\n" + self.BLOCK
                           + "[Guide](beta.md) [More](more.md)\n")
        ja = R.md_headings("# P\n## ベータ\n" + self.BLOCK + "[説明](beta.ja.md)\n## アルファ\n" + self.BLOCK
                           + "[説明](alpha.ja.md) [詳細](more.ja.md)\n")
        self.assertFalse(R.paired(en, ja, 0))
        self.assertFalse(R.paired(en, ja, 1))
        same = R.md_headings("# P\n## アルファ\n" + self.BLOCK + "[説明](alpha.ja.md#概要)\n## ベータ\n" + self.BLOCK
                             + "[説明](beta.ja.md) [詳細](more.ja.md)\n")
        self.assertTrue(R.paired(en, same, 0))
        self.assertTrue(R.paired(en, same, 1))

    def test_html_swapped_links(self):
        pre = "<pre><code>common --help</code></pre>"
        en = R.html_headings(html([(2, "alpha", pre + '<a href="/docs/alpha/">Guide</a>'),
                                   (2, "beta", pre + '<a href="/docs/beta/">Guide</a> <a href="/docs/more/">More</a>')]))
        ja = R.html_headings(html([(2, "ベータ", pre + '<a href="/docs/ja/beta/">説明</a>'),
                                   (2, "アルファ", pre + '<a href="/docs/ja/alpha/">説明</a> <a href="/docs/ja/more/">詳細</a>')]))
        self.assertFalse(R.paired(en, ja, 0))
        self.assertFalse(R.paired(en, ja, 1))
        same = R.html_headings(html([(2, "アルファ", pre + '<a href="/docs/ja/alpha/#x">説明</a>'),
                                     (2, "ベータ", pre + '<a href="/docs/ja/beta/">説明</a> <a href="/docs/ja/more/">詳細</a>')]))
        self.assertTrue(R.paired(en, same, 0))
        self.assertTrue(R.paired(en, same, 1))


class Urls(unittest.TestCase):
    def test_url_form(self):
        self.assertEqual(R.url("en", "member/README.md"), "/docs/member/")
        self.assertEqual(R.url("ja", "member/03-Start.md", "x"), "/docs/ja/member/03-start/#x")
        self.assertEqual(R.url("en", "README.md"), "/docs/")


if __name__ == "__main__":
    unittest.main()
