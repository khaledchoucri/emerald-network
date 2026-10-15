# POC-30: phase strikes for trainers

**Patches:** `0104-POC-30-phase-strikes-for-trainers-too.patch` and `0105-POC-30b-version-0.30.patch`, on top of
0001–0103.

Your pick N7b. POC-26's phase strikes now come from trainers' Pokémon too, Gym Leaders' and rivals' included. The
campaign runs also showed the strikes helping campers, so two things about them changed, in wild battles too.

## The rule

`PhaseStrike` and `UpdateOneEnemy` in `src/pkbn/grid_battle.c`:

- **The trigger:** stand in your back column for 3 seconds of fighting, and the foe blinks to its front column in your
  row.
- **The strike:** its strongest contact move, or its strongest damaging move if it has none.
- **The warning:** your panel lights up first. The warning starts at 60 frames and shortens to 24 the longer you camp.
  The striker is open during the wind-up, so hitting it then is a counter hit.
- **New: on top of the foe's attacks.** The strike comes as soon as the foe is free, with 2.5 seconds between strikes.
  Its own attacks keep their timing.
- **New: the foe blinks back.** Once the strike has landed, the foe returns to the panel it came from.
- **Still without them:** NET CHALLENGE simulations, legendary boss battles and Birch's rescue.
- **Numbers:** TUNE.

## Why the two changes

The first build only took POC-26's wild-only check away. In campaign runs with a player who only holds B
(`PKBN_BOT=buster`), that made camping safer, not riskier: losses fell from 117 to 68 a run, and Winona went from
0 of 3 to 3 of 3.

There were two reasons:

- **The striker stayed in the line of fire.** It stayed in the camper's row and front column until it could act
  again, and the buster hit it all that time. It now blinks back as soon as its strike lands.
- **The strike replaced the foe's attack.** A camper only ever faced telegraphed strikes it could step away from,
  instead of the foe's own moves. Winona's Aerial Ace, for one, is a lock-on. Damage taken against Gym Leaders fell from
  113 to 42 a minute.

The strike now comes on top of the foe's attacks.

## Simulated

Three runs of the hold-B player to Juan, one per starter, against POC-29, which has phase strikes in wild battles
only:

| | POC-29 | First build | POC-30 |
|---|---|---|---|
| Losses a run | 117 | 68 | 148 |
| Gave up on a trainer | 12 | 6 | 13 |
| Winona won | 0 of 3 | 3 of 3 | 0 of 3 |
| Phase strikes a run | 2,520 | 6,570 | 12,180 |

The normal test player (six runs catching Pokémon, as in POC-29) draws about 350 trainer strikes a run while it waits
to aim. It loses 6 battles a run, against 8 on POC-29. Winona was won in 3 of 6 runs, Wattson in 5. Playing the starter
alone, which waits in the back column more, it loses 42 a run, against 33.

## Tests

- **Battle regressions (33):** the same `[pkbn]` logs as POC-29. None of them camps long enough for a strike.
- **Overworld tests:** 51/51.
- **Camping self-test** (`run camp`, POC-26): the Poochyena strikes 4 times instead of 2 in the same battle, because
  its strikes no longer use up its attacks.
- **Patches:** 0001–0105 applied onto the pin give the same tree as the build tested here.
