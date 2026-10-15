# ASSET-010 — Strike effects (tintable)

## Coordination

- State: delivered
- Priority: 10
- Assigned producer: Codex
- Current owner: Codex
- Brief revision: 2
- Based on repository commit: 89c74ed
- Last update (UTC date): 2026-10-15
- Next action / blocker: Review v002 SLASH revision and STAB, SLASH_ARC, CLAW, JAWS source sheets.
  Implementation agent checks anchor, timing and type tinting in the renderer. No visual approval or game acceptance is presumed.

## Purpose and visual brief

- **Intended use.** What a close-range attack looks like where it lands. The game sorts every contact move into a
  strike kind (`StrikeOf` and `Strike` in `src/pkbn/grid_vfx.c:519-606`) and draws that kind's effect, tinted with
  the move's type. Like ASSET-006, these replace extracted Battle Network 6 sprites (`tools/fx_curated.py`), except
  JAWS, which is drawn in code today.
- **Tintable:** all five are drawn in the 5 greys of ASSET-006, and the game recolours them with the type's ramp.
  Normal-type moves show them in plain grey-white.
- **Deliverable type:** production source, as animated sprite sheets.

| Effect | Used for (code) | What it should show |
|---|---|---|
| SLASH | Blade moves, the default strike (Cut, Slash, Leaf Blade, Aerial Ace…) (`grid_vfx.c:600`, `:1315`) | One fast diagonal cut: a thin bright line that sweeps top-right to bottom-left, thickens, then breaks into a few square sparks. Plays once |
| SLASH_ARC | Whips and tails (Vine Whip, Slam, Iron Tail…), and wide blade moves (`:590`, `:600`, `:1318`) | A curved swipe: a crescent sweeping across, thick in the middle and tapering at both ends. Plays once |
| CLAW | Claw moves (Scratch, Fury Swipes, Crush Claw…) and the Dark type's impact (`:164`, `:563`, `:720`) | Three parallel rake marks, torn diagonally downwards. Plays once |
| STAB | Stabs: horns, beaks and stingers (Peck, Horn Attack, Poison Sting, Megahorn…) (`:586`). Today they borrow the upright SPIKE, which stays with the earth effects for Dig (`:794`) | A sharp narrow thrust pointing right, with a small flash at its tip. The game slides it forwards. One frame, or 2 for a glint |
| JAWS | Bites (Bite, Crunch, Hyper Fang, Poison Fang…) (`:565`; drawn by `DrawJaws`, `:984`) | Two rows of fangs snapping shut: upper and lower jaw close, hold, and fade. Plays once |

- **Style:** `STYLE.md` Effects section, and the ASSET-006 HIT (approved) for line weight and sparks. Hard pixel
  edges; motion shown with a few hard-edged trail bands, not blur.
- **Facing:** draw everything facing or moving **right**. The game mirrors it for the foe.
- **Elements to avoid:**
  - copying Battle Network's or Pokémon's slash, claw or bite sprites;
  - any creature's actual mouth or claws (JAWS and CLAW are abstract shapes, not a monster's body parts);
  - text.
- **Variants:** 1. Sample first: SLASH.
- **Not requested:** SLASH_WIDE, SLASH_WIDE2, LONGSWORD and FANG are in `tools/fx_curated.py` but the game never
  draws them (no use outside the effect table), so they aren't worth redrawing.

## Technical target

- **Integration:** the hi-bit renderer's effect atlas (POC-24), through `Fx` in `src/pkbn/grid_vfx.c`.
- **The 5 greys:** exactly as in ASSET-006 (`#202020`, `#585858`, `#909090`, `#c8c8c8`, `#ffffff`), plus fully
  transparent.
