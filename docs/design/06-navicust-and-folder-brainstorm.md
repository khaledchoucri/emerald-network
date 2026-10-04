# 06 — Brainstorm: NaviCust, Chip Folder, and other BN systems

**Status: ideas, not decisions.** BN6 facts come from `research/05-bn6-navicust-folder-rewards.md`, where every claim
has a bn6f citation. Emerald facts are cited inline from the host (pokeemerald pc_port). An idea marked **(design)**
is our own invention.

---

## 0. The ground we stand on

### BN6 (bn6f)
- **NaviCust grid.** It starts at 4×4. Key item `ExpMemry` (max 2) widens it to 5×4, then 5×5
  (data/dat36.s:1325/1340/1355, asm/asm37_0.s:1902). The command line is row 3 of a 7×7 working space
  (asm/asm37_0.s:732).
- **Programs.**
  - 46 programs, each with 1–4 colour variants, 16 bytes per entry (`StructArr_813944C`, data/dat36.s:379).
  - Each entry holds a 7×7 shape, a colour 1–6, a "plus part" flag, an exclusive group, and the bug it causes.
  - A program can be "compressed" by entering a 10-button code, which shrinks its shape (asm/asm37_0.s:1653).
  - You own at most 9 of each.
- **Bugs.** You get bugs when you place:
  - a plus part on the command line;
  - a normal part off the command line;
  - two parts of the same colour touching;
  - 5 or more colours in total;
  - a part on the outer frame.

  Each bug type caps at level 3, and BugStop cancels them all (asm/asm37_0.s:702–1158). In battle, bugs mean HP drain,
  buster misfires, moving by itself, a smaller Custom hand, and status at battle start (asm/asm00_2.s,
  asm/asm03_0.s:8670).
- **What a NaviCust stores:** a 0x40-byte grid plus 49 placed-part slots of 8 bytes each (0x188), i.e. **0x1C8 bytes**,
  plus a 16-byte bug array.
- **Folder rules.**
  - 3 folders of 30 chips. Each chip entry is `id | code<<9`.
  - The chip pack counts each chip in each of its 4 codes, up to 99.
  - Copies of one chip are capped by its MB: ≤19 MB → 5, 20–29 → 4, 30–39 → 3, 40–49 → 2, 50+ → 1
    (asm/asm36.s:10634).
  - Mega and Giga counts are capped by program-raised levels. At most 3 Dark chips.
  - The Regular chip must fit RegUP memory.
- **Rewards.**
  - A Busting Level of 1–11 comes from time, hits, deletions and HP lost (asm/asm00_1.s:16678).
  - It picks a reward from a per-encounter table of 20 entries: a chip, zenny, nothing, or BugFrags
    (data/dat29.s, asm/asm03_0.s:12611). There is a different half of the table when your HP is low.
- **Save footprint:** folders, chip pack, NaviCust and the program inventory come to about 4.9 KB of BN6's 0x6710-byte
  save.

### Emerald / the PC port
- **There's room on every Pokémon for a tag.** `BoxPokemon.unknown` is a spare, unencrypted u16 outside the checksum:
  `CalculateBoxMonChecksum` only adds up the substructs (src/pokemon.c:2790). It can be read and written as
  `MON_DATA_ENCRYPT_SEPARATOR` (src/pokemon.c:3827/4217).
  - It travels with the Pokémon into boxes, the daycare and trades.
  - Only Shedinja's creation clears it (src/evolution_scene.c:561).
  - There are also 4 unused bits (`BoxPokemon.unused`), the substruct's `filler` and 4 `unusedRibbons` bits, but those
    sit inside the encrypted, checksummed data.
- **The save file is ours to extend.** The PC port reads and writes `pokeemerald.sav` (src/platform/sdl2.c:78,214), an
  image of the 128 KB flash. Every flash sector already has an owner (include/save.h:19–31), so new data shouldn't go
  inside it. A **sidecar file next to it** costs nothing, and that only works because we target the PC port.
- **Found while measuring: an upstream PC-port bug.** On 64-bit, `SaveBlock1` is **16,280 bytes**, but the save writes
  **4 × 3,968 = 15,872**. It grows because `ObjectEventTemplate.script` is a pointer: 8 bytes instead of 4, × 64
  templates (include/global.fieldmap.h:107). So the last **408 bytes are never saved**: Walda's phrase, Trainer Hill
  data, the Union Room registered texts and part of the trainer-name records. Worth fixing anyway. It also tells us not
  to grow SaveBlock1.
