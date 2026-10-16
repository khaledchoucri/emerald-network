# POC-32: the folder keeps ladders together, BN6 chip animations for new moves

**Patches:** `0108-POC-32-the-automatic-folder-keeps-each-party-Pokemon.patch` and `0109-POC-32b-version-0.32.patch`, on top of 0001–0107. Version 0.32.

Your 0.31 picks: F1a, K1a, E1a, and 17 animation picks (14 chips, 3 kept as they were).

## The automatic folder keeps ladders together (F1a)

`SeedProgramAdvances` in `src/pkbn/folder.c` runs before the greedy fill. It is used by the automatic folder and by
BALANCED in the FOLDER screen's SELECT menu.

1. **Ladders:**
   - For each party Pokémon in party order, it adds the three ladder moves in their shared code.
   - It uses * when that code has no copy left.
   - It does this only when the pack has all three in that code and the Pokémon can use them.
   - The lead gets two of each, the others one of each.
2. **Program Advances that come naturally** (your note): each named Program Advance whose three chips the pack has in
   one code (or *) and the party can use gets one of each.
3. **Limit:** at most half the folder is filled this way (TUNE). The greedy fill does the rest, as before.

- **The ladder table:** `gPkbnLadderOf[NUM_SPECIES]` (`src/pkbn/move_table.c`), generated from
  `data/learnset_ladders.json` by `tools/gen_move_table.py`.
- **Logging:** each build that seeds anything logs `folder: seeded N ladders and M Program Advances (K chips)`.
- **An edited folder** (FOLDER screen) is used as it is. This only changes the automatic one.

## K1a and E1a

Kept as built in 0.31: a ladder's code is open for its moves from the start, and the 32 early attacks stay.

## BN6 chip animations for new moves (M4b)

Each chip was followed from its attack family (`AIAttackJumptable`, `upstream/bn6f/asm/asm31.s`) to the objects it
spawns (`T1/T3/T4BattleObjectJumptable`, `asm/asm00_1.s`), then to their `sprite_load` calls. `sprite_load(flags,
list * 4, index)` (`asm/sprite.s:56`) picks the sprite from `SpritePointersList`. The tracing script is in the
scratchpad, not the repo. The pixels are generated at build time from your `upstream/bn6f` and never committed, like
the other 55. A second, independent trace corrected three animation numbers (FireBrn's flame, the dragon's
head, the needle) and found Risky Honey's bees, which Bug Buzz now shows instead of the hive.

| Move | Chip | What it shows | Sprite (list:index, animation) |
|---|---|---|---|
| Leaf Storm | Tornado (52) | the tornado, in Grass's colours | 3:0x17, 0, already used by Twister |
| Lava Plume | FireBrn1 (20) | the burner's flame | 3:0x0e, 0 (new: `FIRE_BURNER`) |
| Discharge | ElcPuls1 (34) | the pulse rings | 4:0x40, 0 (new: `ELEC_PULSE`) |
| Earth Power | SandWrm1 (101) | the worm's claw | 1:0x1a, 1 (new: `SANDWORM`) |
| Stone Edge | Lance (119) | the lance | 3:0x44, 0 (new: `LANCE`) |
| Dragon Pulse | HeatDrgn / AquaDrgn (46, 48) | the dragon's head, in Dragon's colours | 1:0x10, 4 (new: `DRAGON`; the chip plays 2–6 as the head arcs) |
| Iron Head | DrilArm (51) | the drill arm, spinning | 3:0x58, 1 (new: `DRILL`) |
| Bug Buzz | RskyHny1 (37) | the bee swarm | 4:0x31, 0 (new: `BEES`) |
| X-Scissor | MoonBld (84) | the crescent | 4:0x3c, 0, already used as `SLASH_WIDE2` |
| Ice Shard | AquaNdl1 (61) | a needle diving from above | 4:0x17, 4 (new: `NEEDLE`; `SPIKE` is its upright frame) |
| Seed Bomb | CornSht1 (64) | the corn burst, in Grass's colours | 5:0x12, 0, already used as `SPLASH` |
| Magnet Bomb | MagCoil (183) | the magnetic field | 4:0x43, 0 (new: `MAGNET_FIELD`) |
| Gunk Shot | BlkBomb (60) | MiniBomb's bomb in the air, darkened | 3:0x24, 0 (`BOMB`). BlkBomb is MiniBomb's sprite in a black palette. |
| Charge Beam | DolThdr1 (31) | the bolt along the row | 4:0x12, 0 (new: `BOLT_ROW`; `BOLT_ORANGE` is its column) |

- **Kept as they were:** Shadow Claw, Close Combat and Air Slash, as you picked.
- **Found along the way:**
  - The `SPLASH` effect we've used since POC-15 is CornSht's corn burst.
  - `FIRE_BURST` (4:0x48), our Fire impact since POC-15, is SandWrm's sand geyser, not a flame. It reads as fire in
    Fire's colours, so I left it. Say if you'd rather have FireBrn's flame there too.
  - DrilArm's hitbox object has no sprite. The drill is MegaMan's held attachment (`tempAttackObject`, entry 0x20 of
    `byte_80B8BD4`).

## The test player looks for Program Advances (`PKBN_BOT_PA=1`)

The campaign's test player never chose a Program Advance on purpose. Any it formed were by chance. With
`PKBN_BOT_PA=1`:

- at a Custom, it first looks for a named recipe in order, or a type trio, in its hand;
- the three chips have to chain (one code, or *) and the Pokémon in has to be able to use them;
- it picks the three in order, then goes on as before.

This is only for testing. Without it, the runs play as in 0.31, so the two can be compared.

## Tests

- **Campaign runs:** the same nine runs to Juan as for 0.30 and 0.31, then again with `PKBN_BOT_PA=1`:

  | | 0.31 | 0.32 | 0.32, test player looks for PAs |
  |---|---|---|---|
  | Catching, folders where the lead could chain a trio | 7 of 249 | 204 of 250 | |
  | Catching, Program Advances a run | 0 | 1.0 | 18.8 |
  | Catching, losses a run | 6.8 | 5.3 | 7.0 |
  | Catching, Winona / Tate & Liza / Juan won | 2 / 4 / 6 of 6 | 4 / 6 / 6 of 6 | 2 / 6 / 6 of 6 |
  | Alone, folders where it could chain a trio | 72 of 124 | 110 of 125 | |
  | Alone, Program Advances a run | 3 | 7 | 76.7 |
  | Alone, losses a run | 29 | 29.7 | 25 |

  - **Which ones (looking for them, all 9 runs):** Grass Trio 102, Water Trio 84, Fire Trio 76, Z-Drain 29,
    Blazing Fury 18, Ground Trio 16, Mudslide 14, and one each of Z-Psi, Verdant Edge, Stampede and Normal Trio.
  - **How folders are seeded:** in the normal runs, 4,398 of 5,146 folders were seeded. The most common seed was 1
    ladder and 1 Program Advance (1,986 folders), then 5 ladders (696).
  - Lead levels are within a level of 0.31's at every gym.
- **Battle regressions (33) and the 7 new-move battles:**
  - 34 give the same log as 0.31.
  - 5 (p1–p5, the Program Advance tests) only add the `folder: seeded` line.
  - 1 (t2) changes from the start: Gloom's folder is seeded with Venom Storm's three chips, so the folder and the
    battle differ. It's still won.
- **Overworld tests:** 51/51.
- **The 14 animations:** checked in the chip gallery (`PKBN_GALLERY`, 14 moves), and on a preview sheet of the
  decoded sprites.
- **Patches:** 0001–0109 applied onto the pin give the same tree as the build tested here.
