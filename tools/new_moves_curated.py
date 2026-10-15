"""POC-31: the Gen 4 moves added to the game (Khaled's picks M1c M2a M3b M4a M5a M6a).

The moves are the 46 of tools/learnset_ladders.py (damaging moves Hoenn Pokemon learn by level-up in Platinum, minus the
ones that need a grid mechanic of their own). Their numbers (power, accuracy, PP, priority, effect chance, target,
contact) are Platinum's and are read from PokeAPI's CSV tables by tools/gen_new_moves.py; nothing numeric is typed here.

Per move, this file only holds what PokeAPI can't give:
  anim  the Emerald battle animation the move borrows (data/battle_anim_scripts.s; used outside grid battles, and by
        tools/gen_move_sounds.py for the move's sounds)
  desc  the summary-screen description (our words, Emerald's style: two short lines)
The grid side lives where every other move's does: tools/attacks_curated.py (kind + fx=, the BN6 effect drawn on
impact in the type's colours) and tools/lanes_curated.py (codes).

Effects: PokeAPI's move effect ids 1-214 are Gen 3's, in the same order as Emerald's EFFECT_* (EFFECT_x = id - 1);
gen_new_moves.py uses that. The Gen 4 effects these moves need are new EFFECT_* constants (EFFECTS below), played by
the grid (src/pkbn/grid_moves.c); in Emerald's own battle engine they hit like EFFECT_HIT.
"""

# PokeAPI effect id -> our new effect (include/constants/battle_move_effects.h)
EFFECTS = {
    218: 'EFFECT_WAKE_UP_SLAP',     # double power against a sleeping target, wakes it
    219: 'EFFECT_HAMMER_ARM',       # lowers the user's Speed
    222: 'EFFECT_BRINE',            # double power against a target at half HP or less
    225: 'EFFECT_HIT',              # Pluck / Bug Bite eat the target's berry: grid battles have no held berries
    230: 'EFFECT_CLOSE_COMBAT',     # lowers the user's Defense and Sp. Def
    254: 'EFFECT_FLARE_BLITZ',      # 1/3 recoil, may burn
    270: 'EFFECT_HEAD_SMASH',       # 1/2 recoil
    274: 'EFFECT_FANG',             # Fire Fang: may burn, may flinch (separate rolls)
    275: 'EFFECT_FANG',             # Ice Fang: may freeze, may flinch
    276: 'EFFECT_FANG',             # Thunder Fang: may paralyse, may flinch
    277: 'EFFECT_SP_ATK_UP_HIT',    # Charge Beam: may raise the user's Sp. Atk
}
NEW_EFFECTS = ['EFFECT_WAKE_UP_SLAP', 'EFFECT_HAMMER_ARM', 'EFFECT_BRINE', 'EFFECT_CLOSE_COMBAT', 'EFFECT_FLARE_BLITZ',
               'EFFECT_HEAD_SMASH', 'EFFECT_FANG', 'EFFECT_SP_ATK_UP_HIT']

