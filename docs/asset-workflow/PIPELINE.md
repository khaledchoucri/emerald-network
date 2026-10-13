# Asset pipeline plan

This plan is from the implementation agent (Claude). It sits on top of [README.md](README.md), which stays the contract.
It says what we are making, in what order, and the rules every request shares.

## The decisions it follows

These are Khaled's picks on the vision pages ("Two Worlds, One Battle" and "Thinking bigger", 2026-10-13):

- **Art direction: hi-bit**, meaning twice Emerald's pixel detail. Battles come first. Towns and routes keep Emerald's
  detail until we decide to redraw them, the largest art job in the plan.
- **Ideas being built:**
  - modern light;
  - every Pokémon animated;
  - rivals who study you;
  - cinematic boss fights;
  - Program Advances as a headline feature.
- **Sharing: friends only for now.** CLAUDE.md rule 6 still applies: no extracted game assets in the repo.

## What Codex makes, and what it doesn't

**Codex makes original art:**

- panels;
- attack effects;
- Program Advance and UI frames;
- the Net backdrop;
- light and particle elements;
- concept frames.

All of it is our own design.

**Codex does not draw:**

- **Pokémon, Mega Man, Navis, or any other existing character.** Concepts use the original placeholder fighters from
  ASSET-001.
- **Logos.**
- **Copies of Battle Network or Pokémon sprites or UI.**

**Pokémon animation is handled differently.** It comes from the games' own animated sprites in the player's own files,
through an importer the implementation agent writes. Those files are never committed.

## Order

1. **Style** (ASSET-001). Three variants of one battle frame. Khaled picks one. The implementation agent then writes
   `STYLE.md`: palette, outlines, light and glow, and pixel density.
2. **Program Advance moment** (ASSET-002). A concept for POC-22, which makes Program Advances found earlier and rewarded.
3. **Battle production assets.** Each batch starts with one reviewed sample before scaling up:
   - panels (ASSET-003);
   - the fire effects (ASSET-004), then the other types' effects, one type per request;
   - the Net backdrop;
   - HUD and Custom-screen frames;
   - Program Advance cards and the emblem.
4. **Later:**
   - light elements for modern light (lamps, window glow, weather particles);
   - boss-fight set pieces (arena break-up frames, cut-in frames).

## Who checks what

**Codex** delivers source art under `poc/assets/generated/<ID>/vNNN/` and records it in the request.

**The implementation agent:**

- snaps the art to the pixel grid;
- quantizes the palette;
- packs the atlas;
- checks it in the renderer.

Nothing is "accepted" until it's seen in the game. Until the hi-bit renderer exists (roadmap round 3), production
sheets are checked with a preview tool, and that limitation is recorded in the request.

## Source-art rules (learned from ASSET-003 and ASSET-004)

The first deliveries were approved on looks, but most of the work to make them usable was cleanup. These rules cut
that work. They apply to every request from ASSET-005 on.

1. **Every pixel is fully opaque or fully transparent.** No soft halo, glow fringe or anti-aliased edge. Glow is drawn
   as hard rings (STYLE.md rule 5). About a quarter of the pixels in the ASSET-004 sheets were semi-transparent.
2. **Nothing outside the art.** The canvas around and between frames is alpha 0. Faint stray pixels across the whole
   canvas made frame-finding unreliable.
3. **Draw at a whole-number multiple of the cell, with the cell's proportions.** If a cell is 88×52, draw it at
   352×208 (4×) or 264×156 (3×), not at 330×213. Then shrinking it to the cell is exact, and nothing gets squashed.
   Say which multiple you used.
4. **One row of frames, evenly spaced, each in its own cell-sized box,** left to right, with at least 8 px of empty
   space between boxes. One PNG per effect or part.
5. **Same geometry for variants.** Colourways or sides (red and blue panels, player and foe plates) share outlines
   pixel for pixel, so only colours differ. Draw one, then recolour it.
6. **Tintable art uses the 5 greys** listed in ASSET-006, so the game can colour it by type.
7. **Programmatic cleanup is welcome.** Thresholding alpha, cropping, recolouring and packing with a script before
   delivery is fine. Record what was done in the producer record.

## Effects still to replace, in order

After ASSET-006 (impacts), one request per family. Each will reuse ASSET-006's tint ramps where it can.
The list comes from `tools/fx_curated.py`.

| Family | Effects |
|---|---|
| Strikes | SLASH, SLASH_WIDE, SLASH_WIDE2, SLASH_ARC, LONGSWORD, CLAW, FANG |
| Water | BUBBLE, BUBBLE_POP, SPLASH, WAVE |
| Electric | BOLT, BOLT_ORANGE, SPARK, SPARKS, PARALYZE |
| Wind and spirit | TORNADO, WIND, VORTEX, CONFUSE |
| Earth | ROCKS, ROCK, BOULDER, METEOR, CRACK, SPIKE, LOGS |
| Ice | ICE, ICE_SPIKE |
| Status and support | POISON, POISON2, HEAL, HEAL2, CHARGE, CHARGE_RINGS, BARRIER, LOCKON, LEAF |
| Shots | SHOT, CANNON, MUZZLE, BOMB, BEAM |

## Practical notes

- **Repository paths.** Paths in requests are relative to the repository. Codex works from Khaled's checkout of this
  repository. The implementation agent works in a cloud copy and commits through Khaled's machine.
- **Generated reference images** in `references/` are our own drawings, each made by a script in `tools/`, so they
  are safe to give the image tool.
- **Project screenshots** in `poc/screens/` show game sprites. Use them for layout and scale only.
