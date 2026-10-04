"""How every Gen 3 move plays on the 6x3 grid (source of truth; generates src/pkbn/move_table.c).

Each entry:  'MOVE': 'KIND [modifiers]'   # why / which BN6 chip it borrows from
The KINDS table below names the BN6 chip each kind is modelled on, with its in-game description
(data/textscript/TextScriptChipDescriptions0.s) and attack family (data/ChipDataArr.s, attack_family/sub).

Modifiers
  hits=N | hits=2-5 | hits=party   number of hits (2-5 uses Gen 3's multi-hit odds; party = Beat Up)
  rows=3                           CANNON / WAVE / SHOCKWAVE travel in the user's row and both neighbours
  plus | x | square | single       BOMB blast pattern
  slow                             slower than the kind's default (bigger telegraph / longer flight)
  fast                             faster than the kind's default
  invuln                           the user can't be hit while the attack winds up (Fly, Bounce, Dig, Dive)
  charge=N                         N frames of wind-up before it fires; the user is exposed
  hold                             a hit pins the target in place for a while (Gen 3 trapping moves)
  push                             a hit knocks the target one panel back (BN AirShot)
  recharge                         Gen 3 recharge: the user can't pick chips at the next Custom (review note)
Everything else (drain, recoil, burn chance, high crit, fixed damage...) comes from the move's own
Gen 3 effect id in gBattleMoves, not from this file.
"""

