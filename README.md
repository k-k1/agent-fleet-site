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
| `site/index.html`, `site/ja/index.html` | The landing page. One stylesheet; the only script is `assets/lightbox.js`, and the page works without it. |
| `site/features/index.html`, `site/ja/features/index.html` | Features: walkthroughs, then a catalogue whose every card links into the user guide. |
| `site/assets/img/` | Console screenshots and demo recordings, copied from a release (below) |
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
[k-k1/agent-fleet-dist](https://github.com/k-k1/agent-fleet-dist) at release time. The demo
recordings (`demo-*.webp`, animated) are left out of the distribution repository for size, so
the script takes them from the main repository at the same release tag. After a release:

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
   For `.jp` Cloudflare warns that the TLD is not supported — that is about moving the
   *registration* to Cloudflare Registrar; choose to add the site anyway. The import probes
   common names, and the parking DNS answers most of them, so each zone arrives with dozens of
   junk `A`, `TXT` and `NS` records. Delete all of them except the ones kept below:

   | Zone | Keep | Add (proxied) |
   |---|---|---|
   | `agent-fleet.org` | nothing | `AAAA www 100::` |
   | `agent-fleet.jp` | TXT `v=spf1 -all` on the apex only | `AAAA @ 100::`, `AAAA www 100::` |

   In the add form the apex is `@`; an emptied name field is rejected, and a stray
   `@.agent-fleet.jp` means the record went to a subdomain named `@`.

   `100::` is Cloudflare's placeholder for a redirect-only hostname: the record has to exist and
   be proxied for a redirect rule to fire, and no request ever reaches the address. The null MX
   on `.org` must go because Email Routing adds its own MX and SPF, and a null MX says the
   domain takes no mail. `.jp` takes none, and its apex SPF `-all` says it sends none either.
2. **Name servers.** At お名前.com, point each domain at the two name servers Cloudflare
   assigned. DNSSEC must be off at お名前.com before this (a DS record left behind breaks
   resolution); neither domain has one today. Wait for Cloudflare to report both zones Active.
3. **Pages.** Workers & Pages → Create application → Pages → Connect to Git → this
   repository. Production branch `main`, framework preset *None*, build command empty, build
   output directory `site`. The *Create application* page opens on Workers; Pages is the small
   link at its foot. If connecting GitHub fails with "could not be installed" although
   <https://github.com/settings/installations> lists *Cloudflare Workers and Pages*, open that
   installation in the popup, change *Repository access* (only `agent-fleet-site`) and *Save*:
   the save sends the callback Cloudflare missed. Then Custom domains → add `agent-fleet.org`;
   Cloudflare creates the apex record itself. Do not create that record by hand first — a record the Pages project
   does not know about answers 522. Every pull request gets a preview URL, and `_headers`
   keeps the `*.pages.dev` alias out of search results.
4. **Redirects.** Rules → Overview → *Rule templates* (the dashboard has no separate Redirect
   Rules menu any more). All three are status 301 with *Preserve query string* on:

   | Zone | Template | Settings |
   |---|---|---|
   | `agent-fleet.org` | *Redirect from HTTP to HTTPS* | as offered |
   | `agent-fleet.org` | *Redirect from WWW to root* | wildcard `https://www.*` → `https://${1}` |
   | `agent-fleet.jp` | *Redirect to a different domain* | custom filter `(http.host eq "agent-fleet.jp") or (http.host eq "www.agent-fleet.jp")` → dynamic `concat("https://agent-fleet.org/ja", http.request.uri.path)` |

   The www-to-root rule only matches `https`, which is why the HTTP-to-HTTPS rule is needed:
   `http://www.agent-fleet.org/` takes two hops. Deploying a rule for `www` or `.jp` warns that
   the hostname may not be proxied — the check does not recognise the `100::` placeholder;
   deploy anyway, and do not let it create another record.

   Also turn **off** Security → Settings → *Email Address Obfuscation*: it is on for a new zone,
   rewrites the footer's `mailto:` into a `/cdn-cgi/` link and injects a decoder script, so
   the served HTML no longer matches this repository and readers without JavaScript see
   "[email protected]" instead of the security contact.
5. **Mail.** On `agent-fleet.org`: the zone's *Email* menu → Email Routing. Add the
   maintainer's address under *Destination addresses* and verify it from the message Cloudflare
   sends, then a routing rule `security@agent-fleet.org` → that destination, and accept the MX /
   SPF / DKIM records it offers; leave the catch-all disabled. Send a test message from another
   provider before anything points at the address — the main repository's `SECURITY.md`, the
   page footer and `security.txt` all do. Routing only receives: a reply goes out from the
   destination mailbox, under that address.
6. **Analytics.** Pages project → Metrics → Web Analytics (on). The beacon is written into the
   pages at deploy time, so switching it on takes effect with the next deployment, not at once.
   It uses no cookies or other client-side state. The injected beacon loads from
   `static.cloudflareinsights.com` and reports to `cloudflareinsights.com/cdn-cgi/rum`; the CSP
   in `_headers` allows exactly those two hosts, so trimming either breaks it silently. Ad blockers
   stop it, so read its numbers as a floor; the zone's own Analytics counts every request,
   bots included. Nothing else is loaded from a third party.

### After switching DNS

```bash
curl -sI https://agent-fleet.org/ | head -1                           # 200
curl -sI http://agent-fleet.org/ | grep -i '^location'                # https://agent-fleet.org/
curl -sI https://www.agent-fleet.org/ja/ | grep -i '^location'        # https://agent-fleet.org/ja/
curl -sI http://www.agent-fleet.jp/ | grep -i '^location'             # https://agent-fleet.org/ja/
curl -sI https://agent-fleet.jp/ | grep -iE '^(HTTP|location)'        # 301, https://agent-fleet.org/ja/
curl -s https://agent-fleet.org/.well-known/security.txt | head -1    # Contact: mailto:…
curl -sI https://agent-fleet.org/ | grep -i content-security-policy   # _headers applied
curl -s https://agent-fleet.org/ | cmp - site/index.html             # served as committed (not once Web Analytics injects its beacon)
```

## License

[Apache License 2.0](LICENSE), like the main repository.
