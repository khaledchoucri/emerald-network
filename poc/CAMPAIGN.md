# Campaign runs: simulated playthroughs to the third badge

**Patch:** `0102-Campaign-runs-…`, on top of 0001–0101. It's a test tool: the game plays the same with it as without it.

A test player starts a new game and fights the story's battles in Emerald's order. It plays from Birch's Poochyena to
Wattson, about 100 battles, and its logs can be read like a playtester's. With no screen and no frame limit, one run
takes about a minute.

## Running it

From the host build folder:

```
bash /path/to/scripts/campaign.sh NAME TREECKO|TORCHIC|MUDKIP [WILD] [env...]
python3 /path/to/tools/campaign_report.py /tmp/pkbn-campaign
```

- **Output:** each run writes `OUT/NAME/plan.txt`, `log.txt` and `playlog.jsonl`. `OUT` defaults to
  `/tmp/pkbn-campaign`.
- **The report:** prints a line per run and writes `OUT/summary.json`.
- **`WILD`:** how much grass the player walks. 1.0 (the default) is about 40 wild battles to Mauville; 0.4 is about 16.

| Setting | What it does |
|---|---|
| `PKBN_TEST_SEED=n` | The same run again, battle for battle |
| `PKBN_CAMP_CATCH=n` | Throws balls at new species while the party has fewer than n (default 4; 0 = the starter alone) |
| `PKBN_BOT=buster` | A player who only holds B (the default is the smart test bot from POC-12) |
| `PKBN_TEST_EXP_SHARE=1` | Gen 6's Exp. Share on from the start |
| `PKBN_TEST_TUTORIAL=1` | The lessons on, as for a new player |

## What the test player does

- **The plan** (`tools/campaign_plan.py`) is generated from the game's own map data:
  - **Trainers:** every one in `data/maps/<map>/map.json` that has a trainer script, minus a few the player can't reach
    yet: swimmers, Cycling Road triathletes and Rusturf's Mike.
  - **Gym Leaders:** after a win, the gym's own "defeated" script runs: badge, flags and TM.
    - Roxanne: `upstream/pokeemerald/data/maps/RustboroCity_Gym/scripts.inc:13`
    - Brawly: `upstream/pokeemerald/data/maps/DewfordTown_Gym/scripts.inc:144`
    - Wattson: `upstream/pokeemerald/data/maps/MauvilleCity_Gym/scripts.inc:86`
  - **Rivals:** the rival trainer that matches the starter, on Route 103, in Rustboro and on Route 110; Wally in Mauville.
  - **Shopping:** heals at towns and buys 5 Poké Balls at each Mart, keeping $500.
- **Wild battles:** the player stands on a grass or cave tile and the map's own table makes the encounter
  (`PkbnWild_CampaignEncounter`, `src/wild_encounter.c`). Slot and level rolls, packs and places all work as in a real
  encounter.
- **Trainer battles:** the player stands next to the trainer and fights through `trainerbattle`, so the place
  (beach, cave) is the trainer's.
- **Its choices:**
  - **Battles:** the smart bot fights.
  - **Catching:** it throws a ball at a new species at half HP, or from the third turn on.
  - **New moves:** it forgets the weakest move when the new one is stronger. Status moves count as 20 power; moves of
    its own type count 1.5x.
  - **Evolution:** it lets its Pokémon evolve.
  - **Healing:** it heals when the lead faints or the party falls below a third of its HP.
- **Losing:** a lost trainer battle whites out as in the game. The player grinds 4 wild battles where it last found
  some, then tries again, up to 3 times, before it gives up (logged as GAVE UP).
- **Not simulated:** walking, items, editing the folder, R's new hand, and looking for Program Advances.

## What the first 30 runs showed (0.28, 15 Oct)

The full report with charts and next-step picks is a separate page.

| Players | Runs | Battles | Losses | Lead at Roxanne / Brawly / Wattson | Bench at the end |
|---|---|---|---|---|---|
| Smart bot, catches 3 | 9 | 107 | 2.6 | Lv 20 / 28 / 40 | Lv 4–17 |
| Starter alone | 3 | 103 | 2.0 | Lv 20 / 28 / 40 | none |
| Holds B, no chips | 3 | 133 | 12.7 | Lv 20 / 28 / 40 | none |
| Exp. Share on | 3 | 100 | 1.0 | Lv 20 / 28 / 39 | Lv 26–33 |

- **Wins and levels:**
  - The normal runs won 97.7% of their battles.
  - Gym aces are Lv 15, 19 and 24 (`upstream/pokeemerald/src/data/trainer_parties.h:3367, 3391, 3415`).
  - Most losses came at three places:
    - Elijah's two Lv 25 Skarmory (`trainer_parties.h:9926`): Agility takes their dodge chance to its 85% cap, and Swift
      is a lock-on.
    - Wattson's Shock Wave lock-ons after Thunder Wave.
    - Mel and Paul (`trainer_parties.h:9202`).
- **`*` chips:** 59% of chip drops came as `*`. There are two causes:
  - `PkbnCode_Fit`'s "your folder's code" bias counts `*`, because `PkbnCode_Unlocked` says yes to `*`, so `*`
    snowballs.
  - `RandomLane` rolls `*` like any other code. Rare drops also pick it from the higher codes.

  In throwaway builds, fixing the bias brought `*` down to 32%, and fixing both brought it to about 21%.
- **Program Advances:** none formed. In none of 210 sampled folders could the lead form a named Program Advance or a
  type trio.
- **The folder:** the share the lead can use falls from 100% to about 61% by Mauville. The buster still does about a
  third of all damage.
- **Places:**
  - The tide washed over 20–80 times a run, falling rocks hit 1–43 times and snares caught 1–9 times.
  - No rain before Mauville, so no puddles.

## Code

| Where | What |
|---|---|
| `src/pkbn/campaign.c` | The driver: plan, waiting for the field to be free, catching and move choices, the log |
| `src/pkbn/owtest.c` | Hands the keys to the campaign while `PKBN_CAMPAIGN` is set |
| `src/wild_encounter.c` | `PkbnWild_CampaignEncounter` |
| `src/pkbn/post_battle.c` | In a campaign, the test player answers the prompts and picks which move to forget |
| `src/pkbn/selftest.c`, `bot.c` | The ball throw (`PkbnBot_CampaignThrow`) |
| `src/pkbn/grid_moves.c` | Counts the player's buster hits and damage for the log (no log line of its own) |
| `src/platform/sdl2.c` | `PKBN_TURBO=1`: as fast as the machine goes, no sound, a picture every 30 frames |

## Tests

- **Battle regressions (33):** the same `[pkbn]` logs as 0.28.
- **Overworld tests:** 51/51.
- **Campaign runs:** the same seed gives the same run twice.
