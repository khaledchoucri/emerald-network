# POC-21: Items, TMs and the NaviCust

**Patches:** these go on top of 0001–0085.

- `poc/patches/0086-POC-21a-…` to `0088-…`.
- Applying 0001–0088 onto the pin was checked in a clean worktree.

This is the hardening round you asked for: "Items from pokemon should not be able to be used together with the navicust
as one essentially should replace the other ... finding a TM should give you chips instead." It follows your picks on
the "POC-21" and "POC-21b" pages.

Values marked TUNE are our own numbers. Unless a line cites code, a rule is our own design.

## 21a: One system for each job

**Held items do nothing in grid battles.** This applies to yours and to the foe's: `MonToBattleMon` clears the item for
the grid. Emerald's own battles keep them (Wally's demo, the Safari Zone, the Battle Frontier, link battles).

**An item with a program becomes the program.** It doesn't matter how you get it: found, hidden, given, bought, or
held by a Pokémon you catch. The message says so: "It became the Leftovrs program!"

- The 27 items that already had a program (Leftovers, Quick Claw, Charcoal, Choice Band, ...).
- Four new ones, from your note "everstone and soothe bell probably can be turned into programs":

| Item | Program | What it does |
|---|---|---|
| Everstone | Everstone | The Pokémon doesn't evolve; in the Day Care it passes on its nature (Emerald's Everstone rules). |
| Soothe Bell | SoothBel | Friendship gains x1.5 (Emerald's Soothe Bell rule). |
| Smoke Ball | SmokeBal | Always escape wild battles. |
| Cleanse Tag | SneakRun | No encounters with weak wild Pokémon (the existing program, from BN6's SneakRun). |

- Everstone, SoothBel and SmokeBal work in Emerald's own code too (evolution, friendship, the Day Care).
- At the Battle Frontier, held items stay items, since the Frontier's battles are Emerald's own.

**Battle-only items can be held only at the Battle Frontier.** This covers berries, White and Mental Herb, Light Ball,
Thick Club, Lucky Punch, Stick, Metal Powder, Soul Dew and the Deep Sea items. Elsewhere, GIVE says "The ORAN BERRY
can't be held here."

**A TM is 3 chips.** A TM never reaches the bag: "It became 3 THUNDER CHIPS!" The copies are spread over the move's
codes (TUNE). An HM stays an item, for its field move, and also gives 3 chips.

**The Move Relearner** also lists every move you own as a chip that the Pokémon can learn, for the same Heart Scale
price, up to 60 moves.

**Exp. Share is a key item you turn ON or OFF.** It starts ON.

- In Gen 3 it was a held item that took half the EXP away from the fighters
  (`src/battle_script_commands.c:3306-3318` at the pin).
- Ours follows the newer games, as your note asked: the Pokémon that fought split the full EXP as in Gen 3, and every
  other Pokémon that can fight gets half a fighter's share (TUNE). Only the fighters gain EVs.

**Old saves convert on load.** TMs, program items and the Exp. Share are converted wherever they are: the bag, the PC's
item storage, and items held by the party and the boxes. The log line says how many were converted.

## 21b: Vitamins and berries

- **Vitamins become their programs**, as you picked: HP Up, Protein, Iron, Calcium, Zinc and Carbos. They do so even at
  the Battle Frontier, which stocks them (`data/maps/BattleFrontier_ExchangeServiceCorner/scripts.inc`, `data/maps/BattleFrontier_Mart/scripts.inc`), so vitamin EVs never stack with programs. EVs now come only from
  battles, and a held Macho Brace still doubles them.
- **Berries have no grid-battle use** (your pick). Pokéblocks still use them. If you keep Chip Forge on the vision
  page, it gives berries a new job.

## Verification

- **Regressions:** all 33 self-test battles end exactly as in POC-20.
- **owtests:** 44 of 44 pass.
- **New owtests:**
  - `gift_items`: a TM becomes chips; Leftovers become the program.
  - `migrate_items`: an old save's TM, Leftovers, Exp. Share and held item convert on load.
  - `vitamin_frontier`: Protein becomes its program at the Battle Frontier.
  - `bt exp_share`: a non-fighter gets half a fighter's EXP (21 against 42).
- **New test switches:**
  - `PKBN_TEST_EXP_SHARE=0|1`: the Exp. Share's state.
  - `PKBN_TEST_MIGRATE`: run the conversion on the starting save.
  - `PKBN_OWTEST_HELD=<item>`: the lead Pokémon holds this item.
  - owtest command `O<item>`: an NPC gives the item, through Emerald's own obtain-item script.

## Open / TUNE

- 3 chips per TM, half a share for non-fighters, EVs only for fighters.
- Not yet tested by hand:
  - the GIVE refusal text;
  - the Relearner's chip moves on a real save;
  - the Everstone, SoothBel and SmokeBal programs in play;
  - the message when a caught Pokémon's item converts.
