# 10 — Catching and chips

Status: **design**, nothing implemented. Decisions of 2026-10-05 are in §10 at the end.

Already in our code:
- **Catching** uses Gen 3's formula in `src/pkbn/grid_catch.c`, ball bonuses included:
  - Repeat Ball ×3 on species you've caught (`grid_catch.c:73`);
  - Net, Dive, Nest and Timer Balls (`src/battle_script_commands.c:9961-9991`).
- **First catch** is detected in `src/pkbn/post_battle.c:309`, through the Pokédex flag `FLAG_GET_CAUGHT`.

**The problem (Khaled):** catching is slow and risky. You whittle the Pokémon down, inflict status and take hits
while balls fail. All of that drags the Busting Level down. Catching should pay out in its **own** currency instead
of being punished.

---

## 1. Capture Grade instead of Busting Level (core)

A battle that ends in a catch is scored with a **Capture Grade** (1–11, S), never the Busting Level. The grade rewards
the things that make catching skilful:

| component | points | why |
|---|---|---|
| HP left at capture | ≤10% → +4, ≤25% → +3, ≤50% → +2, else 0 | you whittled it down without knocking it out |
| status on it at capture | sleep/freeze +3, paralysis/poison/burn +2 | you set up the catch the Gen 3 way (the same ×2 / ×1.5 the catch formula uses) |
| balls thrown | 1 → +3, 2 → +2, 3 → +1, else 0 | a clean catch |
| hits you took that made you flinch | as Busting (1−n, floor −3) | catching shouldn't be reckless |
| "Critical" ball: caught on the first throw at ≥50% HP | +2 | the lucky or skilful one-ball catch |

It's clamped to 1..11, and the grade picks a tier with BN6's table (design 09 §3.1).

The reward list is the caught Pokémon's own moves: **its chips are its data**. These rewards come **on top of** the
Pokémon itself.

---

## 2. First catch: a "Dex chip" (Khaled's idea)

- The first time a species is caught (`FLAG_GET_CAUGHT` not yet set), you get **1 copy of a move it knew in that
  battle**.
- You **choose which of its 4**, so catching Slugma is a way to *pick up Ember*.
- The code comes from the ball (§4), or the move's first lane.
- This gives the Pokédex a chip reason: **202 Hoenn species = up to 202 extra chips**, spread over the game.
- Repeat catches give the Capture Grade reward (§1) instead.

## 3. Pokédex milestones

Birch already rates the Pokédex (`src/birch_pc.c`). Every 10 species caught gives a **choice** item from design
08 §12: a PP Up, then a Heart Scale, then a PP Max every 50. Completionism feeds the folder.

## 4. The ball picks the code

Each ball "imprints" a lane on the chip it earns. If the move doesn't have that lane, it falls back to the first
lane.

| ball | lane | why |
|---|---|---|
| Poké / Great / Ultra | first lane / random lane / your choice | better ball, better control |
| **Net Ball** | B (BIND) | a net |
| **Dive Ball** | R (RAIN) | water |
| **Nest Ball** | G (GROWTH) | young, growing Pokémon |
| **Timer Ball** | T (TEMPO) | time |
| **Repeat Ball** | copies a code you already own for that move | "repeat" |
| **Luxury Ball** | Y (YIELD) | friendship and support |
| **Premier Ball** | **`*`** if the move allows it | the rare commemorative ball |
| **Safari Ball** | random lane, and **2 chips** | the Safari Zone is a chip-hunting ground |
| **Master Ball** | any code, `*` included | — |

Ball choice becomes a real decision: Dive Ball your Wailmer for Water Gun **R**, which joins your rain combos.

## 5. The moves you used to catch it get credit (Mastery tie-in)

If design 08's Mastery is on, a move that **inflicted the status** or **brought it to ≤25% HP** right before a
successful catch counts **×3 uses**. Using Hypnosis well is how you get more Hypnosis.

## 6. Partner chips: the switch chips, earned by catching

