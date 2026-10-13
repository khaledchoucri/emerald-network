# ASSET-004 — Original fire effects (first effect family)

## Coordination

- State: draft
- Priority: 4
- Assigned producer: Codex
- Current owner: implementation agent
- Brief revision: 2
- Based on repository commit: 362b782
- Last update (UTC date): 2026-10-13
- Next action / blocker: the sizes, frame counts and timings are now filled in (revision 2). It still waits for ASSET-001's
  review and `STYLE.md`; the implementation agent marks it ready then.

## Purpose and visual brief

- **Intended use.** Five fire effects that today are Battle Network 6 sprites, extracted at build time
  (`tools/fx_curated.py` lines 22-26; drawn in `src/pkbn/grid_vfx.c`). Original replacements:
  - fit the hi-bit style;
  - remove our dependence on extracted Capcom art for these effects;
  - are the template for the other 54 effects, type by type.
- **Deliverable type:** production source, as animated sprite sheets.

| Effect | Used for (code) | What it should show |
|---|---|---|
| FIREBALL | Fire BALL attacks and the chip preview (`grid_vfx.c:1095`, `:1202`) | A spinning ball of fire travelling sideways; loops |
| FIRE_BURST | The Fire type's impact (`grid_vfx.c:157`) | A short radial burst of flame on a panel; plays once |
| FLAME_JET | Fire LINE3/CONE attacks (`grid_vfx.c:219`, `:1324`) | A horizontal jet of flame from the attacker's side across 2 panels; loops while it lasts |
| FIRE_TALL | FIREHIT attacks and Fire areas (`grid_vfx.c:698`, `:1337`) | A column of flame rising from a panel, about 1.5 panels tall; loops |
| FIRE_PANEL | Will-O-Wisp and burning panels (`grid_vfx.c:383`, `:1283`) | Small flames licking across a panel's face; loops |

- **Style:** follow `STYLE.md` (from ASSET-001). Hard pixel edges. Light-emitting parts in a separate glow layer, if
  `STYLE.md` says so.
- **Elements to avoid:** copying Battle Network's or Pokémon's effect sprites, and any text.
- **Variant count:** 1, after a reviewed sample. First deliver FIREBALL only; after its review, the other four.

## Technical target (required for production assets)

- **Integration:** the hi-bit renderer's effect atlas (roadmap round 3). The code that plays effects is `Fx`/`PlayLoop`
  in `src/pkbn/grid_vfx.c`.
- **Cell sizes, frame counts and timing.** Measured from today's frames (`sBn6Frames` and the animation table that
  `tools/gen_bn6_gfx.py` generates into `include/pkbn/bn6_gfx_data.h`), then doubled and rounded up to even numbers.
  Times are in game frames at 60 per second.

| Effect | Today: frames, sizes (1×), time per frame, loop | Cell at 2× | Frames to deliver |
|---|---|---|---|
| FIREBALL | 3: 40×27, 42×32, 30×32; 2 each; loops | 84×64 | 3 (or 6 at 1 frame each) |
| FIRE_BURST | 4: 24×16, 29×24, 31×39, 34×53, growing; 6 each; plays once | 72×108 | 4 |
| FLAME_JET | 3: 116×60, 116×61, 113×61; 2 each; loops | 232×124 | 3 (or 6) |
| FIRE_TALL | 3: 32×55, 35×56, 39×57; 2 each; loops | 80×116 | 3 (or 6) |
| FIRE_PANEL | 3: 32×47, 32×52, 32×54; 2 each; loops | 64×108 | 3 (or 6) |

  Doubling the frame count, with each frame held half as long, is welcome for smoother loops. Keep the art inside the
  cell; empty space is fine.
- **Anchor.** The point the engine draws at, in the cell, at 2×:
  - FIRE_BURST and FIRE_PANEL: horizontally centred; the flames' base is 16 px above the cell's bottom edge.
  - FIRE_TALL: horizontally centred; the base is 10 px above the bottom edge.
  - FLAME_JET: drawn facing right, the anchor is where the jet starts: 46 px from the cell's left edge and 24 px above
    its bottom edge. The jet extends to the right; the engine mirrors it for the foe.
  - FIREBALL: the anchor is just behind the ball, 6 px left of its back edge, at its vertical centre. The ball travels to
    the right.
  - The implementation agent fine-tunes the offsets in code. These are close enough to draw to.
- **Sheet layout:** frames left to right in one row per effect, one PNG per effect.
- **Format:** PNG with alpha (transparent background).
- **Palette:** per `STYLE.md`; quantized by the implementation agent.
- **Facing:** drawn facing right (the player's attack direction); the engine mirrors it for the foe.

## References

| Path | Role |
|---|---|
| ASSET-001's accepted variant | Style; its fireball is the starting point |
| `poc/screens/POC-5-kinds.png` | Scale of effects on the grid today (contains extracted game art: scale only, don't copy) |

## Acceptance criteria

- **Source art:** each effect reads as fire at native size; loops have no visible pop; the facing is correct.
- **In game** (implementation agent): side-by-side clips of the old and new effect in the same self-test battle
  (`PKBN_SELFTEST`), with frame dumps.

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

- Accepted delivery:
- Integrated paths / patch / commit:
- Conversion details:
- In-game test command or scenario:
- Results and screenshot/log evidence:
- Remaining work:

## Change history

- 2026-10-13 — implementation agent (Claude) — created at revision 1 as a draft; it waits on ASSET-001 and frame
  measurements.
- 2026-10-13 — implementation agent (Claude) — revision 2: measured sizes, frame counts, timings and anchors filled in,
  answering Codex. Still a draft until `STYLE.md` exists.