- **Free item ids.** There are 62 unused item ids (ITEM_034…ITEM_0E8, include/constants/items.h), but the bag pockets
  only hold 30 items each (include/constants/global.h:55).

### Ours so far
- The folder is built automatically from the party's moves. Copies come from the move's max PP (≥30 → 3, ≥15 → 2,
  else 1). Each copy gets one code letter from the curated lanes. 30 chips, a hand of 5.
- Using a chip spends 1 PP. Contest combos, Program Advances and a benched owner switching in are already in.

---

## 1. "Every Pokémon is a Navi" — is per-Pokémon NaviCust too much memory?

**No, not on the PC port.** Rough numbers:

| How we store a layout | Per Pokémon | 6 in the party + 420 in boxes |
|---|---|---|
| BN6's own format (grid + 49 slots + bugs) | ~476 B | ~203 KB |
| **Compact (design):** count + up to 15 parts × 2 bytes (program variant, x:3, y:3, rotation:2) | ~32 B | **~14 KB** |
| Party plus a few saved builds only | 32 B × N | under 1 KB |

**How a Pokémon finds its layout (design):**
- Store a **Navi ID** (1…65535) in `BoxPokemon.unknown`. Id 0 means "fresh, no NaviCust yet".
- The sidecar file `pkbn.sav` holds `navi[id] = { grid size, parts[], program inventory refs, … }`. The grid itself is
  never stored: it is rebuilt from the parts list, as BN6 does every time it runs the NaviCust.
- Edge cases to handle:
  - **Shedinja** (its id gets cleared): give it a fresh id, or copy Nincada's layout.
  - **Traded or event Pokémon:** an id we don't know means a fresh one.
  - **Releasing** a Pokémon frees its id.
  - **Hall of Fame and Battle Frontier rentals** ignore it.
- The 64-bit save bug above is the reason to keep all of this out of SaveBlock1 and in the sidecar.

---

## 2. NaviCust ideas

### 2.1 What a Pokémon's NaviCust looks like
- **The grid grows with the Pokémon (design).** BN6 grows it with ExpMemry. Ours could be:
  - by evolution stage (base 4×4, then 5×4, then 5×5), or
  - by an item (an "ExpMemry" in an unused item id), or
  - by friendship.

  Evolution fits nicely: the mid stage often "learns its kit".
- **Programs are coloured by type (design).** BN6 has 6 colours and bugs on same-colour neighbours. Give every program a
  Pokémon type instead, and let the Pokémon's own types be the colours that never bug. A dual-type Pokémon gets two
  safe colours, so Pokémon with different types need different builds.
- **The command line (design).** In BN6, normal parts must touch it and plus parts must not. Its row could come from the
  nature: the row index is set by the stat the nature raises, so every nature gives a slightly different board.
  Alternatively it stays fixed at row 3, as in BN6.
- **Compression:**
  - **Pokéblocks:** feeding a Pokéblock "compresses" a program of the matching condition, shrinking its shape. Emerald
    condition values (cool, beauty, cute, smart, tough, plus sheen) finally get a battle use.
  - **The Lilycove Move Tutor style:** a person who enters the 10-button code for you.

### 2.2 Where programs come from
- **BN6's 46 programs map well onto Gen 3:**

| BN6 program | What it does in BN6 | Gen 3 twin (design) |
|---|---|---|
| UnderShirt | survive a hit at 1 HP | Sturdy / Focus Band |
| FloatShoes | ignore panel effects | Levitate (no poison panels, no ice slide) |
| AirShoes | stand on holes | Flying types |
| SuperArmor | no flinch knock-back | Inner Focus |
| FirstBarrier | start with a barrier | a free Protect at battle start |
| Custom1/2 | +1/+2 chips in the hand | a "hand size" stat |
| MegaFolder / GigaFolder | more Mega/Giga chips allowed | signature-move limits (§3.5) |
| Attack/Speed/Charge +1 | buster stats | Atk / Spe EV-style bonuses for the buster and movement |
| HP+50…500 | max HP | HP Up |
| BugStop | cancels bugs | Full Heal / Lum-like |
| Collect / Millions | drops / money | Pickup / Amulet Coin |
| SneakRun | weak viruses don't appear | Repel (the same idea) |
| OilBody / Fish / Battery / Jungle | element interactions | weather and type synergies |
| Humor / Poem | flavour (jokes, poems) | Pokémon "talk" lines |

