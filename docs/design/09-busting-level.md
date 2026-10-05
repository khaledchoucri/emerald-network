# 09 — Busting Level: a rank for every grid battle, and what it pays out

Status: **plan**, nothing implemented.

BN6 facts come from `research/06-bn6-busting-level.md`, read from bn6f. The main sources are:
- `sub_800AC20`, asm/asm00_1.s:16678 (the score);
- `sub_80AA910`, asm/asm29.s:10801 (the reward pick);
- `byte_8020B9C`, data/dat01.s:200 (the tier table).

Our adaptations are marked **ADAPT**; numbers we choose are marked **TUNE**.

---

## 1. Why

Today a won wild battle pays only EXP. The Busting Level gives each battle a grade from 1 to 11 (S). The grade picks a reward from a list made from **the wild Pokémon's own moves**. That makes it the main source of pack copies for the folder (design 08 §4): fight Charmander well and you may get Ember O.

## 2. The score

We keep BN6's structure: components are summed, then clamped to 1..11 (asm/asm00_1.s:16897-16907). BN6 selects components with a mask per battle type (0x18F normal/boss, 0xF1 network, asm/asm00_1.s:16681-16684). We have two types: **wild** (BN "normal") and **trainer** (BN "boss rank").

| # | BN6 component (bit) | BN6 points | ours | status |
|---|---|---|---|---|
| 1 | Time (bit 0). Timer stops during the Custom screen and pauses (asm/asm00_1.s:15753-15775). | normal: ≤5 s 6, ≤12 s 5, ≤36 s 4, else 3. boss: ≤30 s 10, ≤40 s 8, ≤50 s 6, else 4 (asm/asm00_1.s:16918-16927) | The fight clock in **turns** (one turn = `CUSTOM_FRAMES` = 480 frames = 8 s, `include/pkbn/grid_internal.h:41`). Wild: won in turn 0 → 6, ≤1 → 5, ≤4 → 4, else 3. Trainer: per enemy Pokémon, average turns ≤1 → 10, ≤2 → 8, ≤3 → 6, else 4. | ADAPT + TUNE. Pokémon have more HP than viruses. Turns also scale with the Custom programs. |
| 2 | Hits that put you in flinch, paralyse, freeze, bubble or push (bit 1). Writers: asm/asm00_2.s:18305-18738. | n<4: 1−n (0 → +1 … 3 → −2); n≥4: −3 | Same rule. **Changed 2026-10-05 (POC-12c):** few Pokémon attacks stun or push, so 0 hits (+1) was nearly free. Now every enemy attack that does damage counts once, however many hits it has. A stun or push that comes without damage still counts. Counted for the side's active Pokémon, whoever it is. | ADAPT (wider than BN6) |
| 3 | Panel moves (bit 2) | ≤2 → +1 | Same: ≤2 player steps all battle | as BN6 |
| 4 | Largest multi-delete (bit 3), deletes within a 10-tick window (asm/asm00_1.s:16931-16972) | (m−1)×2 | Our wild battles have one enemy, so this becomes the **largest same-code chain** that dealt the KO or the last hit: 2 chips → +2, 3 → +4, a Program Advance → +6 | ADAPT |
| 5 | Counter hits (bit 7), asm/asm00_2.s:22012-22044 | +min(n,3) | **New mechanic:** a hit landed while the enemy is in its attack wind-up (`CHIP_LOCKOUT`) or `charging` counts as a counter. The text "COUNTER HIT!" (BN6 TextScript86F0374 entry 14). | ADAPT; also needs the counter-hit mechanic itself |
| 6 | No transformation (bit 8) | +1 | **No Pokémon fainted** → +1. A Cross/Beast Out has no equivalent; fainting is our nearest "used a resource" | ADAPT, TUNE |

Network components (bits 4–6) are not used.

**Ranges:**
- Wild: 3..6 + (−3..+1) + 1 + 0..6 + 0..3 + 1, so −1 to 18, clamped to 1..11. Same as BN6's normal maximum of 18 (research/06 §2).
- A clean wild KO that takes 2 turns: 5 + 1 + 0 + 0 + 0 + 1 = **7**. One counter hit and a 2-chip finish make it 10.
- **S (11) needs a fast, clean, combo kill.**

