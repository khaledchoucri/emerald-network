# 02 — Emerald battle contract (R1)

All citations: `upstream/pokeemerald-pc_port` @ 1165825 unless stated.

**Question:** What does Emerald's overworld hand to a battle, and what must a battle hand back,
so we can swap in our own battle module without breaking the game?

**Method:** Traced overworld → battle → overworld for wild and trainer battles by reading
`src/battle_setup.c`, `src/wild_encounter.c`, `src/battle_main.c`, `src/battle_script_commands.c`,
`src/overworld.c`.

## Conclusion (short)

The seam is small and callback-based:

1. The overworld prepares a few globals, stores **where to return** in `gMain.savedCallback`,
   plays a transition, then calls `SetMainCallback2(CB2_InitBattle)`.
2. The battle runs as its own main loop.
3. The battle sets **`gBattleOutcome`**, restores `gMain.callback1`, and calls
   `SetMainCallback2(gMain.savedCallback)`.
4. The overworld's end callback reads `gBattleOutcome` to decide: white-out, or return to field
   (and, for trainers, set the "trainer defeated" flags).

Everything else (EXP, EVs, money, catching, Pokédex, PP/HP) is **written by the battle itself,
directly into save/party data, during the battle**. The overworld never "collects" results.
So our module must perform those writes itself.

## 1. Entry paths

### Wild battle
- Enemy is built **before** the battle, by the overworld: `CreateWildMon` → `ZeroEnemyPartyMons()`
  then `CreateMon…(&gEnemyParty[0], species, level, …)` (`src/wild_encounter.c:379-414`).
- `BattleSetup_StartWildBattle` (`src/battle_setup.c:393`) → Safari or `DoStandardWildBattle` (`:402`):
  locks player controls, freezes NPCs, sets `gMain.savedCallback = CB2_EndWildBattle`,
  `gBattleTypeFlags = 0` (plus `BATTLE_TYPE_PYRAMID` in the Battle Pyramid), starts the transition task,
  increments game stats.
- `Task_BattleStart` waits for the transition, then `SetMainCallback2(CB2_InitBattle)` (`:373`).
- 9 call sites of `BattleSetup_StartWildBattle` in `src/wild_encounter.c` (lines 589–797).

### Trainer battle
- `BattleSetup_StartTrainerBattle` (`src/battle_setup.c:1308`) sets
  `gMain.savedCallback = CB2_EndTrainerBattle` (`:1353`). Opponent ID is in
  `gTrainerBattleOpponent_A` (`:100`), loaded from the trainer's map script.
- **The enemy party is NOT built yet.** It is built inside battle init:
  `CreateNPCTrainerParty(&gEnemyParty[0], gTrainerBattleOpponent_A, TRUE)` in
  `CB2_InitBattleInternal` (`src/battle_main.c:~697`). → Our module must call this itself.

### Other entries (out of scope for POC, listed so we don't forget them)
Roamers (`:422`), Safari (`DoSafariBattle`), scripted/legendary (`StartWallyTutorialBattle`,
`BattleSetup_StartScriptedWildBattle`, `BattleSetup_StartLegendaryBattle`, `StartRegiBattle`,
`StartGroudonKyogreBattle`), the first rival/Birch battle (`CB2_StartFirstBattle`, `:934`),
rematches (`:1398`), Battle Frontier/Tower, link and recorded battles.

## 2. Inputs our battle module receives

| Input | Where set | Notes |
|---|---|---|
| `gBattleTypeFlags` | battle_setup.c (e.g. `:407`) | 0 = normal wild. Flags select safari, trainer, double, legendary, etc. |
| `gEnemyParty[]` | wild: wild_encounter.c:410/414; trainer: built in battle init | |
| `gPlayerParty[]` | save data | modified in place by the battle |
| `gTrainerBattleOpponent_A/_B` | battle_setup.c:100 | trainer ID → party, money reward |
| `gMain.savedCallback` | battle_setup.c `:405`, `:1353`, … | where to go when done |
| Environment | `BattleSetup_GetEnvironmentId()` (battle_setup.c, called from battle_main.c in init) | grass / long grass / sand / water / pond / mountain / cave / building / underwater / plain — **natural source for panel themes** |

## 3. What the real battle does on the way in
- `CB2_InitBattle` (`src/battle_main.c:588`): `MoveSaveBlocks_ResetHeap()`, allocates battle resources.
- `CB2_InitBattleInternal`: clears all VRAM (`CpuFill32(0, VRAM, VRAM_SIZE)`), builds trainer party,
  `gMain.inBattle = TRUE` (`:703`), friendship event for every party member (`:706-707`).
