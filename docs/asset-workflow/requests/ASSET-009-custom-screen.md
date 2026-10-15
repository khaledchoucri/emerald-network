# ASSET-009 — The Custom screen

## Coordination

- State: accepted
- Priority: 9
- Assigned producer: Codex
- Current owner: —
- Brief revision: 1
- Based on repository commit: cd6822b
- Last update (UTC date): 2026-10-15
- Next action / blocker: Closed: C1–C7 in the game since POC-28.

## Purpose and visual brief

- **Intended use.** The chip-select window that opens at the start of every turn: the player picks chips from their
  hand here. It's the screen players look at most after the battlefield itself, and today it's drawn in code
  (`DrawCustomScreen` and the functions it calls in `src/pkbn/grid_draw.c:1384-1780`).
- **Layout, which stays as it is:**
  - the window covers the left half of the screen;
  - the battlefield stays visible, dimmed, on the right;
  - inside the window, from the top: the title row, the chip art box, the chip's name and info, two rows of chip
    slots, and the key hints at the bottom;
  - the chosen chips appear as tabs just right of the window's edge, stacking downwards, with the Program Advance
    preview under them when three chips combine.
- **The game draws** all text and numbers; the chip pictures, type symbols and code letters; the faint moving grid
  inside the art box; and the dimming. The frames hold them.
- **Deliverable type:** UI production source.
- **Style:** `STYLE.md` and the ASSET-007 HUD family (its revision 2), so the HUD and this screen read as one UI:
  - 1 px dark outline;
  - frames lit on the top and left;
  - stepped inset corners.
  The window is the Net's blue, deeper than the sky so the chips stand out.
