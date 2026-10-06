#!/usr/bin/env bash
# POC-18: the playtest zip for friends (Windows .exe + SDL2.dll + How to Play). Run inside WSL from the project folder:
#   bash scripts/package_playtest.sh
# Output: poc/bin/pkbn-playtest-<version>.zip
#
# The zip contains the built game, so it holds Emerald's and BN6's graphics and music. Sending it to playtesters was
# Khaled's call (POC-18 picks, "Getting it to friends": change rule 6 to allow private playtest builds). It is never
# committed: poc/bin/ is in .gitignore. Share it privately with your testers only.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST_DIR="${PKBN_HOST_DIR:-$HOME/pkbn/emerald-host}"
OUT="$PROJECT_DIR/poc/bin"

command -v zip >/dev/null 2>&1 || { echo "Missing 'zip'. sudo apt install zip"; exit 1; }

bash "$PROJECT_DIR/scripts/setup_host.sh" windows

VERSION="$(sed -n 's/^#define PKBN_VERSION "\(.*\)"/\1/p' "$HOST_DIR/include/pkbn/version.h")"
STAGE="$(mktemp -d)"
DIR="$STAGE/pkbn-playtest-$VERSION"
mkdir -p "$DIR"
cp "$OUT/pokeemerald64.exe" "$OUT/SDL2.dll" "$DIR/"
cp "$PROJECT_DIR/docs/HOW_TO_PLAY.html" "$DIR/"
ZIP="$OUT/pkbn-playtest-$VERSION.zip"
rm -f "$ZIP"
(cd "$STAGE" && zip -qr "$ZIP" "pkbn-playtest-$VERSION")
rm -rf "$STAGE"
echo
echo "Done: $ZIP"
echo "Contents: pokeemerald64.exe, SDL2.dll, HOW_TO_PLAY.html (no saves, logs or replays)"
