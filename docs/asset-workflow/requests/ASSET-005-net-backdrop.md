# ASSET-005 — The Net backdrop

## Coordination

- State: accepted
- Priority: 5
- Assigned producer: Codex
- Current owner: —
- Brief revision: 2
- Based on repository commit: cd6822b
- Last update (UTC date): 2026-10-15
- Next action / blocker: Closed: A, B and C in the game since POC-28.

## Purpose and visual brief

- **Intended use.** The space behind every battle, today a flat colour. Players see it above the grid for the whole
  fight, so it sets the mood more than any other single image.
- **Deliverable type:** production source, as a background plus two small animated sprite sheets.
- **Subject:** the Net sky from ASSET-001 v003, the approved style reference. It has:
  - a deep navy space;
  - a perspective grid floor running to a horizon behind the panels;
  - faint vertical data streams;
  - floating light motes.
- **Camera:** the same as the battle, so the horizon sits behind the back row of panels.
- **Style:** `STYLE.md`, "Net sky" row of the palette. Flat bands, no smooth gradients, hard pixels. The grid lines are
  1 px at the hi-bit size.
- **Parts:**
  - **A. Backdrop**, 528×352, static. Sky, horizon glow band, grid floor. No motes, no streams (those move, so they're
    B and C).
  - **B. Motes**, a sheet of small square light particles in 3 sizes (2×2, 4×4, 6×6 px with a 1 px lighter core), each a
    4-frame twinkle. The engine scatters and drifts them.
  - **C. Data streams**, a sheet of 4 vertical dashed streaks, 4–8 px wide and 40–120 px tall, in the sky's blues.
    The engine scrolls them slowly upward behind the grid.
- **Elements to avoid:** text, logos, symbols that read as letters, characters, any light baked onto where the panels
  sit.
- **Variants:** 1. Deliver A first; B and C after A's review.
- **Accepted creative freedom:** the horizon's exact height and glow, the grid's spacing, and stream shapes.

## Technical target

- **Integration:** the hi-bit renderer (POC-24) draws A first, then C, then B, then the panels. The code that draws the
  battle today is `src/pkbn/grid_draw.c`.
- **Size:** A is exactly 528×352 (2× the 264×176 canvas). The panels cover y 164–333 and the HUD sits on top, so detail
  there is hidden. Put the interest in y 0–164: the layout guide is
  `docs/asset-workflow/references/hibit_battle_layout_528x352.png`.
- **Horizon:** at about y 150, just above the back row (y 164).
- **Alpha:** A is fully opaque. B and C are on transparent backgrounds, every pixel fully opaque or fully transparent.
- **Palette:** A uses at most 16 colours. B and C use the sky's blues and `#3ecbfd`/`#e0f9fd`.
- **Animation:** B: 4 frames per mote size, one row per size, 8 game frames each, loops. C: static sprites, one row.
- **Sheet layout:** see "Source-art rules" in `PIPELINE.md`.
- **Conversion:** the implementation agent quantizes and packs, and tunes drift and scroll speeds in code.

## References

| Path | Role |
|---|---|
| `poc/assets/generated/ASSET-001/v003/variant-a-stepped-corners.png` | Style: its sky, grid floor, streams and motes |
| `docs/asset-workflow/STYLE.md` | Palette and rules |
| `docs/asset-workflow/references/hibit_battle_layout_528x352.png` | Where the panels and HUD sit |

## Acceptance criteria

- **Source art:** A reads as depth (a floor going away), not as a flat pattern. With the approved panels laid over it,
  the panels stay the brightest, clearest thing on screen. No baked light.
- **In game** (implementation agent): a battle screenshot with the new backdrop, panels and HUD, and a short clip
  showing motes and streams moving.

## Producer record

- Brief revision used: 2 (latest delivery v003 B/C; approved A remains v002).
- Tool: image_gen.imagegen; exact prompt/reference list in the sample's PROMPT.md. Raw outputs retained under raw/ for reproducibility, not intended for runtime use.
- Programmatic processing: authorized by PIPELINE.md Source-art rules item 7. Exact config and operations are in processing.json / validation.json; shared helper: poc/assets/generated/_tools/prepare_samples.py. Run from repository root with the sample's processing.json. Python dependencies: Pillow and NumPy.
- Delivery scaling: native files plus exact 4× nearest-neighbor review PNGs and half-size previews. Raw generator dimensions were not native or exact integer multiples; cleanup reconstructs/packs the specified delivery geometry without claiming the raw art met that constraint.
- Visual review performed on native and 4× samples; no visible text, logos or existing characters. User review and implementation integration remain pending.
- References: approved ASSET-001 v003 only. Raw backdrop 1536×1024 RGB.

