# ASSET-002 — The Program Advance moment (storyboard)

## Coordination

- State: delivered
- Priority: 2
- Assigned producer: Codex
- Current owner: Khaled
- Brief revision: 1
- Based on repository commit: 362b782
- Last update (UTC date): 2026-10-13
- Next action / blocker: Khaled reviews the three v001 storyboard frames on GitHub; not yet accepted.

## Purpose and visual brief

- **Intended use and player-facing purpose.** Khaled wants Program Advances (three chips combining into one big attack)
  to be a headline of the game: found earlier, rewarded, and spectacular. This storyboard decides how the moment looks.
  Today it's a 44-frame animation (`PA_ANIM`, `src/pkbn/grid_draw.c:1950`): three chips slide together at the top centre
  of the screen, then flash in the type's colour, and the PA name appears on the bottom line.
- **Deliverable type:** concept.
- **The storyboard:** 3 frames of the same battle, using ASSET-001's composition and placeholder fighters.
  1. **Converge.** Time stops: the field dims and desaturates. Three chip cards fly in from the left, centre and right,
     towards a point above the grid's centre line. Each card shows a type colour and a simple elemental glyph (fire,
     fire, fire).
  2. **Fuse.** The three cards slam together into one larger emblem with a radial burst and speed lines. A wide empty
     banner frame stretches across the screen under it, for the engine to write the PA's name in. Light from the emblem
     hits the panels.
  3. **Release.** The camera has punched in towards the player's placeholder fighter, about 1.25×. The fighter unleashes a
     huge fire beam down the middle row; the foe's panels are lit by it, with a cracked-panel shockwave.
- **Chip cards:** our own design.
  - A rounded rectangle with a type-coloured face, an elemental glyph, a code-letter corner (left blank), and a
    metallic rim.
  - It must not copy Battle Network's chip art or layout.
- **Style:** match approved ASSET-001 v003 (crisp hi-bit pixel art, dark outlines, restrained lighting and squared stepped inset panel corners).
- **Required elements:**
  - the dimmed field in frame 1;
  - the three cards;
  - the fused emblem with the empty name banner;
  - the camera punch-in and the beam in frame 3.
- **Elements to avoid:**
  - any Pokémon, Mega Man, Battle Network character or logo;
  - readable text (leave the banner empty);
  - copying Battle Network chip art.
- **Variant count:** 1 storyboard, with 3 frames.
- **Accepted creative freedom:** burst shapes, speed lines, the emblem's design, the banner's shape, and the beam's
  styling.

## Technical target (required for production assets)

Not applicable: this is a concept. Deliver 3 PNGs at **1056×704** each (4× the game canvas), named `frame1.png` to
`frame3.png`.

## References

| Path | Role | Notes |
|---|---|---|
| ASSET-001's approved v003 image | Style and composition | `poc/assets/generated/ASSET-001/v003/variant-a-stepped-corners.png`. |
| `docs/asset-workflow/references/hibit_battle_layout_528x352.png` | Geometry and HUD zones | Our own drawing. |
| `poc/screens/POC-6-mega-solar-beam.png` | How a Program Advance beam reads today | Project screenshot. It contains game sprites, so use it only for scale and timing; don't copy them. |

## Acceptance criteria

**Source-art review** (Khaled, then the implementation agent):

- It is clear at a glance which frame is converge, fuse and release.
- The name banner is empty and wide enough for 14 characters at the engine's font size, about 60% of the screen width.
- Nothing in it is recognisable from another game.

There is no in-game acceptance: this is a concept. It feeds the POC-22 Program Advance work and a later production
request.

## Producer record

- Brief revision used: 1, resolved to approved ASSET-001 v003 and STYLE.md.
- Assumptions / unresolved constraints: concept frames; exact requested dimensions and strict production pixel/palette rules are not met.
- Tool and generation/edit prompt: image_gen.imagegen; exact prompts in `poc/assets/generated/ASSET-002/v001/PROMPTS.md`.
- References actually supplied to the tool: approved ASSET-001 v003, project-authored layout guide, and prior generated storyboard frames for continuity. Game screenshot not supplied.

### Delivery v001

- Output directory: `poc/assets/generated/ASSET-002/v001/`.
  - `frame1.png`: CONVERGE — three separate fire cards approaching a common point over a dimmed field.
  - `frame2.png`: FUSE — one fire emblem with radial streaks and a wide empty name banner.
  - `frame3.png`: RELEASE — closer battle framing, a large fire beam through the middle row, warm panel illumination and a dark cracked-panel shockwave.
- Actual properties: three opaque RGB PNGs, each 1536×1024 (rather than requested 1056×704). Single full scene per image.
- Visual inspection: all three retain red/blue sides, stepped inset panel corners, original capsule fighters, fire motifs and empty HUD frames. Converge/fuse/release are distinct; no visible readable text or logos. Name-banner visible bounds are about 70% of frame width, exceeding the requested approximate 60%; exact font fitting is untested.
- File checks: PNG chunk CRCs and full pixel decode passed for every file; SHA-256 and properties saved in `validation.json`. Files copied directly from tool outputs without resizing or other programmatic image edits.
- Limitations: frame positions and silhouettes drift slightly between shots; release punch-in is illustrative rather than a verified exact 1.25× transform. Strict hi-bit pixel alignment, tone counts, and absence of all smooth lighting transitions are not certified. Ice crystals retain the concept's raised shape rather than the flat production-tile rule. These are storyboard source concepts, not production sheets or an implemented animation.
- No in-game test applies to this concept. Khaled reviews the storyboard; implementation agent creates the production requests and checks banner/font fit and camera behavior in the renderer later. Delivery is not acceptance.

## Consolidated review

- Reviewed delivery:
- Reviewer:
- Required changes:
- Optional preferences:
- Decision and reason:

## Integration and acceptance (implementation agent)

- Accepted delivery: not applicable (concept).
- Remaining work: a production request for the emblem, cards and burst, once the new renderer can load sprite sheets.

## Change history

- 2026-10-13 — implementation agent (Claude) — created at revision 1, ready.

- 2026-10-13 — Codex — resolved the style-reference selection to approved ASSET-001 v003 after Khaled’s review; storyboard content unchanged.

- 2026-10-13 — Codex — delivered three sequentially generated v001 storyboard concepts, file checks passed; published for GitHub review, approval pending.
