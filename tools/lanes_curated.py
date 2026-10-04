"""Curated chip-code lanes for every Gen 3 move (source of truth).

Format per move:  "Lr Lr ... [*]"  where L = lane letter, r = role. Token order is copy order:
copy k of a chip gets the k-th token (wrapping), so put * first to make a single-copy move a wildcard.
  s = setup   (prepares the lane's plan: weather, stat drops/boosts, status, trapping, aiming)
  p = payoff  (cashes in the plan: the hit you want to land after the setup)
  x = link    (neither; keeps a chain going / bridges two lanes)
  *  = this move's copies may carry the wildcard code (only weak or status moves).
Notes ("# ...") explain non-obvious choices. Design rules: docs/design/03-lanes.md.
"""

LANES = {
 'A': ('AMBUSH',    'Strike first: priority, flinch, surprise hits. Short chains that open a turn.'),
 'B': ('BIND',      'Pin the target in place (trap / grip / web), then finish it.'),
 'C': ('CHARGE',    'Build electricity, paralyse, lock on — then the big bolt. Paralysis payoffs (Smelling Salt).'),
 'D': ('DANCE',     'Every Dance move: Swords, Dragon, Petal, Feather, Teeter and Rain Dance. Boost, then cash in.'),
 'E': ('ENDURE',    'Low HP and retaliation: survive, then punish (Flail, Reversal, Counter, Endeavor).'),
 'F': ('FURY',      'Flurries and escalating hits: multi-hit moves, Rollout, Fury Cutter, Rage.'),
 'G': ('GROWTH',    'Plants: grow, seed, drain, bloom.'),
 'H': ('HARDEN',    'Armour up and turn defence into offence (Defense Curl -> Rollout, Harden -> Tackle).'),
 'I': ('ICE',       'Hail, chill, slow, freeze.'),
 'K': ('KUNG-FU',   'Martial arts: kicks, chops, throws, focus.'),
 'L': ('LOWER',     'Break defences (Defense / Sp. Def drops), then hit hard.'),
 'M': ('MIND',      'Psychic focus: calm, confuse, foresee, screens.'),
 'N': ('NIGHT',     'Dirty tricks: bite, steal, taunt, blind (accuracy drops), dark ambushes.'),
 'O': ('OOZE',      'Attrition: poison, burns, leeching, chip damage over time.'),
 'P': ('PUNCH',     'Fists: every punch, elemental and otherwise.'),
 'Q': ('QUAKE',     'Earth and stone: mud, sand, rocks, bones, quakes, hazards.'),
 'R': ('RAIN',      'Water and storms: rain, sport, pulses, torrents.'),
 'S': ('SUN',       'Fire and daylight: sunshine, flames, solar power.'),
 'T': ('TEMPO',     'Speed and evasion: outpace (Agility), slow them (String Shot), dodge (Double Team).'),
 'U': ('UP',        'Power up, then cash in: Swords Dance / Focus Energy into crits and charged blows.'),
 'V': ('VOICE',     'Sound: songs, roars, screeches and snores.'),
 'W': ('WIND',      'Sky and air: gusts, wings, dives.'),
 'X': ('EXTREME',   'All-in finishers with a cost: recharge, recoil, self-KO. Payoff-only lane.'),
 'Y': ('YIELD',     'Support and team play: heal, shield, soften blows, help the next Pokemon (ties into switching).'),
 'Z': ('ZZZ',       'Sleep and confusion, and the moves that exploit them (Dream Eater, Nightmare, Snore).'),
}

