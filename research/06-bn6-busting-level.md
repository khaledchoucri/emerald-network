# MMBN6 (bn6f): Busting Level and post-battle reward selection

Source: the disassembly at `/home/claude/bn6f`. Every claim cites file:line. Anything marked **UNVERIFIED** is inferred and not shown directly by the instructions. `sub_XXXX` names are unnamed functions; their behaviour was read from the instructions.

---

## 1. Who calls the busting computation, and with what arguments

`sub_800AF84` (asm/asm00_1.s:17153-17180) builds the arguments and calls `sub_800AC20`:
- If `GetBattleEffects() & 0x8` (`BATTLE_EFFECT_NETWORK_BATTLE`, constants/enums/battle_constants.inc:2-5, bit 3) is set, then **r0 = 2** and r1 = the local side's alliance (`oBattleState_Unk_0d`, XOR 1 unless `sub_800A832()==1`) (asm/asm00_1.s:17165-17176).
- Otherwise r1 = 0. r0 = 1 if `GetBattleEffects() & 1` (`BATTLE_EFFECT_BOSS_RANK`, battle_constants.inc:2) is set, else r0 = 0 (asm/asm00_1.s:17158-17163).
- The result is stored in `oBattleState_Unk_1e` (asm/asm00_1.s:13044, 13080 and others).

So the **battle type** index is: 0 = normal (virus) battle, 1 = "boss rank" battle, 2 = network battle.

## 2. `sub_800AC20`: the busting level (asm/asm00_1.s:16678-16928)

- Mask = `0x18F` (bits 0,1,2,3,7,8), or `0xF1` (bits 0,4,5,6,7) when r0==2 (asm/asm00_1.s:16681-16684). The mask is shifted right once per component, and the carry decides whether that component is applied (e.g. 16692, 16720).
- Accumulator `[sp+4]` starts at 0.
- r1 (alliance) is stored to `[sp+0x14]`, which after `sub sp,#0x14` overlaps the saved r4 slot. The caller's r4 therefore comes back as the alliance. This is a harmless quirk (asm/asm00_1.s:16679-16680, 16687).

### Per-battle counters
`sub_800AB3A(side, idx)` reads `byte_203EAE0[side*16 + idx]` (asm/asm00_1.s:16541-16547).
- Writers: `sub_800AB2E` sets a counter (16531-16537), `sub_800AB46` adds with a cap of 255 (16551-16563), `sub_800AB5C` subtracts with a floor of 0 (16567-16577).
- `zeroFill_800AB70` clears 0x20 bytes, i.e. both sides (16580-16586).

### Component table

| bit | used in | what it reads | points | evidence |
|---|---|---|---|---|
| 0 | all | battle timer (frames, BCD-converted) vs a per-type threshold table | see §2.1 | 16691-16718 |
| 1 | non-net | counter 3 = times your Navi entered a hit-reaction state | n<4: `1-n` (0→+1, 1→0, 2→-1, 3→-2); n≥4: -3 | 16720-16738 |
| 2 | non-net | counter 4 = number of panel moves | n≤2: +1, else 0 | 16740-16754 |
| 3 | non-net | `oBattleState_Unk_1b` = largest multi-delete | `(m-1)*2`: single 0, double +2, triple +4, quadruple +6 | 16756-16767 |
| 4 | net only | own HP vs max HP | HP<max/2: 0; <max/2+max/4: +1; <max: +2; full: +3 | 16769-16796 |
| 5 | net only | counter 5 = Recovery-chip uses | 0→0, 1→-1, 2→-2, ≥3→-4 | 16798-16825 |
| 6 | net only | MaxHP difference vs opponent | see §2.6 | 16827-16866 |
| 7 | all | counter 8 = Counter Hits landed | `+min(n,3)` | 16868-16882 |
| 8 | non-net | counter 0xB = "transformation completed" flag | +1 if 0 (never transformed) | 16884-16895 |

**Final clamp** (asm/asm00_1.s:16897-16907): a sum ≤ 0 becomes **1**, and a sum > 11 becomes **11**. Range: 1..11. (**UNVERIFIED**: that 11 is shown as "S".)

### 2.1 Time (bit 0)
- `sub_800A704` returns `oBattleState_Unk_40` (asm/asm00_1.s:15803-15807).
- The timer is incremented by `sub_800A6A6` only when the battle is not time-stopped, paused or over, and battle flag bit 0 is set. It is capped at `0x8C9F` = 35999 frames (asm/asm00_1.s:15753-15775).
- **UNVERIFIED**: that `sub_800A6A6` runs once per frame. It is called from the main battle loop next to `sub_800AE0C` (asm/asm00_1.s:10451-10452, 11051-11052).
- `memory_bcd_8000D84` (asm/asm00_0.s:1414-1460):
  - `sub_8000DE0` splits frames into hours (/216000 = 0x34BC0), minutes (/3600), seconds (/60) and leftover frames (asm/asm00_0.s:1462-1487).
  - The leftover frames become hundredths (`f*100/60`).
  - Each field is BCD-converted and packed as `0xHHMMSScc`. Input above 0x1499727 gives 0x99595999 (1418-1421, 1427-1452).
