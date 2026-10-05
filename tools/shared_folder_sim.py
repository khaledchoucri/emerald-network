#!/usr/bin/env python3
"""Shared move folder for a party of up to 6 (design 08 §11). Run from the host root (reads src/data).

Rule being tested (2026-10-05): one folder for the whole party. A chip is a MOVE, not a Pokemon's: whoever is in
battle can use it if its species can learn the move (level-up incl. pre-evolutions, TM/HM, tutor, egg moves).
Chips no longer switch Pokemon in (special switch chips come later). Copies are the stamina: a used chip is gone
for the battle (no reshuffle, no PP). Unused chips stay in the hand (BN6).

Everything here is read from the port's own data:
  learnsets  src/data/pokemon/{level_up_learnsets,level_up_learnset_pointers,tmhm_learnsets,tutor_learnsets,egg_moves}.h
  evolutions src/data/pokemon/evolution.h      types  src/data/pokemon/species_info.h
  moves      src/data/battle_moves.h           trainer party sizes  src/data/trainer_parties.h
Model numbers (TUNE) are named in CAPS below.
"""
import re, random, collections, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from chip_memory import load as load_moves, mb, cap

D = 'src/data/'
HAND, USE = 5, 2           # Custom hand (BN6), chips used per Custom (typical)
KO_UNITS = 280             # damage units per KO: 4 uses of a 70-effective-power move (Gen 3, equal level)
WILD_SHARE = 0.7
LIFE = (3, 6)              # Customs a Pokemon survives on the field
SWITCH_THEN_ACT = False    # today: nothing can be queued after the Switch slot
LEGENDS = {'REGIROCK', 'REGICE', 'REGISTEEL', 'LATIAS', 'LATIOS', 'KYOGRE', 'GROUDON', 'RAYQUAZA', 'JIRACHI', 'DEOXYS'}

def read(p):
    return open(D + p).read()

def load_species():
    info = read('pokemon/species_info.h')
    types = {m.group(1): (m.group(2), m.group(3)) for m in
             re.finditer(r'\[SPECIES_(\w+)\]\s*=\s*\{.*?\.types = \{ TYPE_(\w+), TYPE_(\w+) \}', info, re.S)}
    lv = read('pokemon/level_up_learnsets.h')
    sets = {m.group(1): re.findall(r'MOVE_(\w+)\)', m.group(2)) for m in
            re.finditer(r'static const u16 (s\w+LevelUpLearnset)\[\] = \{(.*?)\};', lv, re.S)}
    ptr = dict(re.findall(r'\[SPECIES_(\w+)\]\s*=\s*(s\w+LevelUpLearnset)', read('pokemon/level_up_learnset_pointers.h')))
    compat = collections.defaultdict(set)
    for sp, s in ptr.items():
        compat[sp] |= set(sets.get(s, []))
    global LEVELUP
    LEVELUP = collections.defaultdict(set, {k: set(v) for k, v in compat.items()})
    for m in re.finditer(r'\[SPECIES_(\w+)\] = \{ \.learnset = \{(.*?)\} \}', read('pokemon/tmhm_learnsets.h'), re.S):
        compat[m.group(1)] |= set(re.findall(r'\.(\w+) = TRUE', m.group(2)))
    for m in re.finditer(r'\[SPECIES_(\w+)\]\s*=\s*\((.*?)\),', read('pokemon/tutor_learnsets.h'), re.S):
        compat[m.group(1)] |= set(re.findall(r'TUTOR\(MOVE_(\w+)\)', m.group(2)))
    egg = {m.group(1): set(re.findall(r'MOVE_(\w+)', m.group(2))) for m in
           re.finditer(r'egg_moves\((\w+),(.*?)\)', read('pokemon/egg_moves.h'), re.S)}
    evo = collections.defaultdict(list)
    for m in re.finditer(r'\[SPECIES_(\w+)\]\s*=\s*\{(\{.*?\})\}', read('pokemon/evolution.h'), re.S):
        for t in re.findall(r'SPECIES_(\w+)', m.group(2)):
            evo[m.group(1)].append(t)
    pre = {t: s for s, ts in evo.items() for t in ts}
    final = {}
    for sp in list(compat):
        line, x = [sp], sp
        while x in pre:
            x = pre[x]; line.append(x)
        for anc in line[1:]:
            compat[sp] |= compat[anc]          # pre-evolution moves
            LEVELUP[sp] |= LEVELUP[anc]
        compat[sp] |= egg.get(line[-1], set())  # the family's egg moves
        final[sp] = sp not in evo
    return types, compat, final

