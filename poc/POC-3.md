# POC-3 — bomb blast fix, status moves

**Patch:** `poc/patches/0004-POC-3-…patch`.

- **Bomb blast is now a plus (+):** landing panel + 4 orthogonal neighbours, no diagonals.
- **Status moves (new shape STATUS):** every Gen 3 stat-stage move — the `EFFECT_*_UP/_DOWN(_2)`
  families (Growl, Leer, Tail Whip, String Shot, Howl, Harden, Swords Dance, Screech, ...).
  They always land: no aiming, no lock-on, and they go through Barrier and i-frames (our rule —
  in Gen 3 Protect would block Growl). Stages clamp at ±6 like Gen 3 ("won't go lower").
  - Attack/Defense/Sp. stages feed straight into Emerald's damage formula (`APPLY_STAT_MOD`).
  - **Speed stage drives tempo:** it scales your Custom gauge fill and the enemy's attack rate.
  - Accuracy/Evasion moves (Sand-Attack, Double Team, ...) work but have no grid effect yet.
  - HUD shows stages next to HP (e.g. `A-1 D-1`, blue = up, red = down).
- Enemy AI uses status moves but stops stacking at ±2 and skips Accuracy/Evasion ones.
- Still not on the grid: status-condition moves (Thunder Wave, Sleep Powder, Poison Powder, ...).

Self-tests: Torchic vs Zigzagoon (Growl lands, Attack -1); Mudkip (Growl/Tail Whip/Sludge Bomb/
Water Gun) vs Zigzagoon (Growl/Tail Whip/Tackle/Aerial Ace) — stages applied both ways, plus-shaped
bomb landed. Regression runs from POC-2 unchanged.
