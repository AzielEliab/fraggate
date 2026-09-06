#!/usr/bin/env bash
# Pack the counted FragGate tarball (kernel + Worker + mobile). Excludes git and the tarball itself.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/workers/download-tracker/public"
NAME="fraggate-0.1.0"
mkdir -p "$DEST"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/$NAME"
rsync -a \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude 'node_modules' \
  --exclude '.wrangler' \
  --exclude '__pycache__' \
  --exclude '.pytest_cache' \
  --exclude '.fraggate' \
  --exclude 'workers/download-tracker/public/fraggate-0.1.0.tar.gz' \
  "$ROOT/" "$TMP/$NAME/"
tar -C "$TMP" -czf "$DEST/fraggate-0.1.0.tar.gz" "$NAME"
echo "Wrote $DEST/fraggate-0.1.0.tar.gz"
