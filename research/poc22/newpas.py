# POC-22b candidate Program Advances: (name, recipe, effect spec)
NEW = [
 # early (before the second Gym): Route 101-116, Petalburg Woods, Rusturf Tunnel, Granite Cave
 ('SILVER STORM', ['WHIRLWIND', 'GUST', 'SILVER_WIND'],          'WAVE type=BUG power=150 rows=3 speeddown',       'BUG 150 wind over all three rows, slows (code W)'),
 ('SKY RAID',     ['QUICK_ATTACK', 'PECK', 'WING_ATTACK'],      'DASH type=FLYING power=130',                    'FLYING 130 dive down the row (code A)'),
 ('AMBUSH FANG',  ['SAND_ATTACK', 'BITE', 'CRUNCH'],            'LOCKON type=DARK power=160 accdown',            'DARK 160, locks on, never misses, lowers accuracy (code N)'),
 ('MAELSTROM',    ['RAIN_DANCE', 'WATER_GUN', 'WHIRLPOOL'],     'TORNADO type=WATER power=35 hits=4 speeddown',  'WATER 4 x 35 whirl 2 panels ahead, slows (code R)'),
 ('SPORE BLOOM',  ['LEECH_SEED', 'STUN_SPORE', 'MEGA_DRAIN'],   'SPREADER type=GRASS power=110 status=PAR drain=30', 'GRASS 110 burst on the target and around it + paralysis (code G)'),
 ('SUMO SLAM',    ['FOCUS_ENERGY', 'ARM_THRUST', 'VITAL_THROW'], 'GOLEMHIT type=FIGHTING power=140 crit',        'FIGHTING 140 slam on three panels, guaranteed crit (code K)'),
 # mid game
 ('STEEL RAM',    ['METAL_SOUND', 'TACKLE', 'IRON_TAIL'],       'DASH type=STEEL power=170',                     'STEEL 170 charge down the row (code L)'),
 ('BLADE SWARM',  ['SWORDS_DANCE', 'FURY_CUTTER', 'SLASH'],     'WIDESWORD type=BUG power=170 crit',             'BUG 170 wide cut, guaranteed crit (code U)'),
 ('ECHO BLAST',   ['SUPERSONIC', 'SCREECH', 'HYPER_VOICE'],     'WAVE type=NORMAL power=160 rows=3 status=CONF', 'NORMAL 160 sound wave over all three rows + confusion (code V)'),
 ('TOXIC FOG',    ['POISON_GAS', 'SMOG', 'SLUDGE'],             'FIELD type=POISON power=120 nofaint accdown panels=poison', 'POISON 120 on every enemy panel, poisons them, lowers accuracy (code O)'),
 ('QUICKSAND',    ['SAND_ATTACK', 'SAND_TOMB', 'DIG'],          'DIG type=GROUND power=170 speeddown',           'GROUND 170 from below, slows (code Q)'),
 ('HAUNTING',     ['ASTONISH', 'SHADOW_PUNCH', 'SHADOW_BALL'],  'LOCKON type=GHOST power=170 crit',              'GHOST 170, locks on, guaranteed crit (code N)'),
 ('AURORA',       ['POWDER_SNOW', 'ICY_WIND', 'AURORA_BEAM'],   'SWEEP type=ICE power=160 speeddown',            'ICE 160 beam sweeping the enemy area, slows (code I)'),
 ('FOSSIL FURY',  ['ROCK_TOMB', 'ANCIENT_POWER', 'ROCK_SLIDE'], 'GOLEMHIT type=ROCK power=180 panels=crack',     'ROCK 180 slam on three panels, cracks them (code Q)'),
 # the starters' evolutions (mid to late)
 ('VERDANT EDGE', ['SWORDS_DANCE', 'FURY_CUTTER', 'LEAF_BLADE'], 'LIFESWORD type=GRASS power=200 crit',           'GRASS 200, two columns of blades, guaranteed crit (code U)'),
 ('BLAZING FURY', ['FOCUS_ENERGY', 'DOUBLE_KICK', 'BLAZE_KICK'], 'LINE3 type=FIRE power=70 hits=3 status=BRN',   'FIRE 3 x 70 kicks down 3 panels + burn (code K)'),
 ('SWAMP SURGE',  ['MUD_SPORT', 'WATER_PULSE', 'MUDDY_WATER'],  'WAVE type=WATER power=180 rows=3 accdown',      'WATER 180 wave over all three rows, lowers accuracy (code R)'),
 # late
 ('DRAGONFIRE',   ['SUNNY_DAY', 'DRAGON_BREATH', 'FLAMETHROWER'], 'WAVE type=DRAGON power=200 status=BRN',      'DRAGON 200 fire wave down the row + burn (code S)'),
]
