# Sample preparation

Run from the repository root with Python 3, Pillow, and NumPy:

```sh
python poc/assets/generated/_tools/prepare_samples.py poc/assets/generated/ASSET-005/v001/processing.json
python poc/assets/generated/_tools/prepare_samples.py poc/assets/generated/ASSET-006/v001/processing.json
python poc/assets/generated/_tools/prepare_samples.py poc/assets/generated/ASSET-006/v001/ramps_processing.json
python poc/assets/generated/_tools/prepare_samples.py poc/assets/generated/ASSET-007/v001/processing.json
python poc/assets/generated/_tools/prepare_samples.py poc/assets/generated/ASSET-008/v001/processing.json
```

The first, second, fourth, and fifth commands are independent. Run the ramp command after HIT preparation.
Raw generation files remain unchanged. Each processing config records explicit inspected crop boxes and palette
choices. Validation records include exact operations, SHA-256s, dimensions, alpha, palettes, and applicable geometry
checks. These are source-art checks, not renderer acceptance or in-game validation.

ASSET-005 snaps to seven selected flat navy/grid colors at opaque 528×352. It translates the grid down 8 native
pixels from y142 to y150, cropping 8 overflow pixels at the bottom, and flattens the sky into three navy bands
without texture noise. The grid is translated without stretching. ASSET-006 preserves relative HIT phase
sizes using one common scale, centers all cells, uses six 64×64 cells separated by 8 px, and remaps five source tone
bands to the specified grays. Small disconnected source components below 48 pixels are removed before fitting;
the larger intentional square sparks remain. Timing is recorded but playback has not been tested.

ASSET-007 reconstructs the generated wide plate with nine slices: 128×128 source corner patches become 8×8 native
corners, central edge samples repeat, and the center becomes a flat fill. Colorways all share one material-index map
and alpha mask. Full Synchro frame 2 changes only rim highlight/shade entries; dark fill and outline remain fixed.
`synchro.png` packs the two 96×34 animation frames with an 8 px gap. `h1_stretch_preview.png` shows player plates
at 44×24 and 200×34 and a foe plate at 60×34; checks compare all four corner patches exactly and verify uniform
edges and fills after stretching. This is a deterministic preparation preview, not an engine rendering test.

ASSET-008 uses equal source card boxes, aspect-preserving fitting with a one-pixel vertical margin, and one shared
16-color palette. The front symbol reservation is exactly [16,16,56,56]. The 16×16 code reservation is
[52,68,68,84], interpreted as inside the bottom-right outer rim, preserving the silhouette. Front and back alpha
outlines match exactly. Turning frames are outside this reviewed sample.

Files named `_review_4x.png` are integer nearest-neighbor review enlargements, not additional production assets.
Files named `_review_half.png` are nearest-neighbor half-size readability previews, also not production assets.
The HIT type atlas presents all six frames in one row per type; the side-by-side type preview uses the largest HIT
phase. Type order follows the request and type_ramps.json. Native/half-size readability and later renderer previews
still need review; no image-processing check substitutes for that visual assessment.
