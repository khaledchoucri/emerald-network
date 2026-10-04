# POC-2 — new move shapes: Bomb, Lock-on, Barrier

**Patch:** `poc/patches/0003-POC-2-…patch` (on top of 0001 + 0002; `scripts/setup_host.sh` applies all).

## What changed
1. **Attack pipeline.** Every move now goes StartAttack → wind-up → impact. Wind-up is 0 for the
   player's Cannon/Sword/Spreader (instant, like BN chips), a telegraph for enemy ones, flight time
   for bombs, and tracking time for lock-ons. Several attacks can be in the air at once.
2. **Move → shape rules moved to `src/pkbn/move_shapes.c`** (one place to edit).
3. Three new shapes:

| Shape | Which Emerald moves (rule) | Behaviour | Grounding |
|---|---|---|---|
| **BOMB** | curated "thrown" list: Rock Throw, Egg Bomb, Barrage, Sludge Bomb, Octazooka, Shadow Ball, Weather Ball, Rock Tomb | lobbed 3 panels ahead in your row, 3x3 blast on landing; landing zone shows grey (yours) / flashing orange (enemy's) while in the air — dodgeable | BN6 bomb family 0x12 (MiniBomb). Thrower is busy 21 frames = BN6 bomb routine length (`asm31.s`, `sub_80EB644` ends at frame 0x15). 3-panel range per your spec (not yet confirmed in BN6 asm). Gen 3 has no bomb flag → list is our choice |
| **LOCK-ON** | `effect == EFFECT_ALWAYS_HIT` (Swift, Faint Attack, Shadow Punch, Aerial Ace, Magical Leaf, Shock Wave) — beats contact | red crosshair tracks the target for 40 frames, then hits wherever it is; can't be dodged, only blocked by Barrier | Emerald `gBattleMoves[].effect`. Behaviour per your MachGun spec (BN6 MachGun = family 0x29; its routine `sub_80ECF2E` not yet read) |
| **BARRIER** | `effect == EFFECT_PROTECT` (Protect, Detect) | shield absorbs the next hit; only stops moves Protect would stop (`FLAG_PROTECT_AFFECTED`) + Buster shots. Consecutive uses get less reliable: 100% / 50% / 25% / 12.5% | BN6 Barrier chip (family 0x15 sub 4, param 1). Odds and reset rule copied from Gen 3 `Cmd_setprotectlike` + `sProtectSuccessRates` (`battle_script_commands.c:6523`, `:719`) |

Enemy AI: uses all three (won't re-raise a barrier it already has; lines up 3 panels away to bomb).

## Self-test results (2026-10-04, autopilot, frame numbers in log)
| Player vs wild (moves) | Result | Seen in log |
|---|---|---|
| Mudkip L12 (Protect/Swift/Water Gun/Sludge Bomb) vs Zigzagoon L22 (Protect/Swift/Rock Throw/Tackle) | WON 11/35 HP | barrier raised & absorbed enemy move; Swift lock-on hit both ways (enemy: 24 dmg); both sides' bombs landed |
| Mudkip L14 (Water Gun/Sludge Bomb) vs Zigzagoon L20 (Protect/Swift) | WON 15/40 HP | enemy barrier absorbed a Buster shot |
| Treecko L10 (Absorb/Quick Attack/Protect/Leer) vs Poochyena L9 (Tackle/Bite/Protect/Swift) | WON 29/29 HP | Leer correctly not usable (status) |
| Torchic L7 vs Zigzagoon L4 (default) | WON 18/24 HP | regression check |
Screens: `poc/screens/POC-2-selftest.png` (barrier ring, bomb arc + landing shadow, "BARRIER BLOCKED IT!", enemy crosshair).

Run your own: `PKBN_SELFTEST="species:level:move/move/move/move,species:level:..." ./pokeemerald64`
(`PKBN_DUMP_DIR=dir PKBN_DUMP_EVERY=3` saves frames).

## Play-test checklist
- [ ] Bombs: readable arc/landing zone; dodging enemy bombs feels fair.
- [ ] Lock-on: crosshair visible; unavoidable damage feels OK (or should it be dodgeable at the last moment?).
- [ ] Barrier: clear when it's up / when it blocks / when it fails.

## Open design questions
- Should the player's Cannon/Sword also have a short wind-up, or stay instant like BN?
- Lock-on can't be dodged — keep, or give a dodge window in the last few frames?
- Barrier lasts until hit (BN) — add a timeout?
