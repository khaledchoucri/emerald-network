# POC-31: new moves, ladders, the Gen 4 split

**Patches:** `0106-POC-31-46-Gen-4-moves-with-Platinum-s-numbers-M1c-M5.patch` and `0107-POC-31b-version-0.31.patch`, on top of 0001–0105. Version 0.31.

Your picks L1a L2c L3a L4a L5a (ladders) and M1c M2a M3b M4a M5a M6a (new moves), and your approval of the Learnset
Review page as a whole. All numbers not taken from a game are TUNE.

## Where the numbers come from (M6a)

- **PokeAPI's CSV tables** (`data/v2/csv`): `moves.csv`, `move_changelog.csv`, `move_flag_map.csv`, `move_flags.csv`,
  `types.csv`, `version_groups.csv`, and for the review `pokemon_moves.csv`.
- **UNVERIFIED until `upstream/pokeapi` is added.** The build used a copy downloaded from PokeAPI's GitHub on 16 Oct.
  The tools take the folder as an argument, so once you add `upstream/pokeapi` they are rerun on it and the generated
  files must come out the same.
- **Platinum's numbers (M5a):** `moves.csv` holds today's values. `move_changelog.csv` holds, for each version group
  where a field changed, the value it had before. A field's Platinum value is the old value in the first change after
  Platinum that touches it, or today's value if none did. Example: Air Slash has 20 PP in Platinum and 15 from X and Y
  on.
- **Effects:** PokeAPI's move effect ids 1–214 are Gen 3's, in Emerald's order (`EFFECT_x` = id − 1). 333 of Emerald's
  354 moves agree today; the other 21 changed effect after Gen 3.

## 46 new moves (M1c, M5a)

Damaging moves that Hoenn Pokémon learn by level-up in Platinum, minus the 12 that need a grid mechanic of their own
(U-turn, Sucker Punch, Payback, Assurance, Feint, Gyro Ball, Wring Out, Last Resort, Trump Card, Punishment, Natural
Gift, Fling).

- **Numbers:** `MOVE_WAKE_UP_SLAP` (355) to `MOVE_OMINOUS_WIND` (400), in PokeAPI order. `MOVES_COUNT` 355 → 401.
- **Effects:**
  - 35 use an effect Emerald already has: Poison Jab is a poison hit, Brave Bird is Double-Edge's 1/3 recoil, Leaf
    Storm is Overheat, Giga Impact is Hyper Beam, Bullet Punch is Quick Attack, and so on.
  - 8 new effects, played by the grid (`src/pkbn/grid_moves.c`):

    | Effect | Moves | What it does |
    |---|---|---|
    | `EFFECT_WAKE_UP_SLAP` | Wake-Up Slap | x2 against a sleeping target. Every grid hit already wakes the target. |
    | `EFFECT_BRINE` | Brine | x2 against a target at half HP or less |
    | `EFFECT_SP_ATK_UP_HIT` | Charge Beam | 70%: the user's Sp. Atk +1 |
    | `EFFECT_HAMMER_ARM` | Hammer Arm | the user's Speed −1 |
    | `EFFECT_CLOSE_COMBAT` | Close Combat | the user's Defense and Sp. Def −1 |
    | `EFFECT_FLARE_BLITZ` | Flare Blitz | 1/3 recoil, 10% burn |
    | `EFFECT_HEAD_SMASH` | Head Smash | 1/2 recoil |
    | `EFFECT_FANG` | Fire, Ice, Thunder Fang | 10% the type's status and, rolled apart, 10% flinch |

  - Not done: Pluck and Bug Bite eat the target's berry in Platinum. Grid battles have no held berries, so they're plain
    hits. Flare Blitz doesn't thaw its user.
  - In Emerald's own turn-based battles (Safari, Frontier, link) the 8 new effects hit like a plain attack
    (`gBattleScriptsForMoveEffects` points them at `BattleScript_EffectHit`).
- **Names and descriptions:** names in Emerald's capitals. The descriptions are our own words, two short lines each
  (`tools/new_moves_curated.py`).
- **Outside grid battles:** each move borrows a similar Gen 3 move's Emerald animation (Thunder Fang uses Bite's), and
  takes its sounds from it.

## The Gen 4 split (M3b)

Every move is physical, special or status by itself (PokeAPI `damage_class_id`), no longer by its type.

- **Where:**
  - `gPkbnMoveSplit[MOVES_COUNT]` (`src/pkbn/move_split.c`) holds each move's category.
  - `CalculateBaseDamage` (`src/pokemon.c`) uses it, including for the type-boost programs and items.
  - So do Counter's record in grid battles (`grid_moves.c`), and Hustle's accuracy and Counter / Mirror Coat in
    Emerald's battle engine (`src/battle_script_commands.c`).
- **Program Advances:** a PA hits as its last chip does when that chip is damaging, and by Gen 3's type rule
  otherwise.
