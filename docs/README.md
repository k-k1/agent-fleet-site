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
2. Lays `pilot/` over it.
3. Converts the result with `scripts/to_starlight.py`.
4. Builds the site. The link validator fails the build on a broken link or anchor.

## Layout

| Path | What |
|---|---|
| `astro.config.mjs` | Starlight, the topics (user guide / team admin / self-hosting / reference / release notes), the link validator |
| `src/console-slug.mjs` | Heading ids by the Console's rule (`guide/`) or github-slugger (runbooks). See ADR 0131 §2 |
| `scripts/to_starlight.py` | Staged guide → Starlight content: titles, language routes, links, alerts → asides, 2x screenshot widths |
| `scripts/mcp_page.py` | Renders the MCP tool tables from `research/mcp-inventory.md`. Interim: the plan is to generate from the golden `list.json` files |
| `pilot/` | Rewritten pages in the new structure, in Japanese only so far. It mirrors `guide/`: `user/…`, `ref/cli/…`, `ref/mcp/…` |
| `research/page-map.ja.md` | Map from every section of the current `guide/` and the shipped runbooks to a page of the new structure (#3463), agreed with the user on 2026-11-07. Rules in `research/page-map.tsv` and `research/page-titles.tsv`; `scripts/page_map.py <checkout> [--write]` checks that every heading is mapped and regenerates the tables |
| `research/mcp-inventory.md` | The 81 MCP tools: their routes, gates and sources, collected from the code |

Screenshots come from the main repository's `console/scripts/shots/capture.mjs` (scenes marked `guide: true`).

## Deploy

Cloudflare Pages runs `scripts/pages-build.sh` (in the repository root) on every push.

- **Production (`main`) does not publish `/docs/` yet.** The guide is being rewritten into task pages, and the old
  layout is never published (ADR 0132, addendum). Until `scripts/docs-published` exists, `main` deploys `site/` alone.
  Adding that file is the switch the user flips when the pages are ready.
- **Once published**, `main` builds the agent-fleet release tag in `scripts/docs-ref.txt` (it refuses anything else)
  and leaves out the pilot pages. A new release's guide goes live by changing that file.
- **Every other branch is a preview** and always builds `/docs/`, with the pilot pages. To review pages that are not
  released, push a branch here whose `scripts/docs-ref.txt` names an agent-fleet branch (`main`, or a pull request's
  branch); its preview URL shows them.
- Each build checks the output for dead `/docs/` links (`scripts/check_dist.py`).

To reproduce a deploy locally, from the repository root: `CF_PAGES_BRANCH=main bash scripts/pages-build.sh`, or any
other branch name for a preview.

## Pilot pages

| Page | State |
|---|---|
| `user/start/overview`, `quickstart`, `concepts` | First draft. Written before the page model existed, so they still need a rework |
| `user/integrations/aws-sso` | Agreed model. Fact-checked by another model (17 statements: 0 wrong, 5 misleading, fixed). The role-assumption section was added afterwards and is not yet checked |
| `user/security/credentials` | AWS section only |
| `ref/cli/README`, `ref/cli/af-aws-exec` | From `--help`. Not yet fact-checked |
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
