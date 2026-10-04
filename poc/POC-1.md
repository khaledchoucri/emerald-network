# POC-1 — real-time grid battle (is it fun?)

**Patch:** `poc/patches/0002-POC-1-…patch` (on top of 0001; `scripts/setup_host.sh` applies both).
Plain wild battles now open a Battle Network–style 6×3 grid battle. Trainers etc. stay vanilla.

## How to play
| Key | Action |
|---|---|
| Arrows | move on your 3×3 (red) side |
| X (B) | Buster — 1 damage shot down your row (BN6 MegaBuster power) |
| Z (A) | in fight: use the next queued move · in Custom: add the highlighted move |
| Left/Right | Custom: choose move |
| X (B) in Custom | undo last pick |
| Enter (Start) | Custom: confirm and fight |
| A/S (L/R) | open Custom when the gauge is full |
| \ (Select) | run |

Flow: battle opens on the Custom screen → pick moves → fight. Enemy telegraphs its attacks by flashing
the panels it will hit (orange) — step out of them.

## What is grounded in the code
- **Damage:** Emerald's `CalculateBaseDamage` (`src/pokemon.c:3106`) + the exact STAB, type-chart and
  85–100% random steps of `Cmd_typecalc` / `ApplyRandomDmgMultiplier`
  (`src/battle_script_commands.c:1355, 1639`). Real stats, abilities, held items, Levitate.
- **Moves/PP/names/icons:** `gBattleMoves`, `gMoveNames`, `gSpeciesNames`, Pokémon icon graphics +
  palettes (`src/pokemon_icon.c`). PP is spent per use and written back to the party.
- **Contract:** same entry/exit as POC-0, plus HP/PP write-back, battle resources allocated/freed like
  `CB2_InitBattle` (`battle_main.c:588-592`).
- **Shapes:** modelled on BN6 chip families (research/03): Cannon 0x14, LongSword (0x13 sub 2, reach 2),
  Spreader 0x25.

## Design decisions (ours, to judge by playing)
- Move → shape: power 0 (status moves) = not usable yet; contact moves = LongSword; moves that hit both
  foes = Spreader; everything else = Cannon.
- Hand = your lead Pokémon's damaging moves with PP left (no random draw / folder yet).
- Accuracy and move side-effects (burn chance, Absorb drain, stat drops…) are ignored — aiming replaces accuracy.
- Tunables (`TUNE` in `src/pkbn/grid_battle.c`): Custom gauge 8 s, buster every 20 frames,
  45 invincibility frames after being hit, enemy attacks every ~2–3 s scaled by its Speed, 0.6 s telegraph.

## Modes
- default → grid battle · `PKBN_MODE=stub` → POC-0 instant win · `PKBN_MODE=vanilla` (or `PKBN_STUB=0`) → normal battles.
- Headless self-test (what I ran): `PKBN_SELFTEST=1 SDL_VIDEODRIVER=dummy ./pokeemerald64`
  or `PKBN_SELFTEST="283:10,288:5"` (species:level for player,enemy); add `PKBN_DUMP_DIR=dir` to save frames.

## Self-test results (2026-10-04, Linux, autopilot)
| Player vs wild | Result | Notes |
|---|---|---|
| Torchic L7 vs Zigzagoon L4 | WON, 21/24 HP, +34 EXP | Zigzagoon Tackle 3 dmg |
| Mudkip L10 vs Zigzagoon L5 | WON, 31/31 HP, +42 EXP | Mud-Slap 6, Water Gun 12 (STAB) |
| Treecko L8 vs Poochyena L5 | WON, 21/25 HP, +39 EXP | Absorb 6; Tackle 4 |
Screens: `poc/screens/`.

## Play-test checklist (Khaled)
- [ ] Wild encounter opens the grid battle; Custom screen lists your moves.
- [ ] Moving, buster, using moves all respond well; telegraphed enemy attacks are dodgeable.
- [ ] Win → victory music → back on the field with EXP; HP/PP changes persist in the party menu.
- [ ] Lose → white-out works. Run (Select) works.
- [ ] Gut check: is it fun? What feels off (speed, damage, buster, gauge, telegraph)?

## Known gaps
No catching, no switching/party in battle (if your lead faints you white out even if others can fight), no status moves or move effects, no evolution/move learning
on level-up, 1 wild Pokémon only, placeholder graphics (icons + flat panels), no Exp. Share.
