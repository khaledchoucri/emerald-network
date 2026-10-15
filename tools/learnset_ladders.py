#!/usr/bin/env python3
"""Learnset ladders and new moves (Khaled's picks L1a L2c L3a L4a L5a, M1c M2a M3b M5a): a DRAFT for review, nothing
here is built into the game yet.

    python3 tools/learnset_ladders.py <host tree> <pokeapi csv dir> out.json

- New moves (M1c): the damaging moves that Hoenn Pokemon learn by level-up in Platinum and Emerald doesn't have, minus
  the ones that need a mechanic grid battles lack (held items) or a grid version of their own. Power and accuracy as in
  Platinum (M5a: moves.csv, minus later changes in move_changelog.csv). Category (M3b) from moves.csv damage_class.
- Each Hoenn line (a base species of the Hoenn dex and its evolutions) gets a ladder (L1a): three damaging moves of its
  type, at Lv 10, 20 and 30 (L2c), powers up to 55 / 75 / 90, each at least as strong as the one before. The line's own
  moves come first (anything it can learn in Emerald: level-up, TM, tutor, egg), then a new move it learns in
  Platinum, then any Gen 3 move of the type, then any new move of the type (L3a). With the Gen 4 split, a move of the
  category matching the line's stronger attacking stat (final form's Attack vs Sp. Atk) is preferred within each rank.
- Learnsets (M2a, L5a): Emerald's, plus the new moves at the level each species learns them in Platinum, plus the
  ladder at 10 / 20 / 30 for every member of the line (an earlier entry of a ladder move is removed). A move already at
  a ladder level moves to the next free level.
Sources: src/data/pokemon/level_up_learnsets.h, level_up_learnset_pointers.h, species_info.h, evolution.h,
src/data/battle_moves.h, include/constants/pokedex.h (Hoenn dex order), and PokeAPI's data/v2/csv tables."""
import csv, json, os, re, sys, collections

ROOT, API, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
def rd(p): return open(os.path.join(ROOT, p)).read()
def api(f): return list(csv.DictReader(open(os.path.join(API, f))))

# ---- Emerald data ----
learn = {m.group(1): [(int(a), b) for a, b in re.findall(r'LEVEL_UP_MOVE\(\s*(\d+), MOVE_(\w+)\)', m.group(2))]
         for m in re.finditer(r'static const u16 s(\w+)LevelUpLearnset\[\] = \{(.*?)\};', rd('src/data/pokemon/level_up_learnsets.h'), re.S)}
ptr = dict(re.findall(r'\[SPECIES_(\w+)\] = s(\w+)LevelUpLearnset', rd('src/data/pokemon/level_up_learnset_pointers.h')))
moves3 = {}
for m in re.finditer(r'\[MOVE_(\w+)\] =\s*\{(.*?)\n    \}', rd('src/data/battle_moves.h'), re.S):
    b = m.group(2); p = re.search(r'\.power = (\d+)', b); t = re.search(r'\.type = TYPE_(\w+)', b)
    moves3[m.group(1)] = (int(p.group(1)) if p else 0, t.group(1) if t else None)
spec = {}
for m in re.finditer(r'\[SPECIES_(\w+)\]\s*=\s*\{(.*?)\n    \}', rd('src/data/pokemon/species_info.h'), re.S):
    b = m.group(2)
    if '.types' not in b: continue
    g = lambda k: int(re.search(r'\.%s\s*=\s*(\d+)' % k, b).group(1))
    spec[m.group(1)] = dict(types=re.findall(r'TYPE_(\w+)', re.search(r'\.types = \{([^}]*)\}', b).group(1)), atk=g('baseAttack'), spa=g('baseSpAttack'))
pre = collections.defaultdict(list); nxt = collections.defaultdict(list)
for m in re.finditer(r'\[SPECIES_(\w+)\]\s*=\s*\{(.*?)\}\s*,\s*\n', rd('src/data/pokemon/evolution.h'), re.S):
    for _, _, c in re.findall(r'\{EVO_(\w+),\s*(\w+),\s*SPECIES_(\w+)\}', m.group(2)):
        pre[c].append(m.group(1)); nxt[m.group(1)].append(c)
hoenn = [m.group(1) for m in re.finditer(r'HOENN_DEX_(\w+),', rd('include/constants/pokedex.h'))][:202]
def _line(b):
    out = [b]; i = 0
    while i < len(out):
        out += [c for c in nxt[out[i]] if c not in out]; i += 1
    return out
HOENN_SPECIES = {x for sp in hoenn if sp not in pre for x in _line(sp)}
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shared_folder_sim as sim
_, compat, _ = sim.load_species()

