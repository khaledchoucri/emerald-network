# ASSET-009 v002: C1 correction and C3–C7

Tool: image_gen.imagegen. Brief revision 1 plus implementation review, based on 89c74ed. References inspected and supplied: ASSET-009/v001/custom_sample.png (frame family) and ASSET-008/v001/card_front_back_review_4x.png (magenta/card family). No restricted sprite references.

## New parts prompt

Create a production sprite source sheet of ORIGINAL pixel-art game Custom-screen UI pieces. Use the attached accepted blue-silver screen frame and magenta card ONLY as material/corner family references. Crisp hard-edged pixel art, flat colors, top-left light, near-black outer and inner outline, chunky 3-pixel raised rim, square STEPPED inset corners, plain empty interiors. Draw five separated parts across ONE horizontal row on transparent background, ample transparent gaps, no labels, characters, icons, glyphs, words, letters, numbers, logos, circles, chips, sheen in interiors, shadows outside the art, antialiasing or glow.
From left to right:
1) Upright small slot frame proportion44 wide56 tall: grayscale only, dark flat interior, thicker layered light gray top/left frame and darker bottom/right frame.
2) Four separate GOLD L-shaped selection corner brackets as a group, arranged in their natural corners around an otherwise EMPTY invisible upright rectangle. Each L exactly square stepped hard edges.
3) GOLD upright slot frame identical shape/proportions to first grayscale slot, plain very dark amber fill.
4) Long horizontal grayscale tab proportion152 wide28 tall. Flat vertical left end because it slides out from window edge, stepped inset RIGHT end corners. Raised flat gray frame, quiet dark plain interior, no ornamental mid-edge detail.
5) Long horizontal magenta Program Advance preview tab proportion168 wide52 tall, same flat left edge and stepped right corners. Strong raspberry/magenta rim, hot-pink top/left highlights, dark wine/navy plain empty interior.
Keep entire shapes isolated and uncropped. Source art will be normalized to exact dimensions and quantized using a script. No illustrative background or screen mockup.

## Reproducible normalization

Run `python poc/assets/generated/ASSET-009/v002/cleanup.py` from repository root (Pillow, NumPy). Raw output retained as raw/custom_parts_generated.png (2172×724). The raw generation does not meet an exact integer-multiple pixel grid; native delivery geometry is reconstructed by authorized cleanup, not represented as a direct integer-scale output. Crop boxes, palettes and operations are in processing.json.

New parts use generated corner silhouettes; source crops are nearest-neighbor resized, palette-quantized, alpha-thresholded at 128, and normalized to uniform middle edges/flat fills for slicing. Extra generated waist ornaments are removed. C3 uses 8×8 corner patches. C5 is an exact index recolor of C3, with a second rim-brightness frame. Cursor corners derive from the generated top-left L; mirrors and a palette-only blink create four orientations/two states. C6 has a flat left edge and stepped right end, with 8×8 slices. C7 preserves 10×10 corners, changes only rim colors for its flash, and uses colors from the approved ASSET-008 palette.

C1 corrects the straight right and bottom runs to outline / three #536787 / outline, with no right highlight. The optional bluer body fill #0d2347 is adopted. C2 is copied byte-for-byte from approved v001. No earlier delivery is changed.

manifest.json records files, cells, gap/order, slices, holds and loops. Cursor sheet has eight cells in one row: TL1, TR1, BL1, BR1, TL2, TR2, BL2, BR2. The four cursor_*.png sheets each contain one orientation with its two states. All sheet gaps are eight transparent pixels.

Native, 4× nearest-neighbor and half-size PNGs included. parts_review.png summarizes C3–C7. slot_type_checks.png shows Fire/Water/Grass recolors and the 92×56 ball width. stretch_checks.png exercises C3, C6 and C7 beyond their sample widths. layout_review.png is an illustrative arrangement with ten slots, selection brackets, chosen tabs and PA preview, not an engine screenshot or text-fit check.

Checks recorded in validation.json: exact dimensions, full decode, binary alpha, ≤16 combined C1/C2 colors, exact five-grey membership for C3/C6, clear C2 aperture, C1 straight-run edge colors, byte-identical C2, uniform 9-slice edges/fill, blink alpha identity, and transparent eight-pixel gutters. Actual engine rendering, font fit, runtime slicing and blink timing remain implementation checks.

