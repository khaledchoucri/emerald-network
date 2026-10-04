# POC-5 — BN attack kinds, panels, statuses, lane codes

Patch: `poc/patches/0006-POC-5-BN-attack-kinds-for-every-move-panels-Gen-3-st.patch` (on top of 0001–0005).
Design: `docs/design/04-attack-kinds.md`.

## What it adds
- Every move plays as one of 34 attack kinds, with its own timings.
- Projectiles: balls, waves, shockwaves, an Air Hockey puck, a delayed shot.
- Charge-ups, invulnerable wind-ups (Fly, Bounce, Dig, Dive), and multi-hit attacks.
- Panels: cracked, broken, poison, holy and grass.
- Gen 3 statuses, confusion, trapping, Leech Seed, weather and end-of-turn effects, on a turn clock.
- Folder: lane letters, benched chips that switch in, and the wildcard Switch as a permanent 6th slot.
- Code split:
  - `src/pkbn/grid_battle.c`: flow, Custom screen, party, AI
  - `grid_moves.c`: kinds, damage, effects
  - `grid_field.c`: panels, statuses, turns
  - `grid_draw.c`: drawing
  - `move_table.c`: generated

To regenerate the table after editing the curated files:
`python3 tools/gen_move_table.py <pc_port checkout>`

## Verified (headless self-test, Ubuntu, 2026-10-04)
All runs exit with an outcome and no crash. Scenarios, given as player party, then the wild Pokémon:

| Run | Kinds exercised | Seen in the log / frames |
|---|---|---|
| Pikachu vs Zigzagoon | FireHit (Quick Attack), Status (Thunder Wave), LongSword | FireHit warning, enemy dodge (34%), paralysis |
| Gloom vs Machop | Cannon, Ball (Poison Powder), Panel (Toxic seed) | Toxic lands as a 3×3 poison swamp, foe badly poisoned |
| Marshtomp/Pelipper/Kirlia vs Linoone | Dash (Take Down) + recoil, Cannon + Speed drop | benched chips switch in |
| Swellow/Sandslash vs Geodude | Panel (Spikes), Dig, FireHit, enemy Bomb, Field (Self-Destruct) | cracked panels break into holes when stepped off |
| Snorlax/Vulpix vs Altaria | Ball (Will-O-Wisp), Bomb-x (Fire Blast), Tornado, Cannon + recharge | Safeguard set |
| Breloom/Magneton vs Koffing | Cone (Smog), Panel (Poison Gas), Status, Field | poison panels, end-of-turn poison |
| Sandslash vs Wailord | Meteors, Air Hockey, Shockwave rows=3, WideSword | (screens/POC-5-kinds.png) |
| Gardevoir / Lapras / Camerupt / Beautifly / Heracross vs Wailord | Delayed, Ball (sleep), LifeSword, AirShot, Wave, Line3, GolemHit, Rollout chain, Spreader, Whirlwind push, Vulcan | Rollout power doubles on repeat |
| Mudkip vs Graveler / Jigglypuff / Xatu / Pidgeotto / Grimer | enemy Shockwave, Sing ball, Rest + wake on hit, Teleport flee, Fly, Gust push, Poison Gas | outcomes 1, 2 and 10 (Teleport) |

## Not verified yet
- Played by hand. Khaled, please play: wild battles now use every kind.
- Program Advances and combo rewards are not built.
- Earned switch chips are not built.
- Ice panels are not used by any move yet.
- Moves whose kind is NONE (Transform, Sketch and others) say "can't use that on the grid yet".