def hoenn_finals(types, final):
    ped = read('../../include/constants/pokedex.h') if False else open('include/constants/pokedex.h').read()
    hoenn = re.findall(r'HOENN_DEX_(\w+),', ped)[:203]   # Hoenn dex: NONE + 202
    return [s for s in hoenn if s in types and final.get(s) and s not in LEGENDS and s != 'NONE']

def load_chart():
    src = open('src/battle_main.c').read()
    body = re.search(r'gTypeEffectiveness\[\d+\] =\s*\{(.*?)\};', src, re.S).group(1)
    chart = {}
    for a, d, mul in re.findall(r'TYPE_(\w+), TYPE_(\w+), TYPE_MUL_(\w+)', body):
        if a in ('FORESIGHT', 'ENDTABLE'):
            continue
        chart[(a, d)] = {'NO_EFFECT': 0, 'NOT_EFFECTIVE': 0.5, 'SUPER_EFFECTIVE': 2}[mul]
    return chart

def effectiveness(mtype, dtypes):
    x = 1.0
    for d in set(dtypes):
        x *= CHART.get((mtype, d), 1.0)
    return x

def eff_power(mv, sp, types):
    """Damage units of one use: power x hits x STAB x accuracy (no type matchup: the enemy is unknown)."""
    m = MOVES[mv]
    if m['power'] <= 1:
        return 0
    hits = {'EFFECT_MULTI_HIT': 3, 'EFFECT_DOUBLE_HIT': 2, 'EFFECT_TRIPLE_KICK': 6}.get(m['effect'], 1)
    if m['effect'] in ('EFFECT_RECHARGE', 'EFFECT_SOLAR_BEAM', 'EFFECT_RAZOR_WIND', 'EFFECT_SKULL_BASH',
                       'EFFECT_SKY_ATTACK', 'EFFECT_FUTURE_SIGHT', 'EFFECT_EXPLOSION', 'EFFECT_FOCUS_PUNCH'):
        hits *= 0.5                     # costs a turn / the user: worth less per chip
    stab = 1.5 if MTYPE[mv] in types[sp] else 1.0
    return m['power'] * hits * stab * (m['acc'] or 100) / 100

def build_folder(party, size, types, compat, policy, rng):
    """The player's folder: `size` chips, BN6 copy caps by MB. Damaging moves only (status chips are extra slots
    a real player would add; leaving them out is the worst case for 'nothing usable')."""
    cand = {}
    for sp in party:
        for mv in compat[sp]:
            if mv in MOVES and MOVES[mv]['power'] > 1 and MOVES[mv]['effect'] not in CONDITIONAL:
                cand[mv] = cap(mb(MOVES[mv]))
    folder, copies = [], collections.Counter()
    usable = collections.Counter()
    while len(folder) < size:
        best, bv = None, -1
        for mv, c in cand.items():
            if copies[mv] >= c:
                continue
            if policy == 'balanced':     # favour members that have little so far, and moves several can use
                v = AVG_EFF[MTYPE[mv]] * sum(eff_power(mv, sp, types) / (1 + usable[sp]) for sp in party if mv in compat[sp])
            else:                        # 'own': every member takes its own best moves in turn (naive player)
                sp = party[len(folder) % len(party)]
                v = AVG_EFF[MTYPE[mv]] * eff_power(mv, sp, types) if mv in compat[sp] else -1
            v *= 1 + rng.random() * 0.01
            if v > bv:
                best, bv = mv, v
        if best is None:
            break
        folder.append(best); copies[best] += 1
        for sp in party:
            if best in compat[sp]:
                usable[sp] += 1
    return folder

