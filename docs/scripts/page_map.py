#!/usr/bin/env python3
"""Check docs/research/page-map.tsv against a guide/ checkout and print where every old section goes.

Usage: page_map.py <agent-fleet checkout> [--write]

--write regenerates the parts of research/page-map.ja.md between the "generated" markers: the new page tree (from
research/page-titles.tsv) and the full old-section table. Without it the script only checks.

Every H1-H3 heading of every English guide page and shipped runbook must land on a new page: a rule names a file (whole file) or a
heading in it, and a heading rule also covers that heading's sub-headings. A rule that matches no heading fails the
check, because a renamed heading would otherwise silently fall back to the file's default.
"""
import pathlib
import re
import sys
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent.parent


def outline(path):
    """Yield (level, title, words) for the H1-H3 headings, skipping fenced code."""
    fence, cur, out = False, None, []
    for line in path.read_text().splitlines():
        if line.startswith('```'):
            fence = not fence
        m = None if fence else re.match(r'^(#{1,3}) (.*)', line)
        if m:
            cur = [len(m.group(1)), m.group(2).strip(), 0]
            out.append(cur)
        elif cur:
            cur[2] += len(line.split())
    return out


# The runbooks ship in the guide too (deploy/release/stage-docs.sh copies them into operate/runbooks/), so they are
# split by the same map. Their rules name them by their path in the repository.
RUNBOOKS = [
    'deploy/aws/ecs/README.md',
    'deploy/kubernetes/README.md',
    'deploy/compose/README.md',
    'deploy/native/README.md',
    'deploy/local/README-wsl.md',
    'deploy/aws/ec2-single/README.md',
]


def source(guide, f):
    return guide.parent / f if f.startswith('deploy/') else guide / f


def main():
    guide = pathlib.Path(sys.argv[1]) / 'guide'
    rules, used = {}, set()
    for n, line in enumerate((HERE / 'research/page-map.tsv').read_text().splitlines(), 1):
        if not line.strip() or line.startswith('#'):
            continue
        f, h, page = line.split('\t')
        if (f, h) in rules:
            sys.exit(f'page-map.tsv:{n}: duplicate rule for {f} / {h!r}')
        rules[(f, h)] = page
    errors, rows = [], []
    files = sorted(p.relative_to(guide).as_posix() for p in guide.rglob('*.md') if not p.name.endswith('.ja.md'))
    files += RUNBOOKS
    for f in files:
        if (f, '') not in rules:
            errors.append(f'{f}: no whole-file rule')
            continue
        used.add((f, ''))
        stack = []  # (level, page) of enclosing headings that carry a rule
        for level, title, words in outline(source(guide, f)):
            stack = [s for s in stack if s[0] < level]
            page = rules.get((f, title))
            if page:
                used.add((f, title))
                stack.append((level, page))
            rows.append((f, level, title, words, stack[-1][1] if stack else rules[(f, '')], bool(page)))
    for key in rules:
        if key not in used:
            errors.append(f'rule matches no heading: {key[0]} / {key[1]!r}')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        sys.exit(1)

    titles = {}
    for line in (HERE / 'research/page-titles.tsv').read_text().splitlines():
        if line.strip() and not line.startswith('#'):
            page, title, group = line.split('\t')
            titles[page] = (title, group)
    pages = defaultdict(lambda: [0, []])
    for f, level, title, words, page, ruled in rows:
        pages[page][0] += words
        # An H3 shows up as a source only when a rule moved it on its own; otherwise its H2 already stands for it.
        if level <= 2 or ruled:
            src = f.removesuffix('.md') if level == 1 else f"{f.removesuffix('.md')} › {title}"
            if not any(src.startswith(s + ' ›') or s == src for s in pages[page][1]):
                pages[page][1].append(src)
    missing = sorted(set(pages) - set(titles))
    if missing:
        sys.exit('no title in page-titles.tsv for: ' + ', '.join(missing))
    shelves = defaultdict(int)
    for page in titles:
        shelves[page.split('/')[0]] += 1
    new = [p for p in titles if p not in pages]
    print(f'{len(rows)} headings in {len(files)} files -> {len(titles)} pages {dict(shelves)}, '
          f'{len(new)} without an old source', file=sys.stderr)
    if '--write' not in sys.argv:
        return

    tree, last = [], None
    for page, (title, group) in titles.items():
        shelf = page.split('/')[0]
        if (shelf, group) != last:
            if last is None or last[0] != shelf:
                tree.append(f'\n### {SHELVES[shelf]}')
            tree += [f'\n**{group}**\n', '| ページ | タイトル | 元の節 | 語数 |', '|---|---|---|--:|']
            last = (shelf, group)
        words, srcs = pages.get(page, [0, []])
        src = '<br>'.join(f'`{s}`' for s in srcs) or '（新規）'
        tree.append(f'| `{page}` | {title} | {src} | {words or ""} |')
    table = ['| 元のファイル | 見出し | 語数 | 新しいページ |', '|---|---|--:|---|']
    for f, level, title, words, page, _ in rows:
        table.append(f"| `{f}` | {'　' * (level - 1)}{title.replace('|', '\\|')} | {words} | `{page}` |")
    doc = HERE / 'research/page-map.ja.md'
    text = doc.read_text()
    for name, body in (('tree', tree), ('sections', table)):
        text, n = re.subn(rf'(<!-- generated:{name} -->\n).*?(<!-- /generated:{name} -->)',
                          lambda m: m.group(1) + '\n'.join(body).strip('\n') + '\n' + m.group(2), text, flags=re.S)
        if n != 1:
            sys.exit(f'{doc.name}: expected one "generated:{name}" block, found {n}')
    doc.write_text(text)


SHELVES = {'user': 'ユーザーガイド（user/）', 'admin': 'チーム管理（admin/）',
           'operate': 'セルフホスト（operate/）', 'ref': 'リファレンス（ref/）'}


if __name__ == '__main__':
    main()