- **Abilities as built-in programs:** a Pokémon's Gen 3 ability is a pre-placed, unmovable program on its grid.
  Levitate is a 1-cell FloatShoes. That makes abilities visible and lets the rest of the grid build around them.
- **Getting programs:**
  - sold at Pokémarts;
  - trainer and gym rewards (a Gym badge plus a program);
  - wild-battle drops by Busting Level (§4.1);
  - a "program designer" NPC in Slateport or Mauville;
  - held items turned into programs.

### 2.3 Bugs = status, with a Pokémon twist
- BN6's bug effects (HP drain, misfires, moving by itself, a smaller hand, status at battle start) line up with Gen 3
  statuses.
- **Pokérus is literally a virus.** It could be a *good* bug: an infected Pokémon's NaviCust tolerates one extra colour,
  or gets a free program slot, while it lasts. Emerald already spreads it on battle exit (POC-7).

### 2.4 Where you edit it
- Add **NAVICUST** to Emerald's party menu, next to SUMMARY, SWITCH and ITEM.
- The editor itself is BN6's: rotate with L/R, place with A, RUN! to compile.
- The summary screen gets a page showing the compiled result: "HP +100, Custom +1, FloatShoes".

---

## 3. Chip Folder ideas (and how it shows up as moves)

The hard constraint: Emerald's menus think in **4 moves per Pokémon**. The folder must always translate back to
that.

### 3.1 Option A — the folder *is* the moveset (design, the bold one)
- Each Pokémon's chips may come from **at most 4 distinct moves**. Those 4 moves are what the summary screen and
  Emerald's move-learning flow see.
- Editing the folder therefore edits movesets. Adding a chip of a 5th move asks "forget which move?", which is
  Emerald's own `GetMoveSlotToReplace` flow, already used in POC-7.
- **The chip pack** is the moves each Pokémon *can* use (level-up so far, TMs used on it, tutors), each with its lane
  codes. It's a Move Reminder that is always open.
- **Copies:** BN6's MB rule is the cap (5/4/3/2/1). MB comes from power, e.g. MB = power/5, so weak moves get many
  copies and big moves 1–2. Each **PP Up** (`ppBonuses`, 2 bits per move) raises the cap by 1.
- **PP becomes copies.** Instead of 35 PP you have, say, 4 copies, each usable once per battle. Emerald's PP stays
  as-is for the overworld and summary, shown as "PP 4/4" (copies).

### 3.2 Option B — keep auto-building, add "Folder Edit" on top (design, the gentle one)
- The 4 moves stay exactly as they are. The folder editor decides:
  - how many copies of each move go in, within the PP-based cap and the 30-chip limit;
  - which lane letter each copy carries, chosen from that move's curated lanes.

  It's a code-shaping tool with no moveset change at all.
- It translates back trivially: the summary's moves page lists each move's copies and letters under it.

### 3.3 3 folders = 3 party presets (BN6 has 3 folders)
- Each folder remembers its own chip choices (and, under Option A, its movesets). The PC port has space for this.
- Switching folders before a gym is like BN6 folder swapping.

### 3.4 Regular and Tag chips
- **Regular chip (REG):** one chip is always in your first hand. BN6 limits it by RegUP memory; ours could use the lead
  Pokémon's **friendship** (more friendship, bigger REG allowance).
- **Tag chips:** BN6 stores 2 tagged chips (NaviStats 0x56–0x59, pairing rule UNVERIFIED). Ours: **tag two chips that
  form an Emerald contest combo** (`AreMovesContestCombo`, already behind our chain payoffs). A tagged pair is always
  drawn together, so combos become plannable.

### 3.5 Mega and Giga chips
- **Mega chips:** moves only a few species learn, or with big effects (Explosion, Hyper Beam…). At most N per folder,
  where N is raised by MegaFolder programs (BN6: cap 10).
- **Giga chips:** legendary signatures (Psycho Boost, Doom Desire, Eruption-level…), 1 per folder, as in BN6.

### 3.6 Chip Trader and Library
- **Chip Trader:** a machine in Pokémon Centers. Feed it 3 chips (or 3 TMs / Heart Scales) for a random chip whose
  code you don't own. BN6 prefers codes you're missing (asm/asm03_2.s:9401), and Emerald's Lilycove Lottery is a
  similar random-reward machine (src/lottery_corner.c).
- **Library:** a Pokédex-like list of every chip (move + code) you've ever owned. BN6 marks it with event flag
  `0x1E20+id` (asm/asm02.s:59). Rewards for completion.

---

## 4. Other BN systems worth merging

