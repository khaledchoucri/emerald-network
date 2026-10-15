# ASSET-011 — Place hazards (tide, rocks, snares, puddles)

## Coordination

- State: ready
- Priority: 11
- Assigned producer: Codex
- Current owner: Codex
- Brief revision: 1
- Based on repository commit: cd6822b
- Last update (UTC date): 2026-10-15
- Next action / blocker: Codex delivers the sample: R1, the fallen rock with its damage states. Then the rest.

## Purpose and visual brief

- **Intended use.** POC-27 gave four kinds of place their own hazard on the grid (`poc/POC-27.md`). Today they're drawn
  in code, or with a BN6 boulder. These are the pictures for them.
- **How the game uses them:**
  - Overlays sit on top of a panel (88×52 at 2×, the panel face of ASSET-003).
  - The rock stands on a panel like a fighter, its base at the panel's centre.
  - All of them are drawn over the approved panels and under the Pokémon.
- **Style:** `STYLE.md`. These are Net hazards, so they're digital rather than natural. The tide is data washing over
  the panels, the rock a heavy block of data, the snare a tangle of wire-like vines. Hard pixels, binary alpha.
- **Deliverable type:** production source, as sprite sheets.

### The parts

| Part | Used for (code: `src/pkbn/grid_draw.c` `DrawPlace`) | What it should show |
|---|---|---|
| T1 Tide warning | The back columns, the second before the tide washes over | A panel overlay: light glints and a thin wave line creeping over the face. 2 frames, holds 8/8, loop. Mostly transparent, so the panel stays readable |
| T2 Tide wash | The back columns while they carry you (the current panels of ASSET-003 are under it) | A panel overlay: bands of foam running toward the middle of the field, drawn moving **right** (the game mirrors it for the enemy side). 4 frames, holds 3/3/3/3, loop |
| R1 Fallen rock | A rock that fell in a cave and blocks the panel; it takes 3 buster shots | A heavy block, about 56×60 at 2×, base at the bottom centre. 3 states: whole, cracked, badly cracked. Then a 4-frame crumble (holds 3/3/3/3) for when it breaks |
| S1 Snare | A hidden snare springing on whoever steps on it (shown 1.5 s) | A ring of wire-like vines closing around the feet: about 72×32 at 2×, base centre. 3 frames: springs up, tightens, holds. Holds 3/3, then the last frame stays |
| P1 Puddle | Puddle panels in the rain | A panel overlay: a shallow pool covering most of the face, with a highlight. 2 frames for the light shifting, holds 16/16, loop |

- **Colour:**
  - T1, T2 and P1 use the Net sky's cyans and blues (`STYLE.md`).
  - The rock is grey stone in the Rock ramp of ASSET-006 (`type_ramps.json`).
  - The snare is dark green in the Grass ramp.
- **Elements to avoid:** text, symbols that read as letters, any creature, anything copied from Battle Network's or
  Pokémon's sprites.
- **Variants:** 1. Sample first: R1 (its three states and the crumble). Then T1, T2, S1 and P1.

## Technical target

- **Integration:** `tools/pack_hibit.py` packs them as still pictures (like ASSET-007/009) and `DrawPlace` draws them.
  Without them the code-drawn versions stay.
- **Sizes** are at the hi-bit scale (2×). Overlays are exactly 88×52.
- **Sheet layout:** frames left to right, 8 px transparent gaps, one PNG per part; see "Source-art rules" in
  `PIPELINE.md`.
- **Palette:** at most 16 colours per part.

## References

| Path | Role |
|---|---|
| `docs/asset-workflow/STYLE.md` | Rules |
| `poc/assets/generated/ASSET-003/v002/panels_red_source.png`, `panels_blue_source.png` | The panels these sit on |
| `poc/assets/generated/ASSET-006/v002/type_ramps.json` | Rock and Grass ramps |
| `poc/screens/POC-27.png` | Today's code-drawn versions in battle |

## Acceptance criteria

- **Overlays:** the panel and its type still read through T1, T2 and P1.
- **Rock:** reads as an obstacle at half size, and the three states can be told apart.
- **Snare:** reads at the feet of a small Pokémon (Torchic) and of a big one (Wailord).
- **In game** (implementation agent): frame dumps of each place's self-test (`PKBN_TEST_PLACE`).

## Producer record

- Brief revision used:
- Assumptions / unresolved constraints:
- Tool and generation/edit prompt:
- References actually supplied to the tool:

## Consolidated review

- Reviewed delivery:
- Reviewer:
- Required changes:
- Optional preferences:
- Decision and reason:

## Integration and acceptance (implementation agent)

- Packed:
- In-game check:
- Decision:

## Change history

- 2026-10-15 — implementation agent (Claude) — created at revision 1 for POC-27's places, ready for Codex.