### Delivery v001 — initial sample

- Native asset: poc/assets/generated/ASSET-005/v001/backdrop.png, exactly 528×352, fully opaque, ≤16 colours in a dark sky-blue palette.
- Review: backdrop_review_4x.png (2112×1408) and backdrop_review_half.png.
- Processing: nearest-neighbor fit preserving 3:2 aspect, fixed palette snapping; flat sky bands replace source grain; grid is translated 8 pixels down, cropping the overflow at the bottom, to set the horizon at y150. No motes, streams, HUD, panels or fighters are baked into A.
- Checks: dimensions, palette limit, full opacity, nonempty content and preview scaling passed in validation.json. Visible scene reads as a receding grid floor behind a calm sky; no light baked onto future panels.
- Limitations: pixel raster line thickness varies at perspective stair steps; actual layered contrast with integrated panels/HUD and in-game screenshot remain for POC-24. B/C particles and streams not generated until A is reviewed.

### Delivery v002 — revision 2

- Native: `poc/assets/generated/ASSET-005/v002/backdrop.png`, 528×352, opaque, nine colours. Review: `backdrop_review_4x.png` and `backdrop_review_half.png`; `panel_contrast_preview_review_4x.png` overlays approved panels as a contrast aid.
- Clearly separated navy steps use #040c1c, #071833, #0b2550 and #103473. A 12 px stepped glow at y138–149 reaches #1a4f9c. Perspective floor begins at y150, with bright #1460b0 near-horizon lines and five visible dense rows before y164.
- Generated source was 1536×1024. Reproducible `v002/cleanup.py` resizes with nearest neighbour, replaces noisy sky with flat bands, translates generated floor geometry 16 px down and snaps grid colours. Exact prompt, source, processing and validation are retained; Pillow/NumPy required. This version uses its own cleanup script rather than the v001 shared helper.
- Dimension, opacity, palette, sky-step, glow and dense-floor checks pass. Visual review confirms panels remain brighter in the contrast preview. Preview uses cropped/resized source panels; it is not a renderer screenshot. Pixel staircase line width varies in perspective.
- User approval and in-game contrast/HUD integration remain pending. B/C are held. v001 is preserved as review history.

### Delivery v003 — B motes and C data streams, 2026-10-15

- Native B: `poc/assets/generated/ASSET-005/v003/motes.png`, 48×34 RGBA. Three rows for 2×2, 4×4 and 6×6
  squares, each containing four 6×6 cells; 8 px transparent gaps between cells and rows. Each square has one
  lighter core pixel. Frame order is medium / bright / medium / dim; each holds 8 game frames and loops.
- Native C: `poc/assets/generated/ASSET-005/v003/data_streams.png`, 56×120 RGBA. Four 8×120 cells, 8 px clear
  gaps, left-to-right occupied bounds 4×40, 6×64, 8×92 and 4×120. Static dashed streaks; runtime scroll remains
  the implementation agent's responsibility. Body/edge colors are #0b2550 and #103473.
- Both sheets have binary alpha, no opaque pixels in gutters, and zero RGB beneath alpha 0. Motes use four
  quiet blues, with maximum core #2467b0: one step above the review's #1a4f9c reference. No bright cyan/white
  from the original brief palette is used, following the newer v002 review's contrast requirement.
- Raw source: `v003/raw/particles.png`, 1536×1024 RGBA. It contained soft halos and approximate geometry, so
  it did not satisfy the native contract. Authorized scripted processing reconstructs exact square motes, extracts
  strong dash-row geometry from four source crops, removes halo/weak runs, snaps native dimensions and packs.
  Exact generation prompt/references and cleanup assumptions are in `v003/PROMPT.md`; reproduce with
  `python poc/assets/generated/ASSET-005/v003/cleanup.py` using `processing.json` (Pillow/NumPy required).
