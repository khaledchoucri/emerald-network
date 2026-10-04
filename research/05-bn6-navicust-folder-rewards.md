# BN6 Falzar (bn6f) systems: NaviCust, Folder, rewards, save

Repo: `/home/claude/bn6f`. Every claim cites file:line. **UNVERIFIED** marks inference I could not confirm in code. Function names `sub_XXXX` are unnamed. "NaviStats[x]" means a byte at offset x of `navi_stats_struct` (include/structs/NaviStats.inc), accessed via `Get/SetCurPETNaviStatsByte` (out of battle) or `GetBattleNaviStatsByte*` (in battle).

---

## 1. NaviCust

### 1a. Program (NCP) data table

- **Table:** `StructArr_813944C` at data/dat36.s:379 (it ends where `FlagArr_813A01C` starts, data/dat36.s:952). Lookup is `sub_813B780` (asm/asm37_0.s:18), which computes `&StructArr_813944C[idx*0x10]`, so the **stride is 16 bytes**. The table holds 189 entries.
- **Indexing:** entry = `program*4 + variant` (0..3). Each program has up to 4 colour variants. Variant slots with colour 0 do not exist. `sub_803D148` (asm/asm03_1_1.s:8835) scans the 4 variants for a matching `[3]` colour. Entry 0..3 is "None". Entry 188 is "RUN!" (the run row, no shape).
- **Entry layout** (read from the data plus the code that reads it):
  | off | meaning | evidence |
  |---|---|---|
  | +0 | exclusive group. Only one program per non-zero group runs from the command line. Groups: 1=SuperArmor, 2=Shield/Reflect/AntiDmg, 3=OilBody/Fish/Battery/Jungle, 4=Humor/Poem, 5=ChpShufl/NumbrOpn | read at asm/asm37_0.s:2030-2042 (`applyNavicustPrograms_813C684`) |
  | +1 | 1 = "plus part" (Attack+1, HP+50, …). 0 = normal. Value 2 is also checked | asm/asm37_0.s:773-776, 839-842 |
  | +2 | always 1 for real programs (meaning UNVERIFIED) | data/dat36.s:379+ |
  | +3 | colour index 1..6 (0 = variant absent) | asm/asm03_1_1.s:8835-8860 |
  | +4 | **bug type** this program contributes when misplaced or adjacent to the same colour (indexes the 16-byte bug-level array) | asm/asm37_0.s:780, 849, 1069-1073, 1960-1966 |
  | +5..7 | 0xFF padding | data/dat36.s:379+ |
  | +8 | ptr to a 7x7 (0x31-byte) shape, normal | asm/asm37_0.s:42-56 |
  | +0xC | ptr to a 7x7 shape, **compressed** variant. Used when event flag `0x2660+entry` is set | asm/asm37_0.s:47-56 (flag 0x2660 at :70) |