MOVES = {
 'POUND':        'Lp Fs Px *',   # contest: Pound starts Double Slap / Slam
 'KARATE_CHOP':  'Kp Up',        # high-crit: pays off Focus Energy
 'DOUBLE_SLAP':  'Fp Px',
 'COMET_PUNCH':  'Fp Pp',
 'MEGA_PUNCH':   'Pp Lp',
 'PAY_DAY':      'Nx *',
 'FIRE_PUNCH':   'Pp Sp',
 'ICE_PUNCH':    'Pp Ip',
 'THUNDER_PUNCH':'Pp Cp',
 'SCRATCH':      'Lp Ux *',      # contest: follows Leer
 'VICE_GRIP':    'Bs Lp',        # the grip holds the target
 'RAZOR_WIND':   'Up Wp',        # charged + high-crit
 'SWORDS_DANCE': 'Ds Us',        # review: D U (Dance lane)
 'CUT':          'Up Lp',
 'GUST':         'Ws Rx *',
 'WING_ATTACK':  'Wp Ax',
 'WHIRLWIND':    'Ws Tx *',
 'FLY':          'Wp Rx',        # review: W R
 'BIND':         'Bs Fx *',
 'SLAM':         'Lp Bp',        # contest: follows Pound
 'VINE_WHIP':    'Gs Bs *',      # vines grab
 'STOMP':        'Ap Tp',        # punishes Minimize (Tempo)
 'DOUBLE_KICK':  'Kx Fp *',
 'MEGA_KICK':    'Kp',
 'JUMP_KICK':    'Kp Wx',
 'ROLLING_KICK': 'Kp Ax',
 'SAND_ATTACK':  'Qs Ns *',
 'HEADBUTT':     'Ap Hx',
 'HORN_ATTACK':  'Lp Fs',        # contest: Horn Attack starts Fury Attack / Horn Drill
 'FURY_ATTACK':  'Fp Lx *',
 'TACKLE':       'Lp Hp Ax *',   # contest: follows Leer, Harden AND Defense Curl -> the glue move
 'BODY_SLAM':    'Cs Lp',
 'WRAP':         'Bs Fx *',
 'TAKE_DOWN':    'Hp',           # review: too weak for X; stays on H for STAMPEDE
 'THRASH':       'Xp',
 'DOUBLE_EDGE':  'Xp',
 'TAIL_WHIP':    'Ls Vx *',
 'POISON_STING': 'Os Fx *',
 'TWINEEDLE':    'Fp Op',
 'PIN_MISSILE':  'Fp Ax',
 'LEER':         'Ls Ns *',      # contest: Leer starts Scratch / Tackle / Bite
 'BITE':         'Np Ap',        # contest: follows Leer
 'GROWL':        'Vs Ys *',
 'ROAR':         'Vs Ws',
 'SING':         'Vs Zs',
 'SUPERSONIC':   'Vs Zs *',
 'ACID':         'Ls Os *',
 'EMBER':        'Sp Os *',      # burn = attrition
 'FLAMETHROWER': 'Sp',
 'MIST':         'Ys Is *',
 'WATER_GUN':    'Rp Qx *',      # contest: follows Rain Dance and Mud Sport -> water/earth bridge
 'HYDRO_PUMP':   'Rp',
 'SURF':         'Rp',
 'ICE_BEAM':     'Ip',
 'BLIZZARD':     'Ip',
 'PSYBEAM':      'Mp Zs',
 'BUBBLE_BEAM':  'Rp Ts',
 'AURORA_BEAM':  'Ip Ys',
 'HYPER_BEAM':   'Xp',
 'PECK':         'Wp Fx Ax *',   # review: W F A *
 'DRILL_PECK':   'Wp',
 'SUBMISSION':   'Kp',           # review: too weak for X
 'LOW_KICK':     'Kp Tx',
 'COUNTER':      'Ep Kx',
 'SEISMIC_TOSS': 'Kp Ex',
 'STRENGTH':     'Hp Lp',
 'ABSORB':       'Gp Ox *',
 'MEGA_DRAIN':   'Gp Ox',
 'LEECH_SEED':   'Gs Os',
 'GROWTH':       'Gs Ss',        # contest: Growth starts the grass moves; sun boosts it
 'RAZOR_LEAF':   'Gp Up',
 'SOLAR_BEAM':   'Sp Gp',        # deliberate two-lane payoff (Sunny Day and Growth both lead here)
 'POISON_POWDER':'Os Gs *',
 'STUN_SPORE':   'Cs Gs',
 'SLEEP_POWDER': 'Zs Gs',
 'PETAL_DANCE':  'Gp Dp',        # review: G D
 'STRING_SHOT':  'Ts Bs *',
 'DRAGON_RAGE':  'Ap Ex',        # was D; fixed 40 damage opener
 'FIRE_SPIN':    'Bs Ss',
 'THUNDER_SHOCK':'Cs Ax *',
 'THUNDERBOLT':  'Cp',
 'THUNDER_WAVE': 'Cs Ts',
 'THUNDER':      'Cp Rp',        # canon: rain makes Thunder never miss
 'ROCK_THROW':   'Qp Ax *',
 'EARTHQUAKE':   'Qp',
 'DIG':          'Qp Ax',
 'TOXIC':        'Os',
 'CONFUSION':    'Mp Zs *',
 'PSYCHIC':      'Mp',
 'HYPNOSIS':     'Zs Ms',
 'MEDITATE':     'Us Ps *',      # Medicham's line: meditate, then elemental punches
 'AGILITY':      'Ts Ms',
 'QUICK_ATTACK': 'Ap Tp *',
 'RAGE':         'Up Ex *',
 'TELEPORT':     'Tx Yx *',
 'NIGHT_SHADE':  'Np',           # was J
 'MIMIC':        '*',            # copy moves are pure wildcards
 'SCREECH':      'Ls Vs',
 'RECOVER':      'Ys',
 'HARDEN':       'Hs Ys *',      # contest: Harden starts Tackle / Take Down / Rollout
 'SMOKESCREEN':  'Ns Ss *',
 'CONFUSE_RAY':  'Zs Ns',        # was J
 'WITHDRAW':     'Hs Rs *',
 'DEFENSE_CURL': 'Hs Fs *',      # contest: Defense Curl starts Rollout
 'BARRIER':      'Hs Ms',
 'LIGHT_SCREEN': 'Ys Ms',
 'HAZE':         'Is Yx',
 'REFLECT':      'Ys Hs',
 'FOCUS_ENERGY': 'Us Ks',        # contest: Focus Energy starts the heavy physical hits
 'BIDE':         'Ep Hx',
 'METRONOME':    '*',
 'MIRROR_MOVE':  '*',
 'SELF_DESTRUCT':'Xp',
 'EGG_BOMB':     'Xp',
 'LICK':         'Cs Ax *',      # was J; paralysis
 'SMOG':         'Os Ss *',
 'SLUDGE':       'Op',
 'BONE_CLUB':    'Qp Ap',
 'FIRE_BLAST':   'Sp',
 'WATERFALL':    'Rp',
 'CLAMP':        'Bs Rs',
 'SWIFT':        'Tp Ax',
 'SKULL_BASH':   'Hp',           # raises Defense while charging
 'SPIKE_CANNON': 'Fp Qx',
 'CONSTRICT':    'Bs Ts *',
 'AMNESIA':      'Ms Hs',
 'KINESIS':      'Ms Ns *',
 'SOFT_BOILED':  'Ys',
 'HI_JUMP_KICK': 'Kp',
 'GLARE':        'Cs Ns',
 'DREAM_EATER':  'Zp Mp',        # exception: the payoff of both sleep (Z) and psychic (M)
 'POISON_GAS':   'Os Ws *',
 'BARRAGE':      'Fp Ax *',
 'LEECH_LIFE':   'Op Gx *',
 'LOVELY_KISS':  'Zs',
 'SKY_ATTACK':   'Wp',
 'TRANSFORM':    '*',
 'BUBBLE':       'Rs Ts *',
 'DIZZY_PUNCH':  'Pp Zs',
 'SPORE':        'Zs Gs',
 'FLASH':        'Ns Ss *',
 'PSYWAVE':      'Mp Ex',
 'SPLASH':       '*',
 'ACID_ARMOR':   'Hs Os',
 'CRABHAMMER':   'Rp',
 'EXPLOSION':    'Xp',
 'FURY_SWIPES':  'Fp Lx *',
 'BONEMERANG':   'Qp Fp',
 'REST':         'Zs Ys',
 'ROCK_SLIDE':   'Qp Ap',
 'HYPER_FANG':   'Ap Np',
 'SHARPEN':      'Us *',
 'CONVERSION':   '*',
 'TRI_ATTACK':   'Sp Cp Ip',     # deliberate three-way bridge: burn / paralyse / freeze
 'SUPER_FANG':   'Np Ep',
 'SLASH':        'Up Np',
 'SKETCH':       '*',
 'TRIPLE_KICK':  'Kp Fp',
 'THIEF':        'Np Ax *',
 'SPIDER_WEB':   'Bs',           # was J
 'NIGHTMARE':    'Zp Ns',        # was J; pays off sleep
 'FLAME_WHEEL':  'Sp Ax',
 'SNORE':        'Zp Vp *',      # review: Z V *
 'CURSE':        'Us Hs',        # was J; Gen 3 non-Ghost Curse = Atk/Def up
 'FLAIL':        'Ep',
 'CONVERSION_2': '*',
 'AEROBLAST':    'Wp',
 'COTTON_SPORE': 'Ts Gs',
 'REVERSAL':     'Ep Kp',
 'POWDER_SNOW':  'Ip Wx *',
 'PROTECT':      'Ys Hs',
 'MACH_PUNCH':   'Pp Ap *',
 'SCARY_FACE':   'Ts Ns',        # was D; intimidation
 'FAINT_ATTACK': 'Np Ax',
 'SWEET_KISS':   'Zs Vx *',
 'BELLY_DRUM':   'Us Es',
 'SLUDGE_BOMB':  'Op',
 'MUD_SLAP':     'Qs Ns *',
 'OCTAZOOKA':    'Rp Ns',
 'SPIKES':       'Qs Os',
 'ZAP_CANNON':   'Cp',
 'ICY_WIND':     'Ip Ts',
 'DETECT':       'Ys Ks',
 'BONE_RUSH':    'Qp Fp',
 'LOCK_ON':      'Cs Bs',
 'OUTRAGE':      'Up',           # was D; rampage after Dragon Dance (DRAGON RUSH on U)
 'SANDSTORM':    'Qs Ws',
 'GIGA_DRAIN':   'Gp',
 'CHARM':        'Ys Vs',
 'ROLLOUT':      'Fp Hp',
 'FALSE_SWIPE':  'Ux Nx *',
 'SWAGGER':      '*',            # review: wildcard only
 'MILK_DRINK':   'Ys',
 'SPARK':        'Cp Ap',
 'FURY_CUTTER':  'Fp Ux *',
 'STEEL_WING':   'Wp Hs',
 'MEAN_LOOK':    'Bs Ns',        # was J
 'ATTRACT':      '*',            # review: wildcard only
 'SLEEP_TALK':   'Zx *',
 'HEAL_BELL':    'Ys Vs',
 'RETURN':       'Yp',
 'FRUSTRATION':  'Ep Np',
 'SAFEGUARD':    'Ys',
 'SACRED_FIRE':  'Sp',
 'MAGNITUDE':    'Qp',
 'DYNAMIC_PUNCH':'Pp',
 'MEGAHORN':     'Xp',
 'DRAGON_BREATH':'Cs Sx',        # was D; paralysing breath
 'BATON_PASS':   'Ts *',
 'PURSUIT':      'Np Ap *',
 'RAPID_SPIN':   'Hx Tx *',
 'SWEET_SCENT':  'Gs Ns *',
 'IRON_TAIL':    'Lp',
 'METAL_CLAW':   'Up Hx *',
 'VITAL_THROW':  'Kp Tx',
 'MORNING_SUN':  'Ss Ys',
 'SYNTHESIS':    'Gs Ys',
 'MOONLIGHT':    'Ys Ns',
 'HIDDEN_POWER': '*',
 'CROSS_CHOP':   'Kp',
 'TWISTER':      'Wp Rx *',      # review: W R * (leaves the old Dragon lane)
 'RAIN_DANCE':   '* Rs Cs Ds',   # a Dance (review: D = all Dance moves). Its ONE copy (5 PP) is * so it can open
                                 # both TSUNAMI (R) and STORM CALLER (C); letter order = copy order
 'SUNNY_DAY':    'Ss',
 'CRUNCH':       'Np Lp',
 'PSYCH_UP':     'Us *',
 'EXTREME_SPEED':'Ap',
 'ANCIENT_POWER':'Qp',
 'SHADOW_BALL':  'Np',           # was J
 'FUTURE_SIGHT': 'Mp',
 'ROCK_SMASH':   'Kp Ls *',
 'WHIRLPOOL':    'Bs Rs',
 'BEAT_UP':      'Np Yp',        # the whole party attacks: a team move
 'FAKE_OUT':     'As Ns *',
 'HEAT_WAVE':    'Sp',
 'HAIL':         'Is',
 'FLATTER':      '*',            # review: wildcard only
 'WILL_O_WISP':  'Os Ss',        # was J; burn
 'MEMENTO':      'Es Ys',        # faint to weaken the foe for the next Pokemon
 'FACADE':       'Ep Op',
 'FOCUS_PUNCH':  'Pp',
 'NATURE_POWER': '*',
 'CHARGE':       'Cs',
 'ROLE_PLAY':    '*',
 'WISH':         'Ys',
 'ASSIST':       '*',
 'INGRAIN':      'Gs Ys',
 'SUPERPOWER':   'Xp',
 'MAGIC_COAT':   'Ys',           # review: Y
 'REVENGE':      'Ep Kp',
 'BRICK_BREAK':  'Kp Lp',
 'YAWN':         'Zs *',
 'KNOCK_OFF':    'Np Lx *',
 'ENDEAVOR':     'Ep',
 'ERUPTION':     'Sp',
 'SKILL_SWAP':   '*',
 'REFRESH':      'Ys *',
 'SECRET_POWER': 'Qx Nx',        # its effect depends on the terrain (hidden = Night)
 'DIVE':         'Rp Ax',
 'ARM_THRUST':   'Kp Fp *',
 'CAMOUFLAGE':   '*',
 'TAIL_GLOW':    'Us Ms',
 'LUSTER_PURGE': 'Mp',
 'MIST_BALL':    'Mp',
 'FEATHER_DANCE':'Ws Ds',        # review: W D J -> J lane was rejected, so W D
 'TEETER_DANCE': 'Vs Ds Zs',     # review: V D Z
 'BLAZE_KICK':   'Kp Sp',
 'MUD_SPORT':    'Qs Rs *',      # contest: Mud Sport starts Water Gun / Mud-Slap
 'ICE_BALL':     'Ip Fp',
 'NEEDLE_ARM':   'Gp Ap',
 'SLACK_OFF':    'Ys',
 'HYPER_VOICE':  'Vp',
 'POISON_FANG':  'Op Np',
 'CRUSH_CLAW':   'Lp Up',
 'BLAST_BURN':   'Xp',
 'HYDRO_CANNON': 'Xp',
 'METEOR_MASH':  'Pp',
 'ASTONISH':     'As Nx *',      # was J
 'WEATHER_BALL': 'Rp Sp Ip Qp',  # changes type with the weather: one letter per weather
 'AROMATHERAPY': 'Ys Gs',
 'FAKE_TEARS':   'Ls Ns',
 'AIR_CUTTER':   'Wp Up',
 'OVERHEAT':     'Xp',
 'ROCK_TOMB':    'Qp Ts',
 'SILVER_WIND':  'Wp',
 'METAL_SOUND':  'Vs Ls',
 'GRASS_WHISTLE':'Zs Gs *',      # review: Z G *
 'TICKLE':       'Ls Ys *',
 'COSMIC_POWER': 'Hs Ms',
 'WATER_SPOUT':  'Rp',
 'SIGNAL_BEAM':  'Zs Mp',
 'SHADOW_PUNCH': 'Pp Np',        # was J
 'EXTRASENSORY': 'Mp',
 'SKY_UPPERCUT': 'Pp',
 'SAND_TOMB':    'Bs Qs',
 'MUDDY_WATER':  'Rp',
 'BULLET_SEED':  'Gp Fp *',
 'AERIAL_ACE':   'Wp Ap',
 'ICICLE_SPEAR': 'Ip Fp *',
 'IRON_DEFENSE': 'Hs',
 'HOWL':         'Us Vs *',
 'DRAGON_CLAW':  'Up',           # was D; claw like Slash / Crush Claw
 'FRENZY_PLANT': 'Xp',
 'BULK_UP':      'Ks Ps',        # muscles feed kicks and punches
 'BOUNCE':       'Wp',
 'MUD_SHOT':     'Qp Ts',
 'POISON_TAIL':  'Op Up',
 'COVET':        'Np Yx *',
 'VOLT_TACKLE':  'Cp',
 'MAGICAL_LEAF': 'Gp Tx',
 'WATER_SPORT':  'Rs Ys *',
 'CALM_MIND':    'Ms',
 'LEAF_BLADE':   'Gp Up',
 'DRAGON_DANCE': 'Ds Us',        # Dance lane; raises Attack (U)
 'ROCK_BLAST':   'Qp Fp',
 'SHOCK_WAVE':   'Cp Tx',
 'WATER_PULSE':  'Rp Zs',
 'DOOM_DESIRE':  'Mp',
 'PSYCHO_BOOST': 'Xp',
}