# ---- PokeAPI ----
VG = {r['identifier']: r for r in api('version_groups.csv')}
order = {r['id']: int(r['order']) for r in VG.values()}
PT = VG['platinum']['id']
types = {r['id']: r['identifier'].upper() for r in api('types.csv')}
mvs = {r['id']: r for r in api('moves.csv')}
chg = collections.defaultdict(list)
for r in api('move_changelog.csv'): chg[r['move_id']].append(r)
def as_in_platinum(r):
    p, a = r['power'], r['accuracy']
    later = [c for c in chg[r['id']] if order[c['changed_in_version_group_id']] > order[PT]]
    if later:
        c = min(later, key=lambda c: order[c['changed_in_version_group_id']])
        p = c['power'] or p; a = c['accuracy'] or a
    return int(p or 0), int(a or 0)
def ident(r): return r['identifier'].upper().replace('-', '_')
CAT = {ident(r): {'2': 'physical', '3': 'special'}.get(r['damage_class_id'], 'status') for r in mvs.values()}
# Emerald's moves by their number (the same as PokeAPI's move ids), so renamed ones (FAINT_ATTACK = feint-attack) match
for name, num in re.findall(r'#define MOVE_(\w+) (\d+)\n', rd('include/constants/moves.h')):
    if num in mvs: CAT[name] = {'2': 'physical', '3': 'special'}.get(mvs[num]['damage_class_id'], 'status')
# M1c: damaging, a Gen 3 effect or a small new rule does it (see the M1 picks page); not: held items, grid versions
NEEDS_GRID = {'U_TURN', 'SUCKER_PUNCH', 'PAYBACK', 'ASSURANCE', 'FEINT', 'GYRO_BALL', 'WRING_OUT', 'LAST_RESORT', 'TRUMP_CARD',
              'PUNISHMENT', 'NATURAL_GIFT', 'FLING'}
pkid = {r['identifier'].upper().replace('-', '_'): r['id'] for r in api('pokemon.csv')}
idname = {pid: n for n, pid in pkid.items()}
ptlearn = collections.defaultdict(list)   # species -> [(level, move)] for moves Emerald lacks
new = {}
for r in api('pokemon_moves.csv'):
    if r['version_group_id'] != PT or r['pokemon_move_method_id'] != '1': continue
    m = mvs[r['move_id']]
    if int(m['generation_id']) < 4 or CAT[ident(m)] == 'status' or ident(m) in NEEDS_GRID: continue
    p, a = as_in_platinum(m)
    if p <= 1: continue
    if idname.get(r['pokemon_id']) not in HOENN_SPECIES: continue
    new[ident(m)] = dict(type=types[m['type_id']], power=p, acc=a, cat=CAT[ident(m)], pp=int(m['pp']))
    ptlearn[idname.get(r['pokemon_id'])].append((int(r['level']), ident(m)))
def power(m): return moves3[m][0] if m in moves3 else new[m]['power']
def mtype(m): return moves3[m][1] if m in moves3 else new[m]['type']

# ---- lines and ladders ----
EXCL = set('''FUTURE_SIGHT DOOM_DESIRE SELF_DESTRUCT EXPLOSION SKY_ATTACK SOLAR_BEAM HYPER_BEAM FOCUS_PUNCH DREAM_EATER SNORE
FAKE_OUT BIDE COUNTER MIRROR_COAT SPIT_UP RAZOR_WIND SKULL_BASH FLY DIVE DIG BOUNCE OVERHEAT PSYCHO_BOOST ERUPTION
WATER_SPOUT FLAIL REVERSAL REVENGE SMELLING_SALT FACADE SECRET_POWER THIEF COVET UPROAR TRI_ATTACK RETURN FRUSTRATION
HIDDEN_POWER WEATHER_BALL PRESENT MAGNITUDE BEAT_UP PURSUIT SUPER_FANG SONIC_BOOM DRAGON_RAGE SEISMIC_TOSS NIGHT_SHADE
PSYWAVE LOW_KICK ENDEAVOR STRUGGLE FALSE_SWIPE ROLLOUT ICE_BALL FURY_CUTTER HI_JUMP_KICK JUMP_KICK DOUBLE_EDGE
VOLT_TACKLE TAKE_DOWN SUBMISSION THRASH PETAL_DANCE OUTRAGE BLAST_BURN HYDRO_CANNON FRENZY_PLANT ZAP_CANNON
DYNAMIC_PUNCH GIGA_IMPACT FLARE_BLITZ BRAVE_BIRD HEAD_SMASH LEAF_STORM GUNK_SHOT CLOSE_COMBAT HAMMER_ARM STONE_EDGE
MIST_BALL LUSTER_PURGE SACRED_FIRE AEROBLAST EXTREME_SPEED BRINE WAKE_UP_SLAP'''.split())
STEPS = [(10, 55), (20, 75), (30, 90)]
def line_of(base):
    out = [base]; i = 0
    while i < len(out):
        out += [c for c in nxt[out[i]] if c not in out]; i += 1
    return out
