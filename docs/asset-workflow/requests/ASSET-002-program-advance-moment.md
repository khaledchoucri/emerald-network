# ASSET-002 — The Program Advance moment (storyboard)

## Coordination

- State: ready
- Priority: 2
- Assigned producer: Codex
- Current owner: Codex
- Brief revision: 1
- Based on repository commit: 362b782
- Last update (UTC date): 2026-10-13
- Next action / blocker: Codex generates the 3-frame storyboard after ASSET-001's delivery. Use the same style as
  ASSET-001 variant B unless ASSET-001's review picks another.

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
- **Style:** match ASSET-001's chosen look (hi-bit pixel art, dark outlines, additive glow on light sources).
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
| ASSET-001's delivered variant B (or the variant its review picks) | Style and composition | Under `poc/assets/generated/ASSET-001/`. |
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

- Brief revision used:
- Assumptions / unresolved constraints:
- Tool and generation/edit prompt:
- References actually supplied to the tool:

### Delivery v001

- Exact output paths (repository-relative), or attachment plus transfer status:
- Actual file format, dimensions, transparency, and frame layout:
- Visual inspection performed and findings:
- Technical checks performed and results:
- Unchecked requirements / known limitations:
- Conversion or integration still needed, with owner:

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
