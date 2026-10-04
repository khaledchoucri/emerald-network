# POC-6 — Chain payoffs: Program Advances and contest-combo rewards

Patch: `poc/patches/0008-POC-6-chain-payoffs-Program-Advances-and-contest-com.patch` (on top of 0001–0007).
Data: `tools/lanes_curated.py` (`PROGRAM_ADVANCES` recipes), `tools/attacks_curated.py` (`PA_EFFECTS`),
generated into `src/pkbn/move_table.c` by `tools/gen_move_table.py`.

## Program Advances
- **How one forms:** put the three recipe chips into one Custom selection, next to each other and in recipe order. They
  must still be a legal selection (shared letter). A pink "PROGRAM ADVANCE: NAME!" line shows while you pick. When
  you press START, the three chips become one PA chip.
- **Who performs it:** the Pokémon whose chip is the payoff (the third one). If it is on the bench, it switches in
  first. Each of the three moves spends 1 PP.
- **Grounding:** BN6 forms a PA the same way, at the Custom screen from consecutive chips. Its recipe table isn't
  decoded in bn6f yet (the PA routines are unnamed), so the trigger rule and timings are ours.
- **Data fix:** Rain Dance has one chip copy (5 PP) but opens both TSUNAMI (R) and STORM CALLER (C). Its single copy
  is now `*`. The validator now checks that every recipe can be built from real chip copies, and all 19 pass.

| PA | How it plays |
|---|---|
| MEGA SOLAR BEAM | new kind SWEEP: the whole enemy area is marked, then a beam sweeps it row by row (the only escape is a row it already passed) |
| STORM CALLER | bolt on every enemy panel after a short warning; the user doesn't faint |
| TSUNAMI | a 3-row wave |
| PERMAFROST | lock-on + freeze + Speed down |
| EARTH RENDER | 3-row shockwave that cracks every enemy panel it rolls over |
| DREAM DEVOURER | lock-on, drains 50% and heals the benched party too |
| VENOM STORM | 5 drops (only one can hurt), each leaves a poison panel |
| DRAGON RUSH / STAMPEDE | whole-row dash, no recoil, no confusion |
| THOUSAND FISTS | 6 × 30 on a 3-panel line, every hit a crit |
| MUDSLIDE | 3-row ground wave + accuracy down |
| ROLLING THUNDER | Air Hockey puck, up to 5 hits |
| Z-HYDRO / FLARE / VOLT / FROST / PSI / DRAIN / SLUDGE | 200–240 cannon; status 100% (burn / paralysis / freeze / confusion / bad poison) or 100% drain |

## Contest-combo rewards
- **What counts as a combo:** two consecutive chips of one chain where Emerald's own `AreMovesContestCombo(prev, next)`
  is true (contest_effect.c:60). Examples: Leer → Bite, Rain Dance → Water Gun, Growth → Absorb, Charge → Spark.
- **The three rewards you kept, all on by default:**
  - **dmg:** the follow-up does ×1.5. A contest combo doubles appeal (contest.c:4489); battle gets half of that, which is a TUNE value.
  - **effect:** the follow-up's side effect always happens (`secondaryEffectChance` treated as 100%).
  - **panel:** the follow-up changes the target's panel by its type, using BN6 panel types:
    - Ground, Rock, Fighting → cracked
    - Poison, Bug → poison
    - Grass → grass
    - Water, Ice → ice (non-Water Pokémon slide, from the BN6 ice rule)
    - Normal, Psychic → holy
    - other types → no panel
- **Switching rewards on and off:** start the game with `PKBN_COMBO=dmg,effect,panel`, or any subset, to compare how they feel.

## Verified (headless self-test)
Scripted picks are set with `PKBN_TEST_PICKS`, and `PKBN_NO_SHUFFLE` turns off shuffling.
- **Program Advances** formed and hit: Z-HYDRO (101 dmg), MEGA SOLAR BEAM (137), STORM CALLER (115), EARTH RENDER (102).
  VENOM STORM left a trail of poison panels; Wailord took poison-panel damage but dodged both drops aimed at it. See
  `screens/POC-6-*.png`.
- **Combos:** Growth → Absorb (left a grass panel), Charge → Spark (81 dmg, ×1.5), Rain Dance → Water Gun (left an ice panel). Leer → Bite was detected, but Bite missed.
- **No crashes:** all 17 POC-5 runs still finish without crashing, with the same outcomes as before.

## Not verified yet
- Hand play.
- The ×1.5 and the PA powers are first guesses.
