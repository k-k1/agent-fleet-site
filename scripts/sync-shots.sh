#!/usr/bin/env bash
# Copy the Console screenshots and demo recordings into site/assets/img/ from a release,
# so the pages only ever show screens that have shipped.
#
#   scripts/sync-shots.sh            # the latest release
#   scripts/sync-shots.sh v0.24.0    # a given tag
#
# The images are generated in the main repository (console/scripts/shots). The stills are
# seeded into k-k1/agent-fleet-dist at release time; the demo recordings are not (the
# distribution repository leaves demo-* out for size), so they come from the main
# repository at the same release tag — both repositories tag every release alike. This
# script does not render anything itself. The ref it copied from is recorded in
# scripts/shots-ref.txt.
set -euo pipefail

DIST=k-k1/agent-fleet-dist
MAIN=k-k1/agent-fleet
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/site/assets/img"

ref="${1:-}"
if [ -z "$ref" ]; then
  # No token needed: both repositories are public.
  ref="$(curl -fsSL --retry 4 --retry-all-errors "https://api.github.com/repos/$DIST/releases/latest" \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["tag_name"])')"
fi

scenes=(console overview fleetgraph mirror usage launch split scm terminal files workitems imagegen)
demos=(orchestrate sre plan phone)

fetch() { # repo, file
  curl -fsSL --retry 4 --retry-all-errors -o "$OUT/$2.tmp" "https://raw.githubusercontent.com/$1/$ref/docs/img/$2"
  mv "$OUT/$2.tmp" "$OUT/$2"
}

mkdir -p "$OUT"
for lang in en ja; do
  for s in "${scenes[@]}"; do fetch "$DIST" "$s-$lang.webp"; done
  for d in "${demos[@]}"; do fetch "$MAIN" "demo-$d-$lang.webp"; done
done

printf '%s\n' "$ref" > "$ROOT/scripts/shots-ref.txt"
echo "synced ${#scenes[@]} scenes from $DIST@$ref and ${#demos[@]} demos from $MAIN@$ref, x 2 languages"
