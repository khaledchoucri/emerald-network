# ASSET-005 — The Net backdrop

## Coordination

- State: delivered
- Priority: 5
- Assigned producer: Codex
- Current owner: Khaled / implementation agent
- Brief revision: 1
- Based on repository commit: 1eb0e3d
- Last update (UTC date): 2026-10-14
- Next action / blocker: Review backdrop A on GitHub; B/C remain gated on sample review. Integration/layering checks follow in POC-24.

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

- Brief revision used: 1.
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

- 2026-10-14 — Codex — generated initial sample in parallel with ASSET-005..008; performed authorized scripted cleanup/packing and file checks; published for review, acceptance pending.