lines = []
for sp in hoenn:
    if sp == 'NONE' or sp in pre or sp not in spec or sp in [x for l in lines for x in l['line']]: continue
    L = line_of(sp); fin = L[-1]
    t = spec[sp]['types'][0]
    if t == 'NORMAL' and len(set(spec[fin]['types'])) > 1: t = [x for x in spec[fin]['types'] if x != 'NORMAL'][0]
    want = 'physical' if spec[fin]['atk'] >= spec[fin]['spa'] else 'special'
    own = {m for x in L for m in compat.get(x, []) if mtype(m) == t and power(m) > 1 if m in moves3}
    canon = {m for x in L for _, m in ptlearn.get(x, []) if new[m]['type'] == t}
    pool = [m for m in moves3 if moves3[m][1] == t and moves3[m][0] > 1] + [m for m in new if new[m]['type'] == t]
    def rank(m): return 0 if m in own else 1 if m in canon else 2 if m in moves3 else 3
    c = [m for m in pool if m not in EXCL]
    best = None
    # every legal ladder (powers within the steps' caps, rising or equal); the best one: the line's own moves first,
    # then the strongest last step, then fewest category mismatches (M3b), then the strongest middle and first steps
    for a in c:
        if power(a) > STEPS[0][1]: continue
        for b in c:
            if b == a or not power(a) <= power(b) <= STEPS[1][1]: continue
            for d in c:
                if d in (a, b) or not power(b) <= power(d) <= STEPS[2][1]: continue
                trio = (a, b, d)
                score = (sum(rank(m) for m in trio), -power(d), sum(CAT.get(m) != want for m in trio), -power(b), -power(a))
                if best is None or score < best[0]: best = (score, trio)
    ladder = None
    if best:
        ladder = [dict(level=lv, move=m, power=power(m), cat=CAT.get(m),
                       source=['own', 'Platinum', 'borrowed (Gen 3)', 'borrowed (new)'][rank(m)])
                  for (lv, _), m in zip(STEPS, best[1])]
    lines.append(dict(base=sp, line=L, type=t, attacker=want, ladder=ladder))

# ---- codes (L4a): the ladder's three moves share a letter ----
LANES = {m.group(1): [x or '*' for x, _ in re.findall(r"LANE\('(\w)'\)|(LANE_WILD)", m.group(2))]
         for m in re.finditer(r'\[MOVE_(\w+)\] = \{[^\n]*?\{([^}]*)\}\s*\}', rd('src/pkbn/move_table.c'))}
CODE_ORDER = "AVLHGTQKYZONFUSMCEXRWPBIDJ"   # src/pkbn/pkbn_save.c sCodeOrder: the order codes unlock in
for l in lines:
    if not l['ladder']: continue
    sets = [set(LANES.get(s['move'], [])) - {'*'} for s in l['ladder']]
    common = set.intersection(*sets) if all(sets) else set()
    if common:
        l['letter'] = min(common, key=CODE_ORDER.index); l['letter_added_to'] = []
    else:
        # the letter most of the three already have, earliest to unlock; the others get it as one of their codes
        cnt = collections.Counter(x for s in sets for x in s)
        pick = min(cnt, key=lambda x: (-cnt[x], CODE_ORDER.index(x))) if cnt else 'A'
        l['letter'] = pick
        l['letter_added_to'] = [s['move'] for s, st in zip(l['ladder'], sets) if pick not in st]

# ---- learnsets ----
def build(spname, ladder):
    before = sorted(learn.get(ptr.get(spname, ''), []))
    after = list(before)
    for lv, m in ptlearn.get(spname, []):
        if not any(x[1] == m for x in after): after.append((lv, m))
    if ladder:
        lmoves = {s['move'] for s in ladder}
        after = [x for x in after if x[1] not in lmoves]
        taken = collections.Counter(lv for lv, _ in after)
        for s in ladder:
            lv = s['level']
            # L5a: whatever is at the ladder level moves on to the next free level
            moved = [x for x in after if x[0] == lv]
            for x in moved:
                after.remove(x); nl = lv + 1
                while any(y[0] == nl for y in after) or nl in (10, 20, 30): nl += 1
                after.append((nl, x[1]))
            after.append((lv, s['move']))
    return before, sorted(after)
out = dict(new_moves=new, lines=[])
for l in lines:
    members = []
    for x in l['line']:
        b, a = build(x, l['ladder'])
        members.append(dict(species=x, before=b, after=a, added=[m for _, m in a if m not in {y for _, y in b}]))
    out['lines'].append(dict(l, members=members))
json.dump(out, open(OUT, 'w'), indent=1)
used = collections.Counter(s['move'] for l in lines if l['ladder'] for s in l['ladder'] if s['move'] in new)
print('lines', len(lines), 'no ladder', [l['base'] for l in lines if not l['ladder']], 'new moves', len(new), 'in ladders', len(used))
