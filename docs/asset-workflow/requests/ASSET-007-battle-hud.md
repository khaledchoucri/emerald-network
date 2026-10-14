# ASSET-007 — Battle HUD frames

## Coordination

- State: ready
- Priority: 7
- Assigned producer: Codex
- Current owner: Codex
- Brief revision: 2
- Based on repository commit: 1eb0e3d
- Last update (UTC date): 2026-10-14
- Next action / blocker: Codex delivers H1 v002 (revision 2 below); then H2–H5 in the same frame family.

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

- Brief revision used: 1.
- Tool: image_gen.imagegen; exact prompt/reference list in the sample's PROMPT.md. Raw outputs retained under raw/ for reproducibility, not intended for runtime use.
- Programmatic processing: authorized by PIPELINE.md Source-art rules item 7. Exact config and operations are in processing.json / validation.json; shared helper: poc/assets/generated/_tools/prepare_samples.py. Run from repository root with the sample's processing.json. Python dependencies: Pillow and NumPy.
- Delivery scaling: native files plus exact 4× nearest-neighbor review PNGs and half-size previews. Raw generator dimensions were not native or exact integer multiples; cleanup reconstructs/packs the specified delivery geometry without claiming the raw art met that constraint.
- Visual review performed on native and 4× samples; no visible text, logos or existing characters. User review and implementation integration remain pending.
- References: approved red panel source for frame family. Generate one base then script-recolour to guarantee shared geometry; raw HUD 2106×747 RGBA.

### Delivery v001 — initial sample

- Native parts: poc/assets/generated/ASSET-007/v001/player.png, foe.png, synchro1.png, synchro2.png; each96×34. Order in h1_colorways.png: player, foe, Synchro1, Synchro2 (8px gaps).
- Full Synchro sheet: synchro.png (200×34, two96×34 cells and8px gap); intended holds8/8 game frames, loop. Fill stays constant; rim tones pulse. Timing playback remains untested.
- Cleanup: alpha threshold128; explicit main plate crop; 128×128 source corners mapped to8×8 native corners, edges reflowed using uniform middle samples and flat dark fill. Direct six-colour palette snapping preserves outline, shade and silver highlights; all colourways derive from the same index image, with pixel-identical alpha and material geometry. No mid-edge ornaments or fill gradients.
- Tests: exact size, binary alpha, ≤16 colours per part, identical variant geometry and uniform nine-slice edges/fill passed. h1_stretch_preview.png exercises44×24,200×34 player and60×34 foe plates; all four8×8 corner patches preserved exactly. Dark flat text area is available; no actual font rendering test performed.
- Review: h1_colorways_review_4x.png, h1_stretch_preview_review_4x.png, synchro_review_4x.png and half-size colourway preview.
- Limitations: source corner/edge details were normalized by nine-slice reflow. Engine slicing/font fit, low-HP/FullSynchro state screenshots and pulse playback remain for implementation. H2/H3/H4/H5 not generated until this sample is reviewed.

## Consolidated review

- Reviewed delivery: v001 (`h1_colorways.png`, `h1_stretch_preview.png`, `synchro.png`), placed over the ASSET-005 backdrop
- Reviewer: Claude (implementation agent), asked by Khaled to review
- What works: the 9-slice stretching is clean at every in-game size; the three colourways share one shape; the
  Full Synchro pulse changes only the rim.
- Required changes (brief revision 2):
  1. **Separate the player fill from the sky.** The player plate's fill is the backdrop's navy, so the plate vanishes
     where it sits. Use a fill clearly lighter or bluer than the sky (for example `#0d2347`), and add a 1 px dark
     outline (`#0b0a14`) outside the rim on every colourway.
  2. **Match the panel frame family.** The rim is 1–2 px, much lighter than the panels' frame. Follow STYLE.md's
     panel build at HUD scale: 1 px outline, a 3 px frame in the colourway's colour lit on the top and left, a 1 px
     inner outline, then the fill. Keep the stepped corners inside the 8×8 corner slices.
- Decision: revise H1; H2–H5 follow in the revised style.

## Integration and acceptance (implementation agent)

- Accepted delivery:
- Integrated paths / patch / commit:
- Conversion details:
- In-game test command or scenario:
- Results and screenshot/log evidence:
- Remaining work:

## Change history

- 2026-10-14 — implementation agent (Claude) — created at revision 1, ready for Codex.

- 2026-10-14 — Codex — generated initial sample in parallel with ASSET-005..008; performed authorized scripted cleanup/packing and file checks; published for review, acceptance pending.

- 2026-10-14 — implementation agent (Claude) — reviewed v001 for Khaled; brief revision 2 (fill contrast against the sky, panel-weight frame).