def battle(party, folder, m, types, compat, rng, hand=HAND, key=None):
    deck = folder[:]; rng.shuffle(deck)
    foe = types[rng.choice(POOL)]
    dmg = lambda c, sp: eff_power(c, sp, types) * effectiveness(MTYPE[c], foe)
    alive = list(party); active = party[0]; life = rng.randint(*LIFE)
    h = []; hp = KO_UNITS; left = m
    st = collections.Counter()
    while left > 0 and st['customs'] < 60:
        st['customs'] += 1
        while len(h) < hand and deck:
            h.append(deck.pop())
        if not deck and len(h) < hand:
            st['dry'] = 1
        if key and active == party[0]:
            st['keyC'] += 1; st['keyHit'] += key in h
        use = sorted((c for c in h if c in compat[active] and dmg(c, active) > 0),
                     key=lambda c: -dmg(c, active))[:USE]
        if not use:
            bench = [(sum(1 for c in h if c in compat[s] and dmg(c, s) > 0), s) for s in alive if s != active]
            bench = [b for b in bench if b[0] > 0]
            if bench:
                st['forced'] += 1
                active = max(bench)[1]; life = rng.randint(*LIFE)   # the Switch slot
                if SWITCH_THEN_ACT:          # chips can be queued after the Switch slot (proposal)
                    use = sorted((c for c in h if c in compat[active] and dmg(c, active) > 0),
                                 key=lambda c: -dmg(c, active))[:USE]
            else:
                st['dead'] += 1
        for c in use:
            h.remove(c); hp -= dmg(c, active)
            st['uses'] += 1
        if hp <= 0:
            left -= 1; hp = KO_UNITS; foe = types[rng.choice(POOL)]
        life -= 1
        if life <= 0 and left > 0:
            alive.remove(active)
            if not alive:
                st['lost'] = 1; break
            active = max(alive, key=lambda s: sum(1 for c in h if c in compat[s] and dmg(c, s) > 0))
            life = rng.randint(*LIFE)
    return st

def trainer_sizes():
    s = read('trainer_parties.h')
    return [m.group(2).count('.species') for m in re.finditer(r'(sParty_\w+)\[\]\s*=\s*\{(.*?)\};', s, re.S)]

