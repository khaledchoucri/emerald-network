# 00 — Workspace baseline (2026-10-04)

**Question:** Do the upstream sources build, and where are the key entry points we will depend on?

**Method:** Clean shallow clones at the pinned commits (README). Builds run on Ubuntu 24.04
(gcc 13, SDL2 2.30, 2 cores). Symbols located with grep at the pinned commits.

## Build results

| Target | Command | Result |
|---|---|---|
| pokeemerald-pc_port, native Linux | `make linux -j2` | OK in ~2 min → `pokeemerald64`. Boots headless (`SDL_VIDEODRIVER=dummy`) and runs 8 s without crashing (log shows flash-save sector reads). Warnings only. |
| bn6f, GBA ROM | agbcc `new_layout_with_libs` → `make assets` → `make` | OK. `bn6f.gba: OK`, sha1 `0676ecd4d58a976af3346caebb44b9b6489ad099` matches `bn6f.sha1`. **No baserom needed**: data is in the repo; `bin/tail.bin` is 0 bytes. |
| pokeemerald (pret), GBA ROM | not yet built | — |

## Corrections to earlier (pre-code) assumptions

- The pc_port branch renders at **240×160** — `DISPLAY_WIDTH 240` / `DISPLAY_HEIGHT 160`
  (`upstream/pokeemerald-pc_port/include/gba/defines.h:96-97`). The 426×240 widescreen reported
  on forums is **not** in this branch.
- With `PORTABLE` builds (Makefile sets `PORTABLE := 1` for pc targets, `Makefile:30,34`),
  VRAM/OAM/palette RAM become plain arrays (`include/gba/defines.h:46-85`) but keep GBA sizes:
  `VRAM_SIZE 0x18000`, `OAM_SIZE 0x400`. The Emerald heap is still `HEAP_SIZE 0x1C000`
  (`include/malloc.h:13`). → On PC these are just constants we can raise; the PPU limits remain
  until we render outside the GBA draw path.
- The platform layer lives in `upstream/pokeemerald-pc_port/src/platform/`
  (`sdl2.c`, `gba_easy_draw.c`, `gba_fast_draw.c`, `dma.c`, `bios.c`, `cgb_audio.c`, `system.c`, `win32.c`).

## Emerald (host) — verified anchors (pc_port @ 1165825)

| What | Where |
|---|---|
| Battle init callback | `src/battle_main.c:588` `void CB2_InitBattle(void)` |
| Battle type input | `src/battle_main.c:146` `EWRAM_DATA u32 gBattleTypeFlags` |
| Battle result output | `src/battle_main.c:210` `EWRAM_DATA u8 gBattleOutcome` |
| Wild battle entry | `src/battle_setup.c:393` `BattleSetup_StartWildBattle`; return path `CB2_EndWildBattle` at `:606` |
| Damage formula | `src/pokemon.c:3106` `CalculateBaseDamage(...)` |
| Type chart | `src/battle_main.c:335` `gTypeEffectiveness[336]` |
| Move data | `src/data/battle_moves.h:1` `gBattleMoves[MOVES_COUNT]`; struct `include/pokemon.h:327-338` (effect, power, type, accuracy, pp, secondaryEffectChance, target, priority, flags) |
| Counts | `MOVES_COUNT 355` incl. MOVE_NONE (`include/constants/moves.h:360`); `NUM_SPECIES 412` slots (`include/constants/species.h:420`) |
| Species data | `src/data/pokemon/species_info.h:35` `gSpeciesInfo[]` |

## BN6 (reference) — verified anchors (bn6f @ d57c196)

| What | Where |
|---|---|
| Battle start | `asm/asm00_1.s:5414` `StartBattle` |
| Battle main loop / update | `asm/asm00_1.s:9283` `battle_main_8007800`; `:9640` `battle_update_8007A44 (self: * BattleState $r5)` |
| Battle object tick | `asm/asm00_1.s:70` `RunBattleObjectLogic` |
| Battle → overworld handoff | `asm/asm00_1.s:4468` `HandlesBattleMainUntilEndOfBattleThenTriggersEnterMap` |
| Custom gauge | `asm/asm00_2.s:29833` `SetCustGauge` |
| Chip data table | `data/ChipDataArr.s:2` `ChipDataArr_8021DA8`, 411 `chip_data_struct` entries with named fields (codes, attack_element, mb, attack_family, attack_subfamily, attack_power, lockout_frames, …) |
| Struct layouts | `include/structs/*.inc` (43 files incl. `BattleObject.inc`, `BattleState.inc`, `AIData.inc`, `PanelData.inc`, `NaviStats.inc`) |
| Pseudo-C reading aid | `docs/decomp/*.c` (64 files, ~322k lines) — NOT authoritative, see CLAUDE.md rule 3 |

Naming coverage: of 2,646 functions declared with `thumb_func_start`/`arm_func_start`,
1,530 are still unnamed `sub_XXXXXXX` (~58%). Expect to name things ourselves as we go.

## Open questions → see 01-round1-plan.md
