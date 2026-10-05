# 07 — NaviCust: every Pokémon is a Navi

Status: **implemented in POC-9.**

Decisions (2026-10-05):
- 5×4 board.
- The 15 BN6 core programs, plus stat programs translated from Pokémon items, vitamins and abilities.
- Everything unlocked for now.
- The ability is a built-in program.
- Program colours are types.
- Pokéblocks (conditions) compress programs.
- Pokérus is a "good bug".
- Not done: a board that grows.

## 1. Board (BN6's)

**Size.** 5 wide × 4 tall: BN6's middle board template `byte_813B2CD` (bn6f data/dat36.s:1340).

**Command line.** The 3rd row (board y=2). That is row 3 of BN6's 7×7 space (asm/asm37_0.s:732).

**Frame.** A ring of cells around the board, corners excluded. A program part placed there runs but causes a bug, as BN6's overhang does.

**Run ("compile").** Mirrors `sub_813BBD4` (asm/asm37_0.s:702).

Bug sources:
- A **plus** part on the command line.
- A **normal** part off the command line.
- Two parts of the same colour touching.
- A part on the frame.
- Too many colours. BN6 allows 4; at 5 it adds bug type 11 +1, and at 6 or more bug type 12 +2.

Bug rules:
- Bug levels cap at 3.
- BugStop clears all bugs.
- Order: the command line runs right → left (exclusive groups: the first one wins), then plus parts run.

**Caps** (`src/pkbn/navicust.c`, TUNE):

| what | cap |
|---|---|
| extra chips in hand | 3 (BN6 Custom level 8 = 5 + 3) |
| buster levels | 1–5 |
| HP | +50% |
| each stat | +30% |
| each type | +30% |
| Scope Lens stages | 2 |

## 2. The Pokémon twist

**The ability is a program.** Its cells are placed first, on the command line from the left, and can't be moved. The cell count comes from the ability's weight (1–3, `gPkbnAbilityCells`). Some abilities also grant a BN effect:

| ability | grants |
|---|---|
| Levitate | FloatShoes + AirShoes |
| Sturdy | UnderShirt |
| Inner Focus | SuperArmor |

**Colours are types.** Every program comes in 1–3 type colours; SELECT picks one while you're placing it. **Colours matching the Pokémon's own types never bug.** They don't count toward the colour limit and can touch each other. A Fire Pokémon can stack red programs; anyone else has to spread them out.

**Pokéblocks compress.** Each program is tied to one condition (Cool, Beauty, Cute, Smart or Tough). At **80 or more** in that condition (TUNE), the program uses its smaller shape, BN6's compressed shape. A well-fed Pokémon fits more.

**Pokérus is a good bug.** While Pokérus is active (low nibble of `MON_DATA_POKERUS` is not 0):
- the colour limit goes from 4 to 5;
- every bug level drops by 1.

## 3. Programs (48)

**The 15 BN6 programs**, with BN6's shapes and compressed shapes, read from `StructArr_813944C`:

| program | effect |
|---|---|
| SuperArmor | no flinch, no knock-back |
| Custom1 / Custom2 | +1 / +2 chips in hand |
| FirstBarrier | start every battle behind a barrier |
| FloatShoes | panels don't affect you |
| AirShoes | you can stand on broken panels |
| UnderShirt | 1 HP survival |
| BugStop | clears all bugs |
| BustPack | buster Attack, Speed and Charge +3 |
| Attack+1, Speed+1, Charge+1 | buster +1 each |
| HP+50 / 100 / 200 | max HP +5 / 10 / 20% in battle |

**From Pokémon** (Gen 3 numbers from `src/data/items.h` and `src/pokemon.c`):

| group | programs |
|---|---|
| Vitamins | +10% to one stat |
| Held items | Quick Claw (shorter chip lockout), King's Rock (flinch), Scope Lens (crit), BrightPowder (dodge), Leftovers (1/16 HP per turn), Shell Bell (1/8 of damage dealt), Focus Band (10% survive), Choice Band (Attack ×1.5, one chip per Custom), Lucky Egg, Amulet Coin |
| Type items | 17 programs, +10% each |

All 48 are listed in `tools/navicust_curated.py`; the generator writes `src/pkbn/ncp_table.c`.

## 4. Bugs in battle

| bug | effect |
|---|---|
| HP | lose HP every 160/140/120 frames |
| move | random step every 300/240/180 frames |
| panel | cracks under you, chance (lvl+1)/8 per step |
| custom | hand shrinks from turn 5−lvl, minimum 2 |
| buster | misfire table from BN6 |
| status | random PAR/PSN/BRN/confusion at battle start |
| collect | halves prize money |

## 5. Storage

**Navi ID.** Each Pokémon's ID is stored in `BoxPokemon.unknown` (`MON_DATA_ENCRYPT_SEPARATOR`). That field is unencrypted and outside the checksum (src/pokemon.c:2790/3827), so vanilla code ignores it.

**Layouts.** They live in the sidecar `pkbn.sav` next to `pokeemerald.sav` (62 KB).
- Written on every save, read on load, reset on a new game.
- When it's full, layouts no party or box Pokémon references are freed.
- The round-trip self-test is `PKBN_TEST_SAVE_ROUNDTRIP=1`.

## 6. Editor

**Opening it.** Party menu → **NAVICUST**, shown for any non-egg outside the Battle Pike.

**Screen.**
- Left: the board.
- Right: the program list.
- Below: a preview and a description.

**Controls.**

| where | key | action |
|---|---|---|
| list | A | pick a program |
| list | LEFT | edit the board |
| list | START | RUN |
| list | B | leave |
| placing | L / R | rotate |
| placing | SELECT | colour |
| placing | A | put down |
| board | A | pick up a part |

RUN shows "OK! NO BUGS" or the list of bugs, plus the resulting stats.
