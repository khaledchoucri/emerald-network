# POC-10 — Shared chip folder, chip pack, candy, Busting Level, Capture Grade

**Patches:** on top of 0001–0011.
- `poc/patches/0012-POC-10a-shared-chip-folder-chip-pack-type-candy.patch`
- `poc/patches/0013-POC-10b-Busting-Level-Capture-Grade-rewards.patch`

**Design:**
- `docs/design/08-folder-memory.md` §11–12
- `docs/design/09-busting-level.md`
- `docs/design/10-catching-and-chips.md` §10

**New tools (repo `tools/`):**

| tool | what it does |
|---|---|
| `gen_chip_data.py` | Writes `src/pkbn/chip_data.c` from the port's own data: MB per move, and a "can learn" bitset per species (level-up including pre-evolutions, TM/HM, tutor, the family's egg moves). |
| `chip_memory.py` | MB rules. Status moves now use 200/PP instead of 300/PP, so weather moves (PP 5) get 2 copies instead of 1. |
| `shared_folder_sim.py` | The simulation behind design 08 §11. |

## 10a — the folder

- **One folder for the party.** Size 30 + 2 per extra Pokémon. It is built from the **chip pack** in `pkbn.sav`.
  - There's no FOLDER editor yet, so the folder is auto-built.
  - The builder is greedy, one copy at a time. It favours chips several members can use and members that have little
    so far.
  - BN6 copy caps by MB apply.
- **A chip is a move.** Whoever is in battle uses it if its species can learn the move, or already knows it.
  - Chips the Pokémon in battle can't use are greyed and say "CAN'T USE".
  - They stay in the hand until you switch, and switching costs the Custom.
  - A chip nobody still standing can use is discarded.
- **No PP.** Copies are the stamina; the Custom screen shows "xN LEFT" instead of "PP".
  - A used chip is gone for the battle ("folder used up" when you run out).
  - Folders under 15 chips still reshuffle.
- **Learning a move** gives 1 copy with the move's first code, once per move. This covers every learn path, because
  the game scans the party and boxes.
- **Catching gives type candy:** `1 + (255 − catch rate) / 50` of each of its types, ×3 on a first catch.
- **`pkbn.sav` version 2:** pack, granted moves, candy, and folder slots for the editor. Version 1 files load and
  migrate (tested).

## 10b — Busting Level and Capture Grade

**Busting Level** after every won battle:
- **Score:** BN6's components, adapted:
  - time;
  - hits that stunned or pushed you;
  - ≤2 steps;
  - best chain (2/3 chips, Program Advance);
  - counter hits;
  - nobody fainted.
- **Clock:** time is scored by turns, or by BN6's seconds with `PKBN_BUST_CLOCK=seconds`. The log line prints both.
- **Reward:** BN6's tier table picks it from a 20-entry list built from the enemy's own moves: money, HP, or a chip of
  its move, which goes to the pack.
  - The collect bug forces money.
  - AmuletCn doubles the money.
- **EXP:** S gives ×1.2 EXP; level 3 or below gives ×0.9.
- **Counter hits:** "COUNTER HIT!" when you hit an enemy that is busy with its own attack.

**Capture Grade** after a catch:
- **Score:** HP left, status, balls thrown, a first-ball catch at high HP, and hits taken.
- **Reward:** a chip of its moves, whose code depends on the ball:

  | ball | code |
  |---|---|
  | Poké | first lane |
  | Great | random |
  | Ultra | "your choice" |
  | Net / Dive / Nest / Timer / Luxury | their themed lane, otherwise random |
  | Repeat | a code you own |
  | Premier | `*` |
  | Safari | 2 chips |
  | Master | **every move** |

  Lower grades give extra candy instead, and S gives +2 candy.

## Not in yet (next: POC-10c)

- A **FOLDER** screen to edit the folder and see the pack and candy.
- **Spending candy:** the candy shop with level gating.
- **Other chip sources:** PP Up / PP Max on chips, TMs as chips, Heart Scale at the Move Relearner, Mart chip shelves.
- **Smaller pieces:** candy for releasing, Pokédex milestones, egg moves, shiny `*` copies.
- **Choosing a code:** "Your choice" for Ultra and Master Balls auto-picks the code you own most of, until there's a
  picker.
- **Story partner chips.**

## Tests

**Regression:** all 33 earlier battles end the same way, with one exception.
- The self-tests seed the pack with the old PP-based copies, so they test the same chips.
- **e2** (Jigglypuff vs Mudkip) now times out instead of losing. Mudkip's 9-chip folder reshuffles and no longer runs
  out of PP: a stall that a small reshuffling folder allows.

**New tests:**

| test | result |
|---|---|
| shared folder | Body Slam usable by both Combusken and Marshtomp; water chips greyed for Combusken |
| stamina | a 19-chip folder is used up after exactly 19 chips |
| `pkbn.sav` v1 → v2 migration | the NaviCust layout survives |
| candy on catch | candy granted (Zigzagoon: 3 Normal) |
| Master Ball | grants a chip of every move |
| S-rank EXP | 1324 → 1588 EXP |

The busting levels in the bot tests run high (S/9/10), because the bots never move and rarely get hit. Real play will
show lower levels, so the numbers are TUNE.

**Self-test switches:**

| switch | what it does |
|---|---|
| `PKBN_TEST_PACK_LEARNED=1` | use the real "learned = 1 copy" rule |
| `PKBN_TEST_PACK="move:L:n,..."` | add copies to the pack |
| `PKBN_TEST_SIDECAR_READ=<navi id>` | load `pkbn.sav` from the working directory and report what came back |
| `PKBN_BUST_CLOCK=seconds` | score time by BN6's seconds instead of turns |
