# docs/ — the agent-fleet.org/docs/ site (pilot)

The user guide of [Agent Fleet](https://github.com/k-k1/agent-fleet), built with Astro Starlight and served under
`https://agent-fleet.org/docs/`. **Status: pilot.** Nothing here is deployed yet. The direction is recorded in ADR 0131
in the main repository (`docs/decisions/0131-public-docs-site.md`, on `main` since PR #3526), and the work is tracked in k-k1/agent-fleet#3463. Read the ADR first: it holds the decisions, the page model and the screenshot rules. This file covers how to
build the site and the review feedback so far.

## Build and preview

```bash
cd docs
npm ci
scripts/build.sh ~/repos/agent-fleet v0.41.0     # a release tag, never main
npx astro preview --host 127.0.0.1 --port 4410   # http://127.0.0.1:4410/docs/
```

`build.sh` does the following:

1. Takes `guide/`, `deploy/` and `scripts/` from the tag and runs the main repository's
   `deploy/release/stage-docs.sh`, the same closed tree the Console ships.
2. Lays `pilot/` over it, when that directory exists (it is empty now: every pilot page is in the guide).
3. Converts the result with `scripts/to_starlight.py`.
4. Builds the site. The link validator fails the build on a broken link or anchor.
5. Writes redirect stubs for the old URLs of pages that moved, with `scripts/redirect_stubs.py` (below).

## Old URLs

agent-fleet's `guide/_redirects.tsv` lists the pages and sections that moved (`old<TAB>new`, English paths; a left side
with `#anchor` is a section that moved out of a page). Cloudflare Pages serves static files only, so after
`astro build` `scripts/redirect_stubs.py` turns the map into pages:

- **An old page that is not built** gets a stub at its URL, in both languages (`dist/member/lite/index.html`,
  `dist/ja/member/lite/index.html`). Its script reads `location.hash` and goes to that section's row with
  `location.replace`; a hash with no row goes to the page-level target, which a meta refresh also uses without
  JavaScript. The stub has `noindex`, a canonical link and a plain link. Written after the build, it is in neither
  Pagefind nor the sitemap.
- **The page-level target** is the page's own row. A page that has only section rows goes where its first section
  went: the first of its rows in the heading order of the last release that had the page.
- **An old page that is still built** but lost sections gets a small map in its `<head>`: when the hash names no
  element on the page and the map has it, the reader goes to the section's new place.
- **Japanese.** The map's anchors are English heading slugs. The old page's English and Japanese headings are paired
  by position, from the newest release (in the checkout's history) whose two versions have the same heading levels;
  so is a target's anchor, from the built pages. Position alone is not trusted: a pair is kept only when the two
  sections share language-neutral content (ASCII words, numbers, code blocks, table rows, list items, links) and
  fit each other better than they would swapped with any other section of the same level, so headings in a
  different order are not mixed up. What cannot be paired goes to the Japanese page-level target, or to the top of
  the target page. `python3 -m unittest discover -s docs/scripts -p 'test_*.py'` tests this (CI runs it). A row's
  anchor is matched in both the Console's and GitHub's slug form (`a → b` is `a-b` or `a--b`).
- `scripts/check_dist.py` fails the build when a redirect's target page is not built, its anchor is not an id on that
  page, or a stub sits where the sitemap lists a page. It reports the stubs apart from the pages.

The history is why `scripts/pages-build.sh` clones agent-fleet blobless instead of shallow: a shallow clone has no
earlier release, and its Japanese stubs would map no section.

## Text for agents

Every page is also published as Markdown next to its HTML, `/docs/<path>/index.md` (`/docs/ja/<path>/index.md`), and
`/docs/llms.txt` lists every page with its title, its audience and that URL, a section per topic in English and then
in Japanese. `scripts/to_starlight.py` writes both into `agent-text/` from the staged guide, and `build.sh` copies them
into `dist/` after the build. The Markdown is the guide's own: GitHub alerts and code blocks as written, every link an
absolute URL (a page link points at that page's `index.md`). A page the guide has only in English is built at its
Japanese URL too (Starlight's fallback), so its Markdown is copied there and llms.txt marks it 「（英語のみ）」.

The home pages and the self-hosting pages (`operate/`, runbooks included, the shelves in `AGENT_BOX_SHELVES` of
`src/components/ForAgents.astro`) show a "For agents" box with a prompt to copy (`Read
https://agent-fleet.org/docs/<path>/index.md`; the home pages point at llms.txt): under "On this page" in the right
column (`src/components/TableOfContents.astro`), and at the end of the page where there is no right column, on narrow
screens, on pages without headings and on the home pages (`src/components/Footer.astro`). Other pages have no box but
still have their `index.md` and their line in llms.txt. `scripts/check_dist.py` fails when a built page has no `index.md` or llms.txt
does not list it.

## Search quality

Search is Pagefind, built into `dist/pagefind/` by Starlight. It segments Japanese, so a compound such as 「共有サインイン」
matches 「共有」 and 「サインイン」 separately, and the weights in `pagefind.ranking` (`astro.config.mjs`) decide whether a
long chapter or the short task page comes first. To compare a change, run a fixed list of queries against a build:

```bash
node scripts/search_quality.mjs                      # dist/, with the ranking the build embedded
node scripts/search_quality.mjs --ranking '{"pageLength":0.1,"termFrequency":0.1,"termSaturation":2,"termSimilarity":9}'   # Starlight's old defaults
node scripts/search_quality.mjs --compact            # ranks only, one line (for a before/after table)
```

- `research/search-queries.tsv` is the list: query, language, the page that must come back, and the top N it has to be
  in. It runs Pagefind's own browser library on `dist/pagefind` (no server, no network) with the language set as
  `<html lang>` would set it. Exit 1 when a page is outside its top N, or absent from the build, so the check cannot
  pass without finding its page.
- It needs a build that contains the pages the list names. `docs/scripts/build.sh ~/repos/agent-fleet main` has them;
  the release tag in `scripts/docs-ref.txt` may not (`user/integrations/aws-sso` is not in v0.41.0), and then the check
  fails on purpose. `scripts/pages-build.sh` runs it only when `scripts/docs-ref.txt` is not a release tag (a preview that follows an agent-fleet branch); main and tag-pinned builds skip it.
- `--ranking` overrides the weights without a rebuild, so a tuning is tried in seconds; then put the winner in
  `astro.config.mjs` and rebuild to confirm the bundle carries it.
- When adding a query, state which page should win and why; keep English queries in the list, because a tuning that
  fixes Japanese must not move English. Ranks are on the page level (the first result for that page).
- What is left is wording, not weights (#3574, measured on 53 queries): the browser splits a query with
  `Intl.Segmenter` (「共有サインイン」 → 共有 / サイン / イン, 「ワークツリー」 → ワーク / ツリー) and every part also matches
  as a prefix (ワーク → ワークスペース), so a page that says the compound once loses to pages that use its parts often.
  No `ranking` setting near the current one moved a miss, and the page title is already a weight-7 heading (raising it
  to 10 moved one query by one place). Putting the term in the heading of the section that covers it does work: on a
  re-indexed copy, 「共有サインイン」 went from 5 to 2. That change belongs in agent-fleet's `guide/`.

## Layout

| Path | What |
|---|---|
| `astro.config.mjs` | Starlight, the topics (using Agent Fleet / team admin / self-hosting / reference / release notes), the link validator |
| `src/console-slug.mjs` | Heading ids by the Console's rule (`guide/`) or github-slugger (runbooks). See ADR 0131 §2 |
| `scripts/to_starlight.py` | Staged guide → Starlight content: titles, language routes, links, alerts → asides, image sizes (WebP screenshots are 2x: half their width and height; a size it cannot read fails the build) |
| `scripts/redirect_stubs.py` | Redirect stubs for the old URLs (above), written into `dist/` after the build |
| `pilot/` | Draft pages laid over the release's guide in previews (mirrors `guide/`). Absent while there are no drafts; production never uses it (`DOCS_PILOT=0`) |
| `research/page-map.ja.md` | Map from every section of the current `guide/` and the shipped runbooks to a page of the new structure (#3463), agreed with the user on 2026-11-07. Rules in `research/page-map.tsv` and `research/page-titles.tsv`; `scripts/page_map.py <checkout> [--write]` checks that every heading is mapped and regenerates the tables |
| `research/search-queries.tsv`, `scripts/search_quality.mjs` | The search-quality check (above) |
| `research/mcp-inventory.md` | The 81 MCP tools: their routes, gates and sources, collected from the code |

Screenshots come from the main repository's `console/scripts/shots/capture.mjs` (scenes marked `guide: true`).

## Deploy

Cloudflare Pages runs `scripts/pages-build.sh` (in the repository root) on every push.

- **Production (`main`) publishes `/docs/` while `scripts/docs-published` exists.** Remove that file and `main`
  deploys `site/` alone again (ADR 0132, addendum).
- **Once published**, `main` builds the agent-fleet release tag in `scripts/docs-ref.txt` (it refuses anything else)
  and leaves out the pilot pages. A new release's guide goes live by changing that file.
- **Every other branch is a preview** and always builds `/docs/`, with the pilot pages. To review pages that are not
  released, push a branch here whose `scripts/docs-ref.txt` names an agent-fleet branch (`main`, or a pull request's
  branch); its preview URL shows them.
- Each build checks the output for dead `/docs/` links, redirects that point nowhere, and content images without a height
  (`scripts/check_dist.py`): an image whose box is not reserved moves the page when it loads, away from an #anchor.

To reproduce a deploy locally, from the repository root: `CF_PAGES_BRANCH=main bash scripts/pages-build.sh`, or any
other branch name for a preview.

## Pilot pages

A pilot page moves into agent-fleet's `guide/` when it is rewritten, and is deleted here in the same step: a pilot copy
would overwrite the guide's page in every preview. Already in `guide/`: `user/integrations/aws-sso` (k-k1/agent-fleet#3566),
`ref/aws-profiles`, `ref/cli/README` and `ref/cli/af-aws-exec`.

| Page | State |
|---|---|
| `user/start/overview`, `quickstart`, `concepts` | First draft. Written before the page model existed, so they still need a rework |
| `user/security/credentials` | AWS section only |
| `ref/mcp/README` | Generated from the inventory. Not yet fact-checked; admin-tool visibility details are unverified |

## Review feedback so far (from the user)

These are the corrections behind the rules in ADR 0131 §4–5. Check every new page against them.

1. **Conversion alone is not enough.** The pages have to be restructured: the current chapters are hard to read and
   the point is hard to find. Model the structure on a modern docs site: topics across the top, one feature per page.
2. **Do not just summarise the old chapter.** A summary keeps the old chapter's point of view (spec and safety), and
   the things a user needs disappear: what the agent does for you, the settings screen, the login toast. Write from the
   user's flow, and agree the flow with the user before writing.
3. **No preamble and no safety asides on task pages.** "Your company's…" and "secrets are never stored" do not belong
   on a page about using a feature. Secret handling goes to the cross-cutting credentials page.
4. **Titles are what the reader wants to do**: "Use AWS SSO" / 「AWS SSO を使う」, not "AWS".
5. **"How it works" first**: what you do and what the agent does. The agent uses the tools (e.g. `af-aws-exec`), so
   the reader needs this split before anything else.
6. 「しくみ」 read as childish in Japanese. Use 「全体像」 ("How it works"). 「役割分担」 ("Who does what") is the
   alternative if the user prefers it.
7. **Reference is separate**: one page per bundled `af-` command, and a reference for the af MCP tools.
8. **Screenshots show the component and where it opens from, nothing else.** Including the whole WS bar was "too much
   noise". The right crop is the badge plus its popover.
9. Draft and review in Japanese first (the user reviews in Japanese), then write English as the canonical version.

## Known gaps

- English pages: none yet.
- The Console's Markdown viewer does not render GitHub alerts (`> [!TIP]`); the converter turns them into asides.
- Wide tables: first-column code is kept on one line (`src/styles/custom.css`). The MCP tables use three columns, because
  six were unreadable.
