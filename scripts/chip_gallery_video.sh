#!/usr/bin/env bash
# Records every chip's animation to a video (POC-15 chip gallery). Run it from the host build folder (where
# pokeemerald64 is); needs ffmpeg. Each move is played on the same stage - Mew Lv50 at (1,1), Snorlax Lv100 at (4,1) -
# at the game's own speed (60 fps), with a caption: number, move, kind, type.
#   bash scripts/chip_gallery_video.sh [out.mp4] [moves: all | 52,85,...] [side: player | enemy] [frames per move]
# Examples:
#   bash scripts/chip_gallery_video.sh                                   # all 312 chips, ~7 minutes
#   bash scripts/chip_gallery_video.sh fire.mp4 52,53,126,172,221,257    # just these move numbers
#   bash scripts/chip_gallery_video.sh enemy.mp4 all enemy               # the foe uses them on you (telegraphs)
set -eu
OUT=${1:-chip_gallery.mp4}
MOVES=${2:-all}
SIDE=${3:-player}
LEN=${4:-84}
BIN=${PKBN_BIN:-./pokeemerald64}
command -v ffmpeg > /dev/null || { echo "ffmpeg is needed (sudo apt install ffmpeg)"; exit 1; }
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
echo "playing the chips (frames go to $TMP) ..."
env PKBN_SELFTEST="151:50,143:100" PKBN_GALLERY="$MOVES" PKBN_GALLERY_SIDE="$SIDE" PKBN_GALLERY_FRAMES="$LEN" \
    PKBN_GALLERY_LABEL=1 PKBN_DUMP_DIR="$TMP" PKBN_DUMP_EVERY=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
    "$BIN" > "$TMP/log.txt" 2>&1 || true
grep -a "pkbn-gallery\] done" "$TMP/log.txt" || { echo "the gallery didn't finish - see $TMP/log.txt"; trap - EXIT; exit 1; }
echo "encoding $OUT ..."
ffmpeg -loglevel error -y -framerate 60 -pattern_type glob -i "$TMP/g_*.ppm" \
    -vf "scale=iw*3:ih*3:flags=neighbor,format=yuv420p" -c:v libx264 -preset veryfast -crf 20 "$OUT"
echo "done: $OUT"