MOVES = {
 'DISCHARGE':    ('SPARK',          'Loosens a flare of sparks\nall around. May paralyze.'),
 'WAKE_UP_SLAP': ('DOUBLE_SLAP',    'Hits a sleeping foe hard,\nbut also wakes it up.'),
 'AIR_SLASH':    ('AIR_CUTTER',     'Attacks with a blade of\nair. May cause flinching.'),
 'ZEN_HEADBUTT': ('HEADBUTT',       'A headbutt of pure will.\nMay cause flinching.'),
 'AQUA_JET':     ('QUICK_ATTACK',   'Lunges at high speed.\nIt always strikes first.'),
 'PSYCHO_CUT':   ('SLASH',          'Tears with psychic blades.\nHigh critical-hit ratio.'),
 'POISON_JAB':   ('POISON_STING',   'Stabs with a toxic spike.\nMay poison the foe.'),
 'STONE_EDGE':   ('ROCK_SLIDE',     'Stabs with sharp stones.\nHigh critical-hit ratio.'),
 'MAGNET_BOMB':  ('ZAP_CANNON',     'A steel bomb that sticks\nto the foe. Never misses.'),
 'MIRROR_SHOT':  ('FLASH',          'A flash of light off its\nbody. May lower accuracy.'),
 'DOUBLE_HIT':   ('DOUBLE_KICK',    'Slams the foe with its\ntail twice in a row.'),
 'PLUCK':        ('PECK',           'Pecks the foe with its\nsharp beak.'),
 'MUD_BOMB':     ('MUD_SLAP',       'Hurls a ball of mud at the\nfoe. May lower accuracy.'),
 'GUNK_SHOT':    ('SLUDGE_BOMB',    'Shoots filthy garbage.\nMay poison the foe.'),
 'CHARGE_BEAM':  ('THUNDERBOLT',    'Fires a beam of sparks.\nMay raise SP. ATK.'),
 'HAMMER_ARM':   ('MEGA_PUNCH',     "Swings a heavy fist down.\nLowers the user's SPEED."),
 'BRINE':        ('WATER_PULSE',    'Hits harder if the foe has\nhalf its HP or less.'),
 'DRAGON_PULSE': ('DRAGON_BREATH',  'A shock wave from its\nmouth hits the foe.'),
 'POWER_GEM':    ('ANCIENT_POWER',  'Attacks with rays of light\nthat sparkle like diamonds.'),
 'X_SCISSOR':    ('FURY_CUTTER',    'Slashes the foe with\ncrossed scythes or claws.'),
 'ICE_FANG':     ('BITE',           'Bites with icy fangs. May\nfreeze or cause flinching.'),
 'AQUA_TAIL':    ('IRON_TAIL',      'Swings its tail like a\nvicious wave in a storm.'),
 'CROSS_POISON': ('CROSS_CHOP',     'A slash that may poison.\nHigh critical-hit ratio.'),
 'OMINOUS_WIND': ('SILVER_WIND',    "An eerie wind. May raise\nall the user's stats."),
 'LEAF_STORM':   ('RAZOR_LEAF',     'Whips up a storm of leaves.\nSharply lowers SP. ATK.'),
 'NIGHT_SLASH':  ('SLASH',          'Slashes at an opening.\nHigh critical-hit ratio.'),
 'CLOSE_COMBAT': ('SUPERPOWER',     "Fights up close. Lowers\nthe user's DEF and SP. DEF."),
 'LAVA_PLUME':   ('HEAT_WAVE',      'Scarlet flames torch all\naround. May inflict a burn.'),
 'EARTH_POWER':  ('EARTHQUAKE',     'The ground erupts under the\nfoe. May lower SP. DEF.'),
 'THUNDER_FANG': ('BITE',           'Bites with charged fangs.\nMay paralyze or flinch.'),
 'FIRE_FANG':    ('BITE',           'Bites with fiery fangs.\nMay burn or flinch.'),
 'GIGA_IMPACT':  ('DOUBLE_EDGE',    'Charges with all its might.\nThe user must rest after.'),
 'ENERGY_BALL':  ('MAGICAL_LEAF',   'Fires the power of nature.\nMay lower SP. DEF.'),
 'FLARE_BLITZ':  ('FLAME_WHEEL',    'A fiery charge that hurts\nthe user. May burn.'),
 'BRAVE_BIRD':   ('DRILL_PECK',     'A low, wings-tucked dive.\nIt also hurts the user.'),
 'BUG_BITE':     ('BITE',           'Bites the foe with sharp\nmandibles.'),
 'BUG_BUZZ':     ('HYPER_VOICE',    'A buzzing sound wave.\nMay lower SP. DEF.'),
 'SEED_BOMB':    ('EGG_BOMB',       'Slams a barrage of hard\nseeds down on the foe.'),
 'FORCE_PALM':   ('ARM_THRUST',     'A shock wave from the palm.\nMay paralyze the foe.'),
 'SHADOW_SNEAK': ('SHADOW_PUNCH',   'Strikes from its shadow.\nIt always strikes first.'),
 'SHADOW_CLAW':  ('CRUSH_CLAW',     'Slashes with a shadow claw.\nHigh critical-hit ratio.'),
 'IRON_HEAD':    ('HEADBUTT',       'Slams with a steel-hard\nhead. May cause flinching.'),
 'ICE_SHARD':    ('ICICLE_SPEAR',   'Hurls chunks of ice.\nIt always strikes first.'),
 'HEAD_SMASH':   ('TAKE_DOWN',      'A reckless headbutt that\nbadly hurts the user too.'),
 'BULLET_PUNCH': ('MACH_PUNCH',     'A punch as fast as a\nbullet. It strikes first.'),
 'FLASH_CANNON': ('ZAP_CANNON',     'Fires a burst of light.\nMay lower SP. DEF.'),
}