- **Shapes:** 49 bytes each (7 rows x 7), with 1 = cell. Example: SuperArmor normal `FlagArr_813A04D` vs compressed `byte_813A07E` (data/dat36.s:956-963). Rotation is done at runtime by 4 copy routines `sub_813B7EC/7FC/818/830` (asm/asm37_0.s:76-133) into `unk_2009F00`.
- **Compression codes:** `sub_813C334` (asm/asm37_0.s:1653) reads a 10-input sequence per program from `byte_813B522` (data/dat36.s:1378, 10 bytes per program; inputs index the L/R/A/B table at asm/asm37_0.s:1707-1711). It then toggles flags `0x2660+prog*4 .. +4` (asm/asm37_0.s:1677-1690).
- **Count:** 46 real programs (47 names including "None"), with 1-4 colour variants each. Names come from TextScript873EA50 (data/textscript/TextScript873EA50.s:5-146): None, SuprArmr, Custom1, Custom2, MegFldr1, MegFldr2, GigFldr1, FstBarr, Shield, Reflect, AntiDmg, FlotShoe, AirShoes, UnderSht, ChpShufl, NumbrOpn, SneakRun, OilBody, Fish, Battery, Jungle, Collect, Millions, Humor, Poem, SlipRunr, AutoHeal, BustPack, BodyPack, FldrPak1, FldrPak2, BugStop, Rush, Beat, Tango, Attack+1, Speed+1, Charge+1, AttckMAX, SpeedMAX, ChargMAX, HP+50/100/200/300/400/500, then "RUN!".
- **Program effects:** jump table `navicust_jt_NCPs` (asm/asm37_0.s:2111). The handler index is `entry>>2`. Each handler writes NaviStats:
  - SuperArmor sets [0x23]=1 (:2166).
  - Custom1/2 add +1/+2 to [0xA] CustomLevel, capped at 8 (:2180).
  - MegFldr1/2 add +1/+2 to [0xB], cap 10. GigFldr1 adds +1 to [0xC], cap 10 (:2214-2262).
  - FstBarr sets [6]=1. Shield/Reflect/AntiDmg set [7] (L+B ability) to 0x3B/0x8B/0x3D (:2264-2300).
  - Float/Air/UnderShirt set [0x1B]/[0x1C]/[0x1D].
  - ChpShufl sets [0x60]. NumbrOpn sets [0x61]. SneakRun sets [0x1E].
  - OilBody/Fish/Battery/Jungle set [0x27] to 2/4/8/0x10 (:2375-2425).
  - Collect ORs 2 into [0x26]. Millions sets [0x33]. Humor sets [0x25]. Poem sets [0x5F]. SlipRunr sets [0x35]. AutoHeal sets [0x36].
  - BustPack adds +3 to Attack/Speed/Charge [1..3], cap 4 (:2496).
  - BodyPack = SuperArmor + Float + Air + UnderShirt. FldrPak1/2 = MegFldr + Custom.
  - BugStop sets [0x1F]. Rush/Beat/Tango OR 1/2/4 into [0xD].
  - Attack/Speed/Charge+1 add +1 to [1]/[2]/[3], cap 4. The MAX parts set them to 4.
  - HP+N adds N to the u16 at `oToolkit_Unk2004334_Ptr` (:2704-2780).

### 1b. Grid, command line, storage

- **Coordinate space:** 7x7 (0x31 cells). The placement mask is a 15x15 template, with the 7x7 space at offset (5,5) (`sub_813C584` index `15*(y+5)+x+5`, asm/asm37_0.s:1905-1912).
- **Three board templates** are chosen by key item **0x71 "ExpMemry"**: `sub_813B9E0` (asm/asm37_0.s:406) gets its index from the count returned by `CheckKeyItem(0x71)` (asm/asm37_0.s:1902-1904). GiveItem caps item 0x71 at 2 (asm/asm03_1_1.s:8318-8321). Names come from data/textscript/TextScript873D9FC.s:311-314.
  - `byte_813B1EC` (data/dat36.s:1325) is a **4x4** area of `1` cells at x,y = 1..4.
  - `byte_813B2CD` (:1340) is **5 wide x 4 tall**.
  - `byte_813B3AE` (:1355) is **5x5**.
  - Each area is ringed by `3` cells (an "outside" frame that parts may overhang). `0` cells cannot be used.
- **Placement legality** (`sub_813BAEC`/`sub_813BB00`, asm/asm37_0.s:568, 580):
  - A part is illegal if any cell lands on a `0` cell.
  - It is illegal if no cell lands on a `1` cell.
  - It is illegal if it overlaps an occupied cell (`sub_813BB68`, :640).