Display: **11 shows as "S"**, as in BN6 (11 = S is UNVERIFIED in bn6f; it's the BN convention).

## 3. The reward

### 3.1 Selection (BN6's, unchanged)

1. **Pick the enemy:** in a trainer battle, a random Pokémon the trainer sent out. BN6 picks a random enemy from the battle's list (asm/asm29.s:10960-10971).
2. **Pick the tier** from the level and `byte_8020B9C` (data/dat01.s:200-212), 16 columns per level:

   | L | 1–3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 (S) |
   |---|---|---|---|---|---|---|---|---|---|
   | tier | 0 | 0/1 | 1/2 | 2 | 2/3 | 3 | 3 (15/16), 4 (1/16) | 3/4 | 4 |

3. **Pick the entry:** `entry = 2·tier + random bit`, plus 10 if the player's active Pokémon has **HP ≤ 3·(MaxHP>>3)** (the low-HP half, asm/asm29.s:11011-11048).

### 3.2 The 20-entry list: generated per species, not hand-written

BN6 has a hand-made list per virus (data/dat29.s). For 386 species we **generate it** from the wild Pokémon's **current moveset** (the 4 moves it battled with), ordered by MB (design 08):
- **m₁** = its lowest-MB chip move
- **m₂** = its highest-MB chip move

| entries | normal half (0–9) | low-HP half (10–19) |
|---|---|---|
| tier 0 (0–1) | ₽ small | HP recovery small |
| tier 1 (2–3) | ₽ medium | HP recovery small |
| tier 2 (4–5) | ₽ large / **m₁ chip** | HP recovery medium / m₁ chip |
| tier 3 (6–7) | **m₁ chip** / **m₂ chip** | m₁ chip / m₂ chip |
| tier 4 (8–9) | **m₂ chip, rarer code** (either entry) | m₂ chip / m₂ chip, rarer code |

The shape follows BN6's own lists: money at low tiers, the virus's chip at tiers 2–4, and a different code at the top. Mettaur gives Rflectr1 P at tier 3 and Rflectr1 A at tier 4 (research/06 §3.5).

**Chip codes:**
- A normal chip entry rolls one of the move's lanes, with the first lane at half weight (design 08 §4).
- A "rarer code" entry rolls only from the lanes after the first. `*` is allowed when the move's lanes include it, at 1 in 4 (TUNE).

**Money** (Emerald pays nothing for wild battles; TUNE):
- Small = level × 4₽, medium = level × 8₽, large = level × 12₽.
- A level 10 wild gives 40/80/120₽. Ember at 720₽ (design 08) is about 6–10 good battles of saving.

**HP recovery** heals the active Pokémon: small 20 HP, medium 50 HP. This is BN6's type 10 (asm/asm03_0.s:12082-12105).

**Trainer battles:**
- The prize money stays (POC-7, now correctly $1500 for Roxanne).
- The busting reward is **extra**, using the same table, from a random member of the trainer's team.
- Gym leaders: S gives the TM's move chip (TUNE).

**No reward** for a catch (you got the Pokémon) or for running away. On a loss, nothing new happens.

### 3.3 NaviCust tie-ins (programs from design 07)

- **Collect** (BN6 NCP, asm/asm37_0.s:2427-2437): the reward is always a chip if the list has one. The scan goes down from the starting tier, then up (asm/asm29.s:10853-10936). New program, granted for free by **ABILITY_PICKUP**, which already takes 1 ability cell (`src/pkbn/ncp_table.c:209`).
- **The collect bug:** today it halves prize money (POC-9). It becomes BN6's bug row 6: the reward is forced to money and the level is ignored (asm/asm29.s:10815-10831, asm/asm37_0.s:2819-2844).
- **AmuletCn** already doubles prize money. It now doubles busting money too.

### 3.4 Busting Level scales EXP (decided: on)

- **On** (TUNE values): S = ×1.2, ≤3 = ×0.9, applied in `post_battle.c` before EXP is shared.
- It changes level curves, so the balance self-tests are rerun when it lands.

## 4. Screen

After the KO, before "GAINED EXP", the post-battle overlay (`src/pkbn/post_battle.c`) shows:

```
BUSTING LEVEL  S
EMBER  O  got!          (or  120₽ / HP +50)
```

Then the line in the log: `[pkbn] busting L11 tier4 entry9 -> chip EMBER O`.

## 5. Implementation sketch

1. **Battle counters** in `struct GridBattle`: `bustHits`, `bustSteps`, `bustChain`, `bustCounters`, `bustFainted`, `fightFrames`. Set where the events already happen: `stun` assignments, `Field_Step`, the chain resolver, the KO.
2. **`src/pkbn/busting.c`:**
   - `Busting_Level(&battle)` returns 1..11;
   - `Busting_Reward(level, enemyMon, lowHp)` returns an entry, encoded as BN6 does (2-bit kind + payload, asm/asm03_0.s:12611-12647);
   - `byte_8020B9C` copied as a 9×16 table with a citation.
3. **`post_battle.c`:** a `StepBusting` before `StepExpNext`. Chips go to the pack (needs design 08's `pkbn.sav` v2). Until then, a chip reward is logged and shown, but money is paid.
4. **Self-tests:**
   - `PKBN_TEST_SEED` makes the RNG deterministic;
   - the log line above for every battle;
   - a regression to check that levels match hand-computed scores for the x/k/t suites.

## 6. Decisions (2026-10-05) and questions

- **EXP scaling: on.** S = ×1.2, ≤3 = ×0.9 to start (TUNE).
- **Time: build both and compare.**
  - `PKBN_BUST_CLOCK=turns|seconds` picks which one scores.
  - Seconds uses BN6's own thresholds (5/12/36 s wild, 30/40/50 s trainer), timer stopped during the Custom screen.
  - The log line prints both scores, so play sessions show how the two differ.
- **Still open:** "No Pokémon fainted" as the +1, or something else (for example, no Switch used)?
