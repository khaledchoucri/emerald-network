# Design 04 — BN attack kinds for every move, panels, statuses (review round 1 applied)

Status: **built** (POC-5, `poc/patches/0006-*.patch`), awaiting Khaled's round-2 review in the
"Chip Lane Review" page (round-2 verdicts are saved under `v2:` keys in its database).
Sources of truth:
- `tools/attacks_curated.py`: the grid kind of every Gen 3 move, with one comment per non-obvious choice.
- `tools/lanes_curated.py`: chip letters (round-1 edits marked `review:`) and `REMOVED` (moves cut by the review).
- `tools/gen_move_table.py` turns both into `src/pkbn/move_table.c` / `include/pkbn/move_table.h` in the host.

## 1. Round-1 review: what was applied
Read from the review page's database on 2026-10-04: 388 verdicts (326 approve, 18 change, 44 reject), 121 with notes.

- **Shape notes, applied as written.** Wide Sword: Wing Attack, Steel Wing, Cut, Slash, Razor Leaf, Leaf Blade, Crabhammer,
  Clamp, Cross Chop, Iron Tail, Low Kick, Poison Tail, False Swipe. Life Sword: Thrash, Surf, Muddy Water, Leech Life.
  Long Sword: Poison Sting, Twineedle. 3-panel line: Double Kick, Mega Kick, Jump Kick, Hi Jump Kick, Rolling Kick,
  Triple Kick, Blaze Kick, Crush Claw. Whole-row dash: Pursuit, Rollout, Volt Tackle, Waterfall. Gun Del Sol cone:
  Blizzard, Icy Wind, Dragon Breath. Air Hockey: Fire Spin, Bonemerang, Rapid Spin, Vital Throw. Bombs: Bounce, Ice Ball,
  Mist Ball, Water Spout. Fire Blast is a star-shaped bomb (centre plus diagonals). Fly is a slow bomb; the user can't be
  hit while it is in the air, and Fly has a 60-frame recovery. Spreader: Silver Wind. Cannon: Acid, Ancient Power.
- **Behaviour notes.**
  - Priority moves use FireHit (fast).
  - Low-accuracy status moves are slow balls: the lower the accuracy, the slower the ball.
  - Toxic and Poison Gas make poison panels.
  - Hyper Beam (and Blast Burn, Hydro Cannon, Frenzy Plant) recharge: the user can't pick chips at the next Custom.
  - Wish heals when the next Custom opens.
  - Future Sight and Doom Desire fire a delayed shot down the row.
  - Razor Wind is slow to launch.
  - Rest's sleep, and every sleep, breaks when the sleeper is hit.
  - Safeguard is a one-use barrier against status moves.
  - Magic Coat works like Safeguard but bounces the status move back.
  - Sleep Talk calls a random move, like Metronome.
- **Letters.** Every suggested letter set was applied. J was rejected, so Feather Dance's suggested "WDJ" became "WD".
  Take Down and Submission were rejected as "too weak for X"; they keep their chips, on H and on K.
- **Lanes.**
  - D is now DANCE: Swords, Dragon, Petal, Feather, Teeter and Rain Dance.
  - The dragon moves were re-homed: Outrage and Dragon Claw went to U, Dragon Rage to A and E, Dragon Breath to C and S,
    and Scary Face to T and N.
  - J was rejected, so it was removed. Its ghost moves went to N or to their effect lane.
  - B lost the OHKO moves.
  - U, V, W, Y and Z were marked "change" with no note. They were read as the move-level letter edits.
- **Cut (35).**
  - The OHKO moves: Guillotine, Horn Drill, Fissure, Sheer Cold.
  - Everything rejected with "remove", or rejected with no note: Destiny Bond, Disable, Double Team, Encore, Endure,
    Follow Me, Helping Hand, Foresight, Grudge, Imprison, Mind Reader, Minimize, Mirror Coat, Odor Sleuth, Pain Split,
    Perish Song, Present, Recycle, Smelling Salt, Snatch, Sonic Boom, Spite, Stockpile, Spit Up, Swallow, Substitute,
    Taunt, Torment, Trick, Uproar, Block.
- **Combo rewards.**
  - Kept: damage, side effect, panel effect.
  - Dropped: tempo, PP refund, combo meter.
  - The 19 Program Advances were all approved. DRAGON RUSH now chains on U. None of the PAs are built yet.

