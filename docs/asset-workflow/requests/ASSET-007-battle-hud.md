# ASSET-007 — Battle HUD frames

## Coordination

- State: ready
- Priority: 7
- Assigned producer: Codex
- Current owner: Codex
- Brief revision: 1
- Based on repository commit: 1eb0e3d
- Last update (UTC date): 2026-10-14
- Next action / blocker: Codex delivers the sample: the plate (H1) in its three colourways. After review, the rest.

## Purpose and visual brief

- **Intended use.** The frames around the battle's information, which today are flat code-drawn boxes
  (`Draw_Box`, `DrawPlayerHud`, `DrawEnemyHud`, `DrawGauge` and `DrawBottomHud` in `src/pkbn/grid_draw.c`):
  - the player's HP box;
  - the foe's name and HP plate;
  - the status tags;
  - the HP bars;
  - the Custom gauge;
  - the queued-chip line at the bottom.
- **The game draws all the text and numbers itself**, and the frames hold it. So the frames are plain inside, with no
  lettering, and most of them must stretch to fit text of any length.
- **Deliverable type:** UI production source.
- **Style:** `STYLE.md`, the same family as the panels:
  - a 1 px dark outline;
  - a frame in flat tones, lit top and left;
  - stepped inset corners, like the panel faces.
  The HUD sits over the Net backdrop (ASSET-005) and the panels, so the fills are dark and calm, and the panels stay
  the brightest thing on screen.
- **Elements to avoid:**
  - any text, numbers or icons inside the frames;
  - copying Battle Network's HUD;
  - Poké Balls (the game draws the party markers itself).

### The parts

| Part | Used for (code) | What it is |
|---|---|---|
| H1 Plate | Player HP box (`grid_draw.c:1034`), foe plate (`:1083`), Beast Out counter (`:1065`) | A box with a dark fill. Three colourways: **player** (navy fill, blue-silver rim), **foe** (dark wine fill, rose rim), **Full Synchro** (dark amber fill, gold rim; 2 frames, the rim's light shifting, for a pulse) |
| H2 Tag | Status tags such as PSN or SLP, and the foe's program count (`:1046`, `:1089`, `:1100`) | A small pill, drawn in the 5 greys of ASSET-006 so the game can colour it per status |
| H3 Bar | HP bars (`:113`) | A thin trough with a dark inside, plus a separate fill strip in the 5 greys (the game colours it green, yellow or red) |
| H4 Gauge | The Custom gauge (`:1136`) | The gauge's frame at its fixed size; a fill strip in the 5 greys; and a 4-frame "full" overlay, a light running along the rim, played when the gauge is full |
| H5 Line | The queued chip at the bottom (`:1195`) | A low box like H1, slightly brighter, for the next chip's name |

## Technical target

- **Integration:** the hi-bit renderer (POC-24) replaces `Draw_Box` and the bar code with these frames.
- **Stretching (9-slice).** H1, H2, H3 and H5 are drawn at a sample size. The game keeps the corners and stretches the
  edges and the middle:
  - Corners are **8×8 px** (H2 and H3: 6×6).
  - Between the corners, every edge and the fill must be the same all along, with no ornament mid-edge, so stretching
    doesn't distort anything.
  - The stepped corner and any highlight live inside the corner squares.
- **Sizes at 2×** (from the code's 1× boxes):

  | Part | Sample size to deliver | In game |
  |---|---|---|
  | H1 | 96×34 | 96×34 player; foe 60–200 wide × 34; Beast counter 44×24 |
  | H2 | 40×18 | 20–100 wide × 18 |
  | H3 | 88×8 trough, 84×4 fill strip | 40–200 wide |
  | H4 | 224×16 frame, 220×8 fill, overlay 224×16 × 4 frames | fixed |
  | H5 | 160×22 | 40–300 wide × 22 |

- **Text room:** the game's font is 16 px tall at 2× (12 px for the small font). Leave the inside of H1 and H5
  free of detail.
- **Alpha:** see "Source-art rules" in `PIPELINE.md`. H1 and H5 fills may be fully opaque. Translucency isn't
  available, so the game dims the fill itself if it needs to.
- **Palette:** at most 16 colours per part. H2, the H3 fill and the H4 fill use only the 5 greys from ASSET-006.
- **Animation:** H1 Full Synchro, 2 frames, 8 game frames each, loops. H4 overlay, 4 frames, 4 game frames each,
  loops.
- **Conversion:** the implementation agent cuts the slices and wires them in.

## References

| Path | Role |
|---|---|
| `docs/asset-workflow/STYLE.md` | Rules and palette |
| `poc/assets/generated/ASSET-003/v002/` | Approved panels: the frame family to match |
| `docs/asset-workflow/references/hibit_battle_layout_528x352.png` | Where each part sits |
| `poc/screens/POC-23.png` | Today's HUD in play (it contains game sprites: use it for layout only) |

## Acceptance criteria

- **Source art:** the frames stretch cleanly. The implementation agent's preview shows each 9-slice part at its
  narrowest and widest in-game size with no visible seams. Text is readable over every fill.
- **In game** (implementation agent): a battle screenshot with the HUD, at normal HP, with low HP, at Full Synchro and
  with the gauge full.

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
