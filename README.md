# agent-fleet.org

The landing page of [Agent Fleet](https://github.com/k-k1/agent-fleet): English at
`https://agent-fleet.org/`, Japanese at `https://agent-fleet.org/ja/`. `agent-fleet.jp`
answers with a 301 to the Japanese page.

It is a separate repository so that the main repository's docs checks, forbidden-token scan
and release gates do not apply to marketing copy — which also means nothing here checks the
copy for you. The rules below are the whole safety net.

## Layout

| Path | What |
|---|---|
| `site/` | Everything that is served, as is. No build step. |
| `site/index.html`, `site/ja/index.html` | The two pages. One stylesheet; the only script is `assets/lightbox.js`, and the page works without it. |
| `site/assets/img/` | Console screenshots, copied from a release of the distribution repository |
| `site/assets/brand/` | Icons and the banner, from the main repository's `console/public/brand/` |
| `site/og-*.png` | Social preview cards (generated) |
| `site/_headers` | Response headers for Cloudflare Pages (CSP, HSTS, caching) |
| `site/.well-known/security.txt` | RFC 9116 contact file |
| `scripts/` | Sync, render and check tools (below) |

## Editing the copy

- **Change both languages in the same commit.** English is the source; the Japanese page uses
  the main repository's own terms (README.ja.md and the Console's Japanese UI).
- **Every claim has to be true of a released version.** The wording comes from the main
  repository's README and `guide/`; do not describe something that has not shipped.
- A link into the main repository points at `develop`; a heading anchor is checked against
  what GitHub actually renders (`scripts/check.py --online`).

## Updating the screenshots

The screenshots are rendered in the main repository (`console/scripts/shots`) and seeded into
[k-k1/agent-fleet-dist](https://github.com/k-k1/agent-fleet-dist) at release time. After a
release:

```bash
scripts/sync-shots.sh            # latest release; or: scripts/sync-shots.sh v0.24.0
scripts/render-og.py             # the social cards show the console screenshot
scripts/check.py --online
```

`scripts/shots-ref.txt` records the release the screenshots came from. If a scene's image size
changes, the page's `width` / `height` attributes must follow; `scripts/check.py` fails until
they do.

## Previewing and checking

```bash
python3 -m http.server --directory site --bind 127.0.0.1 8000   # then open http://127.0.0.1:8000/
scripts/check.py                 # local links, anchors, image sizes, hreflang, sitemap, security.txt
scripts/check.py --online        # plus every external link and GitHub heading anchor
```

The local server does not apply `_headers`. CI runs the offline check on every push and pull
request, and the online check weekly — the weekly run is also what notices `security.txt`
expiring (it fails 30 days ahead; move `Expires` forward, at most a year).

## Hosting (Cloudflare)

Both domains are registered at お名前.com (Onamae.com); DNS, hosting, redirects, mail
forwarding and analytics are on Cloudflare's free plan.

**Pages project**: connect this repository, production branch `main`, framework preset
*None*, build command empty, build output directory `site`. Custom domains:
`agent-fleet.org` and `www.agent-fleet.org`. Every pull request gets a preview URL, and
`_headers` keeps the `*.pages.dev` alias out of search results.

**DNS**: add `agent-fleet.org` and `agent-fleet.jp` as zones, then change each domain's name
servers at お名前.com to the pair Cloudflare assigns. While the zone is imported, on
`agent-fleet.org` delete the parking records and the null MX (`MX 0 .`) and `v=spf1 -all`
TXT — Email Routing brings its own MX and SPF, and the null MX would reject mail. Keep the
null MX and `-all` on `agent-fleet.jp`, which receives no mail.

**Redirects** (Rules → Redirect Rules, one *single redirect* each, status 301, preserve query
string):

| Zone | When hostname is | Target (dynamic) |
|---|---|---|
| `agent-fleet.org` | `www.agent-fleet.org` | `concat("https://agent-fleet.org", http.request.uri.path)` |
| `agent-fleet.jp` | `agent-fleet.jp` or `www.agent-fleet.jp` | `concat("https://agent-fleet.org/ja", http.request.uri.path)` |

A redirect only fires on a proxied hostname, so `agent-fleet.jp` needs proxied placeholder
records: `AAAA @ 100::` and `AAAA www 100::`, both proxied.

**Mail**: Email Routing on `agent-fleet.org`, a custom address `security@agent-fleet.org`
forwarding to the maintainer's verified address. Send a test message before anything points at
it — the main repository's `SECURITY.md`, the page footer and `security.txt` all do.

**Analytics** (optional): Pages project → Metrics → Web Analytics. It sets no cookies; its
beacon's two hosts are already allowed by the CSP in `_headers`. Nothing else is loaded from a
third party.

### After switching DNS

```bash
curl -sI https://agent-fleet.org/ | head -1                           # 200
curl -sI https://www.agent-fleet.org/ja/ | grep -i '^location'        # https://agent-fleet.org/ja/
curl -sI https://agent-fleet.jp/ | grep -iE '^(HTTP|location)'        # 301, https://agent-fleet.org/ja/
curl -s https://agent-fleet.org/.well-known/security.txt | head -1    # Contact: mailto:…
curl -sI https://agent-fleet.org/ | grep -i content-security-policy   # _headers applied
```

## License

[Apache License 2.0](LICENSE), like the main repository.
