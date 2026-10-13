# ASSET-006 — Impacts (tintable) and the type colour ramps

## Coordination

- State: ready
- Priority: 6
- Assigned producer: Codex
- Current owner: Codex
- Brief revision: 1
- Based on repository commit: 1eb0e3d
- Last update (UTC date): 2026-10-14
- Next action / blocker: Codex delivers the sample: HIT (part A) and the ramp sheet (part C). After review, the rest.

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

- Accepted delivery:
- Integrated paths / patch / commit:
- Conversion details:
- In-game test command or scenario:
- Results and screenshot/log evidence:
- Remaining work:

## Change history

- 2026-10-14 — implementation agent (Claude) — created at revision 1, ready for Codex.
