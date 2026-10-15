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
 'POUND':        'Lp Fs Px * Ax',   # contest: Pound starts Double Slap / Slam  # POC-31 L4a: +A for the ladder of WHISMUR
 'KARATE_CHOP':  'Kp Up',        # high-crit: pays off Focus Energy
 'DOUBLE_SLAP':  'Fp Px Lx',  # POC-31 L4a: +L for the ladder of SKITTY
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
 'HEADBUTT':     'Ap Hx Lx',  # POC-31 L4a: +L for the ladder of ZIGZAGOON
 'HORN_ATTACK':  'Lp Fs',        # contest: Horn Attack starts Fury Attack / Horn Drill
 'FURY_ATTACK':  'Fp Lx *',
 'TACKLE':       'Lp Hp Ax *',   # contest: follows Leer, Harden AND Defense Curl -> the glue move
 'BODY_SLAM':    'Cs Lp Ax',  # POC-31 L4a: +A for the ladder of AZURILL, CASTFORM
 'WRAP':         'Bs Fx *',
 'TAKE_DOWN':    'Hp',           # review: too weak for X; stays on H for STAMPEDE
 'THRASH':       'Xp',
 'DOUBLE_EDGE':  'Xp',
 'TAIL_WHIP':    'Ls Vx *',
 'POISON_STING': 'Os Fx *',
 'TWINEEDLE':    'Fp Op Zx',  # POC-31 L4a: +Z for the ladder of VOLBEAT, WURMPLE
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
 'DIZZY_PUNCH':  'Pp Zs Lx',  # POC-31 L4a: +L for the ladder of SPINDA
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
 'SLASH':        'Up Np Lx',  # POC-31 L4a: +L for the ladder of KECLEON
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
 'DRAGON_BREATH':'Cs Sx Ux',        # was D; paralysing breath  # POC-31 L4a: +U for the ladder of BAGON, LATIAS, LATIOS, RAYQUAZA, SWABLU
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
 'TWISTER':      'Wp Rx * Ux',      # review: W R * (leaves the old Dragon lane)  # POC-31 L4a: +U for the ladder of BAGON, LATIAS, LATIOS, RAYQUAZA, SWABLU
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
 'HYPER_VOICE':  'Vp Ax Fx',  # POC-31 L4a: +AF for the ladder of IGGLYBUFF, WHISMUR
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
 'SILVER_WIND':  'Wp Ox Gx Zx',  # POC-31 L4a: +OGZ for the ladder of CASCOON, ILLUMISE, NINCADA, NINJASK, SHEDINJA, SILCOON, SURSKIT, VOLBEAT
 'METAL_SOUND':  'Vs Ls',
 'GRASS_WHISTLE':'Zs Gs *',      # review: Z G *
 'TICKLE':       'Ls Ys *',
 'COSMIC_POWER': 'Hs Ms',
 'WATER_SPOUT':  'Rp',
 'SIGNAL_BEAM':  'Zs Mp Gx Ox',  # POC-31 L4a: +GO for the ladder of HERACROSS, NINCADA, SHEDINJA
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

 # POC-31: the Gen 4 moves. Codes by type; ladder codes (L4a) as x, from data/learnset_ladders.json
 'WAKE_UP_SLAP': 'Zp Kp',
 'HAMMER_ARM':   'Kp Pp',
 'BRINE':        'Rp Ex',
 'PLUCK':        'Wp Ax',
 'CLOSE_COMBAT': 'Kp Xp',
 'FLARE_BLITZ':  'Sp Xp',
 'FORCE_PALM':   'Kp Cx Lx',  # ladder: MEDITITE
 'POISON_JAB':   'Op Px',
 'NIGHT_SLASH':  'Np Up',
 'AQUA_TAIL':    'Rp Lx',
 'SEED_BOMB':    'Gp Fx',
 'AIR_SLASH':    'Wp Ax',
 'X_SCISSOR':    'Fp Up Gx Ox',  # ladder: NINJASK, PINSIR
 'BUG_BUZZ':     'Vp Lx Ox',  # ladder: CASCOON, ILLUMISE, SILCOON, SURSKIT
 'DRAGON_PULSE': 'Up Mx',
 'POWER_GEM':    'Qp Mx',
 'ENERGY_BALL':  'Gp Lx',
 'BRAVE_BIRD':   'Wp Xp',
 'EARTH_POWER':  'Qp Lx',  # ladder: BALTOY, GROUDON, TRAPINCH
 'GIGA_IMPACT':  'Xp',
 'BULLET_PUNCH': 'Pp Ap Hx',  # ladder: BELDUM
 'ICE_SHARD':    'Ip Ap',
 'SHADOW_CLAW':  'Np Up',
 'THUNDER_FANG': 'Cp Np',
 'ICE_FANG':     'Ip Np',  # ladder: SNORUNT
 'FIRE_FANG':    'Sp Np',
 'SHADOW_SNEAK': 'Np Ap',  # ladder: SHUPPET
 'MUD_BOMB':     'Qp Ns',
 'PSYCHO_CUT':   'Mp Up',
 'ZEN_HEADBUTT': 'Mp Hx',
 'MIRROR_SHOT':  'Hp Ns',
 'FLASH_CANNON': 'Hp Lx',
 'DISCHARGE':    'Cp',
 'LAVA_PLUME':   'Sp Ox',  # ladder: NUMEL, SLUGMA, TORKOAL
 'LEAF_STORM':   'Gp Xp',
 'CROSS_POISON': 'Op Up',  # ladder: ZUBAT
 'GUNK_SHOT':    'Op',
 'IRON_HEAD':    'Hp Ax',  # ladder: ARON, JIRACHI, MAWILE, REGISTEEL, SKARMORY
 'MAGNET_BOMB':  'Hp Cx',
 'STONE_EDGE':   'Qp Up',
 'BUG_BITE':     'Fp Np Zx',  # ladder: WURMPLE
 'CHARGE_BEAM':  'Cs Up',  # ladder: VOLTORB
 'AQUA_JET':     'Rp Ap',  # ladder: CARVANHA, PSYDUCK
 'HEAD_SMASH':   'Xp Qp',
 'DOUBLE_HIT':   'Fp Lx',
 'OMINOUS_WIND': 'Np Wx',
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
 # POC-14: themed after the Gym Leaders' and the Elite Four's own movesets (src/data/trainer_parties.h); every recipe
 # has a code all three share, so a player can chain it too
 ('ROCK AVALANCHE',  ['DEFENSE_CURL', 'ROCK_THROW', 'ROCK_TOMB'],  'ROCK 4 x 130 rocks on the enemy area + slows (Roxanne, code Q)'),
 ('IRON FIST',       ['BULK_UP', 'ARM_THRUST', 'FOCUS_PUNCH'],    'FIGHTING 200, two columns of fists (Brawly, code P)'),
 ('THUNDER CAGE',    ['THUNDER_WAVE', 'SPARK', 'SHOCK_WAVE'],     'ELECTRIC 120 on every enemy panel + paralysis (Wattson, code C)'),
 ('SOLAR FLARE',     ['SUNNY_DAY', 'FLAMETHROWER', 'HEAT_WAVE'],  'FIRE 200 on every enemy panel + burn (Flannery, code S)'),
 ('BATTERING RAM',   ['DEFENSE_CURL', 'HEADBUTT', 'TAKE_DOWN'],   'NORMAL 150 charge down the row, no recoil (Norman, code H)'),
 ('DIVE BOMBER',     ['FEATHER_DANCE', 'STEEL_WING', 'AERIAL_ACE'],'FLYING 170, locks on and never misses (Winona, code W)'),
 ('COSMIC DUET',     ['LIGHT_SCREEN', 'CALM_MIND', 'PSYCHIC'],    'PSYCHIC 170 beam sweeping the enemy area (Tate & Liza, code M)'),
 ('RIPPLE BURST',    ['RAIN_DANCE', 'WATER_PULSE', 'SURF'],       'WATER 160 wave over all three rows + confusion (Juan, code R)'),
 ('NIGHT HUNT',      ['FAINT_ATTACK', 'SLASH', 'CRUNCH'],         'DARK 180 wide cut, guaranteed crit (Sidney, code N)'),
 ('PHANTOM PARADE',  ['CONFUSE_RAY', 'NIGHT_SHADE', 'SHADOW_BALL'],'GHOST 180 cannon + confusion (Phoebe, code N)'),
 ('GLACIAL TOMB',    ['HAIL', 'ICE_BALL', 'ICE_BEAM'],            'ICE 170 on every enemy panel + freeze (Glacia, code I)'),
 ('GEYSER',          ['RAIN_DANCE', 'SURF', 'WATER_SPOUT'],       'WATER 220 erupting under every enemy panel (Wallace, code R)'),
 # POC-22b (Khaled: "increase the amount of program advances in general. But we need to be smart about it"): each fills
 # a type or a stage of the game with few Program Advances; the three moves share a code (in the sketch), go setup ->
 # payoff, and at least one Hoenn Pokemon line can use all three (gPkbnCanLearn). Our design, TUNE; poc/POC-22.md.
 ('SILVER STORM'  , ['WHIRLWIND', 'GUST', 'SILVER_WIND'], 'BUG 150 wind over all three rows, slows (code W)'),
 ('SKY RAID'      , ['QUICK_ATTACK', 'PECK', 'WING_ATTACK'], 'FLYING 130 dive down the row (code A)'),
 ('AMBUSH FANG'   , ['SAND_ATTACK', 'BITE', 'CRUNCH'], 'DARK 160, locks on, never misses, lowers accuracy (code N)'),
 ('MAELSTROM'     , ['RAIN_DANCE', 'WATER_GUN', 'WHIRLPOOL'], 'WATER 4 x 35 whirl 2 panels ahead, slows (code R)'),
 ('SPORE BLOOM'   , ['LEECH_SEED', 'STUN_SPORE', 'MEGA_DRAIN'], 'GRASS 110 burst on the target and around it + paralysis (code G)'),
 ('SUMO SLAM'     , ['FOCUS_ENERGY', 'ARM_THRUST', 'VITAL_THROW'], 'FIGHTING 140 slam on three panels, guaranteed crit (code K)'),
 ('STEEL RAM'     , ['METAL_SOUND', 'TACKLE', 'IRON_TAIL'], 'STEEL 170 charge down the row (code L)'),
 ('BLADE SWARM'   , ['SWORDS_DANCE', 'FURY_CUTTER', 'SLASH'], 'BUG 170 wide cut, guaranteed crit (code U)'),
 ('ECHO BLAST'    , ['SUPERSONIC', 'SCREECH', 'HYPER_VOICE'], 'NORMAL 160 sound wave over all three rows + confusion (code V)'),
 ('TOXIC FOG'     , ['POISON_GAS', 'SMOG', 'SLUDGE'], 'POISON 120 on every enemy panel, poisons them, lowers accuracy (code O)'),
 ('QUICKSAND'     , ['SAND_ATTACK', 'SAND_TOMB', 'DIG'], 'GROUND 170 from below, slows (code Q)'),
 ('HAUNTING'      , ['ASTONISH', 'SHADOW_PUNCH', 'SHADOW_BALL'], 'GHOST 170, locks on, guaranteed crit (code N)'),
 ('AURORA'        , ['POWDER_SNOW', 'ICY_WIND', 'AURORA_BEAM'], 'ICE 160 beam sweeping the enemy area, slows (code I)'),
 ('FOSSIL FURY'   , ['ROCK_TOMB', 'ANCIENT_POWER', 'ROCK_SLIDE'], 'ROCK 180 slam on three panels, cracks them (code Q)'),
 ('VERDANT EDGE'  , ['SWORDS_DANCE', 'FURY_CUTTER', 'LEAF_BLADE'], 'GRASS 200, two columns of blades, guaranteed crit (code U)'),
 ('BLAZING FURY'  , ['FOCUS_ENERGY', 'DOUBLE_KICK', 'BLAZE_KICK'], 'FIRE 3 x 70 kicks down 3 panels + burn (code K)'),
 ('SWAMP SURGE'   , ['MUD_SPORT', 'WATER_PULSE', 'MUDDY_WATER'], 'WATER 180 wave over all three rows, lowers accuracy (code R)'),
 ('DRAGONFIRE'    , ['SUNNY_DAY', 'DRAGON_BREATH', 'FLAMETHROWER'], 'DRAGON 200 fire wave down the row + burn (code S)'),
]
