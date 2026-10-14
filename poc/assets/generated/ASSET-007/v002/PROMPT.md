# ASSET-007 v002 — H1 revised sample

Brief revision 2. Tool: image_gen.imagegen. Transparent background enabled.

References inspected and supplied:
- `poc/assets/generated/ASSET-007/v001/h1_colorways_review_4x.png` — prior plate to revise.
- `poc/assets/generated/ASSET-003/v002/panels_red_source.png` — frame weight and stepped inset corners, style only.

## Exact generation prompt

Revise the FIRST blue-silver HUD plate in reference 1; reference 2 is style only for stepped inset corner and frame thickness. Deliver ONLY ONE wide player UI plate on transparent background, no text icons labels mockup. Rectangular 96:34 proportions at exactly 4x (384x136 if possible). Outer boundary square corners with a one-hi-bit-pixel dark navy #0b0a14 outline around entire outside. Inside it a THREE-hi-bit-pixel blue-silver frame, top and left light steel blue #9db0ca, base #667b99, bottom/right shade #536787. Then one-hi-bit-pixel dark inner outline. Interior entirely flat lighter bluer navy #0d2347, no gradients no sheen no texture. Face corners have square staircase inset notches matching panel family; all special corner geometry stays within 8x8 hi-bit corner squares (32x32 at 4x). Flat horizontal/vertical edges, no mid-edge ornaments, no bolts. Clean pixel art no antialiasing. Much thicker substantial rim than reference 1. Hard fully opaque art, empty transparent outside. This is production HUD frame original artwork, no lettering.

## Reproducible normalization

Raw saved as `raw/h1_generated.png` (2103×748). Generator did not meet requested 384×136 native-multiple proportions and retained soft fill variation. Raw remains unchanged. It is a design reference, not a runtime sheet.

Run `python poc/assets/generated/ASSET-007/v002/cleanup.py` from the repository root (Pillow, NumPy). The script explicitly reconstructs the source's stepped inset shape as a common indexed native template; it does not claim to preserve every raw pixel. It normalizes outer/rim/inner bands to 1/3/1 pixels, corners within 8×8, constant fill, top/left highlights, and uniform edges. The three colorways and both Synchro phases derive from that single indexed geometry. Config/palettes and actual checks are retained in `processing.json` and `validation.json`.

Output: four 96×34 native parts; colorway row 408×34; two-frame Synchro row 200×34; transparent 8px sheet gaps. Exact nearest 4× review and half previews. Stretch preview covers 44×24 player, 200×34 player, 60×34 foe. Uniform edges, unchanged four corner patches, binary alpha, five visible colors per part, common geometry, 1/3/1 material-band widths and unchanged Synchro fill asserted. No actual game-font, animation playback or in-game test performed. H2–H5 remain gated on this revised sample review.
