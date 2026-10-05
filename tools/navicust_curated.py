# NaviCust programs for Pokémon (POC-9). Generated into src/pkbn/ncp_table.c by tools/gen_navicust.py.
#
# Board: BN6's middle board, 5 wide x 4 tall with the command line on its 3rd row and an overhang frame around it
# (byte_813B2CD, bn6f data/dat36.s:1340; command line = row y=3 of the 7x7 space, asm/asm37_0.s:732).
#
# Fields per program:
#   name      8-char name shown in the editor (BN6 style)
#   effect    NCPE_* (what the compiled program does in a grid battle) and its value(s)
#   plus      True = "plus part": must NOT touch the command line (BN6 byte +1); False = normal part: must touch it
#   group     exclusive group (BN6 byte +0): only one program per group runs (asm/asm37_0.s:2030)
#   bug       the bug type it causes when misplaced / same-colour neighbour (BN6 byte +4 numbering)
#   cond      the Emerald condition (Pokéblock stat) that compresses it: COOL BEAUTY CUTE SMART TOUGH
#   types     colour variants = Gen 3 types (design: BN6 colours become types)
#   shape     rows, '#' = cell; cshape = compressed shape (for BN6 programs both copied from bn6f, see `src`)
#   src       where the shape comes from
#   desc      one line for the editor
#
# BN6 shapes below were read from StructArr_813944C (bn6f data/dat36.s:379) with tools/bn6_ncp_shapes.py.

