#!/usr/bin/env bash
# Builds our patched Emerald host (pokeemerald-pc_port + poc/patches/*.patch).
# Run inside WSL from the project folder:
#   bash scripts/setup_host.sh            # Linux build (needs WSLg to show a window) - shows [pkbn] logs
#   bash scripts/setup_host.sh windows    # Windows .exe (copied to poc/bin/)
#   bash scripts/setup_host.sh web        # POC-23: the browser build (copied to poc/bin/web/; needs Emscripten)
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
python3 -c "import numpy, PIL" 2>/dev/null || { echo "Missing numpy / Pillow (POC-24 art packing). sudo apt install python3-numpy python3-pil"; exit 1; }
pkg-config --exists libpng || { echo "Missing libpng. sudo apt install libpng-dev"; exit 1; }
case "$TARGET" in
  linux)   pkg-config --exists sdl2 || { echo "Missing SDL2. sudo apt install libsdl2-dev"; exit 1; } ;;
  web)     pkg-config --exists sdl2 || { echo "Missing SDL2. sudo apt install libsdl2-dev"; exit 1; }
           need emcc "Install Emscripten 3.1.6 (the tested version): git clone https://github.com/emscripten-core/emsdk ~/emsdk && ~/emsdk/emsdk install 3.1.6 && ~/emsdk/emsdk activate 3.1.6, then: source ~/emsdk/emsdk_env.sh"
           need as "sudo apt install binutils"
           python3 -c "import elftools" 2>/dev/null || { echo "Missing pyelftools. sudo apt install python3-pyelftools"; exit 1; } ;;
  windows) need x86_64-w64-mingw32-gcc "sudo apt install g++-mingw-w64-x86-64"; need curl "sudo apt install curl"; need unzip "sudo apt install unzip" ;;
  *) echo "Usage: $0 [linux|windows|web]"; exit 1 ;;
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
# (a patch run that stopped half way is undone first, so the script can simply be run again)
if [ -d .git/rebase-apply ]; then
  echo "==> Undoing an unfinished patch run"
  git am --abort
fi
# Files the game writes when the Linux build is played here. Patch 0039 (POC-14g) committed a play log by mistake (0070
# removes it again), so an untracked one would stop the patches: it's kept aside, with the time, rather than lost.
for f in pkbn_playlog.jsonl; do
  if [ -f "$f" ] && ! git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    echo "==> Keeping your $f aside as $f.$(date +%Y%m%d-%H%M%S)"
    mv "$f" "$f.$(date +%Y%m%d-%H%M%S)"
  fi
done
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

# 3b. POC-24: our own hi-bit battle art (poc/assets/generated), packed for the build (not committed in the host either)
echo "==> Packing the hi-bit art (panels, fire)"
python3 "$PROJECT_DIR/tools/pack_hibit.py" "$PROJECT_DIR" "$HOST_DIR/include/pkbn/hibit_gfx_data.h"

# 3c. POC-25: animated Pokémon from the player's own Black 2 / White 2, when PKBN_SPRITE_ROM points at its .nds.
#     xBRZ (the 2x upscaler) is fetched and compiled once into ~/pkbn/xbrz; it's a build tool and is never shipped.
#     The result, pkbn_b2_sprites.bin, holds Nintendo's sprites: it is never committed (CLAUDE.md rule 6).
SPRITES=""
if [ -n "${PKBN_SPRITE_ROM:-}" ]; then
  [ -f "$PKBN_SPRITE_ROM" ] || { echo "PKBN_SPRITE_ROM: no file at $PKBN_SPRITE_ROM"; exit 1; }
  XBRZ_DIR="${PKBN_XBRZ_DIR:-$HOME/pkbn/xbrz}"
  XBRZ_PIN="0352a872e6ef48997d758b20b8a180e6fb3114ae"   # github.com/ioistired/xbrz.py (xBRZ by Zenju, AGPL-3.0)
  if [ ! -f "$XBRZ_DIR/libxbrz.so" ]; then
    need g++ "sudo apt install g++"
    echo "==> Building xBRZ into $XBRZ_DIR"
    rm -rf "$XBRZ_DIR/src"; mkdir -p "$XBRZ_DIR"
    git clone -q https://github.com/ioistired/xbrz.py "$XBRZ_DIR/src"
    git -C "$XBRZ_DIR/src" checkout -q "$XBRZ_PIN"
    # (its Python module glue isn't needed: xbrz_scale_defaults is plain C)
    sed '/#include "dummy_module.cpp"/d' "$XBRZ_DIR/src/lib/xbrz.cpp" > "$XBRZ_DIR/src/lib/xbrz_plain.cpp"
    g++ -O2 -std=c++17 -shared -fPIC "$XBRZ_DIR/src/lib/xbrz_plain.cpp" -o "$XBRZ_DIR/libxbrz.so"
  fi
  echo "==> Importing the animated Pokémon sprites from $PKBN_SPRITE_ROM"
  SPRITES="$HOST_DIR/pkbn_b2_sprites.bin"
  python3 "$PROJECT_DIR/tools/import_b2_sprites.py" "$PKBN_SPRITE_ROM" "$SPRITES" --xbrz "$XBRZ_DIR/libxbrz.so"
else
  echo "==> No PKBN_SPRITE_ROM: Pokémon keep Emerald's pictures (POC-25 explains the animated ones)"
fi

# 4. Build
# Linux and Windows builds share build/pc64, so objects from one can't be linked into the other (mingw then fails
# with "undefined reference to `stderr'"). Switching target clears them; the converted graphics in build/assets stay.
STAMP="$HOST_DIR/.pkbn_build_target"
PC_TARGET="$TARGET"; [ "$TARGET" = web ] && PC_TARGET=linux   # the web build needs the Linux build's tools and assets
if [ "$(cat "$STAMP" 2>/dev/null || echo none)" != "$PC_TARGET" ] && [ -d build/pc64 ]; then
  echo "==> Target changed to $PC_TARGET: clearing build/pc64"
  rm -rf build/pc64
fi
echo "$PC_TARGET" > "$STAMP"
if [ "$TARGET" = web ]; then
  echo "==> Building the Linux binary first: its tools and converted assets (-j$JOBS)"
  make linux -j"$JOBS"
  echo "==> Building the browser version (-j$JOBS)"
  make -f web.mk -j"$JOBS"
  OUT="$PROJECT_DIR/poc/bin/web"
  rm -rf "$OUT"; mkdir -p "$OUT"
  cp build/web/dist/index.html build/web/dist/pokeemerald.js build/web/dist/pokeemerald.wasm "$OUT/"
  [ -n "$SPRITES" ] && cp "$SPRITES" "$OUT/"   # POC-25: the page loads it if it's there
  echo
  echo "Done: $OUT (index.html, pokeemerald.js, pokeemerald.wasm)"
  echo "Try it: cd $OUT && python3 -m http.server 8000   then open http://localhost:8000"
  echo "It holds the built game: host it only where your testers alone can reach it (docs: poc/POC-23.md)."
elif [ "$TARGET" = linux ]; then
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
  [ -n "$SPRITES" ] && cp "$SPRITES" "$OUT/"   # POC-25: read from next to the .exe
  cp SDL2/x86_64-w64-mingw32/bin/SDL2.dll "$OUT/"
  echo
  echo "Done: $OUT/pokeemerald64.exe (saves and pkbn_log.txt are written next to it)"
fi
