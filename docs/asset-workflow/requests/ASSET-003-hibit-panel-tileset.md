# ASSET-003 — Hi-bit battle panel tileset

## Coordination

- State: accepted
- Priority: 3
- Assigned producer: Codex
- Current owner: —
- Brief revision: 4
- Based on repository commit: 362b782
- Last update (UTC date): 2026-10-13
- Next action / blocker: none (in the game since POC-24)

## Purpose and visual brief

- **Intended use:** the battle grid's panels in the hi-bit renderer. Today they are drawn by code at 44×26
  (`DrawPanel`, `src/pkbn/grid_draw.c:189`; `PANEL_W`/`PANEL_H`, `include/pkbn/grid_internal.h:35-36`).
- **Deliverable type:** production source, as a sprite sheet.
- **Subject:** one panel per cell, seen straight on and slightly from above, as in ASSET-001. Each panel has:
  - a frame in the side's colour (red for the player, blue for the foe);
  - an inner face that shows the panel type.
- **Panel types** (`include/pkbn/grid_internal.h:73-91`). For each, the face and what the player must read from it:

| Cell (column, row) | Type | Face and what the player must read |
|---|---|---|
| (0, 0) | NORMAL | Silvery glossy metal |
| (1, 0) | CRACKED | Metal with crack lines: it will break |
| (2, 0) | BROKEN | A hole with a jagged rim; transparent centre |
| (3, 0) | POISON | Purple with bubbles: it hurts |
| (4, 0) | HOLY | Gold with a glinting cross: it protects |
| (5, 0) | GRASS | Green with blades |
| (0, 1) | ICE | Pale blue with a glint: it's slippery |
| (1, 1) | LAVA | Glowing orange-red: it burns |
| (2, 1) | ROAD UP | Metal with a conveyor chevron pointing up |
| (3, 1) | ROAD DOWN | Metal with a conveyor chevron pointing down |
| (4, 1) | ROAD LEFT | Metal with a conveyor chevron pointing left |
| (5, 1) | ROAD RIGHT | Metal with a conveyor chevron pointing right |

- **Style:** follow `docs/asset-workflow/STYLE.md`, "The panel": the frame, stepped corners, glass sheen, front edge,
  and the type faces (cracked without glow; grass and ice inside the face). Neutral light: no light baked in.
- **Elements to avoid:** text, logos, and copying Battle Network's panel art.
- **Variant count:** 1, after a reviewed sample. First deliver only NORMAL, CRACKED, BROKEN and the front edge for both
  sides, in their sheet positions. Once those are reviewed, do the rest.

## Technical target (required for production assets)

- **Integration:** the hi-bit renderer (roadmap round 3; not yet in code). Until it exists, this sheet is checked by the
  implementation agent's preview tool, not in game.
- **Cell size:** 88×52 per panel (2× of 44×26).
- **Front edge:** one 88×12 strip per side (2× of `PANEL_LIP` 6). The engine draws it under every bottom-row panel
  except BROKEN, which has none (`DrawPanel`, `src/pkbn/grid_draw.c:199-208` and `:338-344`). It uses the side's frame
  colour, the same for every panel type.
- **Anchor:** the top-left of each cell. The panel fills the cell edge to edge.
- **Sheet layout:** one sheet per side (`panels_red.png`, `panels_blue.png`), 528×116:
  - rows 0 and 1: 6 columns × 2 rows of 88×52 cells, at the positions in the table above (no empty cells);
  - row 2 (y 104-115): the front-edge strip at x 0-87; the rest of that row is transparent.
- **Format:** PNG with alpha. Panels are opaque except BROKEN's hole.
- **Palette:** at most 16 colours per panel cell (TUNE; the implementation agent checks this and quantizes).
- **Animation:** none in this request. Grass sway, bubbles and glints come later as separate overlays.
- **Conversion and cleanup:** the implementation agent snaps to the pixel grid, quantizes the palette and packs the atlas.

## References

