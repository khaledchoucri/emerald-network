# Backdrop B/C source

Tool: image_gen.imagegen. References: ASSET-005/v002/backdrop.png and ASSET-001/v003/variant-a-stepped-corners.png, inspected before generation. transparent_background=true. Original source: raw/particles.png.

## Exact prompt

Create ONLY original tiny Net background particles as a transparent sprite source sheet, matching the digital blue sky of reference1 and quiet data accents of reference2. NO backdrop, panels, characters, text, logos or frames. Transparent background. Flat hard pixel art, discrete blue shades, no gradients, no blur or anti-aliasing. Sheet has TWO separated groups: TOP group three rows of four square mote twinkle frames, each frame same square shape, brightness dim-medium-bright-medium, rows intended native2x2,4x4,6x6 pixels; every square has a single brighter core pixel and dimmer blue body. Make sources at 16x native for visibility, ample empty spacing. BOTTOM group four isolated narrow vertical dashed data streaks in one row, native widths4,6,8,6 pixels and heights40,64,96,120. Discrete rectangular dashes with uneven gaps, dim navy blue bodies and occasional single brighter blue segment, no star shapes or connected letters. Use source scale 4x or8x for streams, no smooth shaded strips. Whole sprites comfortably isolated with transparent gutters and no stray pixels. Colors #103473 #144283 #1a4f9c with brightest mote core #2467b0 only; reference2 cyanwhite accents must be made much darker here, keep game panels brightest. Maximum5opaque blue colors. No near-white or cyan. Source sheet for small subtle background elements, straightforward geometry.

## Actual source and cleanup

The generator returned 1536×1024 RGBA with broad soft blue halos, non-square mote shapes, and approximate spacing;
it did not meet the native pixel or binary-alpha contract. The raw file is retained for provenance, not runtime use.
User-authorized PIPELINE.md rule 7 permits deterministic cleanup. `cleanup.py` and `processing.json` record it.

Run from repository root: `python poc/assets/generated/ASSET-005/v003/cleanup.py` (Python, Pillow, NumPy).
Native motes are reconstructed as exact 2×2/4×4/6×6 squares with one lighter core pixel. Their 6×6 atlas cells use
four columns and three rows with 8 px clear gutters: 48×34 total. Four 8-game-tick phases loop; all phases remain
fully opaque within each square and twinkle by color, without changing geometry.

Data-stream dash timing/spacing comes from four explicitly inspected source crops. Alpha≥128 and a local-blue
contrast threshold remove halos; source occupied-row runs shorter than 8 pixels are removed. The remaining dash
rows are trimmed and resampled with nearest neighbor to 40/64/92/120 px heights and snapped to 4/6/8/4 px widths.
Those sizes follow the brief's allowed ranges, rather than claiming the source prompt's approximate sizes were exact.
The 56×120 stream atlas uses four 8×120 cells with 8 px gutters. Stream body/edge colors are #0b2550/#103473.
Mote cores peak at #2467b0, the single brighter step above the review's #1a4f9c cap; no cyan or white survives.

Native, 4× nearest-neighbor, and half-size previews are included. `layered_preview.png` and the 16-frame looping
`layered_playback.gif` demonstrate fixed scatter, 2 px per preview step stream drift, and the mote twinkle over the
approved v002 backdrop, which remains byte-for-byte unchanged. GIF delays alternate 130/140 ms around the exact
8/60-second hold; runtime timing metadata is exact. These views are preparation previews, not in-game evidence.
Final renderer scatter, density, scroll speeds, panel/HUD contrast and acceptance belong to the implementation agent.
