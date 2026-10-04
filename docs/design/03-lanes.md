# Design 03 — Curated chip lanes, Program Advances, combo rewards

Status: **proposal v1 for Khaled's review** (2026-10-04).
Source of truth: `tools/lanes_curated.py` (every Gen 3 move, hand-assigned). Full table: `data/lanes.csv`.
Validation + simulation: `tools/lanes_report.py` → `research/04-lanes-report.md`.
Decisions already made: 3 layers (element / codes / Program Advances); one code per folder copy (BN);
`*` allowed on weak and status moves.

## 1. Design rules (what "curated" means here)
1. **A lane is a battle plan, not an element.** Each letter is a verb with a *setup* and a *payoff*, so
   a chain reads as a little story: Leer (break the guard) → Scratch → Crunch. Element stays with damage.
2. **Every move is tagged by hand with a role per letter:** `s` setup, `p` payoff, `x` link. 353/353
   moves covered (Struggle excluded). Notes in the source explain the non-obvious ones.
3. **Lanes cross types on purpose** (BN's Cannon/Spreader share A/B/C). Average lane spans 6 types; e.g.
   CHARGE (C) holds Electric attacks *and* every paralysis source (Body Slam, Lick, Glare, Stun Spore, Dragon Breath)
   *and* its payoff (Smelling Salt). That is what lets mixed parties chain.
4. **Canon first.** Emerald's hand-made contest combos are the backbone: 198 of its 234 "starter → follow-up"
   pairs can be chained under these lanes (Leer → Bite, Rain Dance → Thunder, Defense Curl → Rollout,
   Mud Sport → Water Gun, Focus Energy → Karate Chop …). Other anchors are battle mechanics: rain makes Thunder
   hit, Smelling Salt punishes paralysis, Dream Eater/Nightmare need sleep, the OHKO moves (Guillotine,
   Horn Drill, Fissure, Sheer Cold) finish a trapped target.
5. **Flexibility is paid for with power (BN rule, measured in BN6).** Weak/status moves: 2–3 letters and may be `*`.
   Strong moves (≥90 power or ≤5 PP): **one letter**, never `*`. Documented exceptions (two-lane payoffs):
   Solar Beam (Sun + Growth), Thunder (Charge + Rain), Dream Eater (Zzz + Mind), Take Down (Harden + Extreme),
   Rain Dance (Rain + Charge), Tri Attack (Sun/Charge/Ice), Weather Ball (one letter per weather).
6. **Pure wildcards are moves whose identity is "becomes something else":** Mimic, Metronome, Mirror Move,
   Transform, Sketch, Conversion 1/2, Hidden Power, Nature Power, Role Play, Skill Swap, Camouflage, Assist, Splash (the joke).

## 2. The 26 lanes and a signature chain for each
| | Lane | Plan | Signature chain (all legal) |
|---|---|---|---|
| A | AMBUSH | strike first: priority, flinch | Fake Out → Quick Attack → Extreme Speed |
| B | BIND | pin it, then finish (trap + OHKO) | Mean Look → Wrap → Horn Drill |
| C | CHARGE | charge, paralyse, then the bolt | Charge → Thunder Wave → Smelling Salt |
| D | DRAGON | dance, breathe, rampage | Dragon Dance → Dragon Breath → Outrage |
| E | ENDURE | survive at 1 HP, punish | Endure → Flail → Reversal |
| F | FURY | flurries and escalation | Defense Curl → Rollout → Fury Cutter |
| G | GROWTH | seed, grow, drain | Leech Seed → Growth → Giga Drain |
| H | HARDEN | armour into offence | Harden → Tackle → Take Down |
| I | ICE | hail, chill, freeze | Hail → Icy Wind → Blizzard |
| J | JINX | curse and haunt | Mean Look → Curse → Shadow Ball |
| K | KUNG-FU | martial arts | Bulk Up → Double Kick → Cross Chop |
| L | LOWER | break defences, hit hard | Leer → Scratch → Crunch |
| M | MIND | calm, confuse, foresee | Calm Mind → Confusion → Psychic |
| N | NIGHT | blind, steal, bite | Sand-Attack → Faint Attack → Crunch |
| O | OOZE | poison, burn, leech (attrition) | Toxic → Leech Seed → Sludge Bomb |
| P | PUNCH | fists | Meditate → Ice Punch → Thunder Punch (Medicham's kit) |
| Q | QUAKE | mud, sand, rock, quake | Mud Sport → Mud-Slap → Earthquake |
| R | RAIN | rain and water | Rain Dance → Water Pulse → Surf |
| S | SUN | sun and fire | Sunny Day → Growth → Solar Beam |
| T | TEMPO | outpace, slow, dodge | String Shot → Agility → Swift |
| U | UP | power up, then crit / charge | Swords Dance → Slash → Crush Claw |
| V | VOICE | songs, roars, dances | Growl → Sing → Hyper Voice |
| W | WIND | gusts, wings, dives | Feather Dance → Aerial Ace → Drill Peck |
| X | EXTREME | finishers with a cost — payoff-only, so they rarely chain (that's their price) | Hyper Beam alone |
| Y | YIELD | heal, shield, help the next Pokémon (pairs with switching) | Helping Hand → Wish → Beat Up |
| Z | ZZZ | sleep, confuse, exploit | Hypnosis → Nightmare → Dream Eater |

**Cross-Pokémon chains this enables (benched chips switch in):**
- Treecko *Leer* (L) → Mudkip enters with *Tackle* (L) — canon Leer → Tackle combo across two Pokémon.
- Wingull *Supersonic* (Z) → Ralts enters with *Confusion* (Z) — stack confusion, then the psychic hit.
- Mudkip *Mud-Slap* (N) → Poochyena enters with *Sand-Attack* (N) → *Bite* (N) — blind them, then bite.
- Camerupt *Sunny Day* (S) → Breloom enters with *Solar Beam*-less Grass moves? No — Breloom's Mega Drain is G;
  Sunny Day is S only. Bridges are deliberate, not universal: Growth (G+S) is the move that joins Sun and Growth.

## 3. Program Advances (layer 3) — brand-new moves
Rules (proposal): exact 3-move order inside one chain; recipe must be letter-legal (all 19 are, checked by the tool);
the 3 chips are consumed and each spends its PP; the PA replaces them with one new move.
| PA | Recipe | New move |
|---|---|---|
| MEGA SOLAR BEAM | Sunny Day → Growth → Solar Beam | Grass 180, no charge, sweeps the enemy area |
| STORM CALLER | Rain Dance → Charge → Thunder | Electric 150, a bolt on every enemy panel |
| TSUNAMI | Rain Dance → Surf → Hydro Pump | Water 200, wave across all rows |
| PERMAFROST | Hail → Icy Wind → Blizzard | Ice 160, freezes the target in place |
| EARTH RENDER | Sandstorm → Magnitude → Earthquake | Ground 180, cracks every enemy panel |
| DREAM DEVOURER | Hypnosis → Nightmare → Dream Eater | Psychic 160 drain, heals the party |
| VENOM STORM | Toxic → Acid → Sludge Bomb | Poison 140, poison panels |
| DRAGON RUSH | Dragon Dance → Dragon Claw → Outrage | Dragon 200 dash, no confusion |
| THOUSAND FISTS | Mach Punch → Comet Punch → Dynamic Punch | Fighting 6×30, guaranteed crits |
| STAMPEDE | Harden → Tackle → Take Down | Normal 120 charge, no recoil |
| MUDSLIDE | Mud Sport → Mud-Slap → Water Gun | Ground/Water 90, muddy panels |
| ROLLING THUNDER | Defense Curl → Harden → Rollout | Rock, 5 bouncing hits |
| Z-HYDRO / Z-FLARE / Z-VOLT / Z-FROST / Z-PSI / Z-DRAIN / Z-SLUDGE | the three tiers of a move family in order (BN's Cannon → HiCannon → M-Cannon = Z-Cannon) | 200–240 power versions |
Open: earlier PAs for the first two gyms (most recipes need moves learned after level 20).

## 4. Combo rewards — options to explore (for Emerald's 2-move contest combos)
Emerald doubles appeal for a completed contest combo (`src/contest.c:4489`). In battle we could:
| # | Reward | Grounding | Feel |
|---|---|---|---|
| 1 | ×1.5 damage on the follow-up | contest ×2 appeal, halved | simple, invisible |
| 2 | **Secondary effect always triggers** (Leer → Bite always flinches, Rain Dance → Thunder always paralyses) | `gBattleMoves[].secondaryEffectChance` → 100% | very Pokémon, readable |
| 3 | **Lane panel effect**: Rain combos leave puddles, Sun scorches, Quake cracks, Ice freezes panels | BN panel types (`PanelData.inc`) | very BN, changes the board |
| 4 | Tempo: combo refills part of the Custom gauge / cuts lockout | BN Custom gauge | rewards speed |
| 5 | PP refund on the follow-up | Pokémon PP economy | rewards planning between Centers |
| 6 | Combo meter that powers Program Advances / a temporary buff | our design | meta-progression inside a battle |
My suggestion: **2 for moves that have a secondary effect, 3 for those that don't** — both are visible and
come straight from the two source games.

## 5. Numbers (`research/04-lanes-report.md`, real learnsets from `level_up_learnsets.h`)
| Party (real level-up moves) | chips/turn, one letter per copy | hands with 2+ chips |
|---|---|---|
| Solo Mudkip / Torchic / Treecko @12 | 2.34 / 2.58 / 2.43 | 100% |
| Mudkip, Wingull, Zigzagoon @12 | 2.60 | 98% |
| Torchic, Ralts, Poochyena @12 | 2.26 | 90% |
| 5 Pokémon @28 | 2.16 | 85% |
| 6 Pokémon @45 | 2.09 | 82% |
Inside BN's ~2–3 band at every stage. (If a chip matched *all* its letters instead, solos would chain 5/5 —
confirms "one letter per copy".)

## 6. What I need from Khaled
1. The lane list (letters, names, plans) — rename/merge/split anything.
2. A pass over `data/lanes.csv` (sort by lane): disagree with any move's letters or role.
3. Program Advance list and new-move specs; which early-game PAs to add.
4. Pick or combine combo rewards from §4.