| Path | Role |
|---|---|
| ASSET-001's accepted variant | Style |
| `docs/asset-workflow/STYLE.md` (to be written) | Palette and outline rules |
| `docs/asset-workflow/references/hibit_battle_layout_528x352.png` | Cell geometry |
| `poc/screens/POC-5-poison-panels.png` | Today's code-drawn panel types, for readability, not style |

## Acceptance criteria

- **Source art:**
  - Every type is identifiable at native size (88×52) and at half size.
  - The red and blue sides match apart from the frame colour.
  - BROKEN's centre is fully transparent.
- **In game** (implementation agent, after the renderer round): a battle preview with every type on the field, captured
  as a screenshot, readable at 1× and 3× scale.

## Producer record

- Brief revision used: 4 (complete v002 set); v001 used revision 3.
- Assumptions / unresolved constraints: generator output is source artwork, not the requested exact packed atlas; see delivery limitations.
- Tool and generation/edit prompt: image_gen.imagegen; exact prompts in `poc/assets/generated/ASSET-003/v001/PROMPTS.md`.
- References actually supplied to the tool: approved ASSET-001 v003 for red; red sample for blue. No game screenshot or extracted sprites supplied.

### Delivery v001

- Files: `poc/assets/generated/ASSET-003/v001/panels_red_source.png` and `panels_blue_source.png`, published for GitHub review.
- Actual properties: both 2014×781 RGBA PNGs. Three visually contiguous panels NORMAL/CRACKED/BROKEN in upper-left plus a separate lip lower-left; unused canvas transparent. These are high-resolution source samples, not 528×116 atlases; sample cells are not in the requested exact coordinates.
- Visual inspection: squared stepped face corners, side-colored frames, neutral cool silver NORMAL, dark non-glowing CRACKED face, jagged BROKEN rim, slate front lip. Blue was derived from red and closely follows its shapes, but exact pixel-identical geometry/faces apart from frame color is not achieved.
- Checks: all PNG chunk CRCs and full pixel decoding passed. BROKEN interior probe at (850,270) is alpha 0 in both files. Sample NORMAL/CRACKED/front-edge pixels have alpha 253–254 rather than fully opaque 255. There are also stray low-alpha pixels around/outside the artwork; clean before use. Aggregate counts, SHA-256 and bounds recorded in `validation.json`.
- Failed/unmet production checks: exact 528×116 atlas dimensions/coordinates, fully opaque solid faces, binary crisp edges, exact matched geometry between sides. At most 16 colors per cell and strict hi-bit pixel alignment are not established. No native 88×52/half-size review or renderer test was performed because the images have not been converted/packed.
- Implementation handoff: clean stray/partial alpha while preserving the BROKEN hole; extract the three panels and lip; establish shared geometry between red/blue; snap to the hi-bit grid and quantize to ≤16 colors per cell; pack panels at (0,0),(88,0),(176,0) with 88×52 cells and lip at (0,104) with 88×12 size into 528×116 sheets. For this initial sample only, all remaining cells and unused lip band stay alpha 0. Validate normal/cracked opacity, broken-hole alpha, exact dimensions, palette and native/half-size readability in the preview tool. Runtime acceptance follows when the renderer exists.
- v001 samples were visually approved by Khaled with the note that blue borders appear thicker. Production acceptance remains pending. The remaining types are now supplied in v002.

### Delivery v002 — complete source sets

