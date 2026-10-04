# Design 01 — Chip folder & switching (Option 2: Switch chips in the folder)

Status: **brainstorm / proposal** (2026-10-04). Decisions needed are marked **DECIDE**.
Grounding: BN6 facts cite `upstream/bn6f` @ d57c196; Emerald facts cite `upstream/pokeemerald-pc_port` @ 1165825.

## 0. What the source games actually do (verified)
| Fact | Source |
|---|---|
| A BN6 folder is **30 entries**; each entry is a u16 = 9-bit chip id + code bits | `FolderTable` (`asm/asm36.s:15207`) entries are 0x3C bytes apart; `sub_8021AB4` copies 0x3C bytes and splits each hword with `split9BitsFromBitfield_8021AE0` (`asm/asm02.s`) |
| Every chip has **up to 4 legal codes** | `ChipData.Codes` (u32, 4 bytes, `include/rom_structs/ChipData.inc`); `validateChipCode_8006EE8` (`asm/asm00_1.s:7872`) checks a code against those 4 bytes |
| Hand size ("Custom") is a Navi stat; **Custom1 +1, Custom2 +2, capped at 8** | `navicust_NCP_Custom1/2` (`asm/asm37_0.s:2180-2210`), NaviStats byte 0xA. Base value (5 in BN) not yet read |
| BN can **stop time** (used by Navi chips etc.); the Custom gauge doesn't fill during it | `battle_isTimeStop` checks in `battle_update_8007A44` and the gauge fill (`asm/asm00_1.s:9709`, `:11096`) |
| Navi chips are one attack family (0x1B, 70 chips) | research/03 |
| Selection rule "same name OR same code OR `*`" | BN rule from play; Custom-screen code compares against 0x1A (likely `*`) around `asm/asm03_0.s:5599-5632` — **UNVERIFIED** |
| Gen 3: **switching out resets the user's stat stages, except via Baton Pass** | `SwitchInClearSetData` (`src/battle_main.c:3152`, Baton Pass check right after) |
| Gen 3 has Baton Pass, Pursuit, Assist, Spikes as move effects | `EFFECT_BATON_PASS 127`, `EFFECT_PURSUIT 128`, `EFFECT_ASSIST 180`, `EFFECT_SPIKES 112` (`include/constants/battle_move_effects.h`) |

## 1. Core model (proposal)
**The party is the folder.** Every chip belongs to an *owner* Pokémon.

- **Move chips** — one per (owner, move) × copies. A chip can only be used while its owner is the
  active Pokémon.
- **Switch chips** — "→ TREECKO", one or more per benched party member. Using it swaps that
  Pokémon in.
- **Folder size 30**, shuffled at battle start; **hand of 5** each Custom (BN), drawn from the top.
- **Selection rule (BN):** in one Custom you may pick several chips only if they share the same
  name or the same code (or are `*`).
- **Projected owner check:** while picking, the Custom screen tracks who *will* be active at that
  point in your queue. A chip is selectable if its owner is active *at that point*, i.e. after any
  Switch chip earlier in the same queue. This is what makes combos:
  `GROWL (Mudkip) G` → `→TREECKO G` → `ABSORB (Treecko) G`.

### Switch execution (Navi-chip feel)
1. Time stops (gauge, enemy, attacks freeze — BN time-stop), screen dims.
2. Outgoing Pokémon recalls; incoming enters on the same panel (~40 frames, TUNE).
3. Outgoing loses its stat stages (Gen 3 rule) unless the switch came from Baton Pass.
4. Enemy debuffs stay on the enemy — so "debuff with A, switch to B, cash in" is the intended loop.

## 2. Where PP fits (proposal)
- **Copies per move from max PP** (TUNE): PP ≥ 30 → 3 copies, 15–25 → 2, ≤ 10 → 1. Cheap spammy
  moves are common draws; Hydro-Pump-tier moves are rare.
- Each use still costs 1 PP. A move at 0 PP leaves **dead chips** in the folder (greyed, still
  occupy hand slots) — PP attrition between Pokémon Centers stays meaningful.

## 3. Codes — the big **DECIDE**
Codes decide which combos are possible. Options:

| Option | How letters are assigned | Feel |
|---|---|---|
| **A. BN-style, per move** | each move gets up to 4 legal codes from a table (e.g. its type's letter + 1-2 fixed letters + rare `*`); switch chips get the *incoming* Pokémon's type letters | Most BN-like; combos follow type themes; needs a folder editor to pick codes |
| **B. Per Pokémon** | all of Treecko's chips share a personal letter; switch chips into Treecko carry Treecko's letter | Very readable ("chain everything with T"); but cross-Pokémon combos need `*` or same name |
| **C. Per type + Normal = `*`** | code = move type letter; Normal-type moves and all switch chips are `*` | Zero editing, automatic, Normal moves become the glue — but switching is always combo-able (maybe too easy) |

Recommendation for the first build: **C** (no editor needed, testable immediately), keep the data
model of **A** (4 legal codes per chip) so we can move to A once there is a folder editor.

## 4. Switch-chip variants (brainstorm)
| Chip | Behaviour | Pokémon anchor |
|---|---|---|
| **Switch → X** | plain swap (above) | normal switching |
| **Baton → X** | swap keeping your stat stages (buffs pass to X) | Baton Pass (`EFFECT_BATON_PASS`) |
| **Assist: X** | X pops in during time-stop, uses one of its moves, leaves; active Pokémon unchanged — a literal BN Navi chip | Assist (`EFFECT_ASSIST` calls a party member's move) |
| **Entry strike** | the incoming Pokémon's first move after a switch gets a bonus (e.g. instant / +power) | BN "Navi chip arrival" spectacle |
| **Pursuit** | punishes enemy switch chips (trainer battles): double damage if it lands during an enemy swap | `EFFECT_PURSUIT` |
| **Spikes** | panels on the enemy side that hurt whoever switches in there | `EFFECT_SPIKES` |

## 5. Edge rules (proposal)
- **Fainting:** time stops and you pick the next Pokémon (not a chip) — the "forced switch" from
  Option 3 exists only as a fallback, never as the main way to switch. The fainted Pokémon's chips
  become dead draws.
- **Hand with no usable chips:** BN's "ADD" button — discard hand, next Custom draws +1 (BN mechanic).
- **Wild Pokémon:** single Pokémon, no folder — keep current AI. **Trainers** get their own folder
  with switch chips later (needs AI for combos).
- **Catching** adds the new Pokémon to the party → its chips/switch chips enter the folder next battle.

## 6. Tuning knobs
Hand size (5, grows with ... badges? held item?), switch animation length, copies-per-PP tiers,
number of switch chips per benched Pokémon (proposal: 2), whether Switch chips can be the first
chip in a queue (proposal: yes).

## 7. Build plan (when decided)
1. Folder data + shuffle + 5-card hand + BN selection rule; owner projection in the Custom screen.
2. Switch chip with time-stop + dim + swap animation; stat-stage reset.
3. Faint → pick next. Dead chips.
4. Baton / Assist variants.
5. Folder viewer (read-only) on the start menu; editor later (needed for code option A).