def run(size, n, policy='balanced', m=None, hand=HAND, parties=150, reps=20, seed=3, key_copies=None):
    rng = random.Random(seed)
    tot = collections.Counter(); usable_share = []
    for _ in range(parties):
        party = rng.sample(POOL, n)
        folder = build_folder(party, size, TYPES, globals()['COMPAT'], policy, rng)
        for sp in party:
            usable_share.append(sum(1 for c in folder if c in COMPAT[sp]) / max(1, len(folder)))
        key = None
        if key_copies:
            own = [c for c in folder if c in COMPAT[party[0]]]
            if own:
                key = '__KEY__'
                COMPAT[party[0]].add(key)
                folder = [c for c in folder if c != key]
                k = [i for i, c in enumerate(folder) if c in COMPAT[party[0]]][:key_copies]
                for i in k:
                    folder[i] = key
        for _ in range(reps):
            mm = m or (1 if rng.random() < WILD_SHARE else rng.choice(TSIZES))
            st = battle(party, folder, mm, TYPES, COMPAT, rng, hand, key)
            tot.update(st); tot['battles'] += 1
        if key:
            COMPAT[party[0]].discard(key)
    c = tot['customs']
    us = sorted(usable_share)
    return dict(lostAll=tot['lost'] / tot['battles'], dead=tot['dead'] / c, forced=tot['forced'] / c, dry=tot['dry'] / tot['battles'],
                lost=tot['lost'] / tot['battles'], customs=c / tot['battles'],
                usable_med=us[len(us) // 2], usable_p10=us[len(us) // 10],
                key=tot['keyHit'] / max(1, tot['keyC']))

MOVES = load_moves('src/data/battle_moves.h')
_src = open('src/data/battle_moves.h').read()
MTYPE, ACC = {}, {}
for _m in re.finditer(r'\[MOVE_(\w+)\]\s*=\s*\{(.*?)\n    \}', _src, re.S):
    MTYPE[_m.group(1)] = re.search(r'\.type = TYPE_(\w+)', _m.group(2)).group(1)
    MOVES.get(_m.group(1), {})['acc'] = int(re.search(r'\.accuracy = (\d+)', _m.group(2)).group(1))
MOVES['__KEY__'] = dict(effect='EFFECT_HIT', power=70, pp=20, prio=0, acc=100); MTYPE['__KEY__'] = 'NORMAL'
# damaging moves that only work in a special state: not useful as general chips
CONDITIONAL = {'EFFECT_DREAM_EATER', 'EFFECT_SNORE', 'EFFECT_FAKE_OUT', 'EFFECT_SPIT_UP', 'EFFECT_FOCUS_PUNCH',
               'EFFECT_SKY_ATTACK'}
TYPES, COMPAT, FINAL = load_species()
POOL = hoenn_finals(TYPES, FINAL)
TSIZES = trainer_sizes()
CHART = load_chart()
AVG_EFF = {t: sum(effectiveness(t, TYPES[sp]) for sp in POOL) / len(POOL) for t in set(MTYPE.values())}

COMPAT_CAN = COMPAT

def make_learned(tm_per_mon=3):
    """Stricter rule: a Pokemon can use a chip only for moves it has LEARNED: its level-up moves (all levels,
    pre-evolutions included) plus a few TM/tutor moves the player taught it (its best ones by expected damage)."""
    out = collections.defaultdict(set)
    for sp in POOL:
        out[sp] = set(LEVELUP[sp])
        extra = sorted((m for m in COMPAT_CAN[sp] - LEVELUP[sp] if m in MOVES and MOVES[m]['power'] > 1),
                       key=lambda m: -AVG_EFF[MTYPE[m]] * eff_power(m, sp, TYPES))[:tm_per_mon]
        out[sp] |= set(extra)
    return out

def set_mode(mode):
    global COMPAT
    COMPAT = COMPAT_CAN if mode == 'can' else make_learned()

def composition(F=30, n=6, parties=200, seed=5):
    rng = random.Random(seed); univ = norm = tot = 0
    for _ in range(parties):
        party = rng.sample(POOL, n)
        f = build_folder(party, F, TYPES, COMPAT, 'balanced', rng)
        tot += len(f)
        univ += sum(1 for c in f if sum(c in COMPAT[sp] for sp in party) >= n - 1)
        norm += sum(1 for c in f if MTYPE[c] == 'NORMAL')
    return univ / tot, norm / tot

def main():
    print('%d fully evolved non-legendary Hoenn species; trainer parties: %s' % (len(POOL), sorted(collections.Counter(TSIZES).items())))
    u, nn = composition()
    print('Balanced folder of 30, full party: %.0f%% of chips usable by 5+ members, %.0f%% Normal-type' % (100 * u, 100 * nn))
    print('Average effectiveness of each type vs the Hoenn pool: ' + ', '.join('%s %.2f' % (t[:3], v) for t, v in sorted(AVG_EFF.items(), key=lambda x: -x[1]) if t != 'MYSTERY'))
    print('\nHow much of the folder each party member can use (balanced builder, full party of 6):')
    for F in (30, 40, 50):
        r = run(F, 6, parties=150, reps=1)
        print('  folder %d: median member can use %2.0f%%, worst 10%% of members %2.0f%%' % (F, 100 * r['usable_med'], 100 * r['usable_p10']))
    print('\nFull party of 6, battle mix (70% wild). dead = no usable chip for anyone in hand; forced = had to spend the')
    print('Custom on the Switch slot; dry = the folder ran out; lost = all 6 fainted before the enemies did.')
    for policy in ('balanced', 'own'):
        for F in (30, 40, 50, 60):
            r = run(F, 6, policy)
            print('  %-8s F=%d  dead %4.1f%%  forced %4.1f%%  dry %4.1f%%' % (policy, F, 100 * r['dead'], 100 * r['forced'], 100 * r['dry']))
    print('\nDepth: full party, balanced, battles vs m enemies (dry %% / lost %%)')
    for F in (30, 40, 50, 60):
        print('  F=%d  ' % F + '  '.join('m=%d %3.0f%%/%3.0f%%' % (m, 100 * run(F, 6, m=m, reps=8)['dry'], 100 * run(F, 6, m=m, reps=8)['lost']) for m in (1, 3, 4, 6)))
    print('\nCopy value: chance the lead\'s key move is in the hand, by copies (full party, balanced)')
    for F in (30, 40, 50):
        print('  F=%d  ' % F + '  '.join('%d cop %2.0f%%' % (k, 100 * run(F, 6, key_copies=k, reps=10, parties=100)['key']) for k in (1, 3, 5)))
    print('\nParty size (balanced, F=30 / 40)')
    for n in (1, 2, 3, 4, 6):
        a, b = run(30, n), run(40, n)
        print('  n=%d  F30 dead %4.1f%% forced %4.1f%% dry %3.1f%% | F40 dead %4.1f%% forced %4.1f%% dry %3.1f%%' % (
            n, 100 * a['dead'], 100 * a['forced'], 100 * a['dry'], 100 * b['dead'], 100 * b['forced'], 100 * b['dry']))

if __name__ == '__main__':
    for mode in ('can', 'learned'):
        set_mode(mode)
        print('\n==================== compatibility rule: %s ====================' % mode)
        main()
