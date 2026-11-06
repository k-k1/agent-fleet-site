#!/usr/bin/env bash
# Build the docs site from a release of the main repository, with the pilot pages laid over it.
#
#   docs/scripts/build.sh <agent-fleet checkout> <tag>     e.g. ~/repos/agent-fleet v0.41.0
#
# Always a tag, never main: main describes features that have not shipped (ADR 0131 §1).
# The input is stage-docs.sh's output, the same closed tree the Console's user guide ships.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${1:?usage: build.sh <agent-fleet checkout> <tag>}"
TAG="${2:?usage: build.sh <agent-fleet checkout> <tag>}"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
git -C "$REPO" archive "$TAG" guide deploy scripts | tar -C "$WORK" -xf -
mkdir -p "$WORK/src" && mv "$WORK/guide" "$WORK/deploy" "$WORK/scripts" "$WORK/src/"
bash "$WORK/src/deploy/release/stage-docs.sh" "$WORK/staged" >/dev/null

# Pilot pages: new paths are added, files that exist in the release are replaced.
cp -r "$HERE/pilot/." "$WORK/staged/"

python3 -I "$HERE/scripts/to_starlight.py" "$WORK/staged" "$HERE" "$TAG"
cd "$HERE"
NODE_OPTIONS="${NODE_OPTIONS:---max-old-space-size=2048}" npx astro build
