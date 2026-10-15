# ASSET-008 — Program Advance moment: production art

## Coordination

- State: delivered
- Priority: 8
- Assigned producer: Codex
- Current owner: Codex
- Brief revision: 2
- Based on repository commit: 89c74ed
- Last update (UTC date): 2026-10-15
- Next action / blocker: Reviewer checks v003 Fighting clenched fist and Ground fissured mound; other15 P5 cells and approved P1–P4/P6 remain unchanged.

## Purpose and visual brief

- **Intended use.** The art for the moment a Program Advance forms, as storyboarded in ASSET-002 v001 (approved):
  1. three chip cards fly in and meet;
  2. they flash into one emblem, with the Program Advance's name on a banner;
  3. the attack fires.
  Program Advances are a headline feature (POC-22), so this is the game's signature moment. Today it's three plain
  boxes and a flash (`DrawPAForming` in `src/pkbn/grid_draw.c:2002`).
- **Deliverable type:** production source, as sprites and UI, some animated.
- **Style:** `STYLE.md`. The storyboard's cards, emblem and rays are the target. Its slanted camera is concept-only:
  the battle is seen straight on.
- **The game draws** the move's name, the chip code letter and the type symbol. The art leaves room for them.
- **Elements to avoid:**
  - text;
  - copying Battle Network's chip or Program Advance art;
  - copying the Pokémon games' type symbols. Part P5 is our own symbols.

### The parts

| Part | Storyboard frame | What it is |
|---|---|---|
| P1 Chip card | 1 | A card with stepped corners and a bright rim. A square window in the middle holds the type symbol; a small corner tab holds the code letter. Two faces: **front** and **back** (a plain pattern, no text). Plus **2 turning frames** between them (three-quarter and edge-on), so a card can flip as it flies |
| P2 Trail | 1 | The streak behind a flying card: 4 frames, in the 5 greys of ASSET-006, so the game colours it by type |
| P3 Emblem | 2 | The merged badge: a stepped octagon with a heavy rim and a 64×64 window for the symbol. It has a 6-frame **arrival**, growing from a flash to the full badge, then a static frame |
| P4 Burst | 2 | Rays and square sparks around the emblem: 6 frames, plays once, in the 5 greys so it takes the type's colour |
| P5 Type symbols | 1–2 | 17 simple symbols of our own design, one per type (flame, drop, leaf, bolt and so on), each in the 5 greys so the game colours them. Shown in the card and emblem windows. They don't replace the game's type labels elsewhere |
| P6 Banner | 2 | The name banner under the emblem, plain inside. It stretches like ASSET-007's frames. Plus a 4-frame **shine** overlay, a light sweeping across it once |

## Technical target

- **Integration:** `DrawPAForming` in `src/pkbn/grid_draw.c` (the timing is in its `k` counter), redrawn by the hi-bit
  renderer (POC-24). The game sets the timing.
- **Sizes at 2×:**

  | Part | Cell | Frames | Anchor |
  |---|---|---|---|
  | P1 Card | 72×88 | 4: front, ¾, edge, back. The symbol window is 40×40, centred 8 px above the card's centre. The code tab is 16×16 at the bottom right | centre |
  | P2 Trail | 96×24 | 4, 2 game frames each, loops | right end (it follows the card) |
  | P3 Emblem | 128×128 | 7: arrival 1–6 (2 game frames each), then the static badge | centre |
  | P4 Burst | 208×208 | 6, 2 game frames each, plays once | centre |
  | P5 Symbols | 32×32 each, 17 in one row in this order: Normal, Fighting, Flying, Poison, Ground, Rock, Bug, Ghost, Steel, Fire, Water, Grass, Electric, Psychic, Ice, Dragon, Dark | static | centre |
  | P6 Banner | 240×36 sample, corners 10×10. In game, 120–420 wide | banner static; shine 4 frames, 3 game frames each, plays once | centre |

- **Colours:**
  - P2, P4 and P5 use only the 5 greys from ASSET-006.
  - The card, emblem and banner are drawn in their own neutral silver and dark, with a **magenta-pink rim** for the
    Program Advance accent. The game uses a hot magenta-pink for Program Advances today (`COL_PA`, `#ff65a5`,
    `grid_draw.c:50`), and the storyboard's rims suit it.
  - At most 16 colours per part.
- **Alpha:** see "Source-art rules" in `PIPELINE.md`.
- **Conversion:** the implementation agent packs the parts, sets the timing and anchors, and wires the moment into
  `DrawPAForming`.

## References

| Path | Role |
|---|---|
| `poc/assets/generated/ASSET-002/v001/frame1.png`–`frame3.png` | The approved storyboard |
| `docs/asset-workflow/STYLE.md` | Rules and palette |
| `poc/assets/generated/ASSET-003/v002/` | Approved panels: the frame family to match |

## Acceptance criteria

- **Source art:**
  - the card reads as a card at 72×88 and at half size;
  - the 17 symbols can be told apart in grey and at 32×32;
  - the turning frames make a believable flip.