- **Command line = row y=3** of the 7x7 space. `sub_813BC1C` scans `(x=6..0, y=3)` (asm/asm37_0.s:732-745). `sub_813BF60` tests whether a shape touches row 3 (asm/asm37_0.s:1207-1236).
- **RAM / save state:** these pointers are fixed offsets from `eGameState`, set up through the table at asm/asm00_1.s:7548. All of them fall inside the saved EWRAM.
  - Grid: `oToolkit_Unk200414c_Ptr`, `unk_200414C` (ewram.s, 68 bytes), zeroed as 0x40 (asm/asm37_0.s:1307-1316). There is one byte per cell holding `placed-slot+1` (asm/asm37_0.s:385-388, 395-402).
  - Placed parts: `oToolkit_Unk2004190_Ptr`, 0x31 slots x **8 bytes** = 0x188 (asm/asm37_0.s:418-425, 432-455, 1310). Slot layout: `+0 u16` NCP entry id, `+3 x`, `+4 y`, `+5 rotation`, `+6` extra arg (meaning UNVERIFIED) (asm/asm37_0.s:438-449).
  - Bug-level array: `oToolkit_Unk200431c_Ptr`, 16 bytes (asm/asm37_0.s:704-708).
  - HP+ total: u16 at `Unk2004334` (asm/asm37_0.s:2704-2710).
  - Backup copies for cancel are at `eTextScript201BA00/byte_201BA40` and `byte_201BC40/80` (asm/asm37_0.s:461-529).
  - **Layout size:** 0x40 + 0x188 = **0x1C8 bytes (456)**. Add 0x10 for bug levels and 4 for HP+ (derived from the sizes above).
- **NCP inventory** lives in the KeyItems array (`eKeyItems` 0x2003134, 404 bytes, ewram.s:346). The item id is `0x90 + entry` (asm/chatbox.s:8565-8575, asm/asm03_1_1.s:8848-8860). The max count is 9 per item id ≥0x90 (asm/asm03_1_1.s:8326-8328). The give-all routine loops ids 0x94..0x14B (asm/asm37_0.s:1330-1357), so the inventory is 188 bytes.

### 1c. Bug rules (compile step `sub_813BBD4`, asm/asm37_0.s:702)

The routine zeroes the 16-byte bug array, then adds bugs as follows:

1. **Plus part on the command line:** `bug[type]++` (byte1==1 branch, asm/asm37_0.s:773-781).
2. **Normal (non-plus) part not on the command line:** `bug[type]++` (asm/asm37_0.s:839-850). A normal program must touch row 3 to run.
3. **Same-colour adjacency:** `sub_813BD24` probes each part's shape shifted ±1 in x and y (asm/asm37_0.s:889-930). `sub_813BE38` adds `bug[neighbour.type]++` for each touching part of the same colour (asm/asm37_0.s:1034-1076).
4. **Colour count:** `sub_813BEA8` counts distinct colours (asm/asm37_0.s:1098-1152). Exactly 5 colours adds +1 to `bug[0xB]`. 6 or more adds +2 to `bug[0xC]`. 4 or fewer is fine.
5. **Parts on the outside frame (`3` cells):** `sub_813C584` adds `bug[type]++` per part (asm/asm37_0.s:1890-1965).

The bug level is the count capped at 3 (`sub_813BF0C`, asm/asm37_0.s:1158). BugStop (NaviStats[0x1F]==1) clears all bugs (`sub_813C490` :1817 and `sub_813CBCC` :2782-2790). The effect table `byte_813CC18` (asm/asm37_0.s:2819) is indexed `type*16 + level*4`, with types 1..12. Each effect writes NaviStats:

