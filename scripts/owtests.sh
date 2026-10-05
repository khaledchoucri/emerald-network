#!/usr/bin/env bash
# Overworld self-tests (POC-11): run from the host build folder (where pokeemerald64 is).
#   bash /path/to/scripts/owtests.sh [outdir]
# Each test starts in a map with a party, plays a key script (src/pkbn/owtest.c documents the syntax),
# dumps frames to OUT/<test>/ow_*.ppm and checks the log for the line that proves the hook ran.
set -u
OUT=${1:-/tmp/pkbn-owtests}
mkdir -p "$OUT"
PARTY="281:20:52/24/64/116|309:8:45/55"     # Combusken L20 (Ember/Double Kick/Peck/Focus Energy), Wingull L8
run() {   # name map keys expect [extra env...]
  local name=$1 map=$2 keys=$3 expect=$4; shift 4
  rm -rf "$OUT/$name"; mkdir -p "$OUT/$name"
  env "$@" PKBN_OWTEST="$map" PKBN_OWTEST_PARTY="${OWPARTY:-$PARTY}" PKBN_OWKEYS="$keys" PKBN_DUMP_DIR="$OUT/$name" \
      PKBN_PLAYLOG="$OUT/$name/playlog.jsonl" SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy timeout 300 ./pokeemerald64 \
      > "$OUT/$name/log.txt" 2>&1
  if grep -aq "$expect" "$OUT/$name/log.txt"; then echo "PASS $name"; else echo "FAIL $name (no '$expect')"; fi
  rm -f pkbn.sav
}
# START menu -> FOLDER (Oldale Town), pages, back to the field
run start_folder 0:10:10:10 "W240,S,W30,D,W15,D,W15,A,W90,P,>,W20,P,B,W90,P,W10,Q" "done at frame"
# party menu -> NAVICUST
run party_navicust 0:10:10:10 "W240,S,W30,D,A,W90,A,W60,D,W30,A,W90,P,B,W120,P,W10,Q" "done at frame"
# Poke Mart -> CHIPS shelf, buy the first chip (Oldale Mart, facing the clerk)
run mart_chips 2:4:2:3 "W200,L,W30,A,W90,A,W260,D,W15,D,W20,A,W120,P,A,W30,P,B,W200,P,W10,Q" "done at frame" PKBN_OWTEST_MONEY=5000
# wild battle from the field (autopilot fights, post-battle text mashed), back to the field, play log written
run wild_battle 0:16:10:10 "W200,G288:4,W60,P,W400,M1500,W60,P,W10,Q" "returning to overworld" PKBN_OW_AUTOBATTLE=1
# a wild pack (POC-11): 3 Pokémon from Route 101's own grass table, fought down one by one
run wild_pack 0:16:10:10 "W200,J,G288:4,W60,P,W200,P,W400,M2500,W60,P,W10,Q" "down, 0 left" PKBN_OW_AUTOBATTLE=1 PKBN_TEST_PACK_EXTRA=2
# a TM given by a script (additem) becomes 2 chips
run tm_script 0:10:10:10 "W200,T323,W60,Q" "chip grant: TM/HM item 323"
# the Move Relearner (Heart Scale) gives a chip in a new code (Wingull relearns Supersonic)
OWPARTY="309:8:45/55|281:20:52/24/64/116" run relearner 5:7:4:5 "W200,U,W20,A,M2500,W10,Q" "chip grant: relearned" PKBN_OWTEST_ITEMS=111:1
