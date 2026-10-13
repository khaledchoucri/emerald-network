# ASSET-008 — Program Advance moment: production art

## Coordination

- State: delivered
- Priority: 8
- Assigned producer: Codex
- Current owner: Khaled / implementation agent
- Brief revision: 1
- Based on repository commit: 1eb0e3d
- Last update (UTC date): 2026-10-14
- Next action / blocker: Review P1 front/back; turning frames and P2..P6 remain gated on sample approval. Renderer/flip tests follow later.

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

- Brief revision used: 1.
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

## Consolidated review

- Reviewed delivery:
- Reviewer:
- Required changes:
- Optional preferences:
- Decision and reason:

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