- **In game** (implementation agent): a clip of a Program Advance forming in a self-test battle (the `trio_pa`
  overworld test), old against new.

## Producer record

- Brief revision used: 2 (latest v003 P5 correction; approved P1–P4/P6 remain v002).
- Tool: image_gen.imagegen; exact prompt/reference list in the sample's PROMPT.md. Raw outputs retained under raw/ for reproducibility, not intended for runtime use.
- Programmatic processing: authorized by PIPELINE.md Source-art rules item 7. Exact config and operations are in processing.json / validation.json; shared helper: poc/assets/generated/_tools/prepare_samples.py. Run from repository root with the sample's processing.json. Python dependencies: Pillow and NumPy.
- Delivery scaling: native files plus exact 4× nearest-neighbor review PNGs and half-size previews. Raw generator dimensions were not native or exact integer multiples; cleanup reconstructs/packs the specified delivery geometry without claiming the raw art met that constraint.
- Visual review performed on native and 4× samples; no visible text, logos or existing characters. User review and implementation integration remain pending.
- References: approved storyboard frame1 plus approved red panels. Raw two-card source1635×962 RGBA.

### Delivery v001 — initial sample

- Native sample: poc/assets/generated/ASSET-008/v001/card_front.png and card_back.png, each72×88; card_front_back.png is152×88 with8px gap. Front/back silhouettes share identical alpha.
- Cleanup: explicit source crops, alpha threshold128, aspect-preserving nearest-neighbor fit72×86 with1px vertical padding, shared16-colour silver/dark/magenta palette; native front window flattened to exact40×40 at[16,16,56,56]. Blank16×16 code area at[52,68,68,84] stays inside the bottom-right rim (documented placement interpretation to preserve silhouette).
- Window centre (36,36), eight pixels above card centre (36,44). Type symbol/code lettering deliberately absent; engine supplies them. Back retains an original plain geometric pattern, no lettering.
- Checks: exact cell size, binary alpha, ≤16 colours per face, shared outline, blank window/tab areas and clear8px sheet gap passed. Native/4× visual review confirms a readable card silhouette and distinct front/back. Half-size preview provided.
- Review: card_front_back_review_4x.png (608×352).
- Limitations: no turning frames yet, hence flip playback untested. Code tab is reserved just inside the outer rim rather than flush to the absolute cell edges; implementation must use recorded coordinates or adjust its placement. P2..P6 and P1 turning frames wait for this sample's review.


### Delivery v002 — complete Program Advance source set

- Tool: image_gen.imagegen, six independent calls in parallel plus one corrective banner generation. Exact prompts/reference list: `poc/assets/generated/ASSET-008/v002/PROMPT.md`; raw files retained. Approved v001 front/back unchanged.
- Native sheets in `poc/assets/generated/ASSET-008/v002/`:
  - `card_flip.png`: 312×88, four72×88 cells in front / ¾ / edge / back order. The v002 front adds the optional1px code-tab outline; back reuses v001. Two generated turning views maintain height and compress width for a flip.
  - `trail.png`: 408×24, four96×24 cells, exact five-grey palette, right-aligned tips at native x94; right-end anchor (96,12). Short trails leave clear space at the left; no stretching used to disguise source proportions.
  - `emblem.png`: 944×128, seven128×128 cells: six arrival stages then static. `emblem_static.png` is128×128. Frames4–7 reserve64×64 dark symbol area at[32,32,96,96], silver outline immediately outside. Engine supplies symbol.
  - `burst.png`: 1288×208, six208×208 cells, exact five-grey palette. Flash expands to eight rays with clear centre, fragments into square sparks.
  - `type_symbols.png`: 672×32, seventeen32×32 cells in brief order (Normal through Dark), original distinct designs in the five greys. Generic subjects are custom artwork; no external game symbols used as references.
  - `banner.png`: 240×36, neutral silver/navy plus magenta. Flat blank interior, uniform nine-slice middle edges with10×10 corners; scalable width remains implementation-owned.
  - `shine.png`: 984×36, four240×36 overlay cells, streak progresses into successive quarter centres. Transparent except streaks.
- All sheets have8px fully transparent frame gaps and binary alpha. P2/P4/P5 use only the specified five-grey palette; other parts use the same16-colour neutral/magenta palette as the approved card. All have4× nearest-neighbour and half-size PNG review files; animation parts have diagnostic playback GIFs. `validation.json` records dimensions, SHA-256, actual palettes, gaps and alpha checks.
- Reproduction: `python poc/assets/generated/ASSET-008/v002/prepare.py` from repository root, Pillow and NumPy. `processing.json` contains every explicit crop, palette and stage configuration. Uses the existing shared helper read-only. Authorized cleanup thresholds alpha128, removes detached components smaller than32 source pixels, trims and aspect-preserving nearest-neighbour fits, packs native cells, normalizes emblem symbol reservation and banner nine-slice interior. Emblem/burst common scale retains staged expansion. Shine placements x18/78/138/198 in240px cells.
- Visual checks: distinct type silhouettes at native and half size; turning views read as the approved card, arrival flashes/badge and burst stages are distinguishable; empty emblem and banner spaces reserved for engine text/symbol. Source-art checks passed. This is delivered for review, not runtime accepted.
- Limitations: raw generator output did not land on requested integer-multiple canvas dimensions; delivery geometry was reconstructed without claiming generator-native grid compliance. Trail silhouettes occupy about55×20 inside96×24 cells to preserve source proportions. Emblem stage3 is a segmented nearly-full rim rather than a smaller uniform scaled badge. GIFs repeat for inspection; actual once/loop policy and game-frame timings remain engine-owned. Flip continuity, 120–420px banner stretches and the full `trio_pa` moment must be checked in the hi-bit renderer before acceptance.