PROGRAMS = [
    # ---- BN6's own programs (15 core) ---------------------------------------------------------------------
    dict(name='SuprArmr', effect=('SUPER_ARMOR', 0), plus=False, group=1, bug=1, cond='TOUGH', types=['STEEL', 'ROCK'],
         shape=['.#.', '###', '###'], cshape=['.#.', '###'], src='bn6f entry 4 (SuprArmr)',
         desc="Flinches and knock-backs don't stop you."),
    dict(name='Custom1', effect=('HAND', 1), plus=False, group=0, bug=4, cond='SMART', types=['PSYCHIC', 'NORMAL'],
         shape=['.#.', '###', '.##'], cshape=['#.', '#.', '##'], src='bn6f entry 8 (Custom1)',
         desc='+1 chip in the Custom hand.'),
    dict(name='Custom2', effect=('HAND', 2), plus=False, group=0, bug=4, cond='SMART', types=['PSYCHIC'],
         shape=['##', '##', '##', '##', '##'], cshape=['##', '##', '##', '#.'], src='bn6f entry 12 (Custom2)',
         desc='+2 chips in the Custom hand.'),
    dict(name='FstBarr', effect=('FIRST_BARRIER', 0), plus=False, group=0, bug=1, cond='TOUGH', types=['PSYCHIC', 'WATER'],
         shape=['###', '###'], cshape=['#.', '##'], src='bn6f entry 28 (FstBarr)',
         desc='Start every battle behind a Barrier.'),
    dict(name='FlotShoe', effect=('FLOAT_SHOES', 0), plus=False, group=0, bug=3, cond='BEAUTY', types=['FLYING', 'GHOST'],
         shape=['..#', '###', '.##'], cshape=['.#', '##', '#.'], src='bn6f entry 44 (FlotShoe)',
         desc='Panels do nothing to you: no poison, no ice, no cracks.'),
    dict(name='AirShoes', effect=('AIR_SHOES', 0), plus=False, group=0, bug=3, cond='BEAUTY', types=['FLYING'],
         shape=['###', '###', '#.#'], cshape=['###', '#.#', '#.#'], src='bn6f entry 48 (AirShoes)',
         desc='You can stand on broken panels.'),
    dict(name='UnderSht', effect=('UNDER_SHIRT', 0), plus=False, group=7, bug=1, cond='TOUGH', types=['NORMAL', 'FIGHTING'],
         shape=['#', '#'], cshape=['#'], src='bn6f entry 52 (UnderSht)',
         desc='A hit that would faint you leaves 1 HP (when above 1 HP).'),
    dict(name='BugStop', effect=('BUG_STOP', 0), plus=False, group=0, bug=0, cond='SMART', types=['BUG'],
         shape=['.##', '##.', '.##', '##.'], cshape=['.#.', '##.', '.##', '.#.'], src='bn6f entry 124 (BugStop)',
         desc='Cancels every bug.'),
    dict(name='BustPack', effect=('BUST_PACK', 3), plus=False, group=0, bug=7, cond='COOL', types=['STEEL'],
         shape=['###', '###', '###'], cshape=['##.', '###', '###'], src='bn6f entry 108 (BustPack)',
         desc='Buster Attack, Speed and Charge +3.'),
    dict(name='Attack+1', effect=('BUSTER_ATK', 1), plus=True, group=0, bug=7, cond='COOL', types=['FIGHTING', 'FIRE', 'NORMAL'],
         shape=['#', '#'], cshape=['#', '#'], src='bn6f entries 140-142 (Attack+1)',
         desc='Buster Attack +1.'),
    dict(name='Speed+1', effect=('BUSTER_SPEED', 1), plus=True, group=0, bug=7, cond='SMART', types=['ELECTRIC', 'FLYING', 'NORMAL'],
         shape=['#'], cshape=['#'], src='bn6f entries 144-146 (Speed+1)',
         desc='Buster Speed +1 (shoots more often).'),
    dict(name='Charge+1', effect=('BUSTER_CHARGE', 1), plus=True, group=0, bug=7, cond='TOUGH', types=['ELECTRIC', 'FIRE', 'NORMAL'],
         shape=['#'], cshape=['#'], src='bn6f entries 148-150 (Charge+1)',
         desc='Buster Charge +1 (hold B: charged shot comes faster).'),
    dict(name='HP+50', effect=('HP_PCT', 5), plus=True, group=0, bug=9, cond='CUTE', types=['NORMAL', 'GRASS', 'WATER'],
         shape=['#', '#'], cshape=['#', '#'], src='bn6f entries 164-166 (HP+50)',
         desc='Max HP +5% in battle.'),
    dict(name='HP+100', effect=('HP_PCT', 10), plus=True, group=0, bug=9, cond='CUTE', types=['NORMAL', 'GRASS', 'WATER'],
         shape=['##', '##'], cshape=['##', '##'], src='bn6f entries 168-170 (HP+100)',
         desc='Max HP +10% in battle.'),
    dict(name='HP+200', effect=('HP_PCT', 20), plus=True, group=0, bug=9, cond='CUTE', types=['NORMAL', 'GRASS', 'POISON'],
         shape=['###', '###'], cshape=['###', '###'], src='bn6f entries 172-174 (HP+200)',
         desc='Max HP +20% in battle.'),

    # ---- vitamins: plain stat programs (design; Emerald's vitamins are the stat items) -----------------------
    dict(name='Protein', effect=('STAT_PCT', 'ATK', 10), plus=True, group=0, bug=7, cond='COOL', types=['FIGHTING', 'NORMAL'],
         shape=['#', '#'], cshape=['#'], src='design', desc='Attack +10% in battle.'),
    dict(name='Iron', effect=('STAT_PCT', 'DEF', 10), plus=True, group=0, bug=7, cond='TOUGH', types=['STEEL', 'ROCK'],
         shape=['#', '#'], cshape=['#'], src='design', desc='Defense +10% in battle.'),
    dict(name='Calcium', effect=('STAT_PCT', 'SPATK', 10), plus=True, group=0, bug=7, cond='BEAUTY', types=['PSYCHIC', 'FIRE'],
         shape=['#', '#'], cshape=['#'], src='design', desc='Sp. Atk +10% in battle.'),
    dict(name='Zinc', effect=('STAT_PCT', 'SPDEF', 10), plus=True, group=0, bug=7, cond='CUTE', types=['WATER', 'PSYCHIC'],
         shape=['#', '#'], cshape=['#'], src='design', desc='Sp. Def +10% in battle.'),
    dict(name='Carbos', effect=('STAT_PCT', 'SPEED', 10), plus=True, group=0, bug=7, cond='SMART', types=['ELECTRIC', 'FLYING'],
         shape=['#', '#'], cshape=['#'], src='design', desc='Speed +10% in battle (moves and steps come sooner).'),
    dict(name='HP Up', effect=('HP_PCT', 10), plus=True, group=0, bug=9, cond='CUTE', types=['NORMAL', 'GRASS'],
         shape=['#', '#', '#'], cshape=['#', '#'], src='design', desc='Max HP +10% in battle.'),

    # ---- held items as programs (design; values from Emerald's item data, src/data/items.h) ------------------
    dict(name='QuickClw', effect=('QUICK_CLAW', 25), plus=False, group=0, bug=4, cond='SMART', types=['NORMAL', 'DARK'],
         shape=['#.', '##'], cshape=['##'], src='design (Quick Claw, holdEffectParam 20)',
         desc='You recover 25% faster after using a chip.'),
    dict(name='KingRock', effect=('KINGS_ROCK', 10), plus=False, group=0, bug=7, cond='COOL', types=['ROCK', 'STEEL'],
         shape=['###', '.#.'], cshape=['##'], src="design (King's Rock, HOLD_EFFECT_FLINCH param 10)",
         desc='Your hits stun the foe 10% of the time.'),
    dict(name='ScopLens', effect=('SCOPE_LENS', 1), plus=False, group=0, bug=7, cond='COOL', types=['PSYCHIC', 'DARK'],
         shape=['##', '##'], cshape=['#.', '##'], src='design (Scope Lens, HOLD_EFFECT_SCOPE_LENS)',
         desc='Critical hits are more likely (+1 stage).'),
    dict(name='BrtPowdr', effect=('BRIGHT_POWDER', 10), plus=False, group=0, bug=3, cond='BEAUTY', types=['BUG', 'PSYCHIC'],
         shape=['#.', '##', '.#'], cshape=['##', '.#'], src='design (BrightPowder, HOLD_EFFECT_EVASION_UP param 10)',
         desc="Foes' warnings last 10% longer against you."),
    dict(name='Leftovrs', effect=('LEFTOVERS', 16), plus=False, group=6, bug=9, cond='CUTE', types=['NORMAL', 'GRASS'],
         shape=['###', '#.#'], cshape=['###'], src='design (Leftovers: 1/16 max HP each turn)',
         desc='Heal 1/16 of max HP every turn.'),
    dict(name='ShelBell', effect=('SHELL_BELL', 8), plus=False, group=6, bug=9, cond='CUTE', types=['WATER', 'NORMAL'],
         shape=['.#.', '###'], cshape=['##'], src='design (Shell Bell, HOLD_EFFECT_SHELL_BELL param 8)',
         desc='Heal 1/8 of the damage you deal.'),
    dict(name='FocsBand', effect=('FOCUS_BAND', 10), plus=False, group=7, bug=1, cond='TOUGH', types=['FIGHTING'],
         shape=['#', '#', '#'], cshape=['#', '#'], src='design (Focus Band, HOLD_EFFECT_FOCUS_BAND param 10)',
         desc='10% chance to survive a fainting hit with 1 HP.'),
    dict(name='ChoiceBd', effect=('CHOICE_BAND', 50), plus=False, group=8, bug=4, cond='COOL', types=['FIGHTING', 'NORMAL'],
         shape=['###', '.#.', '.#.'], cshape=['###', '.#.'], src='design (Choice Band: Attack x1.5, locked to one move)',
         desc='Attack x1.5, but only 1 chip per Custom.'),
    dict(name='LuckyEgg', effect=('LUCKY_EGG', 50), plus=False, group=0, bug=6, cond='CUTE', types=['NORMAL'],
         shape=['##', '#.'], cshape=['#'], src='design (Lucky Egg: EXP x1.5)',
         desc='EXP x1.5 after battle.'),
    dict(name='AmuletCn', effect=('AMULET_COIN', 100), plus=False, group=0, bug=6, cond='CUTE', types=['NORMAL', 'STEEL'],
         shape=['#.', '##'], cshape=['#'], src='design (Amulet Coin: prize money x2)',
         desc='Prize money x2.'),
]

