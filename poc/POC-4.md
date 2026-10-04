# POC-4 — chip folder & switching (Option 2)

**Patch:** `poc/patches/0005-POC-4-…patch`. Design + decisions: `docs/design/01-folder-and-switching.md`.

## Implemented (per decisions of 2026-10-04)
- **Folder from the party, 30 chips max** (BN6 size). Move copies by max PP: ≥30 → 3, ≥15 → 2, else 1.
  Over 30: the biggest stacks are trimmed first. Moves that don't work on the grid yet stay out.
- **Codes = move type** (shown as 3-letter type, e.g. `WAT`, `GRA`). BN rule: everything picked in one
  Custom must share a code.
- **One Switch chip per party Pokémon** ("lean"), carrying 2+ codes = the types of that Pokémon's own
  moves (topped up with the folder's most common other type if it only has one).
- **One wildcard Switch** (`*`): matches anything, lets you pick the target, nothing can be queued after it.
- **Owner rule:** a move chip is only usable while its owner is active. The Custom screen projects who
  will be active at each point of your queue, so `Switch>Treecko (NOR/GRA)` → `Absorb (GRA)` is legal.
  Unusable chips are greyed.
- **Hand of 5** (BN). Unpicked chips stay in hand; queued-but-unused chips are lost when you reopen Custom (BN).
  Used chips go to a discard pile that's reshuffled when the folder runs out (**our change**, BN never reshuffles).
- **Switch execution:** BN-style time-stop (everything freezes, screen dims, "GO! TREECKO!", ~0.8 s).
  Outgoing Pokémon loses its stat stages (Gen 3 `SwitchInClearSetData`), enemy debuffs stay.
- **Baton Pass** (move chip, `EFFECT_BATON_PASS`): pick a target, stat stages carry over; ends the chain.
- **Assist** (move chip, `EFFECT_ASSIST`): a random benched Pokémon pops in during a time-stop and uses one
  of its moves with *its own* stats; only Assist's PP is spent (Gen 3 Assist rule).
- **Fainting:** time stops and you choose the next Pokémon; lose only when nobody is left.
- **EXP split** between Pokémon that battled and are still standing (Gen 3 `Cmd_getexp` ÷ sent-in count),
  EVs to each. HP/PP written back for the whole party.
- Party pips under your HUD (white = active, grey = bench, red = fainted).
- Attacks keep a snapshot of their user, so a bomb thrown before a switch still uses the thrower's stats.

## Self-tests (2026-10-04)
| Party vs wild | Result | Seen |
|---|---|---|
| Mudkip (Water Gun/Baton Pass) + Treecko (Absorb/Assist) vs Zigzagoon L30 | WON, EXP 128 each | Switch>Treecko chained into Absorb; Assist called Mudkip's Water Gun |
| Mudkip + Treecko + Torchic (4/4/3 moves) vs Zigzagoon L18 | WON by Torchic | 30-chip folder; two faint → choose-next replacements; EXP only to the survivor |
| Torchic alone (default) | WON | 6-chip folder (Scratch×3, Growl×3) |
| Mudkip L12 alone (Protect/Swift/Water Gun/Sludge Bomb) vs Zigzagoon L22 | **LOST** (was a win in POC-2) | white-out path works; see finding 2 |
Screens: `poc/screens/POC-4-switching.png`, `POC-4-dead-draws.png`.

## Findings that need a design call
1. **Dead draws.** With 3 Pokémon, ~2/3 of each hand belongs to benched Pokémon and is greyed unless you
   also drew the right Switch chip (see `POC-4-dead-draws.png`: 1 usable chip out of 5). BN never has this
   because every chip belongs to the one Navi.
2. **Code rule bites with few types.** A one-Pokémon folder with 4 different move types can rarely chain
   more than 1 chip per turn, so it's weaker than POC-2 (where the hand ignored codes).
3. Baton Pass / wildcard picks were never made by the autopilot in these runs (it prefers the first legal
   chip) — the code paths for the picker were exercised through faint replacement.
