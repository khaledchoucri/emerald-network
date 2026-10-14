# ASSET-006 — Impacts (tintable) and the type colour ramps

## Coordination

- State: accepted
- Priority: 6
- Assigned producer: Codex
- Current owner: implementation agent
- Brief revision: 2
- Based on repository commit: 89c74ed
- Last update (UTC date): 2026-10-14
- Next action / blocker: All source art approved. Implementation agent packs, times and tints it in the renderer.

## Purpose and visual brief

- **Intended use.** The hits players see most. Every attack ends in one of these, so they replace more Battle Network 6
  art per request than any per-type set. Like ASSET-004, they remove our dependence on extracted BN6 sprites
  (`tools/fx_curated.py`).
- **How the game uses them.** Most attacks don't have their own effect: the game draws one neutral effect and colours
  it with the attacking move's type (`Vfx_TypeColor` and `GFX_TINT` in `src/pkbn/grid_vfx.c`). A Steel hit and a Dragon
  hit are the same HIT in two colours (`grid_vfx.c:149-165`). So:
  - **Tintable effects are drawn in grey** using exactly the 5 grey tones below. The hi-bit renderer swaps each grey
    for the matching tone of the type's ramp (part C), so one drawing becomes 17 coloured versions.
  - **Natural-colour effects** (explosions, smoke) are drawn in their own colours and never tinted.
- **Deliverable type:** production source, as animated sprite sheets, plus a palette sheet.

### Part A — tintable impacts (grey)

| Effect | Used for (code) | What it should show |
|---|---|---|
| HIT | Fighting, Steel, Dragon hits; physical hits (`grid_vfx.c:149`, `:575`) | A strong round impact: a hard flash that bursts into 6–8 rays and breaks into sparks. Plays once |
| HIT_SMALL | The buster, Bug hits (`grid_vfx.c:154`, `:165`, `:622`) | A small, quick spark: a 4-point flash. Plays once |
| HIT_STAR | The default hit for every other type, and critical hits (`grid_vfx.c:146`, `:451`, `:593`) | A star-shaped burst, bigger and sharper than HIT, with a ring. Plays once |
| DUST | Landing, dashing and ground hits (`grid_vfx.c:594`, `:633`, `:1277`) | A low puff kicked up from a panel, spreading sideways. Plays once |

### Part B — natural-colour effects

| Effect | Used for (code) | What it should show |
|---|---|---|
| EXPLODE | Bombs, Self-Destruct, Explosion (`grid_vfx.c:769`, `:1345`) | A big blast: white core, fire body (fire ramp), turning into dark grey smoke. Plays once |
| EXPLODE_SMALL | Small bombs, breaking objects (`grid_vfx.c:739`, `:780`) | The same blast, about half the size and quicker |
| SMOKE | Sleep and Yawn (`grid_vfx.c:382`) | A soft puff of grey-lilac smoke rising and growing. Plays once |

### Part C — the type ramps

A sheet of 17 rows, one per type, each 5 swatches from darkest to lightest: outline, shade, base, light and highlight.
This follows the structure `STYLE.md` sets for fire. Fire's row is already decided (the STYLE.md Fire row). Design the
other 16 so that:

- each type is recognisable from its colour alone at a glance;
- the 5 tones step evenly in brightness, so a grey drawing keeps its shape when recoloured;
- the types that share a hue family stay apart. Fighting, Fire and Ground: red, orange and brown. Water, Ice and
  Dragon: blue, pale cyan and violet-blue. Poison, Ghost and Psychic: violet, dark indigo and pink. Normal, Steel and
  Rock: warm beige, cool silver and tan.

The types: Normal, Fighting, Flying, Poison, Ground, Rock, Bug, Ghost, Steel, Fire, Water, Grass, Electric, Psychic,
Ice, Dragon, Dark. Also write the hex values as a table in the producer record.

- **Style:** `STYLE.md`. Hard pixels, square spark particles 1–2 px, starbursts with 6–8 rays (its Effects section).
- **Elements to avoid:** copying Battle Network's or Pokémon's hit sprites, and any text.
- **Variants:** 1. Sample first: HIT and part C. Then the other six.