- **Cells, frames and timing.** Measured from today's frames (`sBn6Frames` in the build's
  `include/pkbn/bn6_gfx_data.h`), doubled and rounded up to even numbers. JAWS is measured from `DrawJaws`. Times
  are in game frames at 60 per second. More frames, each held for less time, are welcome when the total time stays
  the same.

  | Effect | Today: frames, time per frame | Total | Cell at 2× | Anchor in the cell |
  |---|---|---|---|---|
  | SLASH | 3: 6/4/3 | 13 | 76×142 | centre of the cut |
  | SLASH_ARC | 3 drawn (5 with blank first and last): 3/3/3 | 11 | 142×176 | centre of the arc |
  | CLAW | 3 drawn (5 with blank first and last): 3/3/3 | 11 | 84×204 | centre of the rake marks |
  | STAB | 1 held 5 (2 welcome) | 5 | 62×26 (today's upright SPIKE is 26×62), pointing right | the base of the thrust |
  | JAWS | snaps shut over 6, holds, fades by 20 | 20 | 64×96 | the point where the jaws meet |

  The tall cells for SLASH, SLASH_ARC and CLAW come from today's sprites. Art may use less of the cell; empty space
  is fine.
- **Sheet layout:** frames left to right, one PNG per effect; see "Source-art rules" in `PIPELINE.md`.
- **Conversion:** the implementation agent snaps the greys, packs, sets anchors and checks the tint with the
  ASSET-006 ramps.

## References

| Path | Role |
|---|---|
| `docs/asset-workflow/STYLE.md` | Rules |
| `poc/assets/generated/ASSET-006/v001/hit.png` | Approved HIT: line weight, sparks, the five greys |
| `poc/assets/generated/ASSET-006/v001/type_ramps.json` | The ramps the game will recolour them with |

## Acceptance criteria

- **Source art:**
  - exactly the five greys;
  - each effect reads at native size and at half size;
  - SLASH, SLASH_ARC and CLAW can be told apart by shape alone;
  - JAWS reads as a bite without being any creature's mouth.
- **Tint check:** the implementation agent's sheet of all five recoloured in several ramps (Normal, Grass, Dark,
  Steel) stays readable.
- **In game** (implementation agent): side-by-side clips of old and new strikes in a self-test battle.

## Producer record

### Current delivery — v002, brief revision 2 (2026-10-15)

All paths below are under `poc/assets/generated/ASSET-010/v002/`. Previous v001 files remain unchanged.

| Source sheet | RGBA dimensions | Cell | Frames and holds at 60 fps | Suggested anchor |
|---|---|---|---|---|
| `slash.png` | 328×142 | 76×142 | 4: 4/4/3/3 | (38,71), cut centre |
| `stab.png` | 132×26 | 62×26 | 2: 3/2 | (4,13), left trail base |
| `slash_arc.png` | 742×176 | 142×176 | 5: 1/3/3/3/1, first and last blank | (71,88), arc centre |
| `claw.png` | 452×204 | 84×204 | 5: 1/3/3/3/1, first and last blank | (42,102), rake centre |
| `jaws.png` | 352×96 | 64×96 | 5: 3/3/2/6/6 | (32,48), meeting point |

- Every sheet has 8 px transparent gutters, binary alpha, transparent outer edges and only the five requested opaque gray slots. Art uses less of the tall cells, without stretching. Native anchors are suggestions, not engine-verified placements.
- **SLASH revision 2:** first frame is a continuous thin white core; second retains the strong shaded cut; third starts splitting; fourth keeps the broken diagonal remnant and sparks. First two frames each have exactly one 8-connected opaque component, so there are no lone specks. First white core is also one 8-connected component. The new holds total **14 game frames**: revision 2's explicit 4/4/3/3 overrides the old table's 13-frame total.
- **Other strikes:** STAB's dominant bright flash leads at the right end, with a narrow shaft trailing left and a second-frame small trailing glint; SLASH_ARC is a right-facing crescent with leftward hard trail bands; CLAW has three parallel diagonal rake marks; JAWS has four abstract upper/lower energy fangs that close over the first 6 frames, hold, then break into dimmer opaque fragments by game frame 20. They are abstract effects, with no creature body parts.
- Tool/provenance: `image_gen.imagegen`, transparent output; five independent generations run concurrently. Approved original `ASSET-006/v001/hit_review_4x.png` supplied for line weight, grays and square sparks. SLASH additionally received original v001 SLASH for its approved thick frame. No extracted sprites supplied or copied. Full prompts are in `PROMPT.md`; original generator PNGs retained in `raw/`.
- SLASH row generation repeated the old checkered first-frame core, so a separate no-reference solid-line generation (`raw/slash_first.png`) replaced only frame 1. After native resampling, thin-core dropouts were repaired along the generated row centres to preserve a solid 2 px bright interior where the generated silhouette allows; the generated exterior is preserved. This correction is documented and reproducible, rather than treating the raw output as compliant.
- Cleanup via `cleanup.py` (Pillow, NumPy, SciPy): alpha threshold 192, connected-component dust removal, isolated frame crops, shared isotropic scale per effect, nearest-neighbor resampling, exact gray snapping and equal packing. STAB cells are mirrored because the generator placed its dominant flash on the left; the delivered dominant flash leads right, with shaft trailing left. SLASH first two frames retain only their main component. JAWS final broken remnants are capped at gray #909090 so fading uses geometry and tones with no semitransparency. Raw canvas proportions were approximate; final crops preserve aspect ratio and are repacked into exact native cells.
- Checks: complete PNG decode, native geometry/cell count, gray palette membership, binary alpha, empty 8 px gutters, empty outer edges. Native/4×/half-size visual inspection confirms solid/split/broken SLASH progression, distinct strike silhouettes and abstract closing bite. `validation.json` records dimensions, holds, source crop boxes and SHA-256 hashes; `processing.json` records cleanup choices. All checks are source-level checks.
- Reviews: each sheet has `<effect>_review_4x.png` and `<effect>_review_half.png`. `tint_review.png` statically shows all five with **ASSET-006/v002** approved Normal/Grass/Dark/Steel ramps. Each `<effect>_playback_slow.gif` is a **5× slowed diagnostic loop** using the declared holds plus a final review pause, not a 60 fps game clip. Static tint and diagnostic GIFs do not establish runtime acceptance.
- Remaining implementation work: atlas integration; confirm anchor positions; verify native/half readability against the actual arena, not only transparency previews; 60 fps one-shot playback; old/new strike clips and type ramp checks in the renderer. Review approval remains pending.

