# 08 — Folder memory: base chips, the Chip Pack, and why copies matter

Status: **design**, nothing implemented. Numbers come from two scripts:
- `tools/folder_math.py` (draw probabilities, exact or Monte Carlo)
- `tools/chip_memory.py` (MB and copy caps for all 354 moves, read from `src/data/battle_moves.h`)

Anything not taken from BN6, Emerald or those scripts is **TUNE** (a number we choose) or **UNVERIFIED**.

The request: learning a move gives you one version of its chip (Ember **S**). More copies (Ember **O**/**S**) come from wild battles and shops, and each copy raises the chance of seeing Ember in the Custom screen. That is BN's memory system, so we keep its core: the folder is a deck, and copies are how you shape it.

---

## 1. What BN6 does (the parts we copy)

| BN6 rule | Evidence |
|---|---|
| A folder holds exactly 30 chips | research/05 §Folders |
| The **Pack** stores up to 99 copies per (chip, code); each chip has 4 code slots | research/05 |
| **Copy cap per chip id**, set by the chip's MB: ≤19 MB → 5, 20–29 → 4, 30–39 → 3, 40–49 → 2, ≥50 → 1 | `sub_8135500`, bn6f asm/asm36.s:10634 |
| The copy cap ignores codes: Cannon A and Cannon B count together | Same function. It bins every folder entry that matches the chip by its MB (asm/asm36.s:10642-10680); reading the matched field as the chip id is our interpretation, **UNVERIFIED** |
| Hand of 5, raised by Custom programs | research/05 |
| Used chips are gone for the rest of the battle | BN6. **We reshuffle instead** (design 01): our early folders are tiny |

---

## 2. The model

### 2.1 Three layers

```
Pokémon's 4 moves  ──►  BASE CHIPS     one per move it knows. Bound to that Pokémon, code = the move's 1st lane.
                         (free, can't be lost, can't be farmed)
Chip Pack (global) ──►  PACK COPIES    (move, code) counts, 0-99 each. From wild drops, shops, gifts, Chip Trader.
Folder (30 slots)  ──►  what battles draw from: any mix of base chips and pack copies of moves the party knows.
```

**Why base chips are bound to the Pokémon** and are not just "+1 in the pack":
- **Emerald's menus stay true.** Every move on a summary screen has at least one chip, so a move is never "known but unusable".
- **No farming.** Re-teaching a move (Move Relearner, `src/move_relearner.c`) can't print copies. The base chip comes and goes with the move.
- **Trades carry it.** A traded Pokémon brings its base chips. Its pack copies stay with the old owner, as BN chips do.
- **The user's example works.** Charmander learns Ember and gets **Ember S** (Ember's first lane letter, `tools/lanes_curated.py`). Ember O or more Ember S come from the pack.

### 2.2 Who uses a chip

A chip is a **move**, not a Pokémon. Any party member that knows the move can use it:
1. If the Pokémon in battle knows it, it uses it.
2. Otherwise, the first benched Pokémon that knows it switches in (design 01's Navi-chip switch).

A base chip is the exception: only its owner uses it. If the owner has fainted, the chip is greyed out.

A pack copy of a move nobody in the party knows is a **dead chip**:
- The folder editor greys it out.
- The battle build skips it, so the folder shrinks for that battle. It is not refilled.

### 2.3 Caps (BN6's rule, our MB)

The copy cap counts base chips and pack copies of the same move together, across all codes. Two Pokémon that both know Ember already use 2 of Ember's 5.

**MB per move** (`tools/chip_memory.py`, all TUNE):
- Damaging moves: `MB = round(0.3 × power × hits) + adjustments`. Hits: multi-hit 3, Double Kick 2, Triple Kick 6. Adjustments:
  - priority +8
  - high crit +5
  - recharge, charge-up and self-KO −3 to −10
- Status moves, and fixed or variable damage (power ≤ 1): `MB = round(300 / PP)`. Emerald already prices a move's strength into its PP.

Result over 354 moves:

| copies allowed | 5 | 4 | 3 | 2 | 1 |
|---|---|---|---|---|---|
| moves | 166 | 90 | 65 | 9 | 24 |

| move | power / PP | MB | cap |
|---|---|---|---|
| Ember, Water Gun, Pound | 40 / 25–35 | 12 | 5 |
| Bite | 60 / 25 | 18 | 5 |
| Quick Attack | 40 / 30, priority | 20 | 4 |
| Thunderbolt, Flamethrower, Surf | 95 / 15 | 28 | 4 |
| Earthquake | 100 / 10 | 30 | 3 |
| Fire Blast, Hydro Pump | 120 / 5 | 36 | 3 |
| Hyper Beam | 150 / 5 | 40 | 2 |
| Psycho Boost | 140 / 5 | 42 | 2 |
| Self-Destruct, Explosion, Sheer Cold | — | 50–65 | 1 |
| Swords Dance, Growl, Recover | status, PP 20–40 | 8–15 | 5 |
| Spore | status, PP 15 | 20 | 4 |
| Toxic | status, PP 10 | 30 | 3 |

**PP-based copy rule (current code):** today's `CopiesForPP` (`src/pkbn/folder.c:13`) gives 3/2/1 copies by PP. It is replaced by base chip + pack copies under this cap.

### 2.4 Folder size and PP keep their jobs

- **Folder: 30 max** (BN6). There's no minimum: early on it's whatever you own.
- **Copies set frequency, PP sets stamina.** PP is spent per use, as today, so PP still limits a move across a route between Pokémon Centers. Copies only change how often the move is offered. In one battle, copies rarely hit the PP limit (§3.3).

---

## 3. The maths: what a copy buys

All numbers below are from `tools/folder_math.py`.
- Hand of 5 (BN). Our Custom programs raise it to 6–8 (POC-9).
- Draw rule: a reshuffled draw pile, refilled from the discard pile. That's ours, not BN's.
- 2 chips used per Custom.

### 3.1 Seeing it in the opening hand (folder of 30)

| copies | hand 5 | hand 6 | hand 7 |
|---|---|---|---|
| 1 | 16.7% | 20.0% | 23.3% |
| 2 | 31.0% | 36.6% | 41.8% |
| 3 | 43.3% | 50.1% | 56.4% |
| 4 | 53.8% | 61.2% | 67.7% |
| 5 | 62.7% | 70.2% | 76.4% |

Formula: `P = 1 − C(30−c, h) / C(30, h)`.
- **The first copies are worth the most.** Going 1 → 2 copies adds 14 points. Going 4 → 5 adds 9.
- **Custom programs and copies stack.** 3 copies with a hand of 7 (56%) beats 4 copies with a hand of 5 (54%). The NaviCust and the folder are two levers on the same thing.

### 3.2 Waiting for it (folder of 30)

Average number of Customs until a copy first shows:

| copies | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Customs | 6.6 | 4.2 | 3.0 | 2.3 | 1.9 |

A 1-copy move shows up about once in a typical 3–6-turn battle. A 5-copy move shows up almost every turn.

### 3.3 Uses per battle, and why PP still matters

Number of Customs, out of 8, in which the move is offered (used whenever offered):

| folder | 1 copy | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 12 | 1.8 | 3.6 | 5.2 | 6.7 | 7.6 |
| 20 | 0.9 | 1.9 | 2.8 | 3.7 | 4.6 |
| 30 | 0.6 | 1.3 | 1.9 | 2.5 | 3.1 |

In a full folder, **uses ≈ 0.4 × copies per 8 Customs**: close to linear, so every copy pulls its weight.

Check against PP:
- Fire Blast (cap 3, PP 5): ~1.9 uses per battle. PP lasts 2–3 battles.
- Ember (cap 5, PP 25): ~3.1 uses. PP lasts 8 battles.

Strong moves therefore can't be spammed even at their cap. **The MB cap and PP agree**, because both come from the same Emerald data.

### 3.4 The cost: dilution

Copies of one move push everything else out. Take a move with only its base chip in a 24-chip folder:

| folder size | 24 | 26 | 28 | 30 |
|---|---|---|---|---|
| P(in opening hand) | 20.8% | 19.2% | 17.9% | 16.7% |

That is the BN decision: a focused folder or a broad one. A full party has 24 base chips, which leaves **6 free slots**. To stack more, you **take base chips out**: Growl leaves the folder, and the move stays on the summary screen. That choice is the folder editor's whole game.

### 3.5 Codes: copies are also combo fuel

Probability that the opening hand holds 2 chips of one code (k chips of that code in a folder of 30):

| k | 3 | 5 | 8 | 10 | 15 |
|---|---|---|---|---|---|
| P | 6.4% | 18.3% | 40.5% | 55.1% | 83.5% |

So **which** code a copy carries matters as much as the count:
- Ember **S** sits next to Sunny Day and Fire Spin (lane S, SUN).
- Ember **O** sits next to Toxic and Leech Seed (lane O, OOZE).

Buying Ember O isn't "more Ember". It joins Ember to the OOZE plan. That's the decision we want the shop to pose.

### 3.6 Early game: why copies still help with a tiny folder

- With 1 Pokémon, the folder holds 4 base chips. Every Custom shows all of them, so copies don't change *frequency* (folder of 4 → 100%).
- Copies do give **doubles**: the same-move rule (design 01, `include/pkbn/folder.h`) lets 2 Embers go in one Custom, so 2 copies = a double Ember turn.
- Copies also **grow** the folder. With reshuffling, small folders keep everything visible (folder 8 → 62% per copy).
- The frequency game starts at about 12 chips. A second Pokémon plus a few purchases gets you there, which is roughly Rustboro. That's a gentle on-ramp.

---

## 4. Where copies come from

| source | gives | notes |
|---|---|---|
| Level-up, TM, HM, tutor, egg move | the **base chip** (first lane code) | Bound to the Pokémon (§2.1). Nothing goes to the pack. |
| **Wild battles (Busting Level)** | a pack copy of one of the **wild Pokémon's own moves** | Code: any of that move's lanes. `*` only for moves whose lanes allow it, and rare. Design 09 sets the odds. Viruses drop their own chips in BN6 too (research/05; bn6_busting §3.5: Mettaur → Rflectr1). |
| **Trainer battles** | sometimes a copy of a move the trainer's team used | TUNE. Gym leaders always give their TM's move (Roxanne: Rock Tomb). |
| **Poké Mart "chip shelf"** | fixed (move, code) stock per town | Price = **60 × MB** (TUNE): Ember 720₽, Thunderbolt 1680₽, Fire Blast 2160₽. TMs (3000₽+) teach a move; chips only add copies, so they sell for less. |
| **Chip Trader** (later) | 3 chips in → 1 random chip | Sink for pack copies above the cap. BN6 prefers codes you're missing (asm/asm03_2.s:9401). |
| **Starter gift** | 1 extra copy of the starter's damaging move | So the first folder has a double (§3.6). |

**Code choice for drops and shops:**
- Uniform over the move's lanes.
- The first lane is already guaranteed by the base chip, so drops roll it **at half weight**. That way most drops open a *new* code (Ember O).
- TUNE: this is the "clever" knob. Drops push you toward combos rather than pure stacking.

---

## 5. Folder editor and what the standard menus show

- **Where:** a FOLDER entry in the start menu (PC build). The folder is party-wide, unlike the per-Pokémon NAVICUST in the party menu.
- **Screen:** left, the folder (30 rows: move, code, owner icon for base chips). Right, the pack (moves the party knows first, dead chips greyed). Swap with A; L/R switches between folder and pack.
- **Auto-build:** used when you've never edited.
  1. All base chips go in.
  2. Pack copies of known moves fill the remaining slots, highest MB first.
- **3 folders** (BN6): presets, saved in `pkbn.sav`.
- **Summary screen (moves page):** under each move, its folder copies and codes, e.g. `FLAMETHROWER   PP 15/15   folder ×3  S S O`. PP is unchanged.
- **Save cost** in `pkbn.sav`:
  - Pack: 354 moves × 27 codes, 1 byte each = **9.6 KB** (sparse is possible, not needed on PC).
  - 3 folders × 30 × 3 bytes = 270 B.
  - Base chips need no storage; they're derived from the moves.

---

## 6. Edge cases

| case | rule |
|---|---|
| A Pokémon forgets a move | Its base chip leaves the folder. Pack copies of that move go dead unless someone else knows it. |
| Trade a Pokémon away | Its base chips go with it. The pack is untouched. |
| Shedinja | It is created as a copy of Nincada (src/evolution_scene.c:561 area), so it starts with the same moves and base chips. Pack copies are shared anyway. |
| Party change between battles | The folder is rebuilt at battle start. Dead chips are skipped, and the editor warns you. |
| Copies above the cap | Allowed in the pack (up to 99, BN6), never in the folder. |
| Mega / Giga moves | A later layer. A Mega class (cap-1 moves: Explosion, Sheer Cold, Self-Destruct…) limited to N per folder, with N raised by a MegaFolder program (BN6 caps at 10). Giga = legendary signatures, 1 per folder. |
| Switch | Not a chip. Always the 6th Custom slot with `*` (design 01). |

---

## 7. Implementation sketch (when you say go)

1. `tools/chip_memory.py` → `src/pkbn/chip_memory.c` (`gPkbnMoveMB[]`, cap function).
2. `pkbn.sav` version 2: `pack[MOVES_COUNT][27]`, `folders[3][30]`, `activeFolder`.
3. `PkbnFolder_Build` reads the active folder:
   - base chips resolve to their owner;
   - pack chips resolve to the active or first benched knower;
   - dead chips are dropped.

   `CopiesForPP` goes.
4. Post-battle drops (design 09) add to the pack.
5. Folder editor UI, summary line, Mart shelf.

Self-tests:
- `PKBN_TEST_PACK=` and `PKBN_TEST_FOLDER=` env vars.
- Check that the draw rate matches §3.3 over 1000 seeded Customs.

## 8. Questions (TUNE)

1. **Base chips bound to the Pokémon (recommended), or plain +1 in the pack?**
2. MB factor 0.3 (166 moves get 5 copies) or 0.25 (more moves get 5)?
3. Drop rule: first lane at half weight, or uniform?
4. Mart price of 60 × MB?

---

## 9. Open (2026-10-05): do we drop the 4-move limit?

You asked whether respecting Emerald's 4-move menus costs too much. Battles are ours now, so the only reasons to
keep 4 moves are the **other** systems that read them. In the pinned host, 31 files read `MON_DATA_MOVE1..4` (or
PP1..4). Examples:
- contests (`src/contest.c:2812`)
- the day care's egg moves (`src/daycare.c:654`)
- field moves / HMs (`src/party_menu.c`, `sFieldMoves`)
- the summary screen (`src/pokemon_summary_screen.c:1426`)
- trades, the Frontier, vanilla battles, the Move Relearner and evolution

**Option P: "move pool + 4-slot cache"** (proposal).
- **The pool.** A Pokémon keeps every move it ever learned: level-up, TM, tutor, egg move. Nothing is ever forgotten.
  - The pool lives in `pkbn.sav` under the Navi ID we already have: a 355-bit set = 45 bytes per Pokémon, 27 KB for
    600 Pokémon.
  - Each pooled move is a base chip (§2.1). The **folder of 30** becomes the only real limit, as in BN.
- **The cache.** `BoxPokemon.moves[4]` stays, but as a *cache*. When the folder is saved, each Pokémon's 4 slots are
  rewritten to its 4 moves with the most folder copies. Ties go by MB.
  - Every vanilla system above keeps working unchanged: contests, day care, trades, the Frontier.
  - **Exception: HM checks** read the pool, so Surf never "falls out" of the cache.
- **Level-up** no longer asks "forget which move?". The move joins the pool, with a "new chip!" message.
  - That screen (`GetMoveSlotToReplace`, POC-7) goes, and so do the Move Deleter and Relearner (the Relearner
    becomes pointless).
- **Summary → Moves page** becomes the Pokémon's **chip list**: every pooled move, its folder copies and codes, MB,
  power and kind. It's display only. Editing happens in FOLDER.

**What we give up:**
- The "4 moves" identity of a Pokémon. Its identity becomes "what it brings to the folder".
- Per-move PP outside the cache. Either:
  - (a) PP is stored per pooled move in `pkbn.sav` (1 byte each), or
  - (b) we drop PP as stamina and let **copies be the stamina**: BN6's rule, where a used chip is gone for the rest
    of the battle, with the reshuffle only for folders under ~15 chips.

  (b) is the cleaner BN answer, and §3.3 shows copies already behave like stamina.

**What we gain:**
- A Pokémon's whole learnset is usable, and the folder becomes BN's central decision.
- Copies and codes matter more, because there are more moves to fill 30 slots with.

**Questions:**
- P with PP option (a) or (b)?
- Should the 30-chip folder also cap chips per Pokémon? Without one, a single Pokémon could fill it. TUNE, e.g. 12.

---

## 10. How big should the folder be with 1–6 Pokémon? (2026-10-05)

Decided in §9: the move pool. PP vs copies-as-stamina is still open; the simulation assumes copies (option b). The question here is size. You proposed
`30 + 5 per extra Pokémon` (55 with a full party). `tools/folder_size_sim.py` tests that against the alternatives.

**Simulation inputs** (all TUNE):
- Emerald's real battle mix: 70% wild (1 enemy), 30% trainers. Trainer party sizes come from
  `src/data/trainer_parties.h`: 1 → 305 parties, 2 → 318, 3 → 135, 4 → 36, 5 → 25, 6 → 35.
- 4 chip uses per KO: Gen 3 damage at equal level, plus misses and status.
- 2 chips used per Custom.
- The Pokémon on the field faints after 3–6 Customs.
- No reshuffle.

### 10.1 What size actually controls

1. **Depth.** Does a deck run out mid-battle? A Pokémon on the field draws `5 + 2 × (Customs − 1)` chips:
   - a normal stay of up to 6 Customs → **15 chips**;
   - one Pokémon sweeping a 6-Pokémon team (Wallace) → **27 chips**.

   BN6's 30 is almost exactly the "sweep a full team" number.
2. **Copy value.** How much one extra copy raises the chance that move is in the hand. Bigger decks dilute it
   (§3.1).
3. **Presence.** In a shared deck, a hand often holds nothing for the Pokémon on the field. You then have to switch
   (a "forced" switch).

### 10.2 Results (n = party size)

| design | n | chips | forced switch | copy value |
|---|---|---|---|---|
| A: shared 30 (BN) | 1 / 3 / 6 | 30 | 0% / 6% / **65%** | +11 / +10 / +8 pts |
| **B: shared 30+5(n−1), lead holds 30** | 1 / 3 / 6 | 30 / 40 / 55 | 0% / 3% / **25%** | +11 / +9 / **+6** pts |
| B2: same size, split evenly | 1 / 3 / 6 | 30 / 40 / 55 | 0% / 30% / **62%** | +11 / +7 / +5 pts |
| **C: own deck of 15 per Pokémon + bench slot** | 1 / 3 / 6 | 15 / 45 / 90 | 0% / 0% / 0% | **+15 / +15 / +14** pts |

- Copy value is in percentage points of "this move is in the hand", per extra copy.
- No design ran a battle dry more than 6% of the time.

**Reading it:**
- **Any single shared deck** loses one way or the other as the party grows. If it stays small (A), the lead gets
  crowded out. If it grows (B), copies matter half as much.
- **Your +5 rule is the best shared option.** It works because it really means *"a BN folder for the lead plus 5 per
  bench Pokémon"*. Even so, with a full party:
  - a quarter of Customs force a switch;
  - an extra copy of the lead's move is worth half what it is in BN.
- **Per-Pokémon decks (C)** keep BN's maths identical at every party size, which is exactly why BN gives every Navi
  its own folder.

### 10.3 Proposal: one FOLDER screen, one section per Pokémon

Each party Pokémon has its own section of the folder, from 0 up to **S_max** chips.

**The hand:**
- 5 chips drawn from the **Pokémon in battle's** section;
- plus 1 **bench slot**, drawn from a mixed deck of every benched Pokémon's chips. It replaces today's generic
  Switch slot. Using it brings that Pokémon in, as in design 01, so tag-team play stays a choice and is never forced.

**Section size:**
- **15** is the smallest size that never ran dry in a normal fight (10 ran dry in 75% of 3-enemy battles).
- **30** lets one Pokémon sweep a 6-Pokémon team.
- Proposal: S_max = 30 (BN), **minimum 15** (see §10.4).

**How many chips that is in total:**
- up to 30 per Pokémon (180 with 6);
- in practice it's limited by **pack copies** (the economy) and the per-move caps;
- a Pokémon with 6 moves in its pool and base chips only has a 6-chip section until you invest in it.

**What the player thinks about:**
- "how deep is each Pokémon's kit", instead of "how do 6 Pokémon share 30 slots".
- Copy caps (§2.3) count **per section**, as BN6 counts per folder.

**Open:**
- Should S_max grow with level (e.g. 15 + level/4, capped at 30) so early folders stay small?
- Should one copy be usable in only one section at a time (the BN item feel; the pack drains faster), or in every
  section (easier)?

### 10.4 The minimum and free fill (2026-10-05)

**Why a minimum is needed.** Without one, the smallest section is the best:
- 5 chips show every chip every turn;
- that's vanilla's "all 4 moves, always", with no reason to own copies.

BN avoids this by requiring exactly 30.

**The rule:**
- **Section size:** 15 to 30.
- **Free fill:** empty slots up to 15 get free copies of the Pokémon's own pool moves.
  - They're spread evenly over the whole pool, using each move's first code.
  - You can't pick the fill or leave moves out of it.

  | pool | fill |
  |---|---|
  | {Tackle} | 15 × Tackle |
  | {Scratch, Growl} | 8 + 7 |
  | 5 moves | 3 each |

- **Caps:** fill goes over the copy caps only when the pool is too small to reach 15. That's 1–2-move Pokémon such as
  Magikarp or Unown, which are weak anyway. You can't build "15 × Hyper Beam", because the pool always holds every
  move learned.
- **Your own chips replace fill:** base chips you place and pack copies. Buy 4 Ember → 5 Ember, and the other 10 spread
  over the rest. Growl leaves once you've placed enough of your own chips. Going above 15 takes real chips only.
- **Copy value grows with the pool.** Late game, with 10 moves, fill gives 1–2 copies each:

  | Flamethrower copies in 15 | in the opening hand |
  |---|---|
  | 2 | 57% |
  | 4 | 85% |

  So copies are what make a grown Pokémon consistent.
