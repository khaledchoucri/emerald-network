# ASSET-008 P5 revision2 / delivery v003

Tool: image_gen.imagegen. transparent_background=true. Reference inspected first: `../v002/type_symbols_review_4x.png`, original project artwork, used for weight and grayscale material. Raw returned canvas1774×887, not requested integer multiple; native delivery dimensions are established by documented cleanup.

## Exact prompt

Create TWO ORIGINAL tiny pixel-art game type symbols on transparent background, separated by a broad transparent gap in ONE HORIZONTAL ROW. Match the weight and grayscale style of the reference row; do NOT draw the other symbols. First icon FIGHTING: ONE clear clenched human fist seen from front with four prominent knuckles, thumb curled across fingers, short wrist pointing down, solid strong silhouette. Must read as fist and never crossed bones or danger symbol. Second GROUND: a low broad mound of solid earth, with a jagged dark fissure splitting down its sloped top and front face; earthy slab with irregular raised mound silhouette. Must read cracked ground, never stacked bands, sandwich or boulder. Both fit square32x32 cells at8x256x256 each; keep 16px native-equivalent row gap, substantial alpha padding around each icon; same visual weight, 1px native dark outline and top-left highlights. Only 5 flat greys #202020 #585858 #909090 #c8c8c8 #ffffff plus transparent. Hard pixel steps no antialias blur or gradient. No text, labels or logo, no copying any existing game's symbols.

## Reproduction

Run `python poc/assets/generated/ASSET-008/v003/prepare.py` from repository root with Pillow and NumPy. Config: processing.json. Raw unchanged output: raw/symbols.png. Explicit crops isolate fist/mound, alpha threshold128 removes semitransparency, detached components smaller than64 source pixels removed, trim transparent edges, aspect-preserving nearest-neighbour fit within28×28 and centre in32×32. Nearest fixed five-grey palette without dithering. Replace exactly cells1 and4 in a copy of v002's RGBA sheet; do not recolour or repack the other15 cells or8px gaps. Individual replacement PNGs also provided. Native sheet672×32,4× review2688×128, half-size336×16.

The unchanged-cell checks compare all four RGBA channels, including transparent pixel data. validation.json records source hash, output hash, exact palette, gaps, binary alpha and per-cell equality. Source delivery remains subject to reviewer/in-game acceptance; no gameplay or runtime files changed.
