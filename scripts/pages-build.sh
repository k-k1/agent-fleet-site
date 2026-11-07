#!/usr/bin/env bash
# The Cloudflare Pages build: the static site in site/, plus the user guide built into /docs/.
#
#   Pages settings: build command `bash scripts/pages-build.sh`, build output directory `out`.
#
# The guide is built from the agent-fleet release named in scripts/docs-ref.txt, never from main
# (ADR 0131 §1): main describes features that have not shipped. Bumping that file is how a new
# release's guide goes live.
#
# Production (CF_PAGES_BRANCH=main) publishes the release's guide alone. Every other branch is a
# preview and lays the draft pages of docs/pilot/ over it, so they can be reviewed on the preview
# URL without being published.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/out"
TAG="$(tr -d '[:space:]' < "$ROOT/scripts/docs-ref.txt")"
REPO_URL="${AGENT_FLEET_REPO:-https://github.com/k-k1/agent-fleet.git}"

if [ "${CF_PAGES_BRANCH:-}" = main ]; then
  export DOCS_PILOT=0
fi

SRC="$(mktemp -d)"
trap 'rm -rf "$SRC"' EXIT
git clone --quiet --depth 1 --branch "$TAG" "$REPO_URL" "$SRC/agent-fleet"

(cd "$ROOT/docs" && npm ci --no-audit --no-fund)
bash "$ROOT/docs/scripts/build.sh" "$SRC/agent-fleet" "$TAG"
python3 -I "$ROOT/docs/scripts/check_dist.py" "$ROOT/docs/dist"

rm -rf "$OUT"
cp -r "$ROOT/site" "$OUT"
cp -r "$ROOT/docs/dist" "$OUT/docs"
echo "==> out/: site/ + guide $TAG (pilot pages: ${DOCS_PILOT:-1})"