# Program Advances: an exact 3-move sequence in one chain becomes a brand-new move.
# Moves cut by Khaled's review (2026-10-04). They never become chips.
REMOVED = {
 'GUILLOTINE': 'OHKO (lane B review)',
 'HORN_DRILL': 'OHKO',
 'FISSURE': 'OHKO',
 'SHEER_COLD': 'OHKO',
 'DESTINY_BOND': 'review',
 'DISABLE': 'review',
 'DOUBLE_TEAM': 'review',
 'ENCORE': 'review',
 'ENDURE': 'review',
 'FOLLOW_ME': 'no double battles',
 'HELPING_HAND': 'no double battles',
 'FORESIGHT': 'review',
 'GRUDGE': 'review',
 'IMPRISON': 'review',
 'MIND_READER': 'review',
 'MINIMIZE': 'review',
 'MIRROR_COAT': 'review',
 'ODOR_SLEUTH': 'review',
 'PAIN_SPLIT': 'review',
 'PERISH_SONG': 'review',
 'PRESENT': 'simplicity',
 'RECYCLE': 'review',
 'SMELLING_SALT': 'review',
 'SNATCH': 'review',
 'SONIC_BOOM': 'review',
 'SPITE': 'review',
 'SPIT_UP': 'Stockpile family',
 'STOCKPILE': 'Stockpile family',
 'SWALLOW': 'Stockpile family',
 'SUBSTITUTE': 'simplicity',
 'TAUNT': 'review',
 'TORMENT': 'review',
 'TRICK': 'review',
 'UPROAR': 'review',
 'BLOCK': 'review',
}

