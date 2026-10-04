# 05 — Battle visuals (POC-8)

Everything here is drawn by our code in `src/pkbn/grid_draw.c` and `src/pkbn/grid_vfx.c`. It only reads the
battle state and never changes the rules. Where a picture comes from either game, the source is named.

## The canvas
- **What it is:** the grid battle draws a **264×176** canvas (`PKBN_CANVAS_W/H`, `include/pkbn/render.h`), 10% larger
  than the GBA's 240×160.
- **Panels:** BN6 places objects at `X = panelX*40 - 140`, `Y = panelY*24 - 20` (`object_getCoordinatesForPanels`,
  bn6f `asm/object.s:4576`), so its panels are 40×24. **Ours are 44×26**, as asked: slightly larger than BN's. Six
  columns fill the 264-pixel width exactly, the same way six 40-pixel panels fill BN's 240.
- **The window:** it always shows this canvas at an integer scale (3× = 792×528 by default; `PKBN_SCALE=N` still works).
  Outside battles the 240×160 GBA picture sits centred in it with a 12/8-pixel black border, so nothing is ever
  stretched by a fraction.
- **Self-test dumps:** `PKBN_DUMP_DIR` now saves 264×176 frames.

## Where the pictures come from
| What | Source | How |
|---|---|---|
| Pokémon | Emerald `gMonFrontPicTable` (`anim_front`, 2 frames), `GetMonSpritePalFromSpeciesAndPersonality` (shiny aware), `LoadSpecialPokePic` (Unown, Spinda spots), `gMonFrontPicCoords` y_offset for the feet line | decoded at runtime (`Gfx_LoadMonPic`) |
| Effects | BN6 battle sprites, 55 picked in `tools/fx_curated.py` (category:index anim in `data/SpritePointersList.s`) | extracted at build time from `upstream/bn6f/data/{sprites,compressed}` and inline `.byte` sprites by `tools/gen_bn6_gfx.py`. The output, `include/pkbn/bn6_gfx_data.h`, is gitignored (CLAUDE.md rule 6). |
| Text | Emerald's normal and small fonts (`gFontNormalLatinGlyphs`, `gFontSmallLatinGlyphs`, decoded the way `DecompressGlyphTile` does) | runtime |
| Type icons | Emerald `gMoveTypes_Gfx` / `gMoveTypes_Pal`, layout and palettes from `pokemon_summary_screen.c:774,907` | runtime |
| Poké Ball | Emerald `gBallSpriteSheets` / `gBallSpritePalettes`, `ItemIdToBallId` | runtime |
| Party icons | Emerald `GetMonIconPtr` (as before) | runtime |
| Panels, HUD frames, backdrop, beams, arrows | our own pixel art in the BN style (TUNE) | code |