The special switch chips (design 08 §11: "switch to that Pokémon and use that move") come from catching:
- An **S Capture Grade** on a species gives a **Partner chip** for *that individual* Pokémon: "SWAMPERT·Surf".
- **Friendship** (Emerald's `MON_DATA_FRIENDSHIP`) could unlock a second one at max friendship.
- Partner chips are the only chips tied to a Pokémon, as BN6's Navi chips are tied to a Navi. They cost a Custom
  like any switch.

## 7. Releasing gives its data back (optional, an economy valve)

Releasing a Pokémon from the PC gives **1 random chip of its moves**, much as deleting a virus drops its data in BN.

- It makes duplicate catches useful (catch three Slugma, keep one, release two for Ember copies).
- Balls cost money and catching costs time, so it's self-limiting.
- TUNE: maybe once per species per day (the RTC exists in Emerald).

## 8. Eggs bring egg moves

A Pokémon hatched at the Day Care gives **1 copy of each of its egg moves**. Egg moves are rare moves (Charmander's
Belly Drum, Bulbasaur's Petal Dance), so breeding becomes the way to get them.

## 9. Shiny catches

A shiny catch gives a `*` copy of every move it knew. It's the jackpot moment.

---

## Proposal: what to build first

| priority | items | why |
|---|---|---|
| 1 | Capture Grade (§1) and Dex chip (§2) | answers the problem and the request directly |
| 2 | Ball codes (§4) and Partner chips (§6) | the most "only in this game" ideas |
| 3 | Milestones (§3), credit (§5), release (§7), eggs (§8), shiny (§9) | cheap add-ons once the chip pack exists |

---

## 10. Decisions (2026-10-05) and the revised design

| # | idea | decision |
|---|---|---|
| §1 | Capture Grade | **approved** |
| §2 | Dex chip | **replaced by Candy** (§10.1): one free chip felt punishing |
| §3 | Pokédex milestones | **yes** |
| §4 | ball codes | **reworked** (§10.2); the Master Ball gives **1 copy of every move** it knew |
| §5 | catch credit and Mastery | **no** (Mastery dropped from design 08 §12 too) |
| §6 | Partner chips from S grades | **no**: earned from the story and levelled up like Navi chips (§10.3) |
| §7 | release | **folded into Candy** |
| §8 | eggs bring egg moves | **yes** |
| §9 | shiny `*` copies | **yes** (Gen 3 shiny odds are 1/8192, which keeps it rare) |

### 10.1 Candy: **type candy** (recommended over species candy)

**Sanity check, from the port's data:**

| | species candy | type candy |
|---|---|---|
| currencies | 386 (202 in Hoenn); most are never spent | **17** |
| "catch a higher-level X" incentive | direct | kept by the level gate below |
| farming | per species, so naturally slow | **risk:** common Pokémon flood a type. 24 Hoenn species have catch rate 255 (Zigzagoon, Numel, Feebas…) and 46 Hoenn species are Water-type |
| scarcity | flat | **natural:** Fire 10 Hoenn species, Dragon 10, Ghost 6, Ice 6, Water 46, Psychic 28 |

Type candy is better, provided two brakes from Emerald's own data are in place.

**Earning (TUNE):**
- **Catch:** `1 + (255 − catchRate) / 50` candy of **each** of its types, using `catchRate` from `species_info.h`.
  - Zigzagoon (255) gives 1 Normal, Slugma (190) 2 Fire, Bagon (45) 5 Dragon, Beldum (3) 6 Steel + 6 Psychic.
  - Rare and evolved catches pay more; farming Zigzagoons pays least.
- **First catch** of a species: ×3. This replaces the Dex chip: a first Slugma gives 6 Fire candy, about two Embers.
- **Release:** 1 candy of each of its types, +1 at level 30 or above.
- **Capture Grade S:** +2.

**Spending:**
- You buy a copy of a **damaging or status move of that type** that is in the level-up learnset of a Pokémon **you
  own** (party or PC). That Pokémon must have reached
  `max(the level it learns the move at, the move's MB)` (TUNE).
  - The MB floor is needed because evolved forms learn some strong moves "at level 1": Raichu's Thunderbolt at
    L1, Weezing's Self-Destruct at L1 (`level_up_learnsets.h`). With the floor, Thunderbolt (MB 28) needs a
    level-28 Raichu, Self-Destruct (MB 50) needs level 50, and Psychic (MB 27) needs level 27.
- **Price:** `ceil(MB / 4)` candy. Ember 3, Bite 5, Flamethrower 7, Fire Blast 9, Hyper Beam 10, Explosion 17.
- **Code:** the move's first lane. +2 candy to choose any lane.
- Legendaries' moves can be bought only once you own that legendary.

**Income check:**
- About 5–8 catches an hour at about 2 candy each, ×3 on first catches, gives **~15–25 candy an hour** spread over
  the types.
- That's about **3–5 chosen chips an hour**, on top of the ~10 random drops an hour from busting (design 08 §12.1).

### 10.2 Ball codes, reworked: the ball decides **how** the code is picked

Only 5 of the 25 lanes had a themed ball, so the ball now sets the *rule*, not the lane:

| ball | code of the Capture Grade chip |
|---|---|
| Poké | the move's first lane |
| Great | a random lane of the move |
| Ultra | **you choose** a lane of the move |
| Net / Dive / Nest / Timer / Luxury | their themed lane (B / R / G / T / Y) **if the move has it**, otherwise you choose |
| Repeat | a code you already own for that move (stacks combos) |
| Premier | `*` if the move allows it, otherwise you choose |
| Safari | random lane, 2 chips |
| **Master** | **1 copy of every move it knew**, codes you choose |

### 10.3 Partner chips: from the story, levelled like Navi chips

- **Earned deterministically** at story beats, never from random drops or grades. For example:
  - the **starter's** chip after the first rival battle (Route 103);
  - one more at each of a few badges, assigned to a party Pokémon of your choice.
- A partner chip is tied to that Pokémon: it switches it in and uses its move, costing the Custom.
- **Levels V1 → V2 → V3** (BN6's Roll → RollV2 → RollV3) raise the move's power or add a rider. They come from:
  - **friendship** (`MON_DATA_FRIENDSHIP`, 0–255; e.g. V2 at 150, V3 at 220);
  - or story events (Elite Four).
- **Alternative for later:** "guest" chips of the gym leaders' or rival's signature Pokémon, which appear, attack and
  leave, exactly like BN6's Navi chips. Roxanne's Nosepass Rock Tomb V1 after her badge, V2 after the rematch.

Shiny `*` copies may be strong, but at 1/8192 they're a jackpot moment, not a strategy.
