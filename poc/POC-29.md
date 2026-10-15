# POC-29: fewer `*` chips, a team that grows together, scaled EXP

**Patches:** `0103-POC-29-…`, on top of 0001–0102. The version (0.30) comes with POC-30.

These are your picks N1a, N2a and N3a from the playthrough report. All numbers are TUNE.

## `*` chips (N1a)

The 3-gym runs showed 59% of chip drops coming as `*`. There were two causes:

- **The code bias snowballed.** T2 makes a new chip lean toward the code your folder has most of. It counted `*` as a
  code, so every `*` made the next one likelier (`PkbnCode_Fit`, `src/pkbn/pkbn_save.c`; `PkbnCode_Unlocked` says
  yes to `*`).
- **Drops rolled `*` like a code.** Most moves list `*` among their codes. An ordinary drop picked it at double weight,
  and a rare drop could pick it twice: in its 1 in 4, and again among the higher codes (`RandomLane`,
  `src/pkbn/busting.c`).

Now:

- `*` is never the code a new chip leans toward.
- Ordinary drops never come as `*`.
- A rare drop comes as `*` in its 1 in 4 only. Otherwise it picks among the move's higher lettered codes.
- Unchanged: a shiny's `*` chips, a Premier Ball catch's `*` and the PA Dex's `*` reward chip. Learning a move still
  gives its first three codes, which for a few moves include `*`.

## The team shares the EXP (N2a)

- **The split:** from the start, every Pokémon able to fight gets EXP from each foe it beats:
  - the Pokémon that fought split 2/3 of the EXP, as in Gen 3;
  - the rest of the team splits the last 1/3.
- **Out of the fighters' share:** the bench's share comes out of the fighters'. Gen 6's Exp. Share added it on top,
  which made the 3-gym runs even easier. With nobody on the bench, the fighters get it all.
- **The Exp. Share key item** (Mr. Stone, `upstream/pokeemerald/data/maps/RustboroCity_DevonCorp_3F/scripts.inc:163`)
  is now the switch: use it to turn sharing off, and again to turn it back on.
- **EVs** still go to the fighters only.

## Scaled EXP (N3a)

- **The formula:** Gen 5's. Each Pokémon's share is multiplied by ((2L + 10) / (L + Lp + 10))^2.5. L is the foe's level
  and Lp the Pokémon's own.
- **What it does:** a Pokémon above the foe earns less, and one below earns more. At equal levels nothing changes,
  because it keeps Gen 3's base EXP (yield × level / 7) underneath.
- **Examples:**
  - A Lv 30 Treecko beating a Lv 10 Zigzagoon earns 28% of what it did.
  - A Lv 5 Poochyena on the bench earns 158% of its share from the same Zigzagoon.

Code: `AwardExpForFaintedEnemy` and `ScaledExp` in `src/pkbn/grid_battle.c`, `PkbnExpShare_On` in `src/pkbn/items.c`.

## A crash fixed: Castform

- **The crash:** any battle against Castform crashed the game. The campaign runs found it at Angelica on Route 120
  (`upstream/pokeemerald/data/maps/Route120/scripts.inc:338`).
- **The cause:** Castform's palette holds four 16-colour palettes, one per form. The picture loader decompressed it
  into room for one.
- **The fix:**
  - The buffer now has room for all four (`Gfx_LoadMonPic`, `src/pkbn/gfx.c`).
  - Castform shows its normal form in both animation frames. Its four frames are forms, not an animation.

## The campaign runs go to the eighth badge

`tools/campaign_plan.py` now follows the story to Juan:

- Mt. Chimney, Lavaridge, Petalburg, Route 119 and Fortree, Lilycove and Mt. Pyre, both hideouts, Mossdeep, the
  Space Center, Seafloor Cavern and Sootopolis.
- After Norman, the plan includes swimmers.
- A last argument stops after any badge (`GYMS=3 bash scripts/campaign.sh …`).
- Each Gym Leader's own "defeated" script gives the badge and TM. Norman's badge is given inside his battle script, so
  the driver does the same steps (`campaign.c`, `LeaderScript`).

## Simulated

These are campaign runs to Juan (`scripts/campaign.sh`), 9 per version: the three starters with seeds 1 and 2 catching
up to 6, and each starter alone. The numbers are averages of the 6 runs that catch Pokémon.

| At | Ace | Lead, 0.28 | Lead, POC-29 | Bench, 0.28 | Bench, POC-29 |
|---|---|---|---|---|---|
| Roxanne | 15 | 20.8 | 16.0 | 4.6 | 9.9 |
| Brawly | 19 | 27.8 | 21.0 | 5.9 | 11.3 |
| Wattson | 24 | 39.0 | 28.8 | 9.4 | 18.5 |
| Flannery | 29 | 51.2 | 36.3 | 11.2 | 22.6 |
| Norman | 31 | 54.3 | 39.2 | 11.5 | 23.8 |
| Winona | 33 | 65.2 | 46.5 | 13.2 | 28.9 |
| Tate & Liza | 42 | 72.7 | 51.8 | 18.6 | 32.8 |
| Juan | 46 | 79.8 | 56.3 | 20.1 | 36.2 |

- **Losses:** about 8 a run of about 400 battles, as before.
- **Battle length:** 29 seconds on average, against 24.
- **`*` chip drops:** 11% of chip drops, against 33%.
- **The starter alone:** reaches Juan at Lv 66 instead of 83. It loses about 33 times a run instead of 21, because with
  no bench only the scaling slows it.
- **What stays hard:**
  - Winona: the test player beat her in 0 of 6 runs, against 2 of 6. Her Pokémon all use Aerial Ace, a lock-on.
  - Wattson: 4 of 6.
  - The pace: against Gym Leaders the test player sends about 8 chips a minute while the leader uses about 19 moves.
- **Program Advances:** none formed.

## Tests

- **Battle regressions (33):** every battle plays exactly as in 0.28, move for move, with the same outcome. Only
  what's paid out afterwards changes:
  - 4 tests are identical.
  - 28 differ only in EXP: scaled amounts, and in two of them the bench's new shares.
  - 1 differs in a reward: `GROWL *` now comes with a letter.
- **Overworld tests:** 51/51 (run on the POC-30 build, which contains this).
- **Patches:** 0001–0105 applied onto the pin give the same tree as the build tested here.
