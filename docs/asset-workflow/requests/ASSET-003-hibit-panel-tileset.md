# ASSET-003 — Hi-bit battle panel tileset

## Coordination

- State: draft
- Priority: 3
- Assigned producer: Codex
- Current owner: implementation agent
- Brief revision: 1
- Based on repository commit: 362b782
- Last update (UTC date): 2026-10-13
- Next action / blocker: Wait for ASSET-001's review. The implementation agent then writes `STYLE.md` from the chosen
  variant, confirms the renderer target, and marks this request ready.

## Purpose and visual brief

- **Intended use:** the battle grid's panels in the hi-bit renderer. Today they are drawn by code at 44×26
  (`DrawPanel`, `src/pkbn/grid_draw.c:189`; `PANEL_W`/`PANEL_H`, `include/pkbn/grid_internal.h:35-36`).
- **Deliverable type:** production source, as a sprite sheet.
- **Subject:** one panel per cell, seen straight on and slightly from above, as in ASSET-001. Each panel has:
  - a frame in the side's colour (red for the player, blue for the foe);
  - an inner face that shows the panel type.
- **Panel types** (`include/pkbn/grid_internal.h:73-91`). For each, the face and what the player must read from it:

| Row | Type | Face and what the player must read |
|---|---|---|
| 0 | NORMAL | Silvery glossy metal |
| 0 | CRACKED | Metal with crack lines: it will break |
| 0 | BROKEN | A hole with a jagged rim; transparent centre |
| 1 | POISON | Purple with bubbles: it hurts |
| 1 | HOLY | Gold with a glinting cross: it protects |
| 1 | GRASS | Green with blades |
| 2 | ICE | Pale blue with a glint: it's slippery |
| 2 | LAVA | Glowing orange-red: it burns |
| 2 | ROAD UP / DOWN / LEFT / RIGHT | Metal with a conveyor chevron pointing that way |

- **Style:** follow `docs/asset-workflow/STYLE.md`. It will be written from ASSET-001's chosen variant before this goes
  to ready.
- **Elements to avoid:** text, logos, and copying Battle Network's panel art.
- **Variant count:** 1, after a reviewed sample. First deliver only NORMAL, CRACKED and BROKEN for both sides. Once those
  are reviewed, do the rest.

## Technical target (required for production assets)

- **Integration:** the hi-bit renderer (roadmap round 3; not yet in code). Until it exists, this sheet is checked by the
  implementation agent's preview tool, not in game.
- **Cell size:** 88×52 per panel (2× of 44×26), plus a separate front-edge strip of 88×12 per side (2× of `PANEL_LIP` 6)
  for the bottom row.
- **Anchor:** the top-left of each cell. The panel fills the cell edge to edge.
- **Sheet layout:** one sheet per side (`panels_red.png`, `panels_blue.png`):
  - 6 columns × 3 rows of 88×52 cells, following the row order above, left to right;
  - the two front-edge strips in a fourth row;
  - total 528×168.
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
