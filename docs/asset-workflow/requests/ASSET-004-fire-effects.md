# ASSET-004 — Original fire effects (first effect family)

## Coordination

- State: draft
- Priority: 4
- Assigned producer: Codex
- Current owner: implementation agent
- Brief revision: 1
- Based on repository commit: 362b782
- Last update (UTC date): 2026-10-13
- Next action / blocker:
  - Wait for ASSET-001's review and `STYLE.md`.
  - The implementation agent then measures today's effect frames (their bounds, frame counts and timings, from
    `tools/gen_bn6_gfx.py --preview`) and fills in the exact cell sizes below before marking this ready.

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
- **Cell sizes, frame counts and timing:** to be filled in by the implementation agent from the measured BN6 frames,
  doubled. Proposal only, not confirmed: FIREBALL 64×64, 6 frames at 4 game frames each, looping.
- **Anchor:** the centre of the cell's bottom edge for panel effects; the cell centre for projectiles.
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
