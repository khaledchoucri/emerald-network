# ASSET-008 v002 generation record

Tool: image_gen.imagegen, transparent_background=true for every call. Brief revision1. Outputs copied unchanged to raw/. All references are original project art. Generation requested integer-scale art, but raw canvas dimensions did not satisfy it; final native geometry comes from documented crop/nearest-neighbor processing. Reference for turn, emblem and first banner call: ../v001/card_front_back_review_4x.png (inspected before calls). Other calls had no image reference.

The common prefix for the initial six calls was:

> Original crisp hi-bit pixel-art game asset on transparent background, no text/logos/labels/characters. Hard stepped pixels, no blur, no semitransparency. Strict one horizontal row, equally sized cells separated by clear transparent gaps; no extra cells. Each frame must stay inside its cell.

Suffixes, exact requested descriptions:

## turn.png

Use attached approved front and back as exact material/style reference. Generate ONLY TWO turning views of this same card: first 3/4 front view (vertically upright, compressed width to about 45/72 of front), second edge-on narrow bright 6/72 silver and magenta strip. 72:88 cell aspect, 4x pixel scale each 288x352. Keep card height same; front dark blank square window in first view, code tab at lower right. Neutral silver/navy body, #ff65a5 bright accent. No front/back flat views.

## trail.png

FOUR 96:24 horizontal card-flight trail animation cells at 4x (384x96 each), flowing RIGHT with pointed leading bright end at right, hard horizontal speed streaks behind at left, square sparks. Four subtle successive looping phases with same occupied area. ONLY grayscale #202020 #585858 #909090 #c8c8c8 #ffffff. No card or symbols.

## emblem.png

SEVEN 128:128 square cells at 4x: six-stage badge arrival then final STATIC badge. Frame1 small square white/magenta flash, frame2 larger flash, frame3 forming segmented rim, frame4 emerging small badge, frame5 almost full badge, frame6 full badge with tiny square arrival spark, frame7 full static badge. Same centre throughout. Badge is original stepped octagon heavy rim 128px cell, neutral navy and silver plus #ff65a5 accent matching attached card; blank 64x64 central dark square window for engine symbol. Hard square-notched corners. No text.

## burst.png

SIX 208:208 square frames at 3x of an original Program Advance radial burst: 1 tiny flash;2 sharp compact rays;3 long rays and square sparks around EMPTY CENTRAL WINDOW;4 fragmented rays;5 outward fading square fragments;6 sparse small final particles. Centre anchor. 6-8 rays, geometric pixels not organic. ONLY five greys #202020 #585858 #909090 #c8c8c8 #ffffff.

## symbols.png

SEVENTEEN distinct original tiny 32:32 game type icon cells at 6x each192x192, exact left-to-right row order: Normal (square with central circle), Fighting (two crossing blunt batons), Flying (three sweeping feather strokes), Poison (tilted flask drop), Ground (three stacked earth strata), Rock (angular split boulder), Bug (six-legged segmented beetle), Ghost (square drifting wisp with hollow face), Steel (two interlocking steel bars), Fire (asymmetric split flame), Water (single thick drop), Grass (two sprouting leaves), Electric (jagged lightning fork), Psychic (angular inward spiral), Ice (three pointed crystal shards), Dragon (abstract hooked dragon horn), Dark (eclipsed diamond). ONLY grayscale #202020 #585858 #909090 #c8c8c8 #ffffff. Create our own distinct designs, no copying existing game symbols. Strong readable silhouettes with substantial transparent margins.

## banner.png (static rejected, shine sources retained)

FIVE horizontal 240:36 cells at 4x each960x144: first static original blank name banner, stepped square-notched corners sized10x10 native, neutral silver/navy frame bright #ff65a5 accent matching attached card, blank dark interior for engine text, parallel straight 1px edges. Then FOUR separate shine-only OVERLAY cells (no banner under them): narrow hard-edged diagonal silver streak sweeping left-to-right in successive quarters of banner width. Transparent everywhere else. No text.

## banner_retry.png (no reference)

Original hi-bit pixel art. Transparent background. Draw exactly ONE very wide and shallow horizontal empty nameplate banner, NO CARDS or icons or lettering. Aspect ratio 240:36 (6.667 wide). Draw at4x 960x144 pixels. Square stepped inset corners about40x40 at4x. 1pixel native dark navy outline, neutral silver border with bright #ff65a5 magenta inner rim. Completely blank solid dark navy interior. Top-left single tone highlight, flat material shading, no gradient. Strong straight middle sections for nine-slice stretching. Hard pixel edges no blur no antialias no semitransparency. This is a title BAR, not a chip card.

## Reproduction

From repository root: `python poc/assets/generated/ASSET-008/v002/prepare.py` (Pillow, NumPy; imports existing shared helper read-only). Crops/palette in processing.json. Alpha threshold128; remove detached components smaller than32 source pixels; trim transparent edges; aspect-preserving nearest-neighbor fit. Emblem and burst retain common source scale so flashes don't expand to full badge size. Uniform nine-slice edges/interior with10px corners. Flatten previous central decoration in[25,25,103,103] and reserve64×64 emblem window in frames4–7 with1px silver outline outside[32,32,96,96]. Right-align trail tips to x94. Shine streaks placed at x18,78,138,198 in native240×36 cells. Add optional1px inset code-tab outline to v002 front only, preserving approved v001.

Animation timing/anchors: card centred (engine controls timing); trail right-end anchored, four frames at2 game frames each loop; emblem centred six arrival frames at2 game frames each then static; burst centred six frames at2 game frames each once; banner centred, shine four frames at3 game frames each once. Diagnostic GIFs loop for inspection and are not runtime timing acceptance.