- Files: `poc/assets/generated/ASSET-003/v002/panels_red_source.png` and `panels_blue_source.png`. Blue is derived from the complete red source with explicit instructions to retain its frame geometry/width.
- All 12 types, in order: top row NORMAL, CRACKED, BROKEN, POISON, HOLY, GRASS; bottom row ICE, LAVA, ROAD UP, DOWN, LEFT, RIGHT. One separate front edge per sheet below column 0.
- Actual dimensions: red 2012×782, blue 2011×782, both RGBA. Generator output remains source artwork rather than the 528×116 packed atlas. The one-pixel canvas-width difference alone prevents a pixel-identical red/blue geometry claim.
- Visual check: all types present in the requested order; square inset corners retained; dark non-glowing cracked metal contrasts with orange/yellow lava; poison bubbles, gold holy cross, green grass, flat blue ice facets and road chevrons identifiable. No text or logos. Blue frames more closely follow the red geometry, but exact border equality is not verified.
- PNG CRC and full decode passed for both; interior probe in BROKEN is alpha 0 in both. Partial-alpha pixels and edge residue remain, as with v001; details and file hashes in `validation.json`.
- Exact cell size/atlas placement, fully opaque non-hole faces, crisp binary alpha, palette ≤16 colors per cell, native/half-size readability and runtime acceptance remain unverified or unmet. Implementation agent must apply the v001 cleanup/packing handoff to all 12 cells and explicitly equalize the red/blue frame widths before testing.
- Complete source review pending; sample approval does not imply approval of all new faces or renderer acceptance. Raw images copied without programmatic edits. Prompts/reference record in `v002/PROMPTS.md`.

## Consolidated review

- Reviewed delivery: v001 source samples
- Reviewer: Khaled
- Required changes: blue frames appear thicker; match red frame width and inner-face geometry on both sides.
- Optional preferences: none recorded
- Decision and reason: user approved the panel look and authorized remaining types; production acceptance remains pending.

## Integration and acceptance (implementation agent)

- Implementation review (2026-10-14, Claude), of v002 shrunk to 88×52 on a test field:
  - every type reads at native size, cracked and lava are clearly different, and the red and blue frame widths now
    measure the same;
  - the source panels are about 9% taller in proportion than the 88×52 cell (330×213), so packing squashes them
    vertically; this isn't visible at native size;
  - the front edge shrinks to 15 px tall against the 12 px slot, so it will be trimmed, not squashed;
  - cleanup of semi-transparent pixels is still to do. No redraw needed.

- Accepted delivery: v002 (red and blue)
- Integrated paths / patch / commit: generated include/pkbn/hibit_gfx_data.h; host patch 0094 (POC-24/25)
- Conversion details: tools/pack_hibit.py: each row split into six equal cells (the blue rows touch, so its band is halved); area-average shrink to 88x52, 16 colours per panel, hard alpha (BROKEN keeps its hole); front edge shrunk to 88 wide and trimmed to 12 rows from its middle. Sheet order mapped to the game's panel order (lava last).
- In-game test command or scenario: PKBN_GALLERY (seven Fire moves) and battle self-tests, with PKBN_HIBIT=0 for the old art
- Results and screenshot/log evidence: poc/screens/POC-24.png; battle logs unchanged (33/33)
- Remaining work: the old code-drawn panel animations (poison bubbles, grass, road arrows, lava, glints) are gone until animated panel frames are requested

## Change history

- 2026-10-13 — implementation agent (Claude) — created at revision 1 as a draft; it waits on ASSET-001.
- 2026-10-13 — implementation agent (Claude) — revision 2, answering Codex: revision 1's grid had 18 cells for 12 types
  and asked for two front-edge strips by mistake. Now 12 cells with no gaps, and one strip per side (the code draws
  one). Still a draft until `STYLE.md` exists.

- 2026-10-13 — implementation agent (Claude) — revision 3: STYLE.md written from ASSET-001 v003; ready for Codex.

- 2026-10-13 — Codex — delivered v001 red/blue source samples with NORMAL, CRACKED, BROKEN and lip; exact atlas/alpha cleanup and sample review pending.

- 2026-10-13 — Codex — brief revision 4: Khaled visually approved v001 samples, noted blue borders look thicker, and authorized continuation. Use red frame geometry for both sides.

- 2026-10-13 — Codex — delivered complete v002 red/blue panel source sets using the red border as reference. Geometry/alpha/palette cleanup and full-set review remain pending.

- 2026-10-13 — Codex — Khaled visually approved the full v002 panel source set. Production/native-size/renderer acceptance remains with the implementation agent.

- 2026-10-14 — implementation agent (Claude) — review of the source art recorded; packing and in-game tests follow in POC-24.

- 2026-10-14 — implementation agent (Claude) — integrated in POC-24 and accepted in the game.