### Prior delivery — v001, brief revision 1 (retained record)

- Brief revision used: 2 (latest complete delivery v002; initial v001 retained below).
- Delivery: `poc/assets/generated/ASSET-010/v001/slash.png`, 244×142 RGBA; three 76×142 cells left to right with 8 px empty gutters.
- Reviews: `slash_review_4x.png` (976×568) and `slash_review_half.png` (122×71), in the same delivery directory.
- Assumptions / unresolved constraints: one diagonal cut, thin → thick → square fragments. Suggested cell anchor is (38,71); 6/4/3 game-frame timing is recorded in `processing.json`, but runtime playback/anchor/tint tests are not run. Other strike kinds are deliberately withheld until the sample review.
- Tool and generation/edit prompt: `image_gen.imagegen`; full prompt in `v001/PROMPT.md`, original output retained as `v001/raw/slash.png` (1644×957). Raw image was generated above native scale with approximate sheet proportions; cleanup preserves each frame's aspect ratio and repacks exact cells, rather than stretching the generator's whole canvas.
- References actually supplied to the tool: approved original `poc/assets/generated/ASSET-006/v001/hit_review_4x.png` for line weight, grayscale structure and square sparks. The new ASSET-006 v002 HIT_SMALL was also inspected after generation for consistency; it was not supplied to the image tool.
- Cleanup: reproducible `v001/cleanup.py` (Pillow/NumPy/SciPy): alpha threshold 192, retain main slash and strongest square-particle components (6/7/9 per frame), isolate frames, shared isotropic nearest-neighbor scale to 108 px occupied height, centre in cells, snap luminance to exact five grays, set empty RGB/alpha to zero. No extracted sprites used.
- Checks performed: complete PNG decode; exact five requested grays; binary alpha; exact sheet size/cell spacing; empty 8 px gutters and outer edges; 4× and half-size visual inspection for thin/thick/fractured progression. Details and SHA-256 in `v001/validation.json`. Native half-size remains readable; animation, atlas integration and in-game tint testing are implementation work.

## Consolidated review

- Reviewed delivery: v001 (`slash.png`)
- Reviewer: Claude (implementation agent), asked by Khaled to review
- What works: the thick middle frame is the right weight and shading, and it matches HIT.
- Required changes (brief revision 2):
  1. **Frame 1 is hollow:** an outlined line with a checker inside, which reads as a dotted rope at native size. Make
     it a solid 2–3 px bright line with the dark outline only on its edges.
  2. **Frame 3 loses the cut:** it's only scattered squares, so the sparks seem to come from nowhere. Keep a thin,
     broken remnant of the line with the sparks coming off it, and add one frame between 2 and 3 where the thick line
     starts to split (four frames in total, holds 4/4/3/3).
  3. Remove the lone specks around frames 1 and 2.
- Decision: revise SLASH; the other four strikes may go ahead in the same delivery, following these fixes.

## Integration and acceptance (implementation agent)

- Accepted delivery:
- Integrated paths / patch / commit:
- Conversion details:
- In-game test command or scenario:
- Results and screenshot/log evidence:
- Remaining work:

## Change history

- 2026-10-14 — implementation agent (Claude) — created at revision 1, ready for Codex.
- 2026-10-14 — Codex — delivered SLASH v001 sample after inspecting approved HIT and new v002 impact style; other strikes await sample review. This is source delivery, not in-game acceptance.
- 2026-10-14 — implementation agent (Claude) — reviewed SLASH v001: revised (revision 2); the other strikes released.
- 2026-10-15 — Codex — delivered v002 SLASH revision plus STAB, SLASH_ARC, CLAW and JAWS; exact native geometry/grays/alpha checked, type-ramp review and slowed diagnostic playback supplied. No engine acceptance claimed.