KINDS = {
 # ---- hits from where you stand -------------------------------------------------------------
 'CANNON':    ('Hits the first target down the row.', 'Cannon (0x14) "Cannon to attack 1 enemy"'),
 'AIRSHOT':   ('Cannon that knocks the target 1 panel back.', 'AirShot (0x21) "Knock enmy back 1 square"'),
 'VULCAN':    ('Rapid shots; each hits the first target and the panel behind it.', 'Vulcan1 (0x17) "3-shot to pierce 1 panel!"'),
 'SPREADER':  ('Cannon whose hit splashes the 8 panels around the target.', 'Spreadr1 (0x25) "Spreads damg to adj panls"'),
 'SWORD':     ('The panel in front of you.', 'Sword (0x13/0) "Cuts enmy in front! Range: 1"'),
 'LONGSWORD': ('2 panels ahead in your row.', 'LongSwrd (0x13/2) "Range: 2"'),
 'WIDESWORD': ('The column in front of you, all 3 rows.', 'WideSwrd (0x13/1) "Range: 3"'),
 'LIFESWORD': ('2 columns x 3 rows in front of you.', 'LifeSrd (BN6 Program Advance of the Sword family)'),
 'LINE3':     ('3 panels ahead in your row.', 'FireSwrd (0x13/0xC) "Cut enmy 3sq fwrd w/fire!"'),
 'DASH':      ('Charge through your whole row ahead (up to 5 panels).', 'review: Rollout / Volt Tackle / Waterfall / Pursuit'),
 'CONE':      ('1 panel ahead, then all 3 rows 2 ahead.', 'GunDelS1 (0x37) - review: "Gun Del Sol pattern (cone basically)"'),
 'TORNADO':   ('A multi-hit storm on the panel 2 ahead.', 'Tornado (0x2F/1) "8hit strm 2 squares ahead"'),
 # ---- appears on the target --------------------------------------------------------------------
 'FIREHIT':   ("Spawns on the target's panel after a short warning; step away in time to dodge.", 'FireHit1 (0x1C/8) "Slams closest enemy"'),
 'GOLEMHIT':  ("Like FireHit but slams the target's panel and the panels above and below.", 'GolmHit1 (0x1C/0x15) "Hit 3panl area arnd clst enmy"'),
 'METEORS':   ('Several rocks drop on the enemy area, aimed near the target.', 'Meteors (0x15/0x10) "Drop many meteor on enmy area"'),
 'DIG':       ('Vanish (can\'t be hit), then burst out under the target after a warning.', 'SandWrm1 (0x1C/0xC) "Attk enmy from rear w/snakarm"'),
 'DELAYED':   ('Nothing happens now; a fast shot fires down your row later.', 'review: Future Sight / Doom Desire'),
 'FIELD':     ('Hits the whole enemy area after a warning. The user faints.', 'Gen 3: Explosion / Self-Destruct hit every foe'),
 # ---- things that travel ------------------------------------------------------------------------
 'BOMB':      ('Thrown 3 panels ahead; blast pattern on landing.', 'MiniBomb (0x12/0) "Throws a MiniBomb 3sq ahead"; BigBomb "9 panl bomb"'),
 'SHOCKWAVE': ('A ground wave that rolls along the row, panel by panel.', 'WaveArm1 (0x31) "fire trap wave"; Mettaur-style shockwave'),
 'WAVE':      ('A travelling wave you can see coming (1 or 3 rows).', 'WideSht (0x30) "Fires 3sq shotgun blast!"'),
 'AIRHOCKEY': ('A puck that flies diagonally and bounces off the walls.', 'AirHocky (0x26) "Bounce the puck off walls"'),
 'BALL':      ('A slow ball down your row. Low-accuracy moves fly slower, so they are easy to dodge.', 'Thunder (0x1F) "Pralyzing electric attack!" (slow ball); review: low accuracy = slow projectile'),
 'LOCKON':    ('Locks onto the target, then a hit that can\'t be dodged.', 'MachGun1 (0x29) "Fire 9sts at row w/ clst enmy"'),
 'SWEEP':     ('Program Advance only: a beam sweeps the enemy area row by row.', 'design (Mega Solar Beam)'),
 # ---- no damage ---------------------------------------------------------------------------------------
 'BARRIER':   ('Absorbs the next hit (Gen 3 Protect odds).', 'Barrier (0x15/4) "Nullifies 10 HP of damage"'),
 'STATS':     ('Stat stages; always lands, ignores Barrier and dodging.', 'design rule (POC-3)'),
 'STATUS':    ('A status effect that always lands wherever the target stands.', 'review note on Thunder Wave'),
 'PANEL':     ('Changes panels: poison, cracked, holy, grass.', 'PoisSeed "Makes 9sq poisn swp 3sq ahead"; HolyPanl; GrasSeed; object_panel_setPoison (object.s:2517)'),
 'SELF':      ('Something the user does to itself: heal, cure, shield, set up.', 'Recov10 (0x20) "Recovers 10HP"'),
 'WEATHER':   ('Gen 3 weather for 5 turns (one turn = one Custom gauge).', 'Gen 3 gBattleWeather'),
 'BATON':     ('Baton Pass: switch, keeping stat stages; ends the chain.', 'POC-4'),
 'ASSIST':    ('A benched Pokemon pops in and uses one of its moves.', 'POC-4'),
 'CALL':      ('Uses another move (Metronome, Sleep Talk, Mirror Move, Nature Power).', 'Gen 3 move-calling effects'),
 'NOTHING':   ('Nothing happens (Splash).', 'Gen 3'),
 'NONE':      ('Not on the grid yet.', ''),
}