| bug type (NCP byte4 that causes it) | effect written | battle consumer |
|---|---|---|
| 1 (SuperArmor, FstBarr, Shield/Reflect/AntiDmg, UnderSht, BodyPack) | [0x31]=1 (:2878) | `sub_80103A8` returns 3 when it is set (asm/asm00_2.s:3165). Effect UNVERIFIED. The header calls it "Moving Bug(Panel Skip)" (constants/headers/NCP_Families.h:99) |
| 2 (Humor, Poem) | [0x24] EmotionBug=1 (:2895) | `sub_8013DA0`: every 60 frames it randomly re-rolls the emotion state (asm/asm00_2.s:11188-11240) |
| 3 (FlotShoe, AirShoes, SlipRunr, AutoHeal) | [0x12]=3, [0x13]=2/3/4 by level (:2939-2988) | `sub_8013CC4`: with probability `[0x13]/8` it changes the panel under the player to type [0x12]. Type 3 is a crack (asm/asm00_2.s:11084-11120) |
| 4 (Custom1/2, Meg/GigFldr, ChpShufl, NumbrOpn, FldrPak) | [0x63]=4/3/2 (lv1/2/3), "TurnsUntilCustBugActivates" (:2988) | `sub_802A40C`: from that turn onward the custom draw count drops by (turn − N + 1), min 2 (asm/asm03_0.s:8670-8690) |
| 5 (SneakRun, OilBody, Fish, Battery, Jungle) | [0x28]=1 (:3004) | out-of-battle use at asm/asm29.s:10144 (UNVERIFIED) |
| 6 (Collect, Millions) | [0x26]=1 (:3021) | the reward picker restricts drops to zenny entries when bit 1 is set (asm/asm29.s:10816-10830, `sub_80AAB04` :11075) |
| 7 (BustPack, Atk/Spd/Chg +1/MAX) | [0x14]=6/10/13, [0x15]=1/2/3 (:3065-3080) | `sub_8013D5E` builds a 16-slot table with [0x14] slots of 1 and [0x15] slots of 2, then picks one at random. This is the **buster bug** misfire chance (asm/asm00_2.s:11150-11186). What 1 and 2 do is UNVERIFIED |
| 8 (Rush, Beat, Tango) | [0xD]=0xFF (:3085) | support navis disabled (UNVERIFIED) |
| 9 (HP+ parts) | [0x18] += level, [0x16]=3 (:3126) | `sub_8010230` drains **1 HP every N frames**, with N from `byte_80102A4` = {–,40,35,30,25,20,15,10} by [0x18] (asm/asm00_2.s:2957-2985, 3018). [0x16]=3 means each hit raises [0x18] by 1, up to 7 (`sub_8013F1E`/`sub_8013F96`, asm/asm00_2.s:11397-11480) |
| 10 | [0x62]=3/2/1 (:3174) | no NCP has byte4=10 |
| 11 (5 colours) | [0x1A]=9 (:3190) | `sub_8013E58`: a random status for 300 frames at battle start (asm/asm00_2.s:11273-11380) |
| 12 (6+ colours) | [0x1A]=0xA (:3207) | the same, for 600 frames |

`sub_800FE52` counts how many bug fields are active: [0x31,0x13,0x14,0x16,0x54,0x24,0x18,0x19,0x1A,0x63] (asm/asm00_2.s:2416-2470).

### 1d. Run step into stats

- **Pipeline:** `reloadCurNaviStatBoosts_813c3ac` (asm/asm37_0.s:1720) calls `applyNaviStatsMaybe_813C458` (:1796). That calls `sub_813BBD4` (compile and bugs), `sub_8136C24` (reset base stats, preserving folder/reg/tag/HP; asm/asm36.s:13620-13740), `applyNavicustPrograms_813C684` (:2012), `sub_813CBCC` (apply bugs, :2782), and finally `sub_803CE44` (MaxHP = MaxBaseHP[0x3E] + HP+ total; asm/asm03_1_1.s:8404-8420).
- **Program order in `applyNavicustPrograms_813C684`:**
  1. Command-line parts, x=6 down to 0, applying the exclusive-group rule (:2018-2052).
  2. Off-line plus parts (`unk_2006C88`, :2055-2071).
  3. On-line plus parts (`unk_2006CC0`, :2075-2093).
  4. `sub_803CED4` and `sub_813CEA0`, which clear the Regular chip if its MB exceeds RegUP (:3219-3245).
- **Run triggers:** it also runs when item 0x71 is given (asm/asm03_1_1.s:8339-8341).

---

## 2. Chip folder

### 2a. Folders and pack

- **Folders:** 30 chips x u16 = **0x3C bytes**. The base is `oToolkit_S_Chip_2002178_Ptr` (0x2002178), with folder n at `+n*0x3C` (asm/asm02.s:18-24, asm/asm32.s:36680-36705). The folder count is in `S2001c04+5`. GiveFolder caps it at 3 (asm/asm36.s:15027-15075, `isFolderSlotInUse_81377EC` :15135-15150). The folder slot/type table is `unk_20018EC`, 4 bytes, high nibble = type (asm/asm36.s:15135-15150).
- **Folder entry:** `id | code<<9` (`split9BitsFromBitfield_8021AE0`, asm/asm02.s:46-56).
- **Chip pack:** `oToolkit_Unk2002230_Ptr` (0x2002230), **12 bytes per chip id**. Bytes 0..3 are the counts for that chip's code slots 0..3, max 99 (`getOffsetToQuantityOfChipCodeMaybe_8021c7c` asm/asm02.s:305-325, `addChipsToChipPackOffset_8021b5a` :116-130). Total **0xF00 bytes** (`zeroFill_e2002230` :286-293), which is 320 ids (the 0x140 loop at :336-372).
- **Library:** GiveChips sets event flag `0x1E20+id` (asm/asm02.s:59-75). There are three flag ranges, `0x1E20/0x2020/0x2220`, plus id (asm/asm32.s:36876-36880).