### Delivery v003 — P5 Fighting/Ground revision only

- Brief revision2. Image generation redrew only Fighting as one clenched fist, and Ground as a cracked earth mound with a jagged split. Other artwork remains on the previously approved revisions.
- Native replacement sheet: `poc/assets/generated/ASSET-008/v003/type_symbols.png`,672×32; seventeen32×32 cells with8px clear gaps in the existing order. All15 other cells are **pixel-identical RGBA** to v002, including transparent RGB data; all gaps unchanged. Changed indices1 (Fighting) and4 (Ground).
- Individual replacement cells: `fighting.png` and `ground.png`, each32×32. Reviews: `type_symbols_review_4x.png` (2688×128) and `type_symbols_review_half.png` (336×16).
- Exact five-grey membership, binary alpha, geometry, clear gaps, nonempty sheet and per-cell equality checks passed; output/source hashes and every equality result in `validation.json`. Fist and fissured mound inspected at native,4× and half size; no text, logos or copied game symbols.
- Reproduction: `python poc/assets/generated/ASSET-008/v003/prepare.py` from repository root (Pillow/NumPy). Raw image, exact prompt/reference, crop/palette config and script retained in the same directory. Supported cleanup: threshold alpha128; trim explicit source crops; remove detached components below64 source pixels; aspect-preserving nearest-neighbour fit within28×28 in32×32 cell; quantize to exact five greys; replace two cells in a copy of v002.
- Limitation: raw generator canvas1774×887 did not meet requested integer scale; documented native cleanup supplies delivery geometry. Ground is a deliberately low mound silhouette (about28×15 inside its cell), distinct from Rock's taller boulder. These revised sources await review; in-game acceptance remains implementation-owned.

## Consolidated review

- Reviewed delivery: v001 (`card_front.png`, `card_back.png`)
- Reviewer: Claude (implementation agent), asked by Khaled to review
- Decision: **approved.** The stepped corners and magenta rim fit the panel family; the symbol window ([16,16,56,56])
  and code tab sit exactly where the brief puts them; front and back share the outline pixel for pixel; the back reads
  as a card back with no text.
- Optional: the code tab cuts into the bottom-right rim; keep the cut, but give the tab its own 1 px outline so it reads
  as a tab at half size.

### Review of v002

- Reviewed delivery: v002 (all seven sheets and the playback GIFs)
- Reviewer: Claude (implementation agent), asked by Khaled to review
- Approved: P1 card flip, P2 trail, P3 emblem, P4 burst, P6 banner and the shine. The emblem's arrival reads in order
  and the burst breaks up cleanly.
- P5 type symbols: 15 of 17 approved. Required changes (brief revision 2):
  1. **Fighting** reads as crossed bones, which says poison or danger. Use a clenched fist, or two fists meeting.
  2. **Ground** reads as a stacked sandwich. Use a mound or a cracked-earth slab with a split down it.
  Same 32×32 cell, five greys, same weight as the others. Redeliver `type_symbols.png` as v003 with only those two
  cells changed.
- Optional: the ¾ card frame is sheared sideways rather than turned. The game can make the turn by narrowing the front
  and back, so this frame may not be used; no redraw needed.
- Decision: revise P5 (two cells); everything else accepted for integration.

## Integration and acceptance (implementation agent)

- Accepted delivery:
- Integrated paths / patch / commit:
- Conversion details:
- In-game test command or scenario:
- Results and screenshot/log evidence:
- Remaining work:

## Change history

- 2026-10-14 — implementation agent (Claude) — created at revision 1 from ASSET-002 v001, ready for Codex.

- 2026-10-14 — Codex — generated initial sample in parallel with ASSET-005..008; performed authorized scripted cleanup/packing and file checks; published for review, acceptance pending.

- 2026-10-14 — implementation agent (Claude) — reviewed v001 for Khaled: P1 approved; turning frames and P2–P6 unblocked.

- 2026-10-14 — Codex — delivered v002 complete P1 turning and P2–P6 source sheets; original v001 preserved; source review and in-game acceptance pending.
- 2026-10-14 — implementation agent (Claude) — reviewed v002: P1–P4, P6 and the shine approved; Fighting and Ground symbols revised (revision 2).

- 2026-10-15 — Codex — delivered v003 P5 Fighting/Ground revision; verified other15 cells and gaps unchanged from v002; review pending.