ATTACKS = {
 # Normal / physical basics
 'POUND':         'SWORD',
 'KARATE_CHOP':   'SWORD',                    # high crit (effect)
 'DOUBLE_SLAP':   'SWORD hits=2-5',
 'COMET_PUNCH':   'SWORD hits=2-5',
 'MEGA_PUNCH':    'FIREHIT slow',             # big fist from above; 85% acc = longer warning
 'PAY_DAY':       'CANNON',
 'FIRE_PUNCH':    'SWORD',
 'ICE_PUNCH':     'SWORD',
 'THUNDER_PUNCH': 'SWORD',
 'SCRATCH':       'SWORD',
 'VICE_GRIP':     'SWORD',
 'GUILLOTINE':    'NONE',                     # removed (OHKO)
 'RAZOR_WIND':    'WAVE rows=3 charge=60',    # review: "quite slow to launch"; Gen 3 hits both foes
 'SWORDS_DANCE':  'STATS',
 'CUT':           'WIDESWORD',                # a cut = BN WideSwrd
 'GUST':          'AIRSHOT',                  # wind pushes
 'WING_ATTACK':   'WIDESWORD',                # review
 'WHIRLWIND':     'STATUS',                   # blows the target to its back column (BN GoingRd "Push an enemy to the back")
 'FLY':           'BOMB plus slow invuln',    # review: slow bomb, immune while throwing, long recovery
 'BIND':          'SWORD hold',
 'SLAM':          'LONGSWORD',
 'VINE_WHIP':     'LONGSWORD',                # vines reach 2
 'STOMP':         'SWORD',
 'DOUBLE_KICK':   'LINE3 hits=2',             # review: 3 columns
 'MEGA_KICK':     'LINE3',                    # review
 'JUMP_KICK':     'LINE3',                    # review; Gen 3 crash damage if it hits nothing
 'ROLLING_KICK':  'LINE3',                    # review
 'SAND_ATTACK':   'STATS',
 'HEADBUTT':      'SWORD',
 'HORN_ATTACK':   'LONGSWORD',                # horn reach
 'FURY_ATTACK':   'LONGSWORD hits=2-5',
 'HORN_DRILL':    'NONE',                     # removed (OHKO)
 'TACKLE':        'SWORD',
 'BODY_SLAM':     'LONGSWORD',
 'WRAP':          'SWORD hold',
 'TAKE_DOWN':     'DASH',                     # STAMPEDE's charge; recoil from effect
 'THRASH':        'LIFESWORD',                # review: Life Sword 2x3
 'DOUBLE_EDGE':   'DASH',
 'TAIL_WHIP':     'STATS',
 'POISON_STING':  'LONGSWORD',                # review
 'TWINEEDLE':     'LONGSWORD hits=2',         # review
 'PIN_MISSILE':   'VULCAN hits=2-5',
 'LEER':          'STATS',
 'BITE':          'SWORD',
 'GROWL':         'STATS',
 'ROAR':          'STATUS',                   # push to back column, like Whirlwind
 'SING':          'BALL',                     # review: low accuracy -> slow, dodgeable projectile
 'SUPERSONIC':    'BALL',                     # review
 'SONIC_BOOM':    'NONE',                     # removed
 'DISABLE':       'NONE',                     # removed
 'ACID':          'CANNON',                   # review
 'EMBER':         'CANNON',
 'FLAMETHROWER':  'LINE3',                    # a jet of flame 3 ahead (BN FireBrn "Crcks 3 sqrs ahd with fire")
 'MIST':          'SELF',                     # Gen 3: stat drops blocked for 5 turns
 'WATER_GUN':     'CANNON',
 'HYDRO_PUMP':    'AIRSHOT',                  # the water pressure pushes
 'SURF':          'LIFESWORD',                # review
 'ICE_BEAM':      'CANNON',
 'BLIZZARD':      'CONE',                     # review: Gun Del Sol
 'PSYBEAM':       'CANNON',
 'BUBBLE_BEAM':   'CANNON',
 'AURORA_BEAM':   'CANNON',
 'HYPER_BEAM':    'CANNON recharge',          # review: no chips at the next Custom
 'PECK':          'SWORD',
 'DRILL_PECK':    'LONGSWORD push',           # BN DrilArm "Knocks enmy 2sq away"
 'SUBMISSION':    'SWORD',
 'LOW_KICK':      'WIDESWORD',                # review
 'COUNTER':       'SWORD',                    # Gen 3: 2x the physical damage taken (here: in the last 2 seconds)
 'SEISMIC_TOSS':  'SWORD',                    # level = damage (effect)
 'STRENGTH':      'SWORD push',               # the boulder-pushing move pushes
 'ABSORB':        'CANNON',
 'MEGA_DRAIN':    'CANNON',
 'LEECH_SEED':    'BALL',                     # a seed you can dodge; seeded = drained every turn
 'GROWTH':        'STATS',
 'RAZOR_LEAF':    'WIDESWORD',                # review
 'SOLAR_BEAM':    'CANNON charge=90',         # Gen 3: no charge in sun
 'POISON_POWDER': 'BALL',
 'STUN_SPORE':    'BALL',
 'SLEEP_POWDER':  'BALL',                     # review
 'PETAL_DANCE':   'LIFESWORD',                # rampage family = Thrash
 'STRING_SHOT':   'STATS',
 'DRAGON_RAGE':   'CANNON',                   # fixed 40
 'FIRE_SPIN':     'AIRHOCKEY hold',           # review: Air Hockey
 'THUNDER_SHOCK': 'CANNON',
 'THUNDERBOLT':   'CANNON',
 'THUNDER_WAVE':  'STATUS',                   # review: always lands, through Barrier
 'THUNDER':       'FIREHIT slow',             # bolt from the sky on the target; in rain it can't miss -> lock-on
 'ROCK_THROW':    'BOMB plus',
 'EARTHQUAKE':    'SHOCKWAVE rows=3',         # rolls through the whole enemy area
 'FISSURE':       'NONE',                     # removed (OHKO)
 'DIG':           'DIG',
 'TOXIC':         'PANEL',                    # review: poison swamp 3x3, 3 ahead (BN PoisSeed)
 'CONFUSION':     'CANNON',
 'PSYCHIC':       'FIREHIT',                  # telekinetic crush on the target's panel
 'HYPNOSIS':      'BALL',                     # review
 'MEDITATE':      'STATS',
 'AGILITY':       'STATS',
 'QUICK_ATTACK':  'FIREHIT fast',             # review: priority = FireHit
 'RAGE':          'SWORD',
 'TELEPORT':      'SELF',                     # blink to a random panel of your area
 'NIGHT_SHADE':   'CANNON',                   # level = damage
 'MIMIC':         'CALL',                     # copies the foe's last move (as Mirror Move)
 'SCREECH':       'STATS',
 'DOUBLE_TEAM':   'NONE',                     # removed
 'RECOVER':       'SELF',
 'HARDEN':        'STATS',
 'MINIMIZE':      'NONE',                     # removed
 'SMOKESCREEN':   'STATS',
 'CONFUSE_RAY':   'STATUS',
 'WITHDRAW':      'STATS',
 'DEFENSE_CURL':  'STATS',                    # also doubles Rollout / Ice Ball (Gen 3)
 'BARRIER':       'STATS',                    # the move Barrier (Def +2), not the BN chip
 'LIGHT_SCREEN':  'PANEL',                    # holy panels around you (BN HolyPanl halves damage)
 'HAZE':          'SELF',                     # resets every stat stage
 'REFLECT':       'PANEL',                    # holy panels around you
 'FOCUS_ENERGY':  'SELF',                     # crit stage +2
 'BIDE':          'SELF',                     # stores damage for 2 turns, then a Cannon of 2x
 'METRONOME':     'CALL',
 'MIRROR_MOVE':   'CALL',
 'SELF_DESTRUCT': 'FIELD',
 'EGG_BOMB':      'BOMB plus',
 'LICK':          'SWORD',
 'SMOG':          'CONE',                     # a cloud
 'SLUDGE':        'CANNON',
 'BONE_CLUB':     'LONGSWORD',
 'FIRE_BLAST':    'BOMB x',                   # review: centre + the 4 diagonals (star)
 'WATERFALL':     'DASH',                     # review: whole row
 'CLAMP':         'WIDESWORD hold',           # review
 'SWIFT':         'LOCKON',
 'SKULL_BASH':    'DASH charge=60',           # Gen 3 charges a turn
 'SPIKE_CANNON':  'VULCAN hits=2-5',
 'CONSTRICT':     'SWORD',
 'AMNESIA':       'STATS',
 'KINESIS':       'STATS',
 'SOFT_BOILED':   'SELF',
 'HI_JUMP_KICK':  'LINE3',                    # review
 'GLARE':         'BALL',                     # 75% accuracy -> slow projectile rule
 'DREAM_EATER':   'CANNON',                   # only works on a sleeping target (effect)
 'POISON_GAS':    'PANEL',                    # review: poison panels around the target
 'BARRAGE':       'BOMB single hits=2-5',     # a volley of small bombs
 'LEECH_LIFE':    'LIFESWORD',                # review
 'LOVELY_KISS':   'BALL',                     # review
 'SKY_ATTACK':    'DASH charge=90',           # glows, then dives through the row
 'TRANSFORM':     'NONE',
 'BUBBLE':        'BALL',                     # damaging bubbles drift slowly
 'DIZZY_PUNCH':   'SWORD',
 'SPORE':         'STATUS',                   # 100% accuracy -> always lands
 'FLASH':         'STATS',
 'PSYWAVE':       'WAVE',
 'SPLASH':        'NOTHING',
 'ACID_ARMOR':    'STATS',
 'CRABHAMMER':    'WIDESWORD',                # review
 'EXPLOSION':     'FIELD',
 'FURY_SWIPES':   'SWORD hits=2-5',
 'BONEMERANG':    'AIRHOCKEY hits=2',         # review: Air Hockey
 'REST':          'SELF',                     # full heal + sleep; review: sleep breaks when hit
 'ROCK_SLIDE':    'METEORS',
 'HYPER_FANG':    'SWORD',
 'SHARPEN':       'STATS',
 'CONVERSION':    'SELF',                     # becomes the type of one of its moves
 'TRI_ATTACK':    'CANNON rows=3',            # three beams: your row and both neighbours
 'SUPER_FANG':    'SWORD',                    # halves HP (effect)
 'SLASH':         'WIDESWORD',                # review
 'SUBSTITUTE':    'NONE',                     # removed
 'STRUGGLE':      'SWORD',
 'SKETCH':        'NONE',
 'TRIPLE_KICK':   'LINE3 hits=3',             # review; Gen 3 power 10/20/30
 'THIEF':         'SWORD',
 'SPIDER_WEB':    'STATUS',                   # pinned in place for a long time
 'MIND_READER':   'NONE',                     # removed
 'NIGHTMARE':     'STATUS',                   # sleeping target loses HP every turn
 'FLAME_WHEEL':   'LONGSWORD',
 'SNORE':         'WAVE',                     # usable while asleep
 'CURSE':         'STATS',
 'FLAIL':         'SWORD',
 'CONVERSION_2':  'NONE',
 'AEROBLAST':     'AIRSHOT',
 'COTTON_SPORE':  'STATS',
 'REVERSAL':      'SWORD',
 'SPITE':         'NONE',                     # removed
 'POWDER_SNOW':   'WAVE rows=3',
 'PROTECT':       'BARRIER',
 'MACH_PUNCH':    'FIREHIT fast',             # review: priority
 'SCARY_FACE':    'STATS',
 'FAINT_ATTACK':  'LOCKON',
 'SWEET_KISS':    'BALL',
 'BELLY_DRUM':    'SELF',
 'SLUDGE_BOMB':   'BOMB plus',
 'MUD_SLAP':      'CANNON',
 'OCTAZOOKA':     'BOMB plus',
 'SPIKES':        'PANEL',                    # cracks 3 enemy panels (BN cracked panels break when left)
 'ZAP_CANNON':    'BALL',                     # 50% accuracy: the slowest, heaviest ball
 'FORESIGHT':     'NONE',                     # removed
 'DESTINY_BOND':  'NONE',                     # removed
 'PERISH_SONG':   'NONE',                     # removed
 'ICY_WIND':      'CONE',                     # review
 'DETECT':        'BARRIER',
 'BONE_RUSH':     'VULCAN hits=2-5',
 'LOCK_ON':       'STATUS',                   # your next move becomes a lock-on (Gen 3: next move can't miss)
 'OUTRAGE':       'LIFESWORD',
 'SANDSTORM':     'WEATHER',
 'GIGA_DRAIN':    'CANNON',
 'ENDURE':        'NONE',                     # removed
 'CHARM':         'STATS',
 'ROLLOUT':       'DASH',                     # review; Gen 3 power doubles on each consecutive use
 'FALSE_SWIPE':   'WIDESWORD',                # review; leaves 1 HP
 'SWAGGER':       'STATUS',
 'MILK_DRINK':    'SELF',
 'SPARK':         'LONGSWORD',
 'FURY_CUTTER':   'SWORD',                    # power doubles on each consecutive use
 'STEEL_WING':    'WIDESWORD',                # review
 'MEAN_LOOK':     'STATUS',                   # pinned in place
 'ATTRACT':       'STATUS',
 'SLEEP_TALK':    'CALL',                     # review: random move like Metronome; usable while asleep
 'HEAL_BELL':     'SELF',
 'RETURN':        'LONGSWORD',
 'PRESENT':       'NONE',                     # removed
 'FRUSTRATION':   'LONGSWORD',
 'SAFEGUARD':     'SELF',                     # review: blocks the next status move
 'PAIN_SPLIT':    'NONE',                     # removed
 'SACRED_FIRE':   'GOLEMHIT',                 # a pillar of fire on the target's column
 'MAGNITUDE':     'SHOCKWAVE',                # random power 10-150 (effect)
 'DYNAMIC_PUNCH': 'FIREHIT slow',             # 50% accuracy: long warning, guaranteed confusion
 'MEGAHORN':      'DASH',
 'DRAGON_BREATH': 'CONE',                     # review
 'BATON_PASS':    'BATON',
 'ENCORE':        'NONE',                     # removed
 'PURSUIT':       'DASH',                     # review
 'RAPID_SPIN':    'AIRHOCKEY',                # review; also repairs your cracked panels (Gen 3 clears Spikes)
 'SWEET_SCENT':   'STATS',
 'IRON_TAIL':     'WIDESWORD',                # review
 'METAL_CLAW':    'SWORD',
 'VITAL_THROW':   'AIRHOCKEY',                # review
 'MORNING_SUN':   'SELF',
 'SYNTHESIS':     'SELF',
 'MOONLIGHT':     'SELF',
 'HIDDEN_POWER':  'CANNON',
 'CROSS_CHOP':    'WIDESWORD',                # review
 'TWISTER':       'TORNADO',                  # BN Tornado
 'RAIN_DANCE':    'WEATHER',
 'SUNNY_DAY':     'WEATHER',
 'CRUNCH':        'SWORD',
 'MIRROR_COAT':   'NONE',                     # removed
 'PSYCH_UP':      'SELF',                     # copies the foe's stat stages
 'EXTREME_SPEED': 'FIREHIT fast',             # review: priority
 'ANCIENT_POWER': 'CANNON',                   # review
 'SHADOW_BALL':   'BALL fast',
 'FUTURE_SIGHT':  'DELAYED',                  # review
 'ROCK_SMASH':    'SWORD',
 'WHIRLPOOL':     'TORNADO hold',
 'BEAT_UP':       'VULCAN hits=party',        # one hit per healthy party member (Gen 3)
 'FAKE_OUT':      'FIREHIT fast',             # priority; flinches; only right after coming in
 'UPROAR':        'NONE',                     # removed
 'STOCKPILE':     'NONE',                     # removed
 'SPIT_UP':       'NONE',                     # removed
 'SWALLOW':       'NONE',                     # removed
 'HEAT_WAVE':     'WAVE rows=3',
 'HAIL':          'WEATHER',
 'TORMENT':       'NONE',                     # removed
 'FLATTER':       'STATUS',
 'WILL_O_WISP':   'BALL',                     # 75% accuracy
 'MEMENTO':       'STATUS',                   # user faints; foe Atk/Sp.Atk -2
 'FACADE':        'SWORD',
 'FOCUS_PUNCH':   'SWORD charge=48',          # Gen 3: fails if the user is hit while focusing
 'SMELLING_SALT': 'NONE',                     # removed
 'FOLLOW_ME':     'NONE',                     # removed
 'NATURE_POWER':  'CALL',
 'CHARGE':        'SELF',                     # next Electric move x2
 'TAUNT':         'NONE',                     # removed
 'HELPING_HAND':  'NONE',                     # removed
 'TRICK':         'NONE',                     # removed
 'ROLE_PLAY':     'NONE',
 'WISH':          'SELF',                     # review: heals after the next Custom opens
 'ASSIST':        'ASSIST',
 'INGRAIN':       'PANEL',                    # grass panels under you; heals you every turn on grass
 'SUPERPOWER':    'LONGSWORD',
 'MAGIC_COAT':    'SELF',                     # review: bounces the next status move back
 'RECYCLE':       'NONE',                     # removed
 'REVENGE':       'SWORD',                    # 2x if hit in the last 2 seconds
 'BRICK_BREAK':   'SWORD',                    # also shatters Barrier and holy panels (Gen 3 breaks screens)
 'YAWN':          'STATUS',                   # sleep after the next Custom
 'KNOCK_OFF':     'SWORD push',
 'ENDEAVOR':      'SWORD',
 'ERUPTION':      'METEORS',                  # lava rocks; power falls with the user's HP
 'SKILL_SWAP':    'NONE',
 'IMPRISON':      'NONE',                     # removed
 'REFRESH':       'SELF',
 'GRUDGE':        'NONE',                     # removed
 'SNATCH':        'NONE',                     # removed
 'SECRET_POWER':  'CANNON',
 'DIVE':          'DIG',
 'ARM_THRUST':    'SWORD hits=2-5',
 'CAMOUFLAGE':    'NONE',
 'TAIL_GLOW':     'STATS',
 'LUSTER_PURGE':  'CANNON',
 'MIST_BALL':     'BOMB plus',                # review
 'FEATHER_DANCE': 'STATS',
 'TEETER_DANCE':  'STATUS',
 'BLAZE_KICK':    'LINE3',                    # review
 'MUD_SPORT':     'SELF',                     # Electric damage to you halved while in (Gen 3)
 'ICE_BALL':      'BOMB plus',                # review
 'NEEDLE_ARM':    'LONGSWORD',
 'SLACK_OFF':     'SELF',
 'HYPER_VOICE':   'WAVE rows=3',
 'POISON_FANG':   'SWORD',
 'CRUSH_CLAW':    'LINE3',                    # review
 'BLAST_BURN':    'BOMB square recharge',     # BN BigBomb 3x3
 'HYDRO_CANNON':  'AIRSHOT recharge',
 'METEOR_MASH':   'FIREHIT slow',             # a meteor fist from above
 'ASTONISH':      'FIREHIT fast',             # pops up on the target; flinches
 'WEATHER_BALL':  'BOMB plus',                # type and power follow the weather (effect)
 'AROMATHERAPY':  'SELF',
 'FAKE_TEARS':    'STATS',
 'AIR_CUTTER':    'WAVE rows=3 fast',
 'OVERHEAT':      'BOMB square',
 'ODOR_SLEUTH':   'NONE',                     # removed
 'ROCK_TOMB':     'BOMB single hold',         # rocks pin the target
 'SILVER_WIND':   'SPREADER',                 # review
 'METAL_SOUND':   'STATS',
 'GRASS_WHISTLE': 'BALL',
 'TICKLE':        'STATS',
 'COSMIC_POWER':  'STATS',
 'WATER_SPOUT':   'BOMB plus',                # review
 'SIGNAL_BEAM':   'CANNON',
 'SHADOW_PUNCH':  'LOCKON',
 'EXTRASENSORY':  'CANNON',
 'SKY_UPPERCUT':  'SWORD',                    # also hits a Pokemon in the air (Fly / Bounce)
 'SAND_TOMB':     'TORNADO hold',
 'SHEER_COLD':    'NONE',                     # removed (OHKO)
 'MUDDY_WATER':   'LIFESWORD',                # review
 'BULLET_SEED':   'VULCAN hits=2-5',
 'AERIAL_ACE':    'LOCKON',
 'ICICLE_SPEAR':  'VULCAN hits=2-5',
 'IRON_DEFENSE':  'STATS',
 'BLOCK':         'NONE',                     # removed
 'HOWL':          'STATS',
 'DRAGON_CLAW':   'WIDESWORD',                # a claw slash, like Slash
 'FRENZY_PLANT':  'SHOCKWAVE fast recharge',  # roots burst along the row
 'BULK_UP':       'STATS',
 'BOUNCE':        'BOMB plus invuln',         # review: bomb attack; in the air while it falls
 'MUD_SHOT':      'CANNON',
 'POISON_TAIL':   'WIDESWORD',                # review
 'COVET':         'SWORD',
 'VOLT_TACKLE':   'DASH',                     # review
 'MAGICAL_LEAF':  'LOCKON',
 'WATER_SPORT':   'SELF',                     # Fire damage to you halved while in (Gen 3)
 'CALM_MIND':     'STATS',
 'LEAF_BLADE':    'WIDESWORD',                # review
 'DRAGON_DANCE':  'STATS',
 'ROCK_BLAST':    'VULCAN hits=2-5',
 'SHOCK_WAVE':    'LOCKON',
 'WATER_PULSE':   'WAVE',
 'DOOM_DESIRE':   'DELAYED',                  # review (Future Sight family)
 'PSYCHO_BOOST':  'CANNON',
}