### 4.1 Busting Level → rewards and EXP (strong candidate)
- After every grid battle, compute a BN6-style rank (1–11, S at the top) from time, hits taken and so on
  (asm/asm00_1.s:16678).
- **The rank picks the reward:**
  - Low ranks: Pokédollars.
  - High ranks: a **chip of one of the wild Pokémon's own moves** (BN viruses drop their own chips) or a NaviCust
    program.
  - If you finish at low HP, a different reward set, as in BN6.
- **The rank could scale EXP** too (e.g. S = ×1.2). That's a TUNE decision on top of `Cmd_getexp`.

### 4.2 BugFrags = Game Corner coins
- Emerald already saves a coin count (`SaveBlock1.coins`, include/global.h:1044). Make coins BN6's BugFrags (cap 9999, asm/asm03_1_1.s:8711): earned from bugged
  or low-HP wins, and spent at a BugFrag trader (the Game Corner prize counter is the natural spot).

### 4.3 Cross System / Beast Out → teammates and forms
- **Cross (design):** at the Custom screen, cross with a benched teammate. For a few turns you get its type as a second
  type and its buster style. BN6 picks a Cross at the Custom screen (known from play, not yet traced in bn6f); ours picks a teammate.
- **Beast Out (design):** at 1/3 HP or below (where Gen 3's Blaze, Torrent and Overgrow kick in, src/pokemon.c:3221),
  the starter goes "beast": the buster charges by itself, chips get stronger and aim at the foe by themselves. The
  BN6 Beast Out counter is at NaviStats 0x21 (asm/asm00_2.s:11744); its exact effects are UNVERIFIED in bn6f.
- **Castform** forms by weather already fit as "crosses".

### 4.4 Sub chips = bag items outside battle
- BN6's sub chips (MiniEnrg, FullEnrg, SneakRun, Untrap, LockEnmy, Unlocker; key items 0x80–0x86) already have bag
  twins: Potion, Full Restore, Repel, Escape Rope, ...
- Only the **SubMemory** cap would be new: how many healing items you can carry. That's a difficulty knob.

### 4.5 Full Synchro / Emotion = friendship
- BN6 has an emotion system (there's an emotion bug at asm/asm00_2.s:11188). The Full Synchro specifics are
  **UNVERIFIED**.
- **(design):** a counter-hit (hitting the foe as it starts its own attack) puts you in "Full Synchro": your next chip
  does ×2. Higher friendship makes the window longer.

### 4.6 Jack-in and the Net
- **The PC as a jack-in point:** at any Pokémon Center PC, jack in to a virus training area. Fight grid battles against
  Pokémon from your area's encounter table, with BN's busting ranks. It's an EXP and chip-farming loop separate from
  tall grass.
- **Secret Bases as your Homepage:** BN's homepage was your Navi's base, and Emerald's secret base already has
  decorations and a "battle the owner" mode.

### 4.7 Navi rivals = trainers with NaviCusts
- Gym leaders' Pokémon get pre-built NaviCusts (and folders, under Option A).
- Roxanne's Nosepass with SuperArmor and UnderShirt reads like a BN boss fight.

---

## 5. A possible order (if you like the direction)

1. **Groundwork:**
   - the sidecar save `pkbn.sav`;
   - the Navi ID in `BoxPokemon.unknown`;
   - a "NAVICUST" / "FOLDER" entry in the party menu that opens an empty screen;
   - the upstream save fix (408 bytes).
2. **Folder Edit, Option B first:** codes and copies with no moveset change. Low risk; it teaches us the editor UI.
3. **NaviCust MVP:**
   - a 4×4 grid, about 12 programs (HP+, Custom1, Attack+1, Speed+1, UnderShirt, FloatShoes, AirShoes, SuperArmor,
     FirstBarrier, BugStop, Collect, BustPack);
   - bugs from colour adjacency and the command line;
   - abilities as fixed programs.
4. **Busting Level and rewards:** chips and programs from wild battles.
5. Then the bigger swings: Option A (the folder is the moveset), Cross / Beast Out, Jack-in.

## 6. Questions for you
- Folder: **Option A** (the folder is the moveset, a bold change to Pokémon) or **Option B** (keep the 4 moves, edit
  copies and codes)?
- Program colours: type colours (§2.1) or BN6's own 6 colours?
- How the grid grows: evolution stage, an ExpMemry item, or friendship?
- PP: keep Gen 3 PP as a per-battle resource (now) or switch to "each copy usable once per battle"?
