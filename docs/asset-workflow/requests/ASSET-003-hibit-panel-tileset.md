# ASSET-003 — Hi-bit battle panel tileset

## Coordination

- State: ready
- Priority: 3
- Assigned producer: Codex
- Current owner: Codex
- Brief revision: 3
- Based on repository commit: 362b782
- Last update (UTC date): 2026-10-13
- Next action / blocker: Codex delivers the first sample: NORMAL, CRACKED, BROKEN and the front edge, both sides, in
  their sheet positions, following `docs/asset-workflow/STYLE.md` (the panel section). The rest after its review.

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

- Brief revision used:
- Assumptions / unresolved constraints:
- Tool and generation/edit prompt:
- References actually supplied to the tool:

### Delivery v001

- Exact output paths (repository-relative), or attachment plus transfer status:
- Actual file format, dimensions, transparency, and frame layout:
- Visual inspection performed and findings:
- Technical checks performed and results:
- Unchecked requirements / known limitations:
- Conversion or integration still needed, with owner:

## Consolidated review

- Reviewed delivery:
- Reviewer:
- Required changes:
- Optional preferences:
- Decision and reason:

## Integration and acceptance (implementation agent)

- Accepted delivery:
- Integrated paths / patch / commit:
- Conversion details:
- In-game test command or scenario:
- Results and screenshot/log evidence:
- Remaining work:

## Change history

- 2026-10-13 — implementation agent (Claude) — created at revision 1 as a draft; it waits on ASSET-001.
- 2026-10-13 — implementation agent (Claude) — revision 2, answering Codex: revision 1's grid had 18 cells for 12 types
  and asked for two front-edge strips by mistake. Now 12 cells with no gaps, and one strip per side (the code draws
  one). Still a draft until `STYLE.md` exists.

- 2026-10-13 — implementation agent (Claude) — revision 3: STYLE.md written from ASSET-001 v003; ready for Codex.
