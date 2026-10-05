# 10 — Catching and chips

Status: **brainstorm and proposal**, nothing implemented.

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