### 2b. Edit rules (`sub_8135080`, asm/asm36.s:10011)

- **Dark chips** (ChipData EffectFlags & 0x20): at most 3 per folder (:10031-10050).
- **Mega** (LibraryType 1): the count must be < NaviStats[0xB] MegaLevel. **Giga** (type 2): < NaviStats[0xC] (:10052-10100).
- **Copies of one chip id, by MB** (`sub_8135500` :10634-10755): ≤19MB allows 5, 20-29 allows 4, 30-39 allows 3, 40-49 allows 2, ≥50 allows 1. Error texts are scripts 0x1C-0x20 (`byte_813523C` :10251) in data/textscript/compressed/CompText86CEE84.s:342-413.
- **Regular chip:** NaviStats[0x2D] is the current folder. [0x2E]/[0x2F] are the Reg slot per folder. Reg is cleared (0xFF) if chip MB > RegUP NaviStats[9] (asm/asm37_0.s:3219-3245). RegUP1-3 are key items 0x72-0x74 (TextScript873D9FC.s:317-323).
- **Tag chips:** NaviStats[0x56..0x59] hold Folder1Tag1/2 and Folder2Tag1/2 (include/structs/NaviStats.inc). The tag menu texts are at CompText86CEE84.s:163-185. The tag pairing rule (MB/code) is **UNVERIFIED**.
- **Battle-time check:** `tooManyGigasMegasAntiCheatHappensHere_800B022` (asm/asm00_1.s:17241) re-validates Mega/Giga counts.

### 2c. Codes

- `ChipData` is 0x2C bytes (include/rom_structs/ChipData.inc). `+0 u32 Codes` holds 4 code bytes, 0xFF = none. Other fields: `+7 LibraryType`, `+8 MB`, `+9 EffectFlags`, `+0x15 LibraryNum`, `+0x1A AttackPower`, `+0x1E ChipGateUsageLimit`.
- There are 411 entries (data/ChipDataArr.s). Example: Cannon has `codes: 0x1A020100` (data/ChipDataArr.s:35), which is A,B,C plus 0x1A. That 0x1A means `*` is UNVERIFIED.
- An owned chip stores its code implicitly as the **slot index 0..3** into that chip's Codes array, found by searching for the code (asm/asm02.s:305-325). Folders and rewards store the actual code value in bits 9+.

---

## 3. Other systems

- **Busting level:** `sub_800AF84` → `sub_800AC20` (asm/asm00_1.s:17153, 16678).
  - It is a sum of criteria selected by a bitmask: 0x18F for virus battles, 0xF1 for mode 2. Time thresholds (BCD 0x500/0x1200/0x3600) give 6/5/4/3 points (`off_800ADDC`/`byte_800AE00` :16918-16927). Other terms are counters (hits etc.), a multi-delete bonus `(BattleState_Unk_1b-1)*2`, and an HP-fraction bonus.
  - The result is clamped to **1..11** and stored in `oBattleState_Unk_1e` (asm/asm00_1.s:13044).
- **Rewards:**
  - `sub_80AA910` (asm/asm29.s:10801) picks from a per-encounter table of 20 u16 (`sub_80AAE98` → `byte_80AAEA8`, 0x28 bytes each; asm/asm29.s:11590, data/dat29.s:2).
  - The row offset is `byte_8020B9C[bustLevel*16 + rng&15]` (data/dat01.s:200; values 0/4/8/12/16), plus a random 0 or 2. Another +0x14 is added when HP ≤ 3/8 of max (`sub_80AAA98` asm/asm29.s:11011-11045).
  - **Reward u16 encoding** (`sub_802C54C` asm/asm03_0.s:12611): top 2 bits 0 = chip (id low 9 bits, code bits 9-13), 1 = zenny (14 bits), 2 = no grant, 3 = **BugFrags**. The grant happens in `sub_802CAA6` (asm/asm03_0.s:13320-13355). Up to 2 rewards are given (`sub_802C8FA` :13083-13125).
