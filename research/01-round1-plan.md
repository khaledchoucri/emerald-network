# 01 — Round 1 R&D + POC plan

Goal of round 1: prove the two seams we depend on, using only the code.

## R1. Emerald battle contract (host side) — DONE → 02-emerald-battle-contract.md
What does the overworld hand to a battle, and what does it read back?
- Trace every path into `CB2_InitBattle`. Direct `SetMainCallback2(CB2_InitBattle)` sites at pc_port @1165825:
  `src/battle_setup.c:373, :944`, `src/battle_main.c:1955`, `src/battle_tower.c:2002`, `src/cable_club.c:871, :937`,
  `src/recorded_battle.c:519`, `src/union_room_battle.c:73`. Wild/trainer battles from the overworld may also
  arrive via battle-transition tasks — confirm.
- Inputs: `gBattleTypeFlags`, enemy party, trainer IDs, `gMain.savedCallback`, etc.
- Outputs: `gBattleOutcome`, player party HP/PP/status/EXP/EVs, caught-mon path, trainer flags, money.
- Deliverable: research/02-emerald-battle-contract.md (cited).

## R2. BN6 battle loop and chip model (reference side)
- Read `StartBattle` → `battle_main_8007800` → `battle_update_8007A44`; map the per-frame order.
- Decode `chip_data_struct` fields; check whether `attack_family`/`attack_subfamily` work as reusable
  attack "shapes" (UNVERIFIED hypothesis — this would ground our move-shape templates).
- Custom gauge timing (`SetCustGauge` and callers): frames to fill, what modifies it.
- Deliverable: research/03-bn6-battle-loop.md (cited, asm-confirmed).

## R3. Rendering path in the PC port
- How `src/platform/sdl2.c` presents frames; where a non-GBA renderer could draw a battle screen.

## POC-0 (after R1): "battle stub" — PASSED (play-tested 2026-10-04) → poc/POC-0.md
In a copy of the host (poc/, never upstream/), replace the wild-battle entry with a stub module that
immediately returns a win and writes back the outputs found in R1. Success = overworld continues
correctly (no softlock, party state consistent, save works).

## POC-1 (after R2): grid sandbox
Standalone SDL program: 6×3 grid, one Pokémon on each side, buster + 4 move-chips, using real values
read from Emerald data (`gSpeciesInfo`, `gBattleMoves`, `CalculateBaseDamage`).