- Review files: `motes_review_4x.png`, `data_streams_review_4x.png` and matching `_review_half.png` files;
  `layered_preview.png` plus 4×/half previews; `layered_playback.gif` demonstrates a complete twinkle loop and
  upward stream drift over approved A v002. Fixed preview positions/speeds are illustrative, not engine settings.
  GIF hold rounding is 130/140 ms; source timing remains exactly 8/60 seconds per mote phase.
- `v003/validation.json` records successful dimensions, binary alpha, occupied bounds, clear gutters, exact
  square areas, single core pixels, brightness cap, at least three dashes per stream, GIF frame/delay/loop decoding,
  and unchanged approved-A checksum. Native and enlarged views were inspected; the scene stays quiet and dim.
- A v002 was not regenerated or modified. B/C are delivered for review, not runtime acceptance. Half-size
  nearest-neighbor views can lose one-pixel cores; final readability, scatter density, panel/HUD contrast,
  scrolling and in-game screenshot/clip evidence remain with the implementation agent.

## Consolidated review

- Reviewed delivery: v001 (`backdrop.png`), composited with the approved ASSET-003 panels at their game positions
- Reviewer: Claude (implementation agent), asked by Khaled to review
- What works: clean processing, exact size, opaque, flat colours, grid horizon at y 150 as asked.
- Required changes (brief revision 2):
  1. **The sky must be visible.** Its two bands are `#061833` and `#071833`, one RGB step apart, so y 0–148 reads as one
     flat colour. My STYLE.md palette listed those two near-identical navies; that's fixed now (Net sky row). Use
     the new steps, darkest at the top: `#040c1c`, `#071833`, `#0b2550`, `#103473`.
  2. **A horizon glow you can see:** 6–12 px of flat bands just above the grid (`#103473` up to `#1a4f9c`), not a 2 px line.
  3. **Depth in the floor:** grid lines converging towards the horizon, brighter near it (`#1460b0`), denser with
     distance, so the 14 px between the horizon and the back row reads as a floor going away.
  4. Keep the panels the brightest thing: nothing above `#1a4f9c` except the grid's near-horizon lines.
- Optional: very faint distant shapes in the sky (a far grid wall, large dim squares) if they stay below the glow in
  brightness. Streams and motes stay in B and C.
- Decision: revise A; B and C after A v002 is reviewed.

### Review of v002

- Reviewed delivery: v002 (`backdrop.png`, `panel_contrast_preview_review_4x.png`)
- Reviewer: Claude (implementation agent), asked by Khaled to review
- Decision: **A approved.** The four sky steps read as bands, the glow sits right above the grid, the floor goes away
  into the horizon, and the panels stay the brightest thing on screen.
- Optional (no new version needed): the dense rows between y 150 and 164 get busy at 4×; at native size they read as
  distance, so leave them unless B/C make that strip crowded.
- Next: B and C as briefed. Keep both darker than the panels; the motes' brightest core no brighter than `#1a4f9c`
  plus one step.

### Review of v003 and integration

- Reviewed delivery: v003 (`motes.png`, `data_streams.png`, `layered_preview.png`)
- Reviewer: Claude (implementation agent), asked by Khaled to review
- Decision: **B and C approved, request accepted.** The motes stay below the glow as asked, and the streams read as
  data without pulling the eye from the panels.
- In the game (POC-28): `tools/pack_hibit.py` packs A, the 12 mote cells and 4 streams. `DrawHiBackdrop`
  (`src/pkbn/grid_draw.c`) draws A, scrolls the streams up the sky at 4 speeds and scatters 12 motes that twinkle
  and drift, all above the horizon. Weather lays a wash of its colour over the sky.

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

- 2026-10-14 — implementation agent (Claude) — reviewed v001 for Khaled; brief revision 2 (visible sky steps, horizon glow, floor depth); STYLE.md Net sky row corrected.

- 2026-10-14 — Codex — delivered revision 2 backdrop A with visible sky bands, 12 px horizon glow and dense floor depth; source checks passed, user and runtime review pending.
- 2026-10-14 — implementation agent (Claude) — reviewed v002: backdrop A approved; B and C released.
- 2026-10-15 — Codex — delivered B/C v003 with native transparent sheets, layered playback, reproducible cleanup
  and source validation; approved A v002 preserved. Review and implementation integration pending.
- 2026-10-15 — implementation agent (Claude) — reviewed v003: B and C approved; A, B and C integrated in POC-28; accepted.