- **54 Gen 3 moves change category:**
  - **Now physical (28):** Beat Up, Bite, Blaze Kick, Bullet Seed, Clamp, Crabhammer, Crunch, Dive, Dragon Claw,
    Faint Attack, Fire Punch, Flame Wheel, Ice Ball, Ice Punch, Icicle Spear, Knock Off, Leaf Blade, Needle Arm,
    Outrage, Pursuit, Razor Leaf, Sacred Fire, Spark, Thief, Thunder Punch, Vine Whip, Volt Tackle, Waterfall.
  - **Now special (26):** Acid, Aeroblast, Air Cutter, Ancient Power, Doom Desire, Gust, Hidden Power, Hyper Beam,
    Hyper Voice, Mud Shot, Mud-Slap, Night Shade, Razor Wind, Shadow Ball, Signal Beam, Silver Wind, Sludge, Sludge
    Bomb, Smog, Snore, Sonic Boom, Spit Up, Swift, Tri Attack, Uproar, Weather Ball.
  - Night Shade, Sonic Boom and Spit Up deal fixed or stored damage, so the change doesn't affect them.

## The new moves on the grid (M4a)

Each new move plays the grid kind and BN6 effect from the table on the New Moves and Ladders page. The effect is drawn
in the type's colours. Both are in `tools/attacks_curated.py`, as `fx=`, a new modifier.

- **The table:** `PkbnMoveInfo` gets an `fx` field (`FX_*` + 1; 0 = the type's own picture).
- **Drawing:** `TypeBurst` and the FireHit / GolemHit impact in `src/pkbn/grid_vfx.c` show the move's effect instead of
  the type's.
- **Two effects:** where the table named two ("FANG + ICE"), the close-range picture comes from the strike group and
  `fx=` is the other one:
  - the fangs and Bug Bite bite;
  - Close Combat, Force Palm and Wake-Up Slap are blows;
  - Poison Jab and Pluck stab;
  - Aqua Tail and Double Hit whip;
  - Zen Headbutt, Iron Head, Flare Blitz, Brave Bird, Giga Impact, Head Smash and Aqua Jet are body blows.
- **Priority:** Aqua Jet, Ice Shard, Shadow Sneak and Bullet Punch are `fast`, like Quick Attack and Mach Punch.
- **Examples:**

  | Move | Kind | Effect |
  |---|---|---|
  | Flash Cannon | Cannon | BN Cannon's blast, in Steel's colours |
  | Leaf Storm, Ominous Wind | Tornado | Leaves, wind |
  | Earth Power, Stone Edge | Shockwave | A crack, spikes |
  | Discharge, Lava Plume | Cone | Sparks, fire |
  | Hammer Arm | GolemHit | A crack |
  | Magnet Bomb | Lock-on | A bomb. It never misses. |
  | Giga Impact | Dash | An explosion, then a recharge |

- **M4b:** BN6 chip animations of their own for the headline moves are a separate pick. The candidates are on the
  report page.

## Codes (L4a)

- **New moves:** each one's codes follow its type, like the old moves' (`tools/lanes_curated.py`).
- **Ladders:** every ladder's three moves share a code. 43 lines needed a code added to one of their moves. The added
  codes come last, so the code a move has always had stays first.
  - Old moves that got one: Pound, Double Slap, Headbutt, Body Slam, Twineedle, Dizzy Punch, Slash, Dragon Breath,
    Twister, Hyper Voice, Silver Wind, Signal Beam.
- **Limits:** a move can now have up to 6 codes, up from 4. `lanes[6]`, and the arrays sized by it in `busting.c`,
  `chip_trader.c` and `pkbn_save.c`, were 4 long.
- **Learning:** learning a move still gives one chip in each of its first three codes. Now it also gives one chip in
  each lettered code after those, so a ladder's shared code always comes with the move (`GrantLearned`,
  `src/pkbn/pkbn_save.c`).
- **Open from the start:**
  - **The problem:** codes unlock as you go (POC-26: 6 at the start, 2 more per badge or rival battle). A locked code
    is replaced by an open one, chosen per move. The first campaign runs showed the clash: Torchic's ladder shares S,
    which opens after about 5 steps. Until then Ember came as O, Fire Punch as Z and Blaze Kick as K, and Torchic almost never
    had a trio it could chain (1 of 127 sampled folders could form one).
  - **The fix:** a ladder move's shared code is open for that move from the start (`PkbnCode_OpenFor`,
    `src/pkbn/pkbn_save.c`; `PkbnMoveInfo.ladder`, generated from the ladders). Every other code still waits for its
    unlock.
  - **And it stays:** a chip that comes in its ladder code keeps it. T2's lean toward the code your folder has most of
    doesn't apply to it. In the second set of runs, Blaze Kick's learned S copy kept turning into K, Brick Break's
    code. This is how I read your L4a ("always share a letter"). The report page offers to undo it.
