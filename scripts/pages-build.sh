#!/usr/bin/env bash
# The Cloudflare Pages build: the static site in site/, plus the user guide built into /docs/.
#
#   Pages settings: build command `bash scripts/pages-build.sh`, build output directory `out`.
#
# Production (CF_PAGES_BRANCH=main) publishes /docs/ only once scripts/docs-published exists: the
# guide is being rewritten into task pages and the old layout is never published (ADR 0132, addendum).
# Until then main deploys site/ alone. When it does publish, it builds a release tag and leaves out the
# draft pages of docs/pilot/.
#
# Every other branch is a preview and always builds /docs/, with the pilot pages. A preview branch may
# set scripts/docs-ref.txt to a branch of agent-fleet (main, or a pull request's branch) to show pages
# that are not released yet; main refuses anything but a release tag.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/out"
TAG="$(tr -d '[:space:]' < "$ROOT/scripts/docs-ref.txt")"
REPO_URL="${AGENT_FLEET_REPO:-https://github.com/k-k1/agent-fleet.git}"

rm -rf "$OUT"
if [ "${CF_PAGES_BRANCH:-}" = main ]; then
  if [ ! -e "$ROOT/scripts/docs-published" ]; then
    cp -r "$ROOT/site" "$OUT"
    echo "==> out/: site/ only (/docs/ is not published yet: scripts/docs-published is absent)"
    exit 0
  fi
  case "$TAG" in
    v[0-9]*) ;;
    *) echo "ERROR: main publishes /docs/ from a release tag, not '$TAG' (scripts/docs-ref.txt)" >&2; exit 1 ;;
  esac
  export DOCS_PILOT=0
fi

SRC="$(mktemp -d)"
trap 'rm -rf "$SRC"' EXIT
git clone --quiet --depth 1 --branch "$TAG" "$REPO_URL" "$SRC/agent-fleet"

(cd "$ROOT/docs" && npm ci --no-audit --no-fund)
bash "$ROOT/docs/scripts/build.sh" "$SRC/agent-fleet" "$TAG"
python3 -I "$ROOT/docs/scripts/check_dist.py" "$ROOT/docs/dist"
# Search quality needs pages that a release may not have yet, so only builds that follow an agent-fleet branch run it.
case "$TAG" in v[0-9]*) ;; *) node "$ROOT/docs/scripts/search_quality.mjs" "$ROOT/docs/dist" ;; esac

cp -r "$ROOT/site" "$OUT"
cp -r "$ROOT/docs/dist" "$OUT/docs"
echo "==> out/: site/ + guide $TAG (pilot pages: ${DOCS_PILOT:-1})"
