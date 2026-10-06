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
# releasing a Pokémon from the PC gives type candy (Oldale Pokémon Center PC, Withdraw, Release, Yes)
run release_candy 2:2:10:2 "W200,U,W20,A,Y,A,Y,A,W30,Y,A,Y,A,Y,A,W60,A,W300,D,W30,D,W30,D,W30,A,W90,U,W30,A,W200,P,W10,Q" \
    "candy grant: released species 288" PKBN_OWTEST_BOX=288:35
# a hatching egg brings its egg moves as chips (Mudkip egg knowing Stomp and Curse, one step in Oldale)
OWPARTY="281:20:52/24/64/116|e283:1:33/45/23/174" run egg_moves 0:10:10:10 "W200,H16R,W60,Y,A,W600,Y,A,W200,P,W10,Q" \
    "chip grant: egg move 23"

# Battle self-tests for catch bonuses (no map needed)
bt() {   # name spec expect [extra env...]
  local name=$1 spec=$2 expect=$3; shift 3
  rm -rf "$OUT/$name"; mkdir -p "$OUT/$name"
  env "$@" PKBN_SELFTEST="$spec" SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy timeout 300 ./pokeemerald64 > "$OUT/$name/log.txt" 2>&1
  if grep -aq "$expect" "$OUT/$name/log.txt"; then echo "PASS $name"; else echo "FAIL $name (no '$expect')"; fi
  rm -f pkbn.sav
}
# a 10th species caught gives a PP Up, a 50th a PP Max; a shiny gives * copies of its moves
bt milestone_10 "283:14:33/45,288:5:33/45" "10 SPECIES CAUGHT! GOT A PP UP" PKBN_TEST_DEX_CAUGHT=9 PKBN_TEST_BALLS=4:5 PKBN_TEST_THROW=5
bt milestone_50 "283:14:33/45,288:5:33/45" "50 SPECIES CAUGHT! GOT A PP MAX" PKBN_TEST_DEX_CAUGHT=49 PKBN_TEST_BALLS=4:5 PKBN_TEST_THROW=5
bt shiny_catch "283:14:33/45,288:5:33/45" "IT'S SHINY! GOT 2 \* CHIPS" PKBN_TEST_SHINY=1 PKBN_TEST_BALLS=4:5 PKBN_TEST_THROW=5
# the folder used up with nothing usable in hand -> a Struggle chip (status-only 18-chip folder vs Wailmer)
bt struggle "283:14:45/193/300/182,313:20:150" "folder used up: STRUGGLE chip" PKBN_TEST_PACK_LEARNED=1 \
    PKBN_TEST_PACK="45:A:5,193:A:5,300:A:5,182:A:5,156:A:5,104:A:5"
# POC-13: rain on the map is rain in battle (Route 120, field weather set to rain)
run weather_rain 0:35:10:10 "W200,V3,W30,G288:20,W200,Q" "battle weather 5 (permanent)" PKBN_OW_AUTOBATTLE=1
# (species / move numbers: Swampert, Tyranitar, Manectric...)
# POC-13: a switch-in ability (Tyranitar's Sand Stream) and a double battle against two trainers
bt sand_stream "285:50:57/89,248:40:242/157" "WHIPPED UP A SANDSTORM"
bt two_trainers "285:50:57/89/58/182|338:45:209/85/44/98,288:3:45" \
    "SENT OUT MACHOKE" PKBN_BOT=smart PKBN_TEST_TRAINER=29 PKBN_TEST_TRAINER_B=30
# POC-14: a hidden item also holds chip data (Route 104's hidden Super Potion, a move of a Route 104 wild Pokémon)
run hidden_chip_data 0:19:7:7 "W200,U,W20,A,Y,A,Y,A,Y,A,Y,A,W60,Q" "chip grant: hidden data"
# POC-14: beating a Gym Leader gives their Leader chip and starts the rematch record (Swampert vs Roxanne)
bt leader_chip "285:40:57/341/55/33,288:3:45" "LEADER CHIP V" PKBN_BOT=smart PKBN_TEST_TRAINER=265
# POC-14: PC -> NET CHALLENGE -> PEBBLE STORM, won (first clear pays two programs), back at the PC
OWPARTY="285:40:57/89/58/182|309:8:45/55" run net_challenge 2:2:10:2 \
    "W200,U,W20,A,Y,A,Y,W30,D,W20,D,W20,A,W60,Y,A,W90,W900,P,A,W60,A,W60,A,W60,A,W60,A,W100,P,W10,Q" \
    "net challenge 0 cleared" PKBN_OW_AUTOBATTLE=1 PKBN_BOT=smart PKBN_TEST_CHALLENGE_KEYS="A"
# POC-14: a legendary fought as a BN boss (Kyogre's tide phase), and a NET CHALLENGE as a self-test (DEEP CURRENT)
bt boss_kyogre "279:70:348/337/89/98|338:70:85/242/98/44,404:45" "boss phase: KYOGRE CALLS THE TIDE" PKBN_BOT=smart PKBN_TEST_LEGENDARY=1
bt challenge_deep_current "285:70:57/89/58/182|279:70:348/337/89/98,74:5" "net challenge 7: DEEP CURRENT" PKBN_BOT=smart PKBN_TEST_CHALLENGE=7
# POC-14: Maxie & Tabitha with Steven as the partner (his Pokémon assist), and their team Program Advance
bt steven_partner "285:45:57/89/58/182|279:45:348/337/89/98,288:3" "partner: STEVEN's" PKBN_BOT=smart \
    PKBN_TEST_TRAINER=734 PKBN_TEST_TRAINER_B=514 PKBN_TEST_PARTNER=1
bt team_pa "285:60:57/89/58/182|279:60:348/337/89/98,288:3" "team program advance: TATE&LIZA" PKBN_BOT=smart PKBN_TEST_TRAINER=271
# POC-14: battle replay - record a battle, replay it, and the fight log must be the same line for line
bt replay_record "285:60:57/89/58/182|279:60:348/337/89/98,288:3" "replay saved" PKBN_BOT=smart PKBN_TEST_TRAINER=271
bt replay_play "285:60:57/89/58/182|279:60:348/337/89/98,288:3" "replay: " PKBN_TEST_REPLAY=1
if diff <(grep -a '^\[pkbn f[0-9]*\]' "$OUT/replay_record/log.txt" | grep -v ' f0\]' | grep -v busting) \
        <(grep -a '^\[pkbn f[0-9]*\]' "$OUT/replay_play/log.txt" | grep -v ' f0\]' | grep -v busting) > /dev/null; then
  echo "PASS replay_identical"; else echo "FAIL replay_identical (the replay played out differently)"; fi
rm -f pkbn_replay.bin