# Type-boosting items (Gen 3: +10%, holdEffectParam 10, applied in CalculateBaseDamage, src/pokemon.c:3173).
# Plus parts; one per type; the colour is that type.
TYPE_ITEMS = [
    ('Charcoal', 'FIRE'), ('MystcWtr', 'WATER'), ('Magnet', 'ELECTRIC'), ('MircSeed', 'GRASS'),
    ('NevMeltI', 'ICE'), ('BlkBelt', 'FIGHTING'), ('PoisBarb', 'POISON'), ('SoftSand', 'GROUND'),
    ('ShrpBeak', 'FLYING'), ('TwstSpn', 'PSYCHIC'), ('SlvPowdr', 'BUG'), ('HardStn', 'ROCK'),
    ('SpellTag', 'GHOST'), ('DrgnFang', 'DRAGON'), ('BlkGlass', 'DARK'), ('MetlCoat', 'STEEL'), ('SilkScrf', 'NORMAL'),
]
PHYSICAL = {'NORMAL', 'FIGHTING', 'FLYING', 'POISON', 'GROUND', 'ROCK', 'BUG', 'GHOST', 'STEEL'}  # Gen 3 IS_TYPE_PHYSICAL
for nm, t in TYPE_ITEMS:
    PROGRAMS.append(dict(name=nm, effect=('TYPE_BOOST', t, 10), plus=True, group=0, bug=7,
                         cond='COOL' if t in PHYSICAL else 'BEAUTY', types=[t],
                         shape=['##'], cshape=['#'], src='design (Gen 3 type item, +10%)',
                         desc='%s moves +10%%.' % t.capitalize()))

