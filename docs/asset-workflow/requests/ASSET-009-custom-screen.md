# ASSET-009 — The Custom screen

## Coordination

- State: ready
- Priority: 9
- Assigned producer: Codex
- Current owner: Codex
- Brief revision: 1
- Based on repository commit: 4192432
- Last update (UTC date): 2026-10-14
- Next action / blocker: Codex delivers the sample: the window body (C1) with the art frame (C2) placed in it. Then
  the rest. Start after the ASSET-007 H1 revision, so the frame family is settled.

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

- Brief revision used:
- Assumptions / unresolved constraints:
- Tool and generation/edit prompt:
- References actually supplied to the tool:

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

- 2026-10-14 — implementation agent (Claude) — created at revision 1, ready for Codex.
