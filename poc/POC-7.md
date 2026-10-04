# POC-7 — Catching, trainer battles, EXP / level-ups / new moves / evolution

Patch: `poc/patches/0009-POC-7-catching-trainer-battles-EXP-level-up-move-lea.patch` (on top of 0001–0008).
New files in the host: `src/pkbn/grid_catch.c` and `src/pkbn/post_battle.c`.
Host edits:
- `battle_main.c`: `CreateNPCTrainerParty` is no longer static.
- `battle_setup.c`: single trainer battles are routed to the grid.
- `platform/sdl2.c`: `PKBN_AUTO_PRESS` test hook.

## Catching (Poké Balls from the Custom screen)
- **Where:** the last Custom row is a BALL slot. L/R (left/right) picks among the balls in your bag. Pressing A on it
  throws instead of using chips, like choosing BAG in Emerald, so it only works with no chips queued. Time stops for
  the throw: the ball flies, the Pokémon is drawn in, then it shakes 0–3 times.
- **Odds:** Emerald's own code, `Cmd_handleballthrow` (battle_script_commands.c:9925):
  - The base is catch rate × ball bonus × (3·maxHP − 2·HP) / 3·maxHP.
  - Sleep and freeze multiply it by 2; poison, burn and paralysis by 1.5.
  - Ball bonuses: Ultra 2×, Great 1.5×, Net 3× on Water or Bug, Dive 3.5× underwater, Nest by level, Repeat 3× if
    already caught, Timer +1 per turn (one turn = one Custom gauge). The Master Ball always catches.
  - The shake checks are Random() < 1048560 / Sqrt(Sqrt(16711680 / odds)), up to 4 times.
- **The messages:** Emerald's four break-free texts, and "Gotcha!" with the caught music.
- **After a catch:**
  - The Pokédex caught flag is set, with "…data was added to the POKéDEX.".
  - You're asked about a nickname, and Emerald's naming screen opens if you say yes.
  - `GiveMonToPlayer` puts it in your party, or in someone's / Lanette's PC when the party is full.
  - It keeps its battle HP, status and ball, and the catch counts toward the captures stat.
- **Not shown:** Emerald's Pokédex entry page that appears after a first catch.

## Trainer battles
- **Which ones:** only single battles with `gBattleTypeFlags == BATTLE_TYPE_TRAINER`. Double-battle trainers, two
  approaching trainers, the Battle Frontier, Trainer Hill, secret bases, and scripted or legendary battles stay vanilla.
- **Their party:** built by Emerald's `CreateNPCTrainerParty`. Each Pokémon is marked as seen in the Pokédex when it
  comes out. When one faints the trainer sends out the next one in party order. (Emerald's AI can choose a better
  matchup; that isn't modelled yet.)
- **Rules:** you can't run, Poké Balls are blocked, and Teleport doesn't end the battle.
- **Winning:**
  - "PLAYER DEFEATED CLASS NAME!", then the trainer's lose text.
  - Prize money from `GetTrainerMoneyToGive`: 4 × last Pokémon's level × class value, doubled by an Amulet Coin.
  - Victory music by class: trainer, gym leader, Aqua/Magma, or league.
- **Losing:** "…is out of usable POKéMON! … whited out!", then Emerald's normal white-out (`CB2_EndTrainerBattle`).
  Trainer flags are set by Emerald, as before.

## EXP, level-ups, new moves, evolution
- **EXP is earned when each opponent faints**, following `Cmd_getexp`:
  - It is split between the Pokémon sent in against that opponent.
  - Exp. Share holders get half.
  - Lucky Egg, trainer battles and traded Pokémon each give ×1.5.
  - EVs are given at the same time.
- **After the battle it is paid out one level at a time**, with "grew to LV. N!", the level-up fanfare and a friendship
  gain per level. At each level Emerald's `MonTryLearningNewMove` runs:
  - With room, the move is learned.
  - With four moves already, you get Emerald's flow: delete a move? → the real summary screen to choose one → "1, 2,
    and… Poof!". You can stop learning instead, and HM moves can't be forgotten.
- **After a win**, `GetEvolutionTargetSpecies` and Emerald's `EvolutionScene` run for every Pokémon that levelled up.
  The scene's own move learning works too.
- **Also:** Pay Day coins are paid out after a win, and Pokérus spreads on exit (as `ReturnFromBattleToOverworld` does).

## Verified (headless self-test)
- **Catching:**
  - Poké Ball on a full-HP Lv 5 Zigzagoon: odds 85, caught. The Pokédex message, the nickname question and a party slot all followed.
  - Master Ball: always caught.
  - Lv 40 Absol at 112 → 88 → 64 HP: odds 10 → 14 → 18. Shakes were 0, 0, then 1.
  - Catching with a full party sends it to the PC.
- **Trainer battle (Roxanne):**
  - Win: three Pokémon sent out in order, EXP ×1.5 split by who faced whom, $1200 prize.
  - Loss: white-out text.
- **Level-ups and moves:**
  - A Lv 15 Torchic reaching 16 learned Peck, then actually evolved into Combusken in Emerald's evolution scene
    (`PKBN_AUTO_PRESS`), and learned Double Kick there.
  - A Marshtomp with four moves replaced Water Gun with Mud Shot through the real summary screen.
  - Declining gives "did not learn".
- **No crashes:** all earlier self-test runs still finish without crashing, with the same outcomes as before.

## Not verified yet
- Hand play of all of it.
- Typing a nickname. The naming screen opens and returns, but typing was not automated.
- Trainer battles reached from the overworld. The self-test calls the battle directly, so the intro speech, the trainer
  flags and rematches are untested by me.
