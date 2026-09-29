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
forwarding and analytics are on Cloudflare's free plan. In this order:

1. **Zones.** Add `agent-fleet.org` and `agent-fleet.jp` to the Cloudflare account (free plan).
   Cloudflare imports the existing records; fix them up before switching:

   | Zone | Delete | Add (proxied) | Keep |
   |---|---|---|---|
   | `agent-fleet.org` | parking `A @` and `A www`, null MX `MX 0 .`, TXT `v=spf1 -all` | `AAAA www 100::` | — |
   | `agent-fleet.jp` | parking `A @` and `A www` | `AAAA @ 100::`, `AAAA www 100::` | `MX 0 .`, TXT `v=spf1 -all` |

   `100::` is Cloudflare's placeholder for a redirect-only hostname: the record has to exist and
   be proxied for a redirect rule to fire, and no request ever reaches the address. The null MX
   on `.org` must go because Email Routing adds its own MX and SPF, and a null MX says the
   domain takes no mail; `.jp` takes none, so it keeps them.
2. **Name servers.** At お名前.com, point each domain at the two name servers Cloudflare
   assigned. DNSSEC must be off at お名前.com before this (a DS record left behind breaks
   resolution); neither domain has one today. Wait for Cloudflare to report both zones Active.
3. **Pages.** Workers & Pages → Create application → Pages → Connect to Git → this
   repository. Production branch `main`, framework preset *None*, build command empty, build
   output directory `site`. Then Custom domains → add `agent-fleet.org`; Cloudflare creates the
   apex record itself. Do not create that record by hand first — a record the Pages project
   does not know about answers 522. Every pull request gets a preview URL, and `_headers`
   keeps the `*.pages.dev` alias out of search results.
4. **Redirects.** Rules → Redirect Rules → a single redirect per row, *Wildcard pattern*,
   status 301, *Preserve query string* on:

   | Zone | Request URL | Target URL |
   |---|---|---|
   | `agent-fleet.org` | `http*://www.agent-fleet.org/*` | `https://agent-fleet.org/${2}` |
   | `agent-fleet.jp` | `http*://agent-fleet.jp/*` | `https://agent-fleet.org/ja/${2}` |
   | `agent-fleet.jp` | `http*://www.agent-fleet.jp/*` | `https://agent-fleet.org/ja/${2}` |

   Also turn on SSL/TLS → Edge Certificates → *Always Use HTTPS* for `agent-fleet.org`.
5. **Mail.** On `agent-fleet.org`: Compute → Email Service → Email Routing. Add the
   maintainer's address as a destination and verify it from the message Cloudflare sends,
   then a routing rule `security@` → that destination; accept the MX / SPF / DKIM records it
   offers. Send a test message before anything points at the address — the main repository's
   `SECURITY.md`, the page footer and `security.txt` all do. Routing only receives: a reply
   goes out from the destination mailbox, under that address.
6. **Analytics** (optional). Pages project → Metrics → Web Analytics. It sets no cookies; its
   beacon's two hosts are already allowed by the CSP in `_headers`. Nothing else is loaded from
   a third party.

### After switching DNS

```bash
curl -sI https://agent-fleet.org/ | head -1                           # 200
curl -sI http://agent-fleet.org/ | grep -i '^location'                # https://agent-fleet.org/
curl -sI https://www.agent-fleet.org/ja/ | grep -i '^location'        # https://agent-fleet.org/ja/
curl -sI https://agent-fleet.jp/ | grep -iE '^(HTTP|location)'        # 301, https://agent-fleet.org/ja/
curl -s https://agent-fleet.org/.well-known/security.txt | head -1    # Contact: mailto:…
curl -sI https://agent-fleet.org/ | grep -i content-security-policy   # _headers applied
```

## License

[Apache License 2.0](LICENSE), like the main repository.
