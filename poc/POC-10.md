# POC-10 — Shared chip folder, chip pack, candy, Busting Level, Capture Grade

**Patches:** on top of 0001–0011.
- `poc/patches/0012-POC-10a-shared-chip-folder-chip-pack-type-candy.patch`
- `poc/patches/0013-POC-10b-Busting-Level-Capture-Grade-rewards.patch`
- `poc/patches/0014-POC-10c-FOLDER-screen-candy-shop-chip-sources.patch`
- `poc/patches/0015-POC-10d-FOLDER-screen-fixes.patch`

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

## 10c — FOLDER screen, candy shop, more chip sources

- **Chip pictures:** on the Custom screen chips show a BN-style **icon of the move**: its effect, shrunk onto a
  type-coloured tile. Only partner switch chips will show a Pokémon (Khaled's note). The big chip-art box shows the
  move alone.
- **START menu → FOLDER** (`src/pkbn/folder_ui.c`). The start menu window moves up one row so 9 entries fit.

  | page | what you can do |
  |---|---|
  | FOLDER | the chips battles draw from. A takes one out; SELECT goes back to auto-build. The folder is saved in `pkbn.sav`. |
  | PACK | everything you own, with in-folder / owned counts. A puts a copy in (checks the folder size, copies owned, MB cap, and that someone can use it). START uses a **PP UP**: +1 copy of that chip. SELECT uses a **PP MAX**: copies of that move up to its cap. |
  | CANDY | the candy shop. Moves of a type become buyable once a Pokémon you own (party or PC) has reached them by level-up, and is at least the move's MB in level. Price MB/4, rounded up; +2 to pick another code (SELECT cycles it). Types you have candy for are listed first. |

  The right-hand panel shows the chip icon, code, type, power, MB, cap, owned / in folder, and which party members
  can use it (their icons, as information).
- **More chip sources:**

  | source | gives |
  |---|---|
  | **TMs / HMs** | 2 copies each, when bought (`shop.c`) or found / given (`scrcmd.c` additem). Taking one out of the PC item storage gives nothing. |
  | **Move Relearner** (Heart Scale) | +1 copy in a code you don't own yet for that move (`move_relearner.c`) |
  | **Releasing** | 1 candy of each type, +1 at level 30 or above (`pokemon_storage_system.c`) |
  | **Hatching** | +1 copy of each egg move the hatchling knows (`egg_hatch.c`) |
  | **Pokédex milestones** | a PP UP every 10 species caught, a PP MAX every 50 |
  | **Shiny catch** | a `*` copy of every move it knew |

## 10d — fixes from play-testing (2026-10-05)

- **Copy limit visible.** Every page has a LIMIT column: that move's copies in the folder against its MB limit, e.g.
  `3/4`, orange when full. The panel says `LIMIT 4 (MB 26)`. Adding past the limit explains why.
- **Folder page grouped.** One row per chip (move + code) with a quantity (`EMBER S x3`), sorted by type.
- **Candy unlock rule fixed.** A move unlocks at the level the Pokémon learns it.
  - Only an **evolved form's level-1 moves** (Raichu's Thunderbolt) still need the move's MB in level.
  - The old rule (always the MB in level) hid Water Gun from a level-5 Wingull.
  - Moves your Pokémon will learn later are listed greyed with "LVn" and which Pokémon learns them.


- **Mart chip shelves.** For now the Lilycove TM shelves act as the chip shop, since TMs are chips.
- **A code picker** for Ultra / Master Ball rewards (they take the code you own most of).
- **Story partner chips.**
- **Unverified at runtime** (built, and each hook is a few lines):
  - the START menu entry in the overworld;
  - the hooks for TMs from scripts, the relearner, releasing, hatching, milestones and shiny catches.

  The FOLDER screen itself and the TM grant are tested through the self-test path.

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

**FOLDER screen test** (key script):
- open FOLDER;
- PACK: PP UP on Ember, so 4 → 5 copies;
- CANDY: cycle Ember's code to O, buy it for 5 Fire candy;
- FOLDER: take a chip out;
- leave.

The battle then uses the edited folder (21 chips).

**Self-test switches:**

| switch | what it does |
|---|---|
| `PKBN_TEST_PACK_LEARNED=1` | use the real "learned = 1 copy" rule |
| `PKBN_TEST_PACK="move:L:n,..."` | add copies to the pack |
| `PKBN_TEST_SIDECAR_READ=<navi id>` | load `pkbn.sav` from the working directory and report what came back |
| `PKBN_BUST_CLOCK=seconds` | score time by BN6's seconds instead of turns |
| `PKBN_TEST_FOLDER_KEYS` | key script for the FOLDER screen |
| `PKBN_TEST_CANDY="type:n"` | add candy |
| `PKBN_TEST_ITEMS="item:n"` | add bag items |
| `PKBN_TEST_GRANT_TM=item` | run the TM grant |