- Compare loop (asm/asm00_1.s:16698-16718): `idx` = the first threshold with `time <= thr`, else 3. Points = `byte_800AE00[type*4 + idx]`.

`off_800ADDC` (asm/asm00_1.s:16918-16923), 3 words (12 bytes) per type, decoded as BCD:

| type | thr0 | thr1 | thr2 | points (≤thr0 / ≤thr1 / ≤thr2 / slower) — `byte_800AE00` (16924-16927) |
|---|---|---|---|---|
| 0 normal | 0x500 = 5.00 s | 0x1200 = 12.00 s | 0x3600 = 36.00 s | 6 / 5 / 4 / 3 |
| 1 boss rank | 0x3000 = 30.00 s | 0x4000 = 40.00 s | 0x5000 = 50.00 s | 10 / 8 / 6 / 4 |
| 2 network | 0x3000 = 30.00 s | 0x4500 = 45.00 s | 0x10000 = 1:00.00 | 10 / 8 / 6 / 4 |

### 2.2 Counter 3: "hits" (bit 1)
- The only writers are `sub_800AB46(alliance, 3, 1)` in the player state handlers `sub_80174FE` (flinch), `sub_80175B8` (paralyze), `sub_8017688` (freeze), `sub_8017768` (bubble) and `sub_80178D4` (push, sub-phase 0). See asm/asm00_2.s:18305-18308, 18381-18384, 18480-18483, 18578-18581, 18735-18738.
- The state roles come from the jump table comments at asm/asm31.s:107129-107137.
- **So it counts hits that put MegaMan into a flinch, paralyze, freeze, bubble or push state.** It does not count all damage.
- **UNVERIFIED**: that every damaging hit goes through one of these states.

### 2.3 Counter 4: "moves" (bit 2)
- `sub_80EB088`, the first phase of AI-attack 0x10 (`AIAttackJumptable[0]`, asm/asm31.s:107583), calls `sub_800AB46(alliance,4,1)` after a valid destination panel is reserved (asm/asm31.s:108036-108088).
- This is the player's panel-move action.

### 2.4 `Unk_1b`: multi-delete (bit 3)
- Enemy deletion phase `sub_801664E` calls `sub_800AE44` (asm/asm00_2.s:16402-16409).
- `sub_800AE44` does `Unk_1c++` and sets `Unk_1d = 10` (asm/asm00_1.s:16964-16972).
- `sub_800AE0C` (asm/asm00_1.s:16931-16960):
  - If `Unk_1c > Unk_1b`, then `Unk_1b = Unk_1c`. If that is ≥2 and battle mode ≠ 6, it calls `sub_801E228(Unk_1c-2)`.
  - `Unk_1d` counts down. At 0 it resets `Unk_1c = 0`.
  - So deletes within a 10-tick window chain together.
- `sub_801E228` remaps 2 to 0x13 (asm/asm00_2.s:30223-30228) and prints text from `TextScript86F0374`: 0 = " DOUBLE DELETE!", 1 = " TRIPLE DELETE!", 0x13 = "QUADRUPLE DELETE!" (data/textscript/TextScript86F0374.s).
- `Unk_1b` is set to 1 at battle init (asm/asm00_1.s:8408). It is battle-wide, not per side.

### 2.5 Counter 5: Recovery chips (bit 5, net only)
- AI-attack 0x20 `sub_80EC844` (asm/asm31.s:107599, 111023-111045) heals by `byte_80EC870[param]` = 10, 30, 50, 80, 120, 150, 200, 300, 1000 through `sub_800E2FC`, which calls `object_addHP` (asm/object.s:4685-4699). It then increments counter 5.

### 2.6 MaxHP difference (bit 6, net only)
- `d = |myMax - oppMax| / 100`. If d > 1, round down to even and cap at 4. The possible values are 0, 1, 2 or 4.
- The sign is **+** if your MaxHP is lower and **−** if it is higher (asm/asm00_1.s:16834-16866).

### 2.7 Counter 8: Counter Hits (bit 7)
- `sub_801A45C` runs when the collision flags have 0x40. It increments counter 8 for the **attacker** (`alliance^1` of the object that was hit), clears `oCollisionData_CounterTimer` and calls `sub_801E270` (asm/asm00_2.s:22012-22044).
- The "  COUNTER HIT!" string is entry 14 of TextScript86F0374. **UNVERIFIED**: that `sub_801E270` displays it.

