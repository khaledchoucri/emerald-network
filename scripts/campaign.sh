#!/usr/bin/env bash
# Campaign runs: a test player plays the story's battles up to the third badge (src/pkbn/campaign.c), in about a minute.
# Run from the host build folder (where pokeemerald64 is):
#   bash /path/to/scripts/campaign.sh NAME TREECKO|TORCHIC|MUDKIP [WILD] [env...]
#     WILD   how much wild grass the player walks: 1.0 (default) or e.g. 0.4
#     env    PKBN_TEST_SEED=n (the same run again), PKBN_CAMP_CATCH=n (catch new species up to n in the party, default 4,
#            0 = the starter alone), PKBN_BOT=buster (holds B, no chips), PKBN_TEST_EXP_SHARE=1, PKBN_TEST_TUTORIAL=1
# Writes OUT/NAME/{plan.txt,log.txt,playlog.jsonl} (OUT=${OUT:-/tmp/pkbn-campaign}); then:
#   python3 /path/to/tools/campaign_report.py OUT          a summary of every run in OUT
set -u
NAME=$1 STARTER=$2 WILD=${3:-1.0}; shift 3 2>/dev/null || shift $#
HERE=$(cd "$(dirname "$0")/.." && pwd)
OUT=${OUT:-/tmp/pkbn-campaign}
D=$OUT/$NAME
case $STARTER in TREECKO) SP=277;; TORCHIC) SP=280;; MUDKIP) SP=283;; *) echo "starter: TREECKO, TORCHIC or MUDKIP"; exit 1;; esac
rm -rf "$D"; mkdir -p "$D"
python3 "$HERE/tools/campaign_plan.py" . "$STARTER" "$WILD" > "$D/plan.txt" || exit 1
env PKBN_TURBO=1 PKBN_CAMPAIGN="$D/plan.txt" PKBN_OWTEST=0:16:10:10 PKBN_OWTEST_PARTY="$SP:5" PKBN_OW_AUTOBATTLE=1 \
    PKBN_BOT=smart PKBN_TEST_EVOLVE=1 PKBN_CAMP_CATCH=4 PKBN_DATA_DIR="$D/" PKBN_PLAYLOG="$D/playlog.jsonl" \
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "$@" timeout 1200 ./pokeemerald64 > "$D/log.txt" 2>&1
echo "$NAME rc=$? $(grep -a 'pkbn-camp\] END\|STALLED\|ran out' "$D/log.txt" | tail -1)"
