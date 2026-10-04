# POC-0 — battle stub (does our module own the battle seam?)

**Patch:** `poc/patches/0001-POC-0-…patch` (applied on pc_port @ 1165825 by `scripts/setup_host.sh`)

## What it does
- `src/battle_setup.c` (`Task_BattleStart`): plain wild battles (`gBattleTypeFlags == 0` and
  `gMain.savedCallback == CB2_EndWildBattle`) go to `CB2_PkbnBattleStub` instead of `CB2_InitBattle`.
  All other battles (trainers, first Birch battle, legendaries, safari, frontier…) stay vanilla.
- `src/pkbn/battle_stub.c` mirrors the contract from research/02:
  entry (save/clear `callback1`, `inBattle`), Pokédex "seen", ~30 frames of "battle",
  `gBattleOutcome = WON`, wild EXP to the lead mon (`expYield * level / 7`) + EVs + stat recalc,
  exit (`gSpecialVar_Result`, restore `callback1`, `SetMainCallback2(gMain.savedCallback)`).
- `PKBN_STUB=0` env var → vanilla battles, for A/B comparison.
- Logs to the terminal as `[pkbn] …` (Linux build).

## Build (WSL)
```
cd /mnt/c/Users/Khaled/source/repos/pokemon-battle-network
sudo apt install build-essential git pkg-config libpng-dev libsdl2-dev
bash scripts/setup_host.sh
cd ~/pkbn/emerald-host && ./pokeemerald64
```
Needs WSLg (Windows 11 or recent Windows 10 WSL) for the window. Windows .exe alternative:
`bash scripts/setup_host.sh windows` (untested on my side — archive.org, where INSTALL_PC.md hosts SDL2 2.0.16, was blocked from my sandbox).

Keys: arrows, Z = A, X = B, Enter = Start, \ = Select, A/S = L/R, hold Space = 5× speed, Ctrl+R reset.
Save file `pokeemerald.sav` is written in the folder you run from.

## Test checklist (report results back)
1. New game → get the starter via the Birch rescue (that battle is vanilla, not stubbed).
2. Walk in Route 101 grass until an encounter.
   - [ ] Transition plays, ~0.5 s black, back on the field — no softlock, player can move.
   - [ ] Terminal shows `[pkbn] wild battle: species … Lv …` and `[pkbn] lead slot 0 gained N exp`.
3. Open the party summary: [ ] EXP/level went up after several encounters; [ ] stats recalculated on level-up.
4. Pokédex: [ ] encountered species show as **seen**.
5. Do ~20 encounters, then save, quit, reload: [ ] save loads, party/dex state persisted.
6. A/B: `PKBN_STUB=0 ./pokeemerald64` → [ ] normal battles still work.
7. Talk to a trainer: [ ] trainer battle is vanilla and still works.

## Known gaps (by design for POC-0)
No evolution after level-up, no new moves learned at level-up, no Exp. Share/traded boost, no
catching, no money — those come with the real battle module.
