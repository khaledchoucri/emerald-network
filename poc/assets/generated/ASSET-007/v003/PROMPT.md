# H2–H5, ASSET-007 v003

Brief revision 2, after H1 v002 approval. Tool: image_gen.imagegen; transparent_background=true. Inspected and supplied `poc/assets/generated/ASSET-007/v002/h1_colorways_review_4x.png` as the frame-family reference.

## Exact prompt

Create original pixel art HUD component sheet matching approved reference blue-silver frame, dark navy outline #0b0a14, steel rim lit TOP LEFT, square stepped inset corners, flat untextured dark blue interiors. Only interface frames, no lettering numbers icons logos characters. Transparent background. Show four separated horizontal rows: 1) compact grayscale status pill 40:18 proportions, stepped pill ends no round antialiasing, five flat gray tones only #202020 #585858 #909090 #c8c8c8 #ffffff; 2) thin blue-silver HP trough 88:8 proportions and separate84:4 grayscale fill strip; 3) long custom gauge224:16 proportions, empty dark trough, separate220:8 grayfill strip, below it four rim highlight only overlays each224:16 with highlight moving clockwise top-left, top-right, bottom-right, bottom-left, transparent center; 4) queued-chip blank plate160:22 proportions, silverblue frame and slightly brighter flat navy fill than reference, large empty text room. Draw each component at4x native, strict flat hard pixels no gradients no shadows no translucency. All stretch edges straight uniform no ornaments. Crisp and simple small-scale production UI. Transparent gutters. No text at all.

## Source and normalization

`raw/hud_parts_generated.png` is the unchanged 1536×1024 generator output. Despite the prompt, its parts do not have exact target proportions or a uniform 4× grid; it includes soft background/fill variation and grouped overlays. It is a style source, never a runtime sheet.

`cleanup.py` explicitly interprets its stepped blank-frame design as native indexed masks following the approved H1 palettes. It reconstructs exact edges, uniform fills, text-safe borders, grayscale strips and four clockwise rim-light phases, removing the generated soft background entirely. This is authorized programmatic cleanup under PIPELINE.md rule 7; final files are normalized designs rather than a faithful crop of every generated pixel. Run with `python poc/assets/generated/ASSET-007/v003/cleanup.py` (Pillow, NumPy). `processing.json` records operations/palettes; `validation.json` records actual checks and adaptations.

## Thin-part adaptations requiring implementation review

- H3: a literal pair of 6×6 top/bottom corners cannot fit an 8px-high bar without overlap. Use 6px horizontal caps, split vertically into 4px upper/lower halves, and stretch horizontally. The frame uses outer 1px plus 1px rim, no separate inner outline, leaving the required 84×4 fill room at offset (2,2).
- H4: 224×16 frame uses 2px side borders and 4px top/bottom borders, leaving exactly 220×8 at offset (2,4). Side borders use outer 1px plus 1px rim; horizontal edges also have a dark inner line.
- H5: repeating H1's 1+3+1 border would leave 12px height for the required 16px font. This part uses 1px outer + 1px lit rim + 1px inner, yielding 16px of plain text room. Frame family, corner steps and light direction are retained.

These dimensional adaptations preserve the supplied sizes and are proposals for implementation review, not changes to game code or accepted integration constraints. H1 v002 is untouched.

## Outputs/checks

- `h2_tag.png` 40×18, only the allowed five-gray set (four tones used).
- `h3_trough.png` 88×8; `h3_fill.png` 84×4, grayscale.
- `h4_frame.png` 224×16; `h4_fill.png` 220×8, grayscale.
- `h4_full.png` 920×16, four 224×16 overlays with 8px transparent gaps. Center transparent; hard rim highlight moves clockwise. Native individual overlays retained. Intended game timing 4/4/4/4 frames, loop.
- `h5_line.png` 160×22, plain brighter navy `#14315b`.
- Native, exact nearest-neighbor 4×, half previews; minimum/maximum horizontal stretch checks H2 20/100px, H3 40/200px, H5 40/300px. Overlay composite preview plus GIF at approximately 67ms/frame for visual inspection only.

Assertions: exact component sizes from construction, binary alpha, ≤16 colors per component, gray-palette membership, uniform stretch middles, cap patches preserved at extremes, transparent overlay centers and sheet gaps, all PNGs decode. Native/half/4× and stretch PNGs inspected. The GIF is a standalone review file; its playback and actual game timing were not tested. No game-font rendering, battle integration, low-HP gauge behavior, renderer screenshots or in-game acceptance performed.