## 2. Attack kinds and their BN6 source
Chip names, descriptions and families are read from bn6f: `data/textscript/TextScriptChipNames0.s`,
`TextScriptChipDescriptions0.s`, and `data/ChipDataArr.s` (`attack_family` / `attack_subfamily`).

| Kind | What it does on our grid | BN6 chip (family/sub) and its in-game description |
|---|---|---|
| CANNON | first target down the row (`rows=3`: Tri Attack's three beams) | Cannon (0x14) "Cannon to attack 1 enemy" |
| AIRSHOT | cannon + 1 panel knock-back | AirShot (0x21) "Knock enmy back 1 square" |
| VULCAN | multi-shot, each hits target + panel behind | Vulcan1 (0x17) "3-shot to pierce 1 panel!" |
| SPREADER | cannon + 3×3 splash | Spreadr1 (0x25) "Spreads damg to adj panls" |
| SWORD / LONGSWORD / WIDESWORD | 1 ahead / 2 ahead / column of 3 | Sword, LongSwrd, WideSwrd (0x13) "Range: 1/2/3" |
| LIFESWORD | 2 columns × 3 rows | LifeSrd (Sword-family Program Advance) |
| LINE3 | 3 panels ahead in the row | FireSwrd (0x13/0xC) "Cut enmy 3sq fwrd w/fire!" |
| DASH | the whole row ahead | review note (no single BN chip) |
| CONE | 1 ahead, then 3 rows 2 ahead | GunDelS1 (0x37); shape per review note |
| TORNADO | 4 ticks on the panel 2 ahead (one hit's damage split) | Tornado (0x2F/1) "8hit strm 2 squares ahead" |
| FIREHIT | warned strike on the target's panel; dodgeable | FireHit1 (0x1C/8) "Slams closest enemy" |
| GOLEMHIT | same, target's column of 3 | GolmHit1 (0x1C/0x15) "Hit 3panl area arnd clst enmy" |
| METEORS | 3 warned rocks near the target | Meteors (0x15/0x10) "Drop many meteor on enmy area" |
| DIG | vanish, then burst out under the target | SandWrm1 (0x1C/0xC) "Attk enmy from rear w/snakarm" |
| DELAYED | a shot comes down the row ~4 s later | review note (Future Sight) |
| FIELD | whole enemy area; user faints | Gen 3 Explosion / Self-Destruct |
| BOMB `plus/x/square/single` | thrown 3 ahead, blast pattern | MiniBomb (0x12/0) "Throws a MiniBomb 3sq ahead"; BigBomb "9 panl bomb" |
| SHOCKWAVE | ground wave, panel by panel; stops at holes | WaveArm1 (0x31) "Fllw enmy and fire trap wave" |
| WAVE | flying wave, 1 or 3 rows | WideSht (0x30) "Fires 3sq shotgun blast!" |
| AIRHOCKEY | diagonal puck bouncing off walls | AirHocky (0x26) "Bounce the puck off walls" |
| BALL | slow ball; slower for lower accuracy | Thunder (0x1F) "Pralyzing electric attack!" + review note |
| LOCKON | crosshair, then an undodgeable hit | MachGun1 (0x29) "Fire 9sts at row w/ clst enmy" |
| BARRIER | absorbs the next hit (Gen 3 Protect odds) | Barrier (0x15/4) |
| PANEL | poison / cracked / holy / grass panels | PoisSeed "Makes 9sq poisn swp 3sq ahead", HolyPanl, GrasSeed |

Non-damage kinds:
- STATS: stat stages; always lands.
- STATUS: Gen 3 status; always lands.
- SELF: heals, cures, Wish, Haze, Bide, Belly Drum, Conversion and so on.
- WEATHER: Gen 3, 5 turns.
- BATON, ASSIST: unchanged.
- CALL: Metronome, Sleep Talk, Mirror Move, Mimic, Nature Power.
- NOTHING: Splash.
- NONE: Transform, Sketch, Conversion 2, Role Play, Skill Swap, Camouflage. These were not in the review and need their own design.

## 3. Panels (BN6 code we follow)
| Panel | Effect | Where in bn6f |
|---|---|---|
| cracked (type 2) | breaks into a hole when its occupant steps off | `object_crackPanel`, `object_breakPanel` |
| broken (type 3) | nobody can stand there; comes back after 10 s (TUNE) | `object_breakPanelLoud` (asm/object.s) |
| poison (type 4) | 1 "damage" every 7 frames while standing on it; we scale one damage to maxHP/128 | `object_panel_setPoison` (object.s:2517); timer reload 6 in `sub_801A186` (asm00_2.s:21629) |
| holy (type 5) | damage on it is `(d+1)>>1` | `object_calculateFinalDamage1` (object.s:4811) |
| grass (type 6) | heals Wood-element objects; here Grass types and Ingrain users, 1/16 per turn | `sub_801A186` |
| ice (type 7) | non-Aqua objects keep sliding | asm00_2.s:16535 (**not used yet**) |

## 4. Gen 3 rules carried onto the grid
- **Turn clock:** one Custom gauge of fight time (480 frames, TUNE) is one turn. Each turn applies Gen 3's end-of-turn amounts:
  - poison 1/8 and toxic n/16
  - burn 1/8
  - Leech Seed 1/8 (drained to the other side)
  - Nightmare 1/4 and Ghost Curse 1/4
  - wrap 1/16 for 2–5 turns
  - sandstorm and hail 1/16, with Gen 3's type immunities
  - Ingrain heals 1/16
  - weather lasts 5 turns
- **Statuses:**
  - sleep 2–5 turns (breaks when hit, per the review)
  - freeze thaws 20% per turn, and Fire moves thaw it
  - paralysis: Speed ×1/4 (four times slower steps), 25% full paralysis on chip use
  - confusion 2–5 turns, 50% to hit itself with the Gen 3 40-power self-hit; BN6 Discord-style reversed controls while confused
  - Attract 50%
  - Ability and type immunities as in Gen 3
- **Damage:** CalculateBaseDamage, then crit (Cmd_critcalc stages, Focus Energy +2), Charge ×2, STAB, the type chart,
  Wonder Guard, Levitate, Volt Absorb, Water Absorb, Flash Fire, then the random multiplier.
  Weather goes through gBattleWeather, so rain and sun boosts and Solar Beam's penalty come from Emerald's own code.
- **Power formulas from battle_script_commands.c:**
  - Flail, Reversal
  - Rollout, Ice Ball (doubles on each use, ×2 after Defense Curl)
  - Fury Cutter
  - Return, Frustration
  - Magnitude
  - Hidden Power
  - Beat Up
  - Psywave
  - Low Kick weight table
  - Eruption, Water Spout
  - Weather Ball
  - Facade
  - Revenge
  - Triple Kick 10/20/30
  - Secret Power uses gBattleEnvironment
- **Accuracy:** there are no rolls. The attacker's accuracy stage against the target's evasion stage
  (sAccuracyStageRatios) lengthens or shortens warnings and ball speed, so Sand Attack makes the foe easier to dodge.
- **Teleport** ends a wild battle, as in Gen 3, unless Mean Look or Spider Web is in effect.
- **Roar and Whirlwind** push the target to its back column (BN6 GoingRd) instead of ending the battle.
- **Spikes** crack 3 enemy panels. Rapid Spin repairs your area (BN6 PnlRetrn) and frees you from Wrap and Leech Seed.
  Brick Break clears holy panels and Barrier.

## 5. Folder changes
- Each chip copy carries one lane letter. Copy k takes the move's k-th letter.
- A selection is legal when all its chips share one letter, or are all the same move (BN6 rule).
- A benched Pokémon's chip is selectable when its letter matches. Using it brings that Pokémon in (time-stop), it uses
  the move and it stays in. This is my reading of round-1 point 2 and still needs Khaled's confirmation.
- The wildcard Switch is a permanent 6th Custom slot with code `*`. Nothing can follow it.
- The per-member Switch chips are gone until "earned" switch chips are designed.

## 6. Open questions (also on the review page)
1. Earthquake hits all three rows and can't be dodged, which is faithful to Gen 3 (it can't miss). Keep it?
2. Should freeze break when hit, as sleep now does?
3. Enemy sword users can't reach you while you stand back (same as BN viruses). Should they get a step-in?
4. How are switch chips earned?
