# POC-8 — Battle visuals

**Patch:** `poc/patches/0010-POC-8-battle-visuals-264x176-canvas-with-44x26-panel.patch` (on top of 0001–0009).
**Design notes:** `docs/design/05-visuals.md`, which lists every picture's source and every visual choice.

**New tools (repo `tools/`):**
- `fx_curated.py`: the 55 BN6 effect sprites we use.
- `gen_bn6_gfx.py`: extracts them from `upstream/bn6f`.
- `gen_fx_ids.py`: writes their names to `include/pkbn/fx_ids.h`.

`scripts/setup_host.sh` now runs `gen_bn6_gfx.py` before every build. It needs python3, standard library only. The
extracted pixels go to the host's `include/pkbn/bn6_gfx_data.h`, which is gitignored and never committed (CLAUDE.md
rule 6). On your checkout the output is byte-identical to mine (md5 915e51d1…).

## What changed on screen
- **Canvas:** 264×176, with 44×26 panels (BN6: 40×24, `object_getCoordinatesForPanels`, `asm/object.s:4576`). The
  window opens at 3× (792×528). Outside battles the GBA picture is centred with a thin border, so the scale is always a
  whole number.
- **Pokémon:** Emerald front sprites (shiny palettes, Unown letters and Spinda spots included), mirrored on your side.
  - Breathing idle, an attack pose (Emerald's 2nd frame) with a lunge, and a white-flash jolt when hit.
  - Status looks for sleep, paralysis, freeze, poison, burn and confusion.
  - Fly, Dig and Dive, the faint slide, and a ball-burst grow-in on every send-out.
- **Field:** BN-style panels (silver face, red/blue frame, front edge) with drawn cracked, hole, poison, holy, grass and
  ice states. BN's yellow warning flash. A Net backdrop that changes with the weather, plus rain, hail, sand and sun.
- **Attacks:** BN6 effect sprites chosen by attack kind, then by Gen 3 type. Examples:
  - Slash arcs.
  - Flame jet (Flamethrower).
  - Meteors (Rock Slide).
  - Water spray (Surf).
  - Bolts on every panel (Storm Caller).
  - Lock-on reticle, tornado, bomb, explosions.

  Program Advances get type-coloured flashes, beams and shakes. Damage numbers use Emerald's font. Heavy hits shake
  the screen.
- **HUD:** BN's HP box (big number) with a Gen 3 HP bar, name, level and status tag, and party balls. The enemy panel
  shows the trainer's remaining Pokémon. The Custom gauge says PRESS L / R when full. The next chip shows at the bottom.
  All text uses Emerald's fonts.
- **Custom screen:** BN6 layout.
  - A chip picture showing the owner's sprite and a looping preview of the move's effect.
  - An info line: Emerald type icon, name, power, kind, PP.
  - Five chip slots with owner icons and code letters, plus the wildcard Switch, Poké Ball and OK.
  - Chosen chips stacked on the right, and a flashing Program Advance banner.
  - Input is unchanged.

## Verified
- **All 33 self-test battles** (t2–t7, k1–k6, e1–e5, p1–p5, c1, x1–x10) produce **byte-identical battle logs** to
  POC-7. The visuals change nothing in the rules (the only change in `grid_moves.c` records what hit each panel, for
  drawing).
- **All patches 0001–0010 apply cleanly** on the pinned pc_port commit.
- **Contact sheets** from self-test dumps of every attack kind, the Program Advances, status moves, panel types, the
  time-stop switch, trainer send-outs, the throw, and the Custom screen with each slot type (shown in chat, not
  committed, because they contain BN6 sprites).

## Not verified / known gaps
- Hand play at full speed.
- Big Pokémon overlap the panels next to them, since 64×64 sprites sit on 44-pixel panels.
- The post-battle screens (EXP, learning moves, evolution) are unchanged Emerald screens; they sit inside the border.
- Every visual mapping is TUNE: which BN6 sprite goes with which kind and type, the tints, and the shake thresholds.
- Not done yet: Emerald's per-species front animations (`sMonFrontAnimIdsTable`), Emerald's move-animation
  backgrounds, a Program Advance cut-in, and BN's real chip images.