- **Check:** all 112 ladders share a code (`tools/learnset_ladders.py`'s data, checked against `lanes_curated.py`).

## Learnsets (L1a L2c L3a L5a M2a)

- **Source:** `tools/gen_learnsets.py` writes `data/learnset_ladders.json`, the reviewed data, into
  `src/data/pokemon/level_up_learnsets.h` for the 201 members of the 112 Hoenn lines.
- **Check:** before writing, it confirms each learnset is still the one reviewed.
- **Order within a level:** Emerald's own entries keep Emerald's order and the new ones follow. Wild and trainer
  Pokémon keep the last four moves they learned.
- **One fix on top of the review:**
  - **The problem:** a ladder step removes its move's earlier entry. In 32 learnsets that left the Pokémon with no
    damaging move until Lv 10. Examples: Wingull's Water Gun, Taillow's Peck, Ralts' and Kirlia's Confusion,
    Marill's and Skitty's Tackle, Oddish's Absorb, Pikachu's ThunderShock.
  - **The fix:** those earlier entries stay, so the first damaging move comes when it did in Emerald.
  - **The list:** `gen_learnsets.py` prints all 32.
- **Size:** `MAX_LEVEL_UP_MOVES` 20 → 22 (Hariyama has 21 entries plus one of these).
- **Chips:** the "can use" tables were rebuilt from the new learnsets (`tools/gen_chip_data.py`), so any Pokémon that
  learns a new move can use its chip.

## Saves

- **The format:** `pkbn.sav` v10. The per-move arrays (chips owned, "learned" grants, the library) grow from 355 moves
  to 401. A file now records the move count it was written with (`movesCount`).
- **Older files:** v1–v9 are read in the old layout, brought up to v9 as before, then copied field by field into v10
  (`Widen`).
- **Test:**
  - A v9 file filled with random bytes was read by 0.30 and by 0.31.
  - All 42 fields have the same checksum in both. That covers every field, and only the first 355 moves for the per-move
    arrays.
  - The v10 file 0.31 writes reads back on its own.
  - The test: `PKBN_TEST_SIDECAR_READ=1 PKBN_TEST_SAVE_SUMS=1`.

## Tests

- **Battle regressions (33):** 23 give the same `[pkbn]` log as 0.30. The other 10 change where the split or the codes
  say they should:
  - **8 at the first hit of a move whose category changed:** Bite, Mud-Slap (twice), Gust, Silver Wind, Sludge Bomb,
    Acid, Hyper Beam. One of them changes the outcome: e4, where Pidgeotto's Gust now finishes Mudkip.
  - **2 in a reward's code:** Headbutt comes as L, a code it gained for a ladder. Rock Throw keeps its ladder code Q
    instead of leaning toward the folder's A.
- **The new moves:** 7 battles using all 46 (`n1`–`n7`). Every move plays. Recoil (Head Smash, Flare Blitz), Close
  Combat's drops and Charge Beam's raise show in the logs.
- **Overworld tests:** 51/51 on the final build. Two were updated: the chip gallery expects 358 chips, and team_pa's Sceptile has Giga
  Drain instead of Leaf Blade, now physical.
- **Save migration:** see Saves.
- **Campaign runs:** the nine runs to Juan, as for 0.30:

  | | 0.30 | 0.31 |
  |---|---|---|
  | Catching, losses a run | 6.0 | 6.8 |
  | Catching, folders where the lead could chain a trio | 0 of 252 | 7 of 249 |
  | Catching, … where anyone in the party could | 20 of 252 | 23 of 249 |
  | Catching, Winona / Tate & Liza / Juan won | 3 / 5 / 5 of 6 | 2 / 4 / 6 of 6 |
  | Alone, losses a run | 42 | 29 |
  | Alone, folders where it could chain a trio | 8 of 125 | 72 of 124 |
  | Trios formed (all 9 runs) | 0 | 9 (Fire 5, Grass 2, Water 1, Ground 1) |

  Lead levels are within a level of 0.30's at every gym. With six Pokémon, the automatic folder rarely keeps a ladder
  together, so trios stay rare in a normal game. That's the next pick (F1 on the report page).
- **Patches:** 0001–0107 applied onto the pin give the same tree as the build tested here.

## Tools

| Tool | What it does |
|---|---|
| `tools/gen_new_moves.py <host> <pokeapi csv>` | Moves, effects, names, descriptions, borrowed animations, `move_split.c`. Writes between `pkbn POC-31` markers and can be run again. |
| `tools/new_moves_curated.py` | Per move: the borrowed animation and the description. The PokeAPI effect → new effect map. |
| `tools/gen_learnsets.py <host> [json]` | The learnsets, from `data/learnset_ladders.json` |
| `tools/learnset_ladders.py` | The draft generator behind the review (reads an unmodified Emerald tree) |
| `tools/gen_move_table.py` | Now with `fx=` and up to 6 codes |
| `tools/chip_memory.py` | Flare Blitz and Head Smash cost a little less, like the other recoil moves |