- **Elements to avoid:**
  - text;
  - copying Battle Network's Custom screen;
  - Poké Balls (the ball slot's picture is drawn by the game).

### The parts

| Part | Used for (code) | What it is |
|---|---|---|
| C1 Window | The window body (`DrawCustomScreen`, `grid_draw.c:1730`) | The whole left panel, 264×352, with a bright rim down its right edge. A title band at the top (room for "CUSTOM" and the folder count) and a footer band at the bottom (room for the key hints) |
| C2 Art frame | The chip art box (`DrawArtBackground`, `:1406`) | A bezel around a 244×112 window. The window itself stays empty: the game fills it with the chip's picture over its type colour |
| C3 Slot | Each chip slot, and the Switch and ball slots (`DrawSlotFrame`, `:1384`) | A small upright card frame in the 5 greys, so the game colours it by the chip (type, Mega, Giga) and dims it when the chip can't be picked. It stretches sideways for the wider ball slot |
| C4 Cursor | The cursor (`DrawCursorFrame`, `:1394`) | Four corner brackets placed around the selected slot, 12×12 each. 2 frames for the blink, in gold |
| C5 OK | The OK slot (`:1647`) | A gold slot, the same shape as C3, with room for "OK" |
| C6 Chosen tab | Each chosen chip, right of the window (`DrawChosenColumn`, `:1656`) | A tab with a flat left end (it slides out from the window's edge) and a stepped right end, in the 5 greys so the game colours it by type |
| C7 PA preview | The Program Advance preview under the tabs (`:1687`) | The C6 tab, taller, in the ASSET-008 magenta family. 2 frames, the rim's light swapping, for its flash |

## Technical target

- **Integration:** the hi-bit renderer (POC-24) draws these in place of the code-drawn boxes.
- **Sizes at 2×** (from the code's 1× constants: `CUS_W` 132, `ART_*` at `:1217-1224`, `SLOT_W`/`SLOT_H` 24/28):

  | Part | Size to deliver | In game |
  |---|---|---|
  | C1 | 264×352. Title band about y 0–28, footer band about y 324–352 | fixed |
  | C2 | Outer bezel 252×120, with the 244×112 window at (4,4) | fixed, top-left at (6,26) in the window |
  | C3 | 44×56 | 44×56; the ball slot 92×56; 9-slice, corners 8×8 |
  | C4 | 4 corners, 12×12 each, × 2 frames | placed around a slot, 4 px outside it |
  | C5 | 44×56 × 2 frames (its label blinks; a slight brightness swap) | fixed |
  | C6 | 152×28 sample | 152×28; 9-slice, corners 8×8 |
  | C7 | 168×52 × 2 frames | 168×52; 9-slice, corners 10×10 |

- **Text room:** the game's font is 16 px tall at 2× (12 px small). Keep the title band, the footer band and the
  insides of C5, C6 and C7 plain.
- **Colours:**
  - C3, C6 and C4's blink use the 5 greys of ASSET-006 where the game colours them (C3, C6). C4 is drawn in its own gold.
  - C1 and C2 use at most 16 colours together.
  - C7 matches ASSET-008's palette.
- **Alpha:** see "Source-art rules" in `PIPELINE.md`. C1 is fully opaque.
- **Animation:** C4: 2 frames, 8 game frames each, loops. C5: 2 frames, 16 each. C7: 2 frames, 4 each.
- **Conversion:** the implementation agent cuts the slices and wires the parts in.

## References

| Path | Role |
|---|---|
| `docs/asset-workflow/STYLE.md` | Rules and palette |
| `docs/asset-workflow/requests/ASSET-007-battle-hud.md` | The HUD frame family to match (after its revision 2) |
| `poc/assets/generated/ASSET-008/v001/card_front.png` | The approved card: the corner and rim style for C3 and C7 |
| `poc/screens/POC-22.png` | Today's Custom screen in play (it contains game sprites: layout only) |

## Acceptance criteria

- **Source art:**
  - at native size the hand of five slots, the cursor, and the art box read at a glance;
  - the slots, recoloured with three different ASSET-006 ramps, stay distinct from one another and from the window;
  - every 9-slice part stretches to its in-game sizes without seams.
- **In game** (implementation agent): screenshots of the Custom screen with a full hand, with three chips chosen and
  a Program Advance previewed, and with Must Recharge showing.

## Producer record

- Brief revision used: 1. Revised ASSET-007 H1 v002 style dependency satisfied before generation.
- Tool: image_gen.imagegen; exact prompt, reference, source provenance and cleanup details in `poc/assets/generated/ASSET-009/v001/PROMPT.md`.
- Reference supplied: revised `ASSET-007/v002/h1_colorways_review_4x.png`, inspected before generation. No restricted game art supplied.
- Sample v001: `poc/assets/generated/ASSET-009/v001/window_body.png` (C1, 264×352, fully opaque), `art_frame.png` (C2, 252×120, 244×112 transparent window at 4,4); `custom_sample.png` places C2 at 6,26. Each has `_review_4x.png` and `_half.png` companions.
- Processing: PIPELINE.md item 7 permits scripted cleanup. Raw 1086×1448 generation retained under `raw/custom_generated.png`. Exact C1 geometry is reflowed from H1 v002 corners/edges; flat deep-blue fill, plain title/footer fields, bright right inner rim. C2 frame geometry normalized to the exact aperture. `cleanup.py`, `processing.json`, `validation.json` record reproducible operations/results. C1 and C2 use 7 opaque colors combined; alpha is binary.
- Technical adaptation for review: C2's required 4 px bezel cannot fit H1's 1+3+1 px frame thickness. C2 uses 1 outer + 2 lit + 1 inner px, with square steps on its outer corners and the ENTIRE rectangular art window transparent. C1 uses H1's full weight and stepped inset corners.
- Validation: full PNG decode; exact part sizes; C1 fully opaque; C2 complete 244×112 aperture clear; ≤16 shared colors; binary alpha; C2 composite position. Native/4× visual inspection: clean plain interiors, no text/icons/logos. Rendering/text fit/game screenshots untested. C3–C7 not generated pending sample review.

### Delivery v002 — C1 edge correction and C3–C7

- Brief revision 1 plus consolidated C1/C2 review; original v001 preserved. Files under `poc/assets/generated/ASSET-009/v002/`.
- C1 `window_body.png`: 264×352 opaque. Right and bottom straight runs now outline / three #536787 / outline, checked numerically. Optional #0d2347 body fill adopted to separate the window from the Net sky. C2 `art_frame.png` is byte-identical to approved v001. `custom_sample.png` composites C2 at (6,26).
- C3 `slot.png`: 44×56 in the exact five greys, 8×8 slice corners. C5 `ok.png`: two 44×56 cells, 8 px gap, gold index recolors of the identical C3 geometry; holds 16/16, loop.
- C4 `cursor.png`: eight 12×12 cells in one row with 8 px gaps, ordered TL1/TR1/BL1/BR1/TL2/TR2/BL2/BR2; each orientation blinks with holds 8/8, loop. Separate `cursor_tl.png`, `cursor_tr.png`, `cursor_bl.png`, `cursor_br.png` contain two states each for convenient import. Gold palette, transparent L-shaped brackets.
- C6 `chosen_tab.png`: 152×28 in the exact five greys; flat left end, stepped right end, 8×8 slices. C7 `pa_preview.png`: two 168×52 cells, 8 px gap, approved ASSET-008 magenta palette, 10×10 slices, identical geometry and flat fill; holds 4/4, loop. Light moves only on the rim.
- Source: original image_gen output `raw/custom_parts_generated.png` (2172×724). References inspected/supplied: v001 Custom sample and approved ASSET-008 front/back review. Full prompt in `PROMPT.md`. `cleanup.py` + `processing.json` reproduce crop, nearest-neighbor resize, palette quantization, alpha threshold, preservation of generated corner silhouettes, uniform edge reflow, flat-fill cleanup, exact recolors and sheet packing. Raw geometry was approximate, not a claimed exact integer multiple. Delivery is native scale, plus exact 4× and half-size previews.
- Review views: `parts_review.png`, `layout_review.png` (illustrative arrangement only), `stretch_checks.png`, `slot_type_checks.png` (Fire/Water/Grass and widened 92×56 ball slot). All have `_review_4x.png` and `_half.png` versions.
- Checks in `validation.json`: decoded PNGs, exact cells/sheets, binary alpha, C1 fully opaque, C2 transparent window preserved, C1 edge fix, C2 byte identity, ≤16 shared C1/C2 colors, exact C3/C6 grey membership, uniform 9-slice edges/fills, unchanged blink alpha masks, transparent 8 px gaps. Visual inspection at native/4×: clean blank fills, distinguishable tinted slots and selection brackets, no text/icons/logos. Manifest specifies holds/order/slices; actual game playback, font fit, slice wiring and required game screenshots remain implementation work.

## Consolidated review

- Reviewed delivery: v001 (`window_body.png`, `art_frame.png`, `custom_sample.png`)
- Reviewer: Claude (implementation agent), asked by Khaled to review
- What works: C1 has H1's full frame weight and stepped corners; the title and footer bands are where the text goes;
  C2's 244×112 window is fully clear. The 1+2+1 px bezel for C2 is accepted.
- Required change: **C1's right edge has a highlight on its outer side** (`#9db0ca` at x 262) while the bottom edge,
  lit the same way, doesn't. With the light from the top left, the right and bottom edges should match: outline,
  three `#536787`, outline. The "bright rim down its right edge" in the brief is drawn by the game where the window
  meets the battlefield, so the art doesn't need it.
- Optional: the body fill (`#071833`) is a sky colour; a step bluer (H1's `#0d2347`) would help the window read as
  a panel over the backdrop.
- Decision: approved with the C1 edge fix, delivered with C3–C7.

### Review of v002 and integration

- Reviewed delivery: v002 (C1 corrected, C3–C7, layout and stretch checks)
- Reviewer: Claude (implementation agent), asked by Khaled to review
- Decision: **approved, request accepted.** The C1 edge is fixed, and the bluer fill separates the window from the
  sky.
- In the game (POC-28):
  - C1 window, C2 art frame.
  - C3 slots in each chip's colour, dimmed when it can't be picked; the ball slot is 9-sliced wide.
  - C4 bracket cursor with its blink; C5 OK with its pulse.
  - C6 chosen tabs in the chip's type colour; C7 Program Advance preview.

## Integration and acceptance (implementation agent)

- Accepted delivery:
- Integrated paths / patch / commit:
- Conversion details:
- In-game test command or scenario:
- Results and screenshot/log evidence:
- Remaining work:

## Change history

- 2026-10-14 — implementation agent (Claude) — created at revision 1, ready for Codex.

- 2026-10-14 — Codex — delivered C1/C2 sample v001 in revised H1 family; exact geometry/alpha/palette checks passed; dimensional bezel adaptation recorded; sample review pending.
- 2026-10-14 — implementation agent (Claude) — reviewed C1/C2 v001: approved with a C1 right-edge fix; C3–C7 released.

- 2026-10-15 — Codex — delivered v002 corrected C1, preserved approved C2, and C3–C7 with palette/alpha/slice/geometry checks; implementation review pending.
- 2026-10-15 — implementation agent (Claude) — reviewed v002: approved; C1–C7 integrated in POC-28; accepted.