# Program Advances (recipes: lanes_curated.PROGRAM_ADVANCES). How each new move plays on the grid.
# Modifiers: type=T power=N rows=3 hits=N crit status=BRN|PAR|FRZ|CONF|TOX drain=50|100 partyheal
#            panels=crack|poison hitonce nofaint speeddown accdown fast
PA_EFFECTS = {
 'MEGA SOLAR BEAM': 'SWEEP type=GRASS power=180',                       # sweeps the enemy area row by row, no charge
 'STORM CALLER':    'FIELD type=ELECTRIC power=150 nofaint fast',       # a bolt on every enemy panel
 'TSUNAMI':         'WAVE type=WATER power=200 rows=3',                 # a wave across all three rows
 'PERMAFROST':      'LOCKON type=ICE power=160 status=FRZ speeddown',   # freezes the target in place + slows
 'EARTH RENDER':    'SHOCKWAVE type=GROUND power=180 rows=3 panels=crack', # cracks every enemy panel it rolls over
 'DREAM DEVOURER':  'LOCKON type=PSYCHIC power=160 drain=50 partyheal', # drain that heals the whole party
 'VENOM STORM':     'METEORS type=POISON power=140 hits=5 hitonce panels=poison', # poison rain: each drop leaves a poison panel
 'DRAGON RUSH':     'DASH type=DRAGON power=200',                       # no confusion after
 'THOUSAND FISTS':  'LINE3 type=FIGHTING power=30 hits=6 crit',         # 6 x 30, guaranteed crits
 'STAMPEDE':        'DASH type=NORMAL power=120',                       # no recoil
 'MUDSLIDE':        'WAVE type=GROUND power=90 rows=3 accdown',         # muddies the enemy (accuracy down)
 'ROLLING THUNDER': 'AIRHOCKEY type=ROCK power=40 hits=5',              # 5 rolling hits bouncing between rows
 'Z-HYDRO':         'CANNON type=WATER power=240',
 'Z-FLARE':         'CANNON type=FIRE power=240 status=BRN',
 'Z-VOLT':          'CANNON type=ELECTRIC power=240 status=PAR',
 'Z-FROST':         'CANNON type=ICE power=240 status=FRZ',
 'Z-PSI':           'CANNON type=PSYCHIC power=240 status=CONF',
 'Z-DRAIN':         'CANNON type=GRASS power=200 drain=100',
 'Z-SLUDGE':        'CANNON type=POISON power=200 status=TOX',
}