- **BugFrags:** an encrypted `oGameState_ProtectedBugfrags`, capped at 9999 (`GiveBugfrags` asm/asm03_1_1.s:8711-8735).
- **Chip Trader:**
  - The per-map list is chosen by map group/number (`selectChipTraderRewardList_804BFF0` asm/asm03_2.s:9401). List entries are 6 bytes: u16 id plus 4 codes.
  - It builds a pool of chips with or without the library flag 0x1E20+id, grouped by rarity (`sub_804BDB4` :9073).
  - New codes are favoured over owned ones by a weighted table (`sub_804BF18` :9274; comment ":75% new code" at :9312).
- **Library screen:** `HandleLibraryMenu8124B3C` (asm/asm33.s:3092) uses ChipData +0x15 LibraryNum and +0x16 LibraryFlags (asm/asm33.s:4798-4805).
- **Beast Out / Cross:**
  - `SetBeastOutCounterTo3` writes NaviStats[0x21] (asm/asm00_2.s:11744). The tutorial text says Beast lasts until the EmotionCounter reaches 0 (data/textscript/TextScriptDadCybeastTut.s:8-140).
  - Cross activation is at `activateCrossHappensHere_8014944` (asm/asm00_2.s:12882). The current form is NaviStats[0x2C] Transformation.
  - Text names 10 crosses: Heat, Elec, Slash, Erase, Charge, Spout, Tengu, Tomahawk, Ground, Dust (rg over data/textscript, e.g. compressed/CompText86D0614.s:563-877). Which are available in Falzar is UNVERIFIED.
- **Sub chips:** key items 0x80-0x86 (MiniEnrg, FullEnrg, SneakRun, Untrap, LocEnemy, Unlocker, SbChpSet; TextScript873D9FC.s:349-367). For 0x80-0x85 the max is the KeyItems[0x75] "SubMemry" count (asm/asm03_1_1.s:8310-8316).
- **HP Memory:** key item 0x70 (TextScript873D9FC.s:311). How it raises MaxBaseHP is **UNVERIFIED**.
- **Custom draw count:** NaviStats[0xA] CustomLevel plus `byte_20349B1`, capped at 8 (asm/asm03_0.s:8640-8655). That `byte_20349B1` is the "Add" bonus is UNVERIFIED.
- **Chip Gate:** ChipData +0x1E `ChipGateUsageLimit` (include/rom_structs/ChipData.inc). No consumer was traced (UNVERIFIED).
- **Style/Soul:** no Style or SoulUnison strings or labels were found (grep over data/textscript and asm). BN6 uses Cross/Beast instead (UNVERIFIED as a design statement).

---

## 4. Save and RAM sizes

- **SRAM save:** **0x6710 bytes** copied from EWRAM `timer_2000000` to `0xE000100` (`sub_803F79E` asm/asm03_1_1.s:13364-13371, 13450-13452).
- **"Toolkit extra" game-data block:** 0x35BC bytes from `eGameState` 0x2001B80 (asm/asm00_1.s:7471-7476, constants.ld:2). The offsets table is at asm/asm00_1.s:7548.

| region | addr | size |
|---|---|---|
| folders | 0x2002178 | 3 x 0x3C = 0xB4 |
| chip pack | 0x2002230 | 0xF00 |
| key items (incl. NCP inventory at +0x90) | 0x2003134 | 0x194 (NCP part 188) |
| NaviCust grid | 0x200414C | 0x40 |
| NaviCust placed parts | 0x2004190 | 0x188 |
| bug levels + HP+ | 0x200431C / 0x2004334 | 0x10 / 4 |
| NaviStats x2 | 0x20047CC | 0x64 each |

Folders + pack + NaviCust (grid and parts) + NCP inventory come to about 0xB4+0xF00+0x1C8+0xBC = **0x1340 bytes (~4.9 KB)**.