- When ready, the start handler saves the overworld's per-frame callback and replaces it:
  `gPreBattleCallback1 = gMain.callback1; gMain.callback1 = BattleMainCB1;`
  (`CB2_HandleStartBattle`, `:1139`).

## 4. Writes the battle performs (must be replicated by our module)

| Effect | Real implementation |
|---|---|
| HP / PP / status of player mons | battle controller writes into `gPlayerParty` (`SetPlayerMonData`, `src/battle_controller_player.c:1949`) |
| EXP + level-ups | `Cmd_getexp` (`src/battle_script_commands.c:3255`) |
| EVs | `MonGainEVs(&gPlayerParty[…], species)` (`:3420`) |
| Pokédex "seen" | `HandleSetPokedexFlag(…, FLAG_SET_SEEN, …)` (`:4707`) |
| Catching | `Cmd_handleballthrow` (`:9925`), `Cmd_givecaughtmon` → `GiveMonToPlayer` (`:10077-10079`), dex "caught" (`:10107-10118`) |
| Prize money | `Cmd_getmoneyreward` → `AddMoney` (`:5655-5661`) |
| Pickup ability items | `Cmd_pickup` (`:9674`) |
| Post-battle evolution | `gLeveledUpInBattle` → `TryEvolvePokemon` (`src/battle_main.c:5188`) |
| Pokérus spread | `ReturnFromBattleToOverworld` (`:5228`) |
| Roamer HP / deactivate | same function |

## 5. The exit (verbatim behaviour of `ReturnFromBattleToOverworld`, `src/battle_main.c:5228-5259`)
```
gSpecialVar_Result = gBattleOutcome;   // scripts read the result
gMain.inBattle     = FALSE;
gMain.callback1    = gPreBattleCallback1;  // restore overworld per-frame callback
SetMainCallback2(gMain.savedCallback);
```
Note: the pc_port moved `FreeAllWindowBuffers()` earlier to avoid a use-after-free (`:5159-5166`) —
memory-lifetime bugs around this seam are real on PC.

## 6. Outcomes and what the overworld does with them
`gBattleOutcome` values (`include/constants/battle.h:100-110`): WON 1, LOST 2, DREW 3, RAN 4,
PLAYER_TELEPORTED 5, MON_FLED 6, CAUGHT 7, NO_SAFARI_BALLS 8, FORFEITED 9, MON_TELEPORTED 10.

- `IsPlayerDefeated` (`src/battle_setup.c:1003`): LOST and DREW → defeated; all else → not.
- `CB2_EndWildBattle` (`:606`): clears BG palette + OAM, then `CB2_WhiteOut` if defeated, else
  `CB2_ReturnToField`.
- `CB2_EndTrainerBattle` (`:1363`): if won → `RegisterTrainerInMatchCall()` and
  **`SetBattledTrainersFlags()`** (`:1281`) — so trainer flags are the overworld's job, not ours.
- White-out (`src/overworld.c:358`): halves money, heals party, warps to last heal spot.

## Implications for our battle module
- Minimum contract: read the inputs above → run → write `gBattleOutcome` (+ party/save writes from §4)
  → restore `gMain.callback1` → `SetMainCallback2(gMain.savedCallback)`.
- The return path reloads the map, and real battles clear VRAM on entry — so the battle screen
  can use video memory freely (to confirm in POC-0).
- We can reuse Emerald's own helpers for the writes instead of re-implementing them:
  `CreateNPCTrainerParty`, `MonGainEVs`, `GiveMonToPlayer`, `HandleSetPokedexFlag`, `AddMoney`,
  `GetTrainerMoneyToGive`, `GetEvolutionTargetSpecies`/`EvolutionScene`. (Several are `static` in
  battle_script_commands.c — exposing them is a small patch; the EXP logic in `Cmd_getexp` is
  interleaved with battle UI and will need extracting.)

## Open questions
- Does `CB2_ReturnToField` fully reload overworld graphics after a module that bypasses the GBA
  renderer? (POC-0)
- Is it safe to skip `gMain.inBattle` / `gPreBattleCallback1` for a one-frame stub, or must the stub
  mirror them? (POC-0 will mirror them to be safe.)
- Extracting EXP gain from `Cmd_getexp` (`:3255-~3440`) without its message/animation states.