PROGRAM_ADVANCES = [
 # name, recipe (in order), new-move sketch
 ('MEGA SOLAR BEAM', ['SUNNY_DAY', 'GROWTH', 'SOLAR_BEAM'], 'GRASS 180, no charge; beam sweeps the whole enemy area row by row'),
 ('STORM CALLER',    ['RAIN_DANCE', 'CHARGE', 'THUNDER'],    'ELECTRIC 150; a bolt on every enemy panel, never misses'),
 ('TSUNAMI',         ['RAIN_DANCE', 'SURF', 'HYDRO_PUMP'],   'WATER 200; a wave rolls across all three rows'),
 ('PERMAFROST',      ['HAIL', 'ICY_WIND', 'BLIZZARD'],       'ICE 160; freezes the target in place (BN freeze) + slows'),
 ('EARTH RENDER',    ['SANDSTORM', 'MAGNITUDE', 'EARTHQUAKE'],'GROUND 180; cracks every enemy panel'),
 ('DREAM DEVOURER',  ['HYPNOSIS', 'NIGHTMARE', 'DREAM_EATER'],'PSYCHIC 160 drain; heals the whole party'),
 ('VENOM STORM',     ['TOXIC', 'ACID', 'SLUDGE_BOMB'],       'POISON 140; leaves poison panels'),
 ('DRAGON RUSH',     ['DRAGON_DANCE', 'DRAGON_CLAW', 'OUTRAGE'],'DRAGON 200 dash through the row; no confusion after'),
 ('THOUSAND FISTS',  ['MACH_PUNCH', 'COMET_PUNCH', 'DYNAMIC_PUNCH'],'FIGHTING 6 x 30, guaranteed crits'),
 ('STAMPEDE',        ['HARDEN', 'TACKLE', 'TAKE_DOWN'],      'NORMAL 120 charge down the row, no recoil (contest: Harden starts Tackle / Take Down)'),
 ('MUDSLIDE',        ['MUD_SPORT', 'MUD_SLAP', 'WATER_GUN'], 'GROUND/WATER 90; muddies the enemy area (accuracy down) (early game)'),
 ('ROLLING THUNDER', ['DEFENSE_CURL', 'HARDEN', 'ROLLOUT'],  'ROCK 5 rolling hits that bounce between rows'),
 # tier trios: the BN Z-Cannon pattern (Cannon -> HiCannon -> M-Cannon)
 ('Z-HYDRO',         ['WATER_GUN', 'BUBBLE_BEAM', 'HYDRO_PUMP'],'WATER 240 cannon'),
 ('Z-FLARE',         ['EMBER', 'FLAMETHROWER', 'FIRE_BLAST'],  'FIRE 240 + burn'),
 ('Z-VOLT',          ['THUNDER_SHOCK', 'THUNDERBOLT', 'THUNDER'],'ELECTRIC 240 + paralysis'),
 ('Z-FROST',         ['POWDER_SNOW', 'ICE_BEAM', 'BLIZZARD'],   'ICE 240 + freeze'),
 ('Z-PSI',           ['CONFUSION', 'PSYBEAM', 'PSYCHIC'],       'PSYCHIC 240 + confusion'),
 ('Z-DRAIN',         ['ABSORB', 'MEGA_DRAIN', 'GIGA_DRAIN'],    'GRASS 200, heals 100% of damage'),
 ('Z-SLUDGE',        ['POISON_STING', 'SLUDGE', 'SLUDGE_BOMB'], 'POISON 200 + bad poison'),
]