# Abilities as fixed programs (design): every Pokémon's ability sits on the left end of the command line, in the
# Pokémon's first type, and can't be moved. Size tiers (TUNE): 1 cell for minor abilities, 3 cells (an L) for the
# strongest; everything else 2 cells. A few abilities also grant a program effect (BN-style twins).
ABILITY_SIZE_3 = ['WONDER_GUARD', 'HUGE_POWER', 'PURE_POWER', 'SPEED_BOOST', 'SHADOW_TAG', 'ARENA_TRAP', 'DRIZZLE',
                  'DROUGHT', 'SAND_STREAM', 'LEVITATE', 'INTIMIDATE']
ABILITY_SIZE_1 = ['RUN_AWAY', 'PICKUP', 'ILLUMINATE', 'STENCH', 'KEEN_EYE', 'OWN_TEMPO', 'OBLIVIOUS', 'SUCTION_CUPS',
                  'STICKY_HOLD', 'CACOPHONY', 'EARLY_BIRD', 'SHIELD_DUST', 'PLUS', 'MINUS', 'FORECAST', 'LIMBER',
                  'TRUANT', 'MAGMA_ARMOR', 'WATER_VEIL', 'INSOMNIA', 'VITAL_SPIRIT', 'IMMUNITY', 'HYPER_CUTTER',
                  'CLEAR_BODY', 'WHITE_SMOKE', 'SOUNDPROOF', 'LIQUID_OOZE', 'DAMP', 'SAND_VEIL', 'CUTE_CHARM']
ABILITY_GRANTS = {
    'LEVITATE': ['FLOAT_SHOES', 'AIR_SHOES'],   # floats: panels and holes don't matter
    'STURDY': ['UNDER_SHIRT'],                  # BN-ified Sturdy
    'INNER_FOCUS': ['SUPER_ARMOR'],             # Gen 3 Inner Focus already blocks flinch
}