## Technical target

- **Integration:** the hi-bit renderer's effect atlas (POC-24). Effects play through `Fx`/`PlayLoop` in
  `src/pkbn/grid_vfx.c`.
- **The 5 greys for tintable effects** (part A), darkest to lightest. Use only these, plus fully transparent:

  | Tone | Grey | Becomes the type's |
  |---|---|---|
  | 0 | `#202020` | outline |
  | 1 | `#585858` | shade |
  | 2 | `#909090` | base |
  | 3 | `#c8c8c8` | light |
  | 4 | `#ffffff` | highlight (the flash core) |

  Delivering at a large size is fine: the implementation agent snaps every pixel to the nearest of these five. So use
  flat areas of these greys, without blending them.
- **Cells, frames and timing.** Measured from today's frames (`sBn6Frames` in the build's
  `include/pkbn/bn6_gfx_data.h`), doubled and rounded up to even numbers. Times are in game frames at 60 per second.
  More frames, each held for less time, are welcome when the total time stays the same.

  | Effect | Today: frames, time per frame | Total | Cell at 2× | Anchor in the cell |
  |---|---|---|---|---|
  | HIT | 6: 1/1/2/2/2/2 | 10 | 64×64 | centre |
  | HIT_SMALL | 4: 1 each | 4 | 64×56 | centre |
  | HIT_STAR | 5: 2/3/3/2/2 | 12 | 92×86 | centre of the burst |
  | DUST | 1 (we'd like 4: 2 each) | 8 | 64×46 | centre of the puff's base |
  | EXPLODE | 6: 2/4/4/4/4/4 | 22 | 112×112 | centre |
  | EXPLODE_SMALL | 6: 2/3/3/3/4/4 | 19 | 64×94 | centre of the base, which sits low |
  | SMOKE | 8: 2 each | 16 | 32×32 (it may grow to 48×48) | centre |

- **Part C format:** a PNG of 17 rows × 5 swatches, each swatch 16×16, in the type order above. Plus the hex table in
  the record.
- **Alpha:** see "Source-art rules" in `PIPELINE.md`.
- **Sheet layout:** frames left to right, one PNG per effect.
- **Conversion:** the implementation agent snaps the greys, packs, sets anchors and builds the tint tables from part C.

## References

| Path | Role |
|---|---|
| `docs/asset-workflow/STYLE.md` | Rules; the Fire row is the model ramp |
| `poc/assets/generated/ASSET-004/` | Approved fire effects: line weight, spark size, energy |
| `poc/assets/generated/ASSET-001/v003/variant-a-stepped-corners.png` | The impact starburst in the concept |

## Acceptance criteria

- **Source art:** the greys are exactly the five listed. Each effect reads at native size and at half size. HIT,
  HIT_SMALL and HIT_STAR can be told apart by shape alone.
- **Part C:** a test sheet from the implementation agent, with HIT recoloured in all 17 ramps side by side, shows 17
  distinct, readable hits.
- **In game** (implementation agent): side-by-side clips of old and new hits in the same self-test battle.

## Producer record

- Brief revision used: 1.
- Tool: image_gen.imagegen; exact prompt/reference list in the sample's PROMPT.md. Raw outputs retained under raw/ for reproducibility, not intended for runtime use.
- Programmatic processing: authorized by PIPELINE.md Source-art rules item 7. Exact config and operations are in processing.json / validation.json; shared helper: poc/assets/generated/_tools/prepare_samples.py. Run from repository root with the sample's processing.json. Python dependencies: Pillow and NumPy.
- Delivery scaling: native files plus exact 4× nearest-neighbor review PNGs and half-size previews. Raw generator dimensions were not native or exact integer multiples; cleanup reconstructs/packs the specified delivery geometry without claiming the raw art met that constraint.
- Visual review performed on native and 4× samples; no visible text, logos or existing characters. User review and implementation integration remain pending.
- References: approved original FIREBALL source for pixel energy/particles only; no extracted effect sprites. Type palette proposals are numeric original designs, rendered deterministically as exact swatches; Fire is fixed by STYLE.md. Raw HIT 2041×771 RGBA.

### Delivery v001 — initial sample

- Native HIT: poc/assets/generated/ASSET-006/v001/hit.png, 424×64, six 64×64 cells with 8px empty gaps; order left-to-right. Centre anchor (32,32); intended holds 1/1/2/2/2/2 game frames, 10 total, one-shot.
- Cleanup: explicit frame partitions, alpha threshold128 and small-component filtering, one shared scale across all phases to preserve relative growth, centre placement, exact five-gray band mapping. No semi-transparent halo/fringe remains in the delivered native PNG. Details in processing.json/validation.json.
- Palette: type_ramps.png, 80×272, 17 rows in request order and five16×16 swatches per row; exact hex table below and machine-readable type_ramps.json. All ramps have monotonic linear luminance and Fire exactly matches STYLE.md. Equal perceptual brightness steps are not claimed.
- Tint review: hit_all_types.png (17 animation-strip rows), hit_types_side_by_side.png (same peak frame in 17 colourways). Exact grey-index replacement preserves geometry. Fourfold review previews provided for HIT, ramps and peak colours.
- Checks: native dimensions, binary alpha, ≤5 visible colours and exact five-grey membership, all five greys used, six nonempty stages and clear8px gaps passed. Palette/tint checks passed in ramps_validation.json. Rerun ramps_processing.json after processing.json to reproduce ramp/tint outputs.
- Visual review: flash grows into a strong round/rayed impact and breaks into square fragments; native stages remain distinct, 17 peak previews show proposed type colours. Half-size review provided.
- Limitations: cell-centre alignment is verified as packing, not exact semantic focal-point tracking; actual animation timing/playback and old/new self-test clips unrun. Other six effects remain gated on HIT/ramp review.

### Type ramp hex values

| Type | Outline | Shade | Base | Light | Highlight |
| --- | --- | --- | --- | --- | --- |
| Normal | `#302c25` | `#6d6553` | `#b4a68e` | `#ded1b4` | `#fff2dc` |
| Fighting | `#39131b` | `#7d2434` | `#c94250` | `#ef8b87` | `#ffe2d6` |
| Flying | `#1e2b45` | `#53688f` | `#91aacf` | `#c5d8f0` | `#f0f7ff` |
| Poison | `#2c123e` | `#5c2877` | `#9744b5` | `#cb87df` | `#f2d6fa` |
| Ground | `#302014` | `#68442a` | `#ad7945` | `#dca563` | `#fbe2b6` |
| Rock | `#302922` | `#665542` | `#a48d68` | `#d3bd91` | `#f4e4c5` |
| Bug | `#1f3014` | `#4b6420` | `#8fa83c` | `#c8db75` | `#edf7c9` |
| Ghost | `#15132f` | `#39345f` | `#65568f` | `#9c89c2` | `#ddd1f2` |
| Steel | `#172b34` | `#47636c` | `#819aa4` | `#b5d0d8` | `#edf9fc` |
| Fire | `#9d220f` | `#dc4b24` | `#fc871f` | `#fef237` | `#fefdf2` |
| Water | `#092b46` | `#125786` | `#248fc4` | `#75c8ea` | `#d6f3ff` |
| Grass | `#103019` | `#245f31` | `#45a64a` | `#8cd979` | `#dff7cb` |
| Electric | `#3c2c06` | `#826011` | `#d5a21b` | `#f6da57` | `#fff4b5` |
| Psychic | `#3e1634` | `#81245f` | `#c84c98` | `#ed97cb` | `#ffe0f3` |
| Ice | `#163b43` | `#33747d` | `#77c3cc` | `#b7e9ed` | `#eaffff` |
| Dragon | `#1c164c` | `#44318b` | `#745bd0` | `#aa97f0` | `#e4dcff` |
| Dark | `#141722` | `#34394b` | `#5b6377` | `#919bb0` | `#d6dfec` |


### Delivery v002 — revision 2 ramps and six remaining effects

- Tool: six independent `image_gen.imagegen` calls run concurrently. Exact prompts and inspected original references are in `poc/assets/generated/ASSET-006/v002/PROMPT.md`; raw sources retained in `raw/`. Approved HIT v001 is unchanged.
- Revision: Normal is lighter warm cream, Rock dark cool grey-brown, Ground richer orange earth. Optional Dragon changed toward blue to separate it from Ghost. The other 13 ramps, including fixed Fire, are unchanged. Numeric original ramps rendered deterministically; full hex table below and `v002/type_ramps.json`.
- Native outputs under `poc/assets/generated/ASSET-006/v002/`:

| File | Native PNG | Cells | Target holds at 60 fps | Target anchor |
| --- | --- | --- | --- | --- |
| hit_small.png | 280×56 | 4 × 64×56, 8 px gaps | 1/1/1/1 (4 total) | (32,28), centre |
| hit_star.png | 492×86 | 5 × 92×86, 8 px gaps | 2/3/3/2/2 (12 total) | (46,43), burst centre |
| dust.png | 280×46 | 4 × 64×46, 8 px gaps | 2/2/2/2 (8 total) | (32,43), base |
| explode.png | 712×112 | 6 × 112×112, 8 px gaps | 2/4/4/4/4/4 (22 total) | (56,56), centre |
| explode_small.png | 424×94 | 6 × 64×94, 8 px gaps | 2/3/3/3/4/4 (19 total) | (32,90), low base |
| smoke.png | 440×48 | 8 × 48×48, 8 px gaps | eight holds of 2 (16 total) | (24,24), centre |

- Cleanup is authorized by PIPELINE.md item 7. Reproduce from repository root: `python poc/assets/generated/ASSET-006/v002/process.py`, then `python poc/assets/generated/_tools/prepare_samples.py poc/assets/generated/ASSET-006/v002/ramps_processing.json`. Dependencies Pillow/NumPy. Source columns explicitly partitioned in processing.json; alpha threshold 220 removes generated fringes, components below 48 source pixels removed, alpha crops, one shared aspect-preserving nearest-neighbour scale per effect, packed into exact cells with 8 px transparent gaps. Base alignment used for DUST/EXPLODE_SMALL; others centered. HIT_SMALL deliberately occupies a smaller footprint. Tintables mapped exactly to five specified grays; natural fire/smoke use fixed 9- and 4-color palettes.
- Raw images did not meet the requested integer scale/cell spacing and contained translucent halos. Native outputs reconstruct the delivery geometry; no claim that raw generation met those constraints. Threshold cleanup removes fringe rather than retaining glow.
- File checks passed: exact dimensions, binary alpha, palette membership/limits, nonempty individual frames, clear 8 px gaps and outer padding, frame-count/target-duration consistency. Ramps: monotonic linear luminance, Fire match, exact grey-to-ramp replacement preserving HIT geometry; validation.json and ramps_validation.json record checks and SHA-256. Even perceptual luminance spacing is not claimed.
- Visual review performed at native, half and 4× sizes: small four-point spark, larger pointed/ring HIT_STAR, low widening DUST, white/fire-to-grey blast stages, grey-lilac rising smoke. Tiny final dissipation stages are intentionally faint at half size. All are original art; no extracted sprites.
- Reviews: each effect has *_review_4x.png and *_review_half.png; combined effects_review_2x.png, effects_native_review.png; revised hit_types_side_by_side_review_4x.png plus type_ramps_review_4x.png. Review-board labels and dark background are preview-only, never included in native sprites.
- Limitations: intended holds are metadata, not tested playback; cell packing anchors are documented but exact semantic focal-point movement is unverified. Palette/readability review is not engine acceptance. Implementation agent owns preview playback, semantic-anchor adjustment, atlas integration and old/new battle clips. No additional sample approval gate remains from v001; all six requested effects delivered for consolidated review.

### Revision 2 type ramp hex values

| Type | Outline | Shade | Base | Light | Highlight |
| --- | --- | --- | --- | --- | --- |
| Normal | `#332f28` | `#827968` | `#c4b9a4` | `#e5dcc8` | `#fff7e7` |
| Fighting | `#39131b` | `#7d2434` | `#c94250` | `#ef8b87` | `#ffe2d6` |
| Flying | `#1e2b45` | `#53688f` | `#91aacf` | `#c5d8f0` | `#f0f7ff` |
| Poison | `#2c123e` | `#5c2877` | `#9744b5` | `#cb87df` | `#f2d6fa` |
| Ground | `#352015` | `#794528` | `#b97942` | `#e3aa69` | `#ffe0b0` |
| Rock | `#29282a` | `#514e50` | `#817c79` | `#aaa29a` | `#d6cec3` |
| Bug | `#1f3014` | `#4b6420` | `#8fa83c` | `#c8db75` | `#edf7c9` |
| Ghost | `#15132f` | `#39345f` | `#65568f` | `#9c89c2` | `#ddd1f2` |
| Steel | `#172b34` | `#47636c` | `#819aa4` | `#b5d0d8` | `#edf9fc` |
| Fire | `#9d220f` | `#dc4b24` | `#fc871f` | `#fef237` | `#fefdf2` |
| Water | `#092b46` | `#125786` | `#248fc4` | `#75c8ea` | `#d6f3ff` |
| Grass | `#103019` | `#245f31` | `#45a64a` | `#8cd979` | `#dff7cb` |
| Electric | `#3c2c06` | `#826011` | `#d5a21b` | `#f6da57` | `#fff4b5` |
| Psychic | `#3e1634` | `#81245f` | `#c84c98` | `#ed97cb` | `#ffe0f3` |
| Ice | `#163b43` | `#33747d` | `#77c3cc` | `#b7e9ed` | `#eaffff` |
| Dragon | `#141d4a` | `#2b4291` | `#526fda` | `#94b0fa` | `#dbeaff` |
| Dark | `#141722` | `#34394b` | `#5b6377` | `#919bb0` | `#d6dfec` |

## Consolidated review

- Reviewed delivery: v001 (`hit.png`, `type_ramps.json`, `hit_types_side_by_side_review_4x.png`)
- Reviewer: Claude (implementation agent), asked by Khaled to review
- HIT: approved. Flash, 8-ray burst, square sparks breaking apart, fade; exactly the five greys; 6 × 64×64 cells.
- Ramps: approved except one group. Required change (brief revision 2): **Normal and Rock are nearly the same beige,
  and Ground is close to both.** In the side-by-side they can't be told apart. Make them three clearly different
  materials:
  - Normal: warm cream/beige, low saturation (keep as is, or lighter);
  - Ground: orange-brown earth (keep);
  - Rock: cool grey-brown stone, noticeably greyer and darker than Normal.
  Check the result in the same side-by-side at native size.
- Optional: Ghost and Dragon are close (indigo vs violet-blue); push Dragon bluer or brighter if it's easy.
- Decision: HIT and 14 ramps approved; revise Rock/Normal/Ground; continue with the remaining six effects.

### Review of v002

- Reviewed delivery: v002 (`type_ramps.json`, `hit_types_side_by_side_review_4x.png`, `effects_review_2x.png`, the six
  sheets)
- Reviewer: Claude (implementation agent), asked by Khaled to review
- Ramps: **approved.** Normal (cream), Rock (grey-brown stone) and Ground (orange earth) are now three materials; Dragon
  is clearly bluer than Ghost.
- HIT_SMALL, HIT_STAR, DUST, EXPLODE, EXPLODE_SMALL, SMOKE: **approved.** EXPLODE's first three frames are flame-shaped,
  so it's close to the fire effects; that suits bombs and Self-Destruct, so keep it.
- Decision: request accepted. Anchors, holds and playback are checked in the renderer (integration below).

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

- 2026-10-14 — implementation agent (Claude) — reviewed v001 for Khaled: HIT approved; Normal/Rock/Ground ramps to be separated; remaining effects unblocked.

- 2026-10-14 — Codex — revision 2: separated material ramps and Dragon, generated remaining six effects concurrently, scripted native cleanup and inspected native/half/4×; delivered v002 for review, playback/integration pending.
- 2026-10-14 — implementation agent (Claude) — reviewed v002: ramps and all six effects approved; request accepted for integration.