### 2.8 Counter 0xB: transformation (bit 8)
- It is set to 1 (not incremented) in the last phase of the transformation sequences dispatched by `sub_8014A38` on the "transformation" byte from `sub_801595E` (asm/asm00_2.s:13015-13090, 14785-14793). The writes are:
  - `sub_8014CC0` (forms 1..0xA, 13306-13323)
  - `sub_8015128` (forms 0xD..0x16 with stat 0x2c ≤10, 13822-13839)
  - `sub_80155CC` (forms 0xD..0x16 otherwise, 14364-14381)
- Bonus +1 only if it is still 0, i.e. **no Cross/Beast transformation completed**.
- **UNVERIFIED**: mapping 1..10 to Crosses, 0xB/0xC to Beast Out, and so on. Forms 0xB-0xC and 0x17-0x18 set **counter 2** instead (asm/asm00_2.s:13427, 13688, 13968). Counter 2 is not part of the busting level; it gates a BeastOutCounter (stat 0x21) increment at asm/asm00_1.s:10049-10061.

Maximum raw scores: normal 6+1+1+6+3+1 = 18; boss 10+1+1+6+3+1 = 22; net 10+3+0+4+3 = 20. All of these clamp to 11.

---

## 3. Rewards

### 3.1 Collection (`sub_802C8FA`, asm/asm03_0.s:13083-13163)
- Stores the type, the time (`[r7+4]`) and the busting level L (`[r7+1]`, from `Unk_1e`, 13105).
- For non-network battles it calls `sub_80AA8E0(list, count, L, HP, MaxHP, alliance)` (asm/asm03_0.s:13127):
  - `list` = `BattleState+0x4C+8*enemySide` (u16 enemy NameIDs)
  - `count` = `BattleState[8+enemySide]`
- `sub_80077D2` appends each spawned enemy's `oBattleObject_NameID` to that list and increments the count (asm/asm00_1.s:9256-9272).
- Result: reward1 goes to `[r7+8]` and reward2 = `oBattleState_Unk_36` goes to `[r7+0xA]` (asm/asm29.s:10773-10796).
  - `Unk_36` is written by `sub_80DA974` from an object's Param1 (asm/asm31.s:73181-73189). **UNVERIFIED**: which object, likely a special bonus drop.
- If the count is 0, both rewards are 0 (asm/asm29.s:10780-10781).
- Network battles use `sub_80AAC8C` instead (asm/asm03_0.s:13133; asm/asm29.s:11297). Not decoded here.

### 3.2 Reward list per enemy
- `sub_80AAE98(id)` = `byte_80AAEA8 + id*0x28`: **20 u16 entries per enemy NameID** (asm/asm29.s:11590-11599; data/dat29.s:2).
- Entries 0-9 are the **normal half**. Entries 10-19 are the **low-HP half**.

### 3.3 Selection (`sub_80AA910`, asm/asm29.s:10801-10938)
Branch on NaviStats byte 0x26 (asm/asm29.s:10810-10814):

**(a) Normal (no 0x26 flags)** (10833-10851):
1. Pick a random enemy: `list[RNG % count]` (`sub_80AAA3C` mode 0, 10960-10971).
2. Compute the byte offset with `sub_80AAA98(L, HP, MaxHP, 0)` (asm/asm29.s:11011-11048):
   ```
   rng   = GetPositiveSignedRNG()
   low   = (HP <= 3*(MaxHP>>3)) ? 0x14 : 0          ; HP <= 37.5% (floored)
   col   = (rng >> 16) & 0xF
   sub   = ((rng >> 8) & 1) * 2
   off   = byte_8020B9C[L*16 + col] + sub + low      ; byte offset into the 20-entry list
   entry = off/2
   ```
   So `entry = 2*tier + (0|1) + (lowHP ? 10 : 0)`, with tier from this table.

`byte_8020B9C` (data/dat01.s:200-212), 16 columns per L, decoded as tier = value/4:

| L | tier distribution (out of 16) | entries (normal / low HP) |
|---|---|---|
| 0-3 | t0 ×16 | 0-1 / 10-11 |
| 4 | t0 ×8, t1 ×8 | 0-3 / 10-13 |
| 5 | t1 ×8, t2 ×8 | 2-5 / 12-15 |
| 6 | t2 ×16 | 4-5 / 14-15 |
| 7 | t2 ×8, t3 ×8 | 4-7 / 14-17 |
| 8 | t3 ×16 | 6-7 / 16-17 |
| 9 | t3 ×15, t4 ×1 | 6-9 / 16-19 |
| 10 | t3 ×8, t4 ×8 | 6-9 / 16-19 |
| 11 | t4 ×16 | 8-9 / 18-19 |

(`byte_8020C5C` at data/dat01.s:213 is **not** a reward table. It is the random-encounter rate table used by `sub_80AA4C0`, asm/asm29.s:10101-10137.)