**BN6 sprite format** (checked by rendering MegaMan's 24 animations from `battleSpriteMegaMan.spr`):
- Byte 3 is the animation count. u32 offsets at +4 (relative to +4) point to the animations.
- Each frame is 20 bytes: `{tileset, palette, sub-anim, OAM, delay, -, flags, -}`. Flags 0x80 = last frame, 0x40 = loop.
- OAM entries are 5 bytes: `{tile, x, y, size, shape|hflip 0x40|vflip 0x80}`.
- Compressed entries are GBA LZ77 with a 4-byte size prefix.

The generator gives byte-identical output on the cloud copy and on your `upstream/bn6f` (pinned d57c196).

## Field
- **Panel art:**
  - A silvery face inside a red (player) or blue (enemy) frame, with a front edge on the bottom row (BN6 look, our art).
  - Cracked: crack lines.
  - Broken: a hole with a jagged rim.
  - Poison: purple with rising bubbles.
  - Holy: gold with a glinting cross.
  - Grass: green with swaying blades.
  - Ice: pale blue with a glint sliding across.
- **Attack warnings:** BN's flashing yellow on the panels about to be hit. Your own attack's area gets a light tint.
- **Backdrop:** a scrolling "Net" grid. Rain, sun, sandstorm and hail change its colours and add particles.

## Fighters
- **The sprite:** the Emerald front picture, mirrored on the player's side so both face each other. Fighters are drawn by
  row, back row first, as BN draws objects. Each has a shadow ellipse on its panel.
- **Idle:** a 1-pixel breathing bob.
- **Attacking:** Emerald's second front frame plus a 3-pixel lunge, for 14 frames.
- **Hit:** white every other frame plus a jolt (BN). While invincible: BN's blink.
- **Status:**
  - Frozen: tinted ice-blue.
  - Paralysis: a yellow flicker plus BN sparks.
  - Poison and burn: a tint pulse.
  - Sleep: frame 0 with floating "z".
  - Confusion: BN's dizzy birds.
- **Charging:** BN's charge rings. **Barrier:** BN's barrier.
- **Fly:** 48 px up with a small shadow. **Dig / Dive:** a moving mound or ripple on the panel.
- **Faint:** the picture slides down into its panel, as Emerald's faint does.
- **Send-out (battle start, switches, trainer send-outs):** a white burst and sparkles, then the Pokémon grows in from the
  ball, white at first.

## Attacks (`grid_vfx.c`: kind first, then the Gen 3 type)
| Kind | Visual |
|---|---|
| CANNON / AIRSHOT / VULCAN / SPREADER | BN muzzle flash + a shot down the row; burst only where it hits. Program Advance cannons: a beam down the row. |
| SWORD / LONGSWORD / DASH | BN slash (tinted by type) + type burst |
| WIDESWORD / LIFESWORD | BN slash arc; Water: BN water spray |
| LINE3 / CONE | type burst on each panel; Fire: BN flame jet (its burner nozzle clipped off) |
| FIREHIT / GOLEMHIT | Fire: tall flames; Electric: bolt; Ice: ice; others: big star + dust; screen shake |
| METEORS | Rock / Ground / Fire / Steel: BN meteor + explosion; others: a falling drop of the type + its burst |
| FIELD | Electric: a bolt on every panel; Water / Ice: spray / spikes; others: BN explosions; flash + long shake |
| BOMB | BN bomb in an arc, small explosion |
| SHOCKWAVE | a rock riding a dust plume along the floor |
| WAVE | BN water wave (Water / Ice) or wind (others), tinted |
| BALL | Fire: BN fireball; Electric: sparks; Water: bubble; otherwise a glowing orb in the type colour |
| TORNADO | BN tornado |
| LOCKON | BN lock-on reticle, then a big hit |
| DELAYED | BN vortex drifting down the row |
| SWEEP | a beam band across each swept panel |
| STATUS | on the target: BN paralysis / dizzy birds / poison swirl / smoke (sleep) / flame (burn) |
| STATS | rising (raised) or falling (lowered) arrows in red / blue |
| SELF | heals: BN heal sparkles; others: charge rings |

**Type bursts (TypeImpact):**
- Normal: star.
- Fighting / Steel / Dragon: hit flash.
- Flying: wind.
- Poison: swirl.
- Ground / Rock: rocks.
- Fire: fire burst.
- Water: spray.
- Grass: green sparkles.
- Electric: spark.
- Psychic / Ghost: vortex.
- Ice: ice spikes.
- Dark: claw.
- Buster: small spark.

**Other feedback:**
- Damage numbers in Emerald's font, only for 2+ HP: white for damage, green for healing.
- Shake: a quarter of max HP or more shakes the screen hard; one twelfth or more shakes it lightly.
- Program Advance launch: a flash in the type's colour.

## Custom screen (BN6 layout)
- **The window:** fills the left half of the screen; the field stays visible, dimmed, on the right.
- **Chip picture:**
  - Shows the owner's front sprite and a looping preview of the effect that move makes.
  - The background is tinted by type, with a moving grid.
  - The code letter sits in the corner.
- **Info line:** Emerald type icon, move name, power, kind, PP, and "X IN" when a benched owner will switch in.
- **Slots:**
  - 5 chips, each showing the owner's icon, the code letter and a type-coloured face. Picked chips show their order
    number; chips you can't pick right now are dimmed.
  - Row 2: the wildcard Switch, the Poké Ball slot (ball sprite, count, `<>` to change) and OK (START).
- **Cursor:** BN's blinking gold corner brackets.
- **Chosen chips:** stack on the right in type colours. A forming Program Advance shows under them, flashing.
- **Input:** unchanged. Up and down still step through the slots in order, and left/right on the ball slot change the
  ball.

## TUNE / to review
- Which BN sprite goes with each kind and type, the tints, and the shake thresholds.
- Panel art and colours.
- Damage numbers on or off: BN shows none; ours appear for 2+ damage.
- Emerald sprites are 64×64 on 44-pixel panels, so big Pokémon overlap neighbouring panels (as BN navis overlap upward).
