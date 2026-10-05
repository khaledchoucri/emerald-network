# POC-9 — NaviCust for every Pokémon

**Patch:** `poc/patches/0011-POC-9-NaviCust-for-every-Pokemon.patch`, on top of 0001–0010.

**Design:** `docs/design/07-navicust.md`.

**Plans (not implemented yet):**
- `docs/design/08-folder-memory.md`: chip pack and copies.
- `docs/design/09-busting-level.md`.

**Research:** `research/06-bn6-busting-level.md`.

**New tools (repo `tools/`):**

| tool | what it does |
|---|---|
| `navicust_curated.py` | The 48 programs (source of truth). |
| `gen_navicust.py` | Generates `src/pkbn/ncp_table.c` and `include/pkbn/ncp_table.h` from `navicust_curated.py`. |
| `bn6_ncp_shapes.py` | Reads BN6's program table and shapes from `upstream/bn6f`. |
| `folder_math.py` | Draw probabilities (design 08). |
| `chip_memory.py` | MB and copy caps (design 08). |

## What's new

- A **NAVICUST** entry in the party menu. It opens a 5×4 board editor for that Pokémon. Design 07 covers the details.
- In battle:
  - **Buster:** levels, charge shot.
  - **Abilities:** SuperArmor, FloatShoes, AirShoes, UnderShirt, FirstBarrier.
  - **Hand size:** Custom1/2 bring the hand up to 8; the Custom screen now fits 8 chips.
  - **Item programs:** Quick Claw, King's Rock, Scope Lens, BrightPowder, Leftovers, Shell Bell, Focus Band, Choice Band, Lucky Egg, Amulet Coin.
  - **Bonuses:** stat and type bonuses, HP bonus.
  - **Bugs:** HP drain, random steps, panel cracks, smaller hand, buster misfire, status at start, halved prize money.
- **Sidecar save `pkbn.sav`:** written and read alongside the normal save.
- **Bug fix (POC-7):** trainer prize money reused a loop variable. Roxanne now pays $1500, not $1200 (`post_battle.c` TrainerMoney).

## Tests

**Regression:** all 33 earlier self-test battles give identical logs. The only exception is x3, where the prize fix changes $1200 → $1500.

**NaviCust self-tests:**

| test | result |
|---|---|
| n2 | buster 5/5/5 and a 50-damage charged shot |
| n3 | bugs move 1, buster 3, HP 1, status 1, and "IS POISONED! (BUG)" |
| n4 | Custom2 compressed by Smart 120 → "custom hand: 7 chips" |
| n5 | FirstBarrier absorbed a hit; UnderShirt left 1 HP |
| e1–e3 | editor screenshots via a key script |
| save round trip | OK |

**Not verified yet:**
- Opening NAVICUST from the real party menu, and returning from it. This needs a play test; the editor itself is tested through the self-test path.
- FloatShoes and AirShoes, and Leftovers, King's Rock, Shell Bell and the other item programs in a live battle. They are only covered by a build and a code read.

## Self-test switches

| switch | example | sets |
|---|---|---|
| `PKBN_TEST_NCP` | `"0:Custom2@3,0,0;Custom1@0,3,0/1:HP+50@0,0,0"` | programs per party slot: name@x,y,rotation[,colour variant] |
| `PKBN_TEST_COND` | `"0:cool,beauty,cute,smart,tough"` | conditions |
| `PKBN_TEST_POKERUS` | `"0:33"` | Pokérus byte |
| `PKBN_TEST_NCP_KEYS` | — | key script for the editor (U D L R A B S E < > .) |
| `PKBN_TEST_SAVE_ROUNDTRIP` | `1` | runs the save round-trip check |
