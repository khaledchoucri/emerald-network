# Battle style guide (hi-bit)

**Source.** Khaled approved ASSET-001 v003, `poc/assets/generated/ASSET-001/v003/variant-a-stepped-corners.png`, as the
style reference for every battle asset. This guide turns that image into rules a production asset can be checked
against. The image is a concept: when it and this guide disagree, this guide wins.

**Scale.** The concept is 1536×1024. The hi-bit battle canvas is 528×352 (2× the game's 264×176), so one hi-bit pixel
is about 2.9 concept pixels. Every size below is in **hi-bit pixels**, the pixels you deliver.

## Rendering rules

1. **Pixel art on the hi-bit grid.** Hard pixel edges, no anti-aliasing, no soft brushes, no blur. A diagonal is a
   pixel staircase.
2. **Dark outline, 1 px,** around every object and every panel part. Use near-black navy `#0b0a14`, or the material's
   darkest tone, never pure black on a lit edge.
3. **Flat shading: 2–3 tones per material, plus one highlight tone** for edges that face the light (top and left). No
   smooth gradients. The one exception is the panel glass sheen (below).
4. **Light comes from the top left** for shading.
5. **Glow only on things that emit light** (fire, impacts, visors). Draw it as a hard-edged ring 1–2 px wide in the
   lighter tones, not a blur.
6. **Don't bake in light from other objects.** In the concept, the fireball lights the nearby panels. In production the
   engine does that (modern light), so tiles and sprites are delivered in neutral light.
7. **Readable at 1×.** Check every asset at its delivered size and at half size. If a panel type or an effect can't be
   told apart there, it fails.

## Palette

Sampled from v003 (hex). Shades in between are allowed if they keep the 2–3 tone rule.

| Material | Outline / darkest | Shade | Base | Light | Highlight |
|---|---|---|---|---|---|
| Player frame (red) | `#200105` | `#74011c` | `#fb2c2d` | `#fb5430` | — |
| Foe frame (blue) | `#02021b` | `#000cad` | `#035bfa` | `#0597fb` | — |
| Panel face (silver glass) | `#151626` | `#536787` | `#667b99` | `#9db0ca` | `#edf2fa` |
| Net sky | `#040c1c` (top) | `#071833` | `#0b2550` | `#103473` (horizon), `#083e86`–`#1460b0` (grid lines) | `#3ecbfd` (motes) |
| Front edge (lip) | `#101b3a` | `#283653` | `#667a99` | `#8e9fb6` | — |
| Fire | `#9d220f` | `#dc4b24` | `#fc871f` | `#fef237` | `#fefdf2` (core) |
| Grass | `#073919` | `#01501d` | `#15a31e` | `#51cb1c` | `#74ee1b` |
| Ice | `#0a3ea5` | `#0186fa` | `#3ecbfd` | `#89e1fa` | `#e0f9fd` |
| Cracked (metal) | `#170a1a` | `#52324a` | `#6c4254` | `#754856` | — |

## The panel

Built from the outside in, in a 88×52 cell (ASSET-003):

1. **Outline:** 1 px, dark.
2. **Frame:** about 4 px in the side's colour (red or blue base), its outer edge 1 px lighter on the top and left. A
   1–2 px shade band runs on the inside of the frame.
3. **Inner outline:** 1 px, dark, around the face.
4. **Stepped corners.** At each of the face's four corners, the inner outline steps inward once, a square notch about
   4×4 px. No round corners, no diagonal chamfers, no bolts or rivets (ASSET-001 review: "A's crisp look with C's
   squared inset corners").
5. **Face rim:** a 1–2 px highlight inside the inner outline on the top and left (`#bdcbdd` to `#edf2fa`), shade on the
   bottom and right.
6. **Glass sheen:** two flat diagonal bands one tone lighter than the face, about 30° from horizontal, 3–5 px wide, in
   the top-left half. They're flat bands, not a gradient.
7. **Front edge** (the bottom row only): the lip palette, flat, with a 1 px highlight line on its top.

**Panel types** keep the frame and the stepped corners, and only the face changes:

- **Cracked:** dark fissure lines in the cracked palette. **No glow:** in the concept the cracks glow orange and read as
  lava, which is its own panel type.
- **Grass:** blades fill the face. The tips stay inside the face.
- **Ice:** a frosted face with faceted crystals drawn flat on it. The tall crystals in the concept are concept-only
  because a tile can't extend past its cell.
- **Lava:** the glowing one, with orange-to-yellow cracks on dark rock (fire palette).
- **Poison, holy and roads:** follow the same tone rules. See ASSET-003 for what each must show.

## Effects

- **Fire** follows the concept's fireball:
  - a white-yellow core, a yellow then orange body, and a red-orange trail;
  - square spark particles 1–2 px, in 2–3 sizes;
  - impacts are a hard-edged starburst with 6–8 rays.
- **Other types:** take their ramp from the type's colour in the same 5-tone structure, with the same particle sizes.
- **Facing:** draw effects facing right (the player's direction); the engine mirrors them.

## Not taken from the concept

- **Its dimensions and grid placement:** they're approximate. The layout guide and each request's technical target
  decide sizes.
- **The placeholder capsule fighters:** they stand in for Pokémon in concept frames only.
- **The baked fireball light, the glowing cracks and the tall ice crystals** (see above).

*2026-10-14: the Net sky row was corrected. It listed `#061833` and `#071833`, which are one step apart and read as one colour (ASSET-005 v001 review).*
