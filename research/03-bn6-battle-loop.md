# 03 — BN6 battle loop, chip model, Custom gauge (R2)

All citations: `upstream/bn6f` @ d57c196. Ground truth = assembly (CLAUDE.md rule 3).

**Question:** How does BN6 run a battle frame, how is a chip turned into an attack, and how does the
Custom gauge fill? In particular: is `attack_family` a reusable "attack shape" we can map Pokémon moves onto?

## Conclusion (short)
- **Yes — with a refinement.** A chip's `AttackFamily` becomes the battle object's `CurAction`, and
  actions ≥ 0x10 dispatch into a table of **79 attack routines** (`AIAttackJumptable`). `AttackSubFamily`
  and four `AttackParam` bytes parameterise the routine. So the reusable unit is
  **(family routine, subfamily, params)**: 411 chips → 47 families → 184 family/subfamily pairs.
- Some families are true shapes (Cannon, Sword, Vulcan, Spreader, Bomb), others are catch-alls
  (0x15: 84 chips; 0x1B: 70 chips = Navi chips). Our move templates should copy the *structure*
  (routine + params), not assume one family = one shape.
- Custom gauge: a single u16 in EWRAM (`eStruct2035280 + 0x20`), capped at 0x4000.

## 1. Chip data
- Layout: `include/rom_structs/ChipData.inc:3-36`, 0x2C bytes per chip. Fields: Codes (u32, 0x0),
  AttackElement 0x4, Rarity 0x5, ChipElement 0x6, LibraryType 0x7, MB 0x8, EffectFlags 0x9,
  StaminaDamageCounterFrames 0xA, **AttackFamily 0xB**, **AttackSubFamily 0xC**, DarkSoulUsage 0xD,
  LockOnEnable 0xF, **AttackParam1-4 0x10-0x13**, LockoutFrames 0x14, …, **AttackPower u16 0x1A**,
  icon/image/palette pointers 0x20-0x28.
- Table: `data/ChipDataArr.s:2` `ChipDataArr_8021DA8`, **411 entries** (counted).
  Note: the comment `[*const ChipData; 206]` at `asm/asm02.s:6` is wrong — an example of why we verify.
- Accessor: `getChip8021DA8` (`asm/asm02.s:4-10`) = `&table[idx * 44]`.
- Names: `data/textscript/TextScriptChipNames0.s` + `…Names1.s` (355 strings). Index alignment with the
  table checked on samples: Cannon 40 / HiCannon 100 / M-Cannon 180, Vulcan1-3 10/15/20, Sword 80,
  AquaNdl1 element 2, CornSht1 element 4, BlkBomb element 1. Entries 355-410 have no name in these files.
- AttackElement values seen: 0 (320 chips), 1 (27), 2 (22), 3 (22), 4 (20). Samples are consistent with
  1 = Fire, 2 = Aqua, 4 = Wood; **3 = UNVERIFIED** (Elec expected but TenguMan has 3).
- 46 chips have non-zero LockoutFrames.

## 2. How a chip becomes an attack
1. Code reads the chip and copies its fields into the attacker's attack variables, e.g. `sub_80129A6`
   (`asm/asm00_2.s:8341-8366`) and the AI path at `asm/asm03_0.s:14845-14866`:
   SubFamily → `AIAttackVars_Unk_03`, Params → `Unk_0c`, AttackPower → `Damage`,
   LockoutFrames → `+5`, then `ldrb r0,[chip,#0xb]` (AttackFamily) → `object_setAttack0..5`.
2. `object_setAttackN` (`asm/asm00_2.s:5557-5600`) stores it in `oBattleObject_CurAction` and resets phase.
3. `RunAIAttack` (`asm/asm00_2.s:~24779-24800`): if `CurAction >= 0x10`, call
   `AIAttackJumptable[CurAction - 0x10]` (`asm/asm31.s:107582`, 79 entries). Named examples:
   `megamanChargeShotAiAttack` (0x16), `bubbleShotAttack` (0x25), `tornadoAiAttack` (0x2F),
   `greatfirePossiblyOthersAiAttack` (0x35), `airspinAttack` (0x38), `aquaSpiralAiAttack` (0x3A).