**(b) Stat 0x26 bit 1 = NCP "Collect"** (`navicust_NCP_Collect` ORs in 2, asm/asm37_0.s:2427-2437), at asm/asm29.s:10853-10936:
1. Pick a random enemy, but **only among enemies whose 20-entry list contains at least one chip** (`sub_80AAA3C` mode 1 + `sub_80AAA1C` type mask, 10940-11009). If there is none, the result is 0xFFFF (no reward).
2. The offset uses the same table, but the sub-entry is forced to +2 (the 2nd entry of the tier; `sub_80AAA98` mode 2, 11037-11041). The low-HP half is kept (10869-10872).
3. Scan the current tier's two entries for type-0 (chip) entries. If none, go down one tier at a time to tier 0. Then go up from the starting tier to tier 4 (10873-10920).
4. A random chip is picked from the first tier that has any (10922-10928). If none is found, 0xFFFF.
5. The busting level only sets the starting tier. Collect returns a chip whenever the chosen half of the list has one.

**(c) Stat 0x26 bit 0** (checked first) (10815-10831):
- Set to 1 by bug-effect row 6 (levels 1-3) of `byte_813CC18` via `sub_813CDA0` (asm/asm37_0.s:2819-2844, 3021-3027). **UNVERIFIED**: the in-game name of this bug.
- Pick a random enemy, then `sub_80AAB04` (asm/asm29.s:11075-11119): from the 10 entries of the normal or low-HP half, pick a random **zenny** (type 1) entry. If there is none, use entry 0 or 1 at random.
- **The busting level is ignored.**

### 3.4 Entry encoding
Decoder `sub_802C54C` (asm/asm03_0.s:12611-12647); granting in `sub_802CAA6` (13320-13362):

| bits 15-14 | meaning | payload |
|---|---|---|
| 00 | chip | id = bits 0-8, code = bits 9-13 → `GiveChips(id, code, 1)` (13322-13341) |
| 01 | zenny | bits 0-13 → `GiveZenny` (13347-13351) |
| 10 | HP recovery | bits 0-13; 0 = full heal (`MaxHP` copied to `HP`), else `object_addHP` (asm/asm03_0.s:12082-12105, display via `sub_802C646` and state change at asm/asm03_0.s:12045-12056) |
| 11 | BugFrags | bits 0-13 → `GiveBugfrags` (13357-13361) |
| 0xFFFF | none | returns type 0xFF (12644-12645) |

- Chip names come from TextScriptChipNames0/1 (by id).
- Enemy names come from TextScriptVirusChipNames, used for ids ≤ 0xFF by `selectVirusOrNaviNamesAndWhich_800EC56` (asm/object.s:6010-6016).
- **UNVERIFIED**: the code letter mapping 0=A … 25=Z, 26=`*`.

### 3.5 Decoded examples (data/dat29.s, `byte_80AAEA8 + id*0x28`)

**id 1 Mettaur**:
- Normal half: [0-3] 100z, [4-5] 150z, [6-7] `0x1E83` = chip 0x83 Rflectr1 code 15 (P), [8-9] `0x0083` = Rflectr1 code 0 (A).
- Low-HP half: [10-15] `0x8064` = HP+100, [16-17] Rflectr1 P, [18-19] Rflectr1 A.
- Outcomes:
  - L=11, healthy: entry 8/9 gives Rflectr1 A.
  - L=7: 50% tier 2 (150z), 50% tier 3 (Rflectr1 P).
  - L≤3 at low HP: HP+100.
  - With Collect at L=1: tiers 0-2 have no chips, so the scan goes up to tier 3 and gives Rflectr1 P.

**id 2 Mettaur2**:
- [0-1] 100z, [2-3] 150z, [4] 200z, [5] `0x3084` = Rflectr2 code 24 (Y), [6] 250z, [7] Rflectr2 Y, [8-9] `0x0C84` = Rflectr2 code 6 (G).
- Low-HP half: [10-14,16] HP+150, [15,17] Rflectr2 Y, [18-19] Rflectr2 G.
- L=5, healthy: entries 2-5, so 150z / 150z / 200z / Rflectr2 Y at 25% each.

**id 7 Piranha**:
- [0-1] 100z, [2-3] 150z, [4] 200z, [5] `0x0A18` = TrnArrw1 code 5 (F), [6] 250z, [7] TrnArrw1 F, [8] 350z, [9] `0x0018` = TrnArrw1 A.
- L=9, healthy: 15/16 tier 3 (250z or TrnArrw1 F), 1/16 tier 4 (350z or TrnArrw1 A).

**id 4 Mettaur[SP]**: all 20 entries are zenny (500 / 1000 / 1200 / 1300 / 1500 by tier, same in both halves). With Collect it never qualifies as the chosen enemy (§3.3b step 1).
