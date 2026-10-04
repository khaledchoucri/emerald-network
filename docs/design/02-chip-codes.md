# Design 02 — Chip codes, done properly

Status: **strategy / proposal for review** (2026-10-04). Nothing built yet.
Replaces the "type = letter" shortcut from POC-4. Grounding: bn6f @ d57c196, pokeemerald-pc_port @ 1165825.
Simulator: `tools/codes_sim.py` (real Emerald data, random 5-chip hands).

## 1. What BN6 actually does with codes (measured from `data/ChipDataArr.s`)
| Observation | Evidence |
|---|---|
| **Codes are not elements.** A chip's element (`AttackElement`) and its codes (`Codes`) are separate fields. Cannon is Null-element with codes A/B/C/*. | `include/rom_structs/ChipData.inc` |
| Each chip *family* has a **legal set of up to 4 codes**; each copy in a folder has exactly **one** of them. Folder-building = choosing codes. | `Codes` u32 = 4 bytes; folder entries are chip id + one code (`split9BitsFromBitfield_8021AE0`) |
| Typical chip: **3 letters + `*`**. Distribution over the 355 named chips: 0 codes 17, 1 code 90, 2 codes 20, 3 codes 118, 4 codes 110. | counted |
| `*` is common, not special: **152 of 355** chips have it. | counted |
| **Letter lanes cross families on purpose:** Cannon `A B C *` = Spreadr2 `A B C *`; HiCannon `L M N *` = Spreadr1 = YoYo; the whole Sword line `H L S *`; M-Cannon `R S T *` ~ Spreadr3 `Q R S *`. Lanes are how unrelated chips become a folder. | counted |
| **Flexibility is paid for with power.** Rarity 0: avg 2.26 letters, 63% have `*`. Rarity 3: 1.8 letters, 15% `*`. Rarity 4: 1.38 letters, 19% `*`. SuprVulc = `V` only; GunDelEX = `G` only; WideBlde `B R W`, no `*`. | counted by `chip_rarity` |
| Same-name chips always chain. | BN rule (selection code not yet located in asm) |

## 2. What Emerald already gives us (designer-made, not invented by us)
| Asset | What it is | Evidence |
|---|---|---|
| **Contest combos** | A hand-authored graph: 62 "starter" groups; 201 of 354 moves belong to ≥1 group. A starter followed by one of its listed moves is a combo. Examples: Leer → Scratch / Tackle / Bite; Rain Dance → Water Gun / Surf / Hydro Pump / **Thunder**; Charge → every Electric attack; Focus Energy → heavy physical hits; Sand-Attack → Mud-Slap; Defense Curl → Tackle / Rollout. | `src/data/contest_moves.h` (`comboStarterId`, `comboMoves`) |
| Combo reward | A completed contest combo **doubles** the appeal (`comboAppealBonus = baseAppeal * completedCombo`). | `src/contest.c:4482-4489`; check via `AreMovesContestCombo` (`:1532`) |
| **Contest category ("suit")** | Every move has one of 5: Cool 83, Smart 83, Tough 74, Beauty 65, Cute 49. Cross-type and hand-assigned. | `contest_moves.h` `.contestCategory` |
| Power / PP | Natural rarity proxies (BN's flexibility-vs-power rule). | `battle_moves.h` |

Membership is not random: weak/status moves are often starters, follow-ups are often the payoff
moves — the exact "set up / debuff, then hit" pattern we want.

## 3. Proposed architecture (three separate layers)
1. **Element = type.** Damage, STAB, effectiveness. *Not* used for chaining (BN separation).
2. **Codes = lanes (letters A–Z + `*`).** Each move gets a **curated legal set of 1–4 letters**:
   - Lanes come from the contest-combo groups, **merged by us into ~20 themed lanes** (62 groups is too
     many for 26 letters). Draft: `R` Rain/water (Rain Dance, Water Sport, Surf, Dive), `S` Sun/fire,
     `F` Focus (Focus Energy, Swords Dance, Rage), `M` Mind (Calm Mind, Confusion, Kinesis, Psychic, Hypnosis),
     `G` Growth (Growth, Sweet Scent), `C` Charge (Charge, Lock-On), `L` Leer/intimidate (Leer, Scary Face,
     Mean Look, Taunt), `H` Harden/guard (Harden, Defense Curl, Endure), `D` Dragon, `B` Bone, `P` elemental Punches,
     `T` Terrain (Mud-Slap, Mud Sport, Sand-Attack, Sandstorm), … — **to be finalised together** (Khaled reviews the table).
   - Moves in no group (153, incl. Pound, Poison Sting, Howl) get a lane from their **contest suit**.
   - **Flexibility vs power (BN rule):** weak/high-PP moves get 3 letters (+ maybe `*`), mid moves 2, strong /
     low-PP moves 1 and never `*`.
   - **Each folder copy carries one letter** (BN). Auto-assigned spread at first; a folder editor later
     lets the player choose — that's where the depth lives.
3. **Combos = ordered pairs (our Program Advance).** If a contest starter is followed *later in the same
   chain* by one of its follow-ups, the follow-up gets a **COMBO bonus** (Emerald doubles appeal; we propose
   ×1.5 damage or a lane-specific effect, TUNE). Works across Pokémon: Treecko's Leer → Mudkip switches in
   with Tackle = COMBO. This is the "debuff with one, cash in with another" loop, and it's canon data.

**Switching (from our last round):** benched Pokémon's chips switch them in (Navi-chip style, they stay);
the wildcard Switch is always the 6th Custom slot and ends the chain; earned Switch chips become
**lane bridges** (2 lanes) with a stronger entrance.

## 4. Numbers so far (`tools/codes_sim.py`, raw 62 groups, no merging yet)
| Scheme | Party of 3 | Mudkip alone |
|---|---|---|
| Type = letter (POC-4) + benched chips switch in | 3.7 chips/turn | 3.3 |
| Combo groups + suit, **one code per copy (BN)** | **1.9** | **2.2** |
| Combo groups + suit, a chip matches all its legal codes | 2.6 | 3.5 |
BN-like target is roughly 2–3 per turn. Merging groups into ~20 lanes will raise the per-copy numbers;
we tune lane sizes until the target holds for early, mid and late parties.

Example legal sets with the raw groups (before merging):
Tackle {DefenseCurl, Harden, Leer, suit:Tough} · Water Gun {MudSport, RainDance, WaterSport, suit:Cute} ·
Leer {Leer, Rage, ScaryFace, suit:Cool} · Absorb {Growth, suit:Smart} · Pound {Pound, suit:Tough}.

## 5. Decisions for Khaled
1. Adopt the three-layer split (element / lanes / combos)?
2. Lanes from contest combos + suits, curated together into ~20 letters?
3. One letter per copy (BN, needs a folder editor eventually) or a chip matches all its legal letters?
4. `*` on weak move chips (BN has it on 43% of chips) — or keep `*` only on the wildcard Switch?
5. Combo reward: ×1.5 damage, or per-lane effects (Rain lane combos ignore Barrier, Leer lane combos stun, …)?

## 6. Work plan once decided
1. `data/lanes.csv`: every move → legal letters + rationale column (generated draft from contest data, then hand-edited).
2. Extend `tools/codes_sim.py` to read the CSV and report chips/turn for early / mid / late sample parties.
3. Generator → C table; replace the type-letter code in `folder.c`; add COMBO detection
   (reuse Emerald's `AreMovesContestCombo`).
4. Folder viewer, then folder editor (per-copy letters).
