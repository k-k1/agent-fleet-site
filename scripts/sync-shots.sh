#!/usr/bin/env bash
# Copy the Console screenshots into site/assets/img/ from a release of the
# distribution repository, so the page only ever shows screens that have shipped.
#
#   scripts/sync-shots.sh            # the latest release
#   scripts/sync-shots.sh v0.24.0    # a given tag
#
# The screenshots are generated in the main repository (console/scripts/shots) and
# seeded into k-k1/agent-fleet-dist at release time; this script does not render
# anything itself. The ref it copied from is recorded in scripts/shots-ref.txt.
set -euo pipefail

DIST=k-k1/agent-fleet-dist
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/site/assets/img"

ref="${1:-}"
if [ -z "$ref" ]; then
  # No token needed: the distribution repository is public.
  ref="$(curl -fsSL --retry 4 --retry-all-errors "https://api.github.com/repos/$DIST/releases/latest" \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["tag_name"])')"
fi

scenes=(console overview fleetgraph mirror usage launch split scm terminal)

mkdir -p "$OUT"
for s in "${scenes[@]}"; do
  for lang in en ja; do
    f="$s-$lang.webp"
    curl -fsSL --retry 4 --retry-all-errors -o "$OUT/$f.tmp" "https://raw.githubusercontent.com/$DIST/$ref/docs/img/$f"
    mv "$OUT/$f.tmp" "$OUT/$f"
  done
done

printf '%s\n' "$ref" > "$ROOT/scripts/shots-ref.txt"
echo "synced ${#scenes[@]} scenes x 2 languages from $DIST@$ref"
