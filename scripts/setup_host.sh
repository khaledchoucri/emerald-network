#!/usr/bin/env bash
# Builds our patched Emerald host (pokeemerald-pc_port + poc/patches/*.patch).
# Run inside WSL from the project folder:
#   bash scripts/setup_host.sh            # Linux build (needs WSLg to show a window) - shows [pkbn] logs
#   bash scripts/setup_host.sh windows    # Windows .exe (copied to poc/bin/)
# The host source lives on the WSL filesystem (default ~/pkbn/emerald-host): building on /mnt/c is very slow.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST_DIR="${PKBN_HOST_DIR:-$HOME/pkbn/emerald-host}"
UPSTREAM_URL="https://github.com/Kurausukun/pokeemerald.git"
PIN="116582559947f4c9fbd5cdfd601f258b553661d5"   # pc_port, see README "Pinned upstream commits"
TARGET="${1:-linux}"
JOBS="$(nproc)"

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing '$1'. $2"; exit 1; }; }
need git  "sudo apt install git"
need make "sudo apt install build-essential"
need gcc  "sudo apt install build-essential"
need pkg-config "sudo apt install pkg-config"
need python3 "sudo apt install python3"
pkg-config --exists libpng || { echo "Missing libpng. sudo apt install libpng-dev"; exit 1; }
case "$TARGET" in
  linux)   pkg-config --exists sdl2 || { echo "Missing SDL2. sudo apt install libsdl2-dev"; exit 1; } ;;
  windows) need x86_64-w64-mingw32-gcc "sudo apt install g++-mingw-w64-x86-64"; need curl "sudo apt install curl"; need unzip "sudo apt install unzip" ;;
  *) echo "Usage: $0 [linux|windows]"; exit 1 ;;
esac

# 1. Fetch the pinned upstream commit (once)
if [ ! -d "$HOST_DIR/.git" ]; then
  echo "==> Fetching pc_port @ ${PIN:0:7} into $HOST_DIR"
  mkdir -p "$HOST_DIR"
  git -C "$HOST_DIR" init -q
  git -C "$HOST_DIR" remote add origin "$UPSTREAM_URL"
  git -C "$HOST_DIR" fetch -q --depth 1 origin "$PIN"
fi
cd "$HOST_DIR"

# 2. Reset to the pin and apply our patches (refuses to discard local edits)
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "Host has uncommitted edits in $HOST_DIR - commit or stash them first."; exit 1
fi
git checkout -q -B pkbn "$PIN"
for p in "$PROJECT_DIR"/poc/patches/*.patch; do
  echo "==> Applying $(basename "$p")"
  git -c user.name=pkbn -c user.email=pkbn@localhost am -q "$p"
done

# 3. BN6 battle effect sprites: extracted from upstream/bn6f into the host on every build.
#    They are never committed (CLAUDE.md rule 6); include/pkbn/bn6_gfx_data.h is gitignored by our patches.
echo "==> Extracting BN6 effect sprites from upstream/bn6f"
python3 "$PROJECT_DIR/tools/gen_bn6_gfx.py" "$PROJECT_DIR/upstream/bn6f" "$HOST_DIR/include/pkbn/bn6_gfx_data.h"
python3 "$PROJECT_DIR/tools/gen_bn6_results.py" "$PROJECT_DIR/upstream/bn6f" "$HOST_DIR/include/pkbn/bn6_results_data.h"   # POC-19: BN6's results window

# 4. Build
# Linux and Windows builds share build/pc64, so objects from one can't be linked into the other (mingw then fails
# with "undefined reference to `stderr'"). Switching target clears them; the converted graphics in build/assets stay.
STAMP="$HOST_DIR/.pkbn_build_target"
if [ "$(cat "$STAMP" 2>/dev/null || echo none)" != "$TARGET" ] && [ -d build/pc64 ]; then
  echo "==> Target changed to $TARGET: clearing build/pc64"
  rm -rf build/pc64
fi
echo "$TARGET" > "$STAMP"
if [ "$TARGET" = linux ]; then
  echo "==> Building Linux binary (-j$JOBS)"
  make linux -j"$JOBS"
  echo
  echo "Done: $HOST_DIR/pokeemerald64"
  echo "Run:  cd $HOST_DIR && ./pokeemerald64      (PKBN_STUB=0 ./pokeemerald64 for vanilla battles)"
else
  if [ ! -d SDL2 ]; then
    # POC-18: SDL 2.0.22 from SDL's own GitHub releases (archive.org's 2.0.16 copy isn't always reachable). Same API.
    echo "==> Downloading SDL2 2.0.22 mingw dev libs"
    curl -fL -o /tmp/sdl2-mingw.tar.gz https://github.com/libsdl-org/SDL/releases/download/release-2.0.22/SDL2-devel-2.0.22-mingw.tar.gz
    tar -xzf /tmp/sdl2-mingw.tar.gz && mv SDL2-2.0.22 SDL2
  fi
  echo "==> Building Windows .exe (-j$JOBS)"
  make winwsl -j"$JOBS"
  OUT="$PROJECT_DIR/poc/bin"
  mkdir -p "$OUT"
  cp pokeemerald64.exe "$OUT/"
  cp SDL2/x86_64-w64-mingw32/bin/SDL2.dll "$OUT/"
  echo
  echo "Done: $OUT/pokeemerald64.exe (saves and pkbn_log.txt are written next to it)"
fi