4. Player Navi per-frame update `playerObject_update_80EA484` (`asm/asm31.s:107072-107096`) runs the
   AI-attack path via `PlayerObjectAIAttackJumptables` — the player and AI share the attack machinery.

Families with most chips (count): 0x15 (84), 0x1B Navi chips (70), 0x1C (54, incl. MegaBuster),
0x14 Cannon-like (45), 0x13 Sword (17), 0x12 Bomb/Seed (16). Single-purpose families include
Vulcan 0x17, Spreader 0x25, TankCannon 0x24, AirShot 0x21, Recover 0x20.

## 3. Battle frame order
`battle_update_8007A44` (`asm/asm00_1.s:9640-9774`), per frame when not terminating:
mode handler from `off_8007B50` (normal mode → `sub_8009158`) → `RunBattleObjectLogic` →
`camera_802FFF4` → `panel_800BFC4` → `setChipsForPlayerObjects_800FDC0` → (unnamed subs) →
`handleVariableDamageChip_800AEE8` → frame counters (skipped while paused / time-stopped) →
a fixed list of unnamed subs (rendering/sprites likely, UNVERIFIED).
Battle modes: `constants/enums/battle_constants.inc` (NORMAL, CROSSOVER, tutorials, VIRUS_BATTLER, …);
`BATTLE_ACTORS_PER_SIDE = 4`.

## 4. Custom gauge
- Storage: `eStruct2035280 + 0x20` (u16). `SetCustGauge` clamps to 0x4000 (`asm/asm00_2.s:29833-29846`);
  add/sub helpers `sub_801DFB8` / `sub_801DFD0` (`:29848-29877`); getter `sub_801DFE4`.
- Fill: battle state `sub_800855E` adds **0xD per frame unless time-stop** (`asm/asm00_1.s:11096-11100`).
  If that is the only increment, a full gauge = 0x4000 / 0xD ≈ 1260 frames ≈ 21 s. **UNVERIFIED** —
  other modifiers (Custom1/2, fast/slow gauge, "full" threshold) not found yet.

## 5. Battle objects and panels
- `include/structs/BattleObject.inc`: CurAction 0x9, Element 0xE, PanelX/Y 0x12-0x13,
  FuturePanelX/Y 0x14-0x15, Alliance/DirectionFlip 0x16-0x17, ChipsHeld 0x1A, HP/MaxHP 0x24-0x26,
  Chip 0x2A, Damage 0x2C, fixed-point X/Y/Z + velocities 0x34-0x48.
- `include/structs/PanelData.inc`: per-panel Type 0x2, Alliance 0x3, Flags 0x14 (documented bits:
  blocks movement, enemy panel, ally/enemy support object, ally/enemy attack object).
  **Panel type values (grass/ice/lava…) are not named in the repo yet.**

## Implications for our design
- Model each Pokémon move as **(routine, subfamily, params, power, element, lockout)** — the same shape
  BN6 uses. Our ~20 "shape templates" ≈ a curated subset of BN6's routines.
- BN6's routines are code, not data: we re-implement the few we need in C, using these asm routines
  as the reference for timing and hit patterns.

## Open questions (next R&D)
1. Real gauge fill time — **measure in mGBA**: build `bn6f.gba`, watch u16 at `0x020352A0`
   (= `eStruct2035280+0x20`, UNVERIFIED address arithmetic) during a battle.
2. What family 0x15 and 0x1C actually do per subfamily (largest families).
3. Panel type enum values and their effects (grass/ice/lava/holy…).
4. How damage is applied (Element vs AttackElement, counters, guard) — trace `Damage` writes.
