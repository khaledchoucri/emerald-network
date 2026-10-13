# ASSET-004 — Original fire effects (first effect family)

## Coordination

- State: delivered
- Priority: 4
- Assigned producer: Codex
- Current owner: Khaled / implementation agent
- Brief revision: 3
- Based on repository commit: 362b782
- Last update (UTC date): 2026-10-13
- Next action / blocker: review v001 FIREBALL source sample, then implementation agent packs/aligned frames and tests the loop. Other four effects remain gated on sample review.

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

- Brief revision used: 3
- Assumptions / unresolved constraints: choose the 3-frame option, 2 game frames per frame; source output not native packed dimensions. Loop and anchors require implementation validation.
- Tool and generation/edit prompt: image_gen.imagegen; exact prompt in `poc/assets/generated/ASSET-004/v001/PROMPT.md`.
- References actually supplied to the tool: approved ASSET-001 v003 only; no game screenshot/extracted effect sprite.

### Delivery v001

- File: `poc/assets/generated/ASSET-004/v001/fireball_source.png`, available on GitHub for review.
- Actual format: 1971×798 RGBA PNG, three visually separate right-facing fireball phases in one row on transparent canvas. This is source art; requested packed output is 252×64, three 84×64 cells, held 2 game frames each.
- Visual review: white-yellow round cores, yellow/orange bodies, red-orange rear lobes, square sparks and crisp pixel clusters; faces right, no text/logo/background or other scene art. The three silhouettes/spacing differ slightly; shared anchor alignment and a seamless loop are not established.
- File checks: all PNG chunk CRCs and full decode passed; transparent pixels present, with partial-alpha edges/residue remaining. Properties/counts and SHA-256 in `validation.json`.
- Required implementation work: extract three sprites, clean alpha and stray edge pixels, snap/quantize according to STYLE.md, align identical projectile anchors (6 pixels left of each ball's back edge at vertical center), fit all content within 84×64 cells, pack one 252×64 row, play sequence 0→1→2→0 at 2 game frames per frame, inspect the final→first seam, then check native-size readability and renderer integration. No animation preview/playback or in-game check has been executed.
- Sample not yet approved. FIRE_BURST, FLAME_JET, FIRE_TALL, FIRE_PANEL are not generated; wait for FIREBALL review before proceeding.

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

- 2026-10-13 — implementation agent (Claude) — revision 3: STYLE.md written from ASSET-001 v003; ready for Codex.

- 2026-10-13 — Codex — delivered v001 three-phase FIREBALL source sample; loop/anchor/native packaging and review pending.
