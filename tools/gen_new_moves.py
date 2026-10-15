#!/usr/bin/env python3
"""POC-31: adds the Gen 4 moves (tools/new_moves_curated.py) to the port, and writes the Gen 4 physical / special
split for every move (Khaled's picks M1c M2a M3b M5a M6a).

    python3 tools/gen_new_moves.py <host tree> <pokeapi csv dir>      (upstream/pokeapi/data/v2/csv)

Writes, between "pkbn POC-31" markers so it can be run again:
  include/constants/moves.h               MOVE_* 355.. (after Psycho Boost) and MOVES_COUNT
  include/constants/battle_move_effects.h the new EFFECT_* (new_moves_curated.NEW_EFFECTS)
  src/data/battle_moves.h                 gBattleMoves entries, Platinum's numbers
  src/data/text/move_names.h              names
  src/data/text/move_descriptions.h       descriptions (new_moves_curated.MOVES)
  data/battle_anim_scripts.s              gBattleAnims_Moves: the borrowed Emerald animation
  data/battle_scripts_1.s                 gBattleScriptsForMoveEffects: the new effects hit like EFFECT_HIT
  src/pkbn/move_split.c, include/pkbn/move_split.h   gPkbnMoveSplit[MOVES_COUNT] (M3b)

Platinum's numbers (M5a): moves.csv holds today's values; move_changelog.csv holds, for each version group where a
field changed, the value it had BEFORE. A field's Platinum value is the old value in the first change after Platinum
that touches it, or today's if none did.
Emerald's move numbers are PokeAPI's move ids up to 354, so the split for Gen 1-3 moves is looked up by number.
"""
import csv, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from new_moves_curated import MOVES, EFFECTS, NEW_EFFECTS

ROOT, API = sys.argv[1], sys.argv[2]
def path(p): return os.path.join(ROOT, p)
def rd(p): return open(path(p)).read()
def wr(p, s): open(path(p), 'w').write(s)
def api(f): return list(csv.DictReader(open(os.path.join(API, f))))
BEGIN, END = 'pkbn POC-31 BEGIN (tools/gen_new_moves.py)', 'pkbn POC-31 END'

def strip(s):
    """drops a previous run's blocks (comment lines carrying the markers, and everything between)"""
    b, e = re.escape(BEGIN), re.escape(END)
    s = re.sub(r'(?<=\n)\n[^\n]*%s.*?%s[^\n]*\n(?=\n)' % (b, e), '', s, flags=re.S)   # a block between blank lines
    return re.sub(r'\n[^\n]*%s.*?%s[^\n]*' % (b, e), '', s, flags=re.S)

# ---- PokeAPI ----
vg = {r['id']: r for r in api('version_groups.csv')}
order = {i: int(r['order']) for i, r in vg.items()}
PT = next(i for i, r in vg.items() if r['identifier'] == 'platinum')
types = {r['id']: r['identifier'].upper() for r in api('types.csv')}
mv = {r['id']: r for r in api('moves.csv')}
byname = {r['identifier'].upper().replace('-', '_'): r for r in mv.values()}
chg = {}
for r in api('move_changelog.csv'):
    chg.setdefault(r['move_id'], []).append(r)
flags = {}
fid = {r['identifier']: r['id'] for r in api('move_flags.csv')}
for r in api('move_flag_map.csv'):
    flags.setdefault(r['move_id'], set()).add(r['move_flag_id'])

def platinum(r, field):
    later = sorted((c for c in chg.get(r['id'], []) if order[c['changed_in_version_group_id']] > order[PT] and c[field] != ''),
                   key=lambda c: order[c['changed_in_version_group_id']])
    return later[0][field] if later else r[field]

TARGET = {'10': 'MOVE_TARGET_SELECTED', '11': 'MOVE_TARGET_BOTH', '9': 'MOVE_TARGET_FOES_AND_ALLY', '7': 'MOVE_TARGET_USER',
          '8': 'MOVE_TARGET_RANDOM'}
FLINCHERS = {31, 146, 150, 157}   # Emerald effects that flinch on their own: no King's Rock (FLINCH_HIT, TWISTER, ...)

new = []
for name in MOVES:
    r = byname[name]
    eid = int(platinum(r, 'effect_id'))
    effect = EFFECTS.get(eid) or ('EFFECT_%d' % (eid - 1) if eid <= 214 else None)
    if effect is None:
        raise SystemExit('%s: PokeAPI effect %d has no Emerald effect and no entry in EFFECTS' % (name, eid))
    f = flags.get(r['id'], set())
    fl = (['FLAG_MAKES_CONTACT'] if fid['contact'] in f else []) + (['FLAG_PROTECT_AFFECTED'] if fid['protect'] in f else []) \
       + (['FLAG_MIRROR_MOVE_AFFECTED'] if fid['mirror'] in f else []) + (['FLAG_KINGS_ROCK_AFFECTED'] if eid - 1 not in FLINCHERS else [])
    new.append(dict(name=name, id=int(r['id']), type=types[platinum(r, 'type_id')], power=int(platinum(r, 'power') or 0),
                    acc=int(platinum(r, 'accuracy') or 0), pp=int(platinum(r, 'pp')), prio=int(platinum(r, 'priority')),
                    chance=int(platinum(r, 'effect_chance') or 0), target=TARGET[platinum(r, 'target_id')],
                    effect=effect, eid=eid, flags=fl, split={'2': 'SPLIT_PHYSICAL', '3': 'SPLIT_SPECIAL'}[r['damage_class_id']]))
new.sort(key=lambda m: m['id'])   # PokeAPI (national) order
EFFNUM = {}

# ---- include/constants/battle_move_effects.h ----
s = strip(rd('include/constants/battle_move_effects.h'))
n0 = max(int(x) for x in re.findall(r'#define EFFECT_\w+ (\d+)', s)) + 1   # Emerald's 214
s = re.sub(r'#define NUM_BATTLE_MOVE_EFFECTS \d+', '#define NUM_BATTLE_MOVE_EFFECTS %d' % n0, s)
block = ['// %s: Gen 4 effects, played by the grid (src/pkbn/grid_moves.c)' % BEGIN]
for i, e in enumerate(NEW_EFFECTS):
    block.append('#define %s %d' % (e, n0 + i)); EFFNUM[e] = n0 + i
block.append('// %s' % END)
s = s.replace('#define NUM_BATTLE_MOVE_EFFECTS %d' % n0, '\n'.join(block) + '\n\n#define NUM_BATTLE_MOVE_EFFECTS %d' % (n0 + len(NEW_EFFECTS)))
wr('include/constants/battle_move_effects.h', s)
# the Emerald effect names, to write EFFECT_HIT rather than EFFECT_0
ENAME = {int(n): e for e, n in re.findall(r'#define (EFFECT_\w+) (\d+)', s)}
for m in new:
    if m['effect'].startswith('EFFECT_') and m['effect'][7:].isdigit():
        m['effect'] = ENAME[int(m['effect'][7:])]

# ---- data/battle_scripts_1.s ----
s = strip(rd('data/battle_scripts_1.s'))
lines = s.split('\n')
i = lines.index('gBattleScriptsForMoveEffects::') + 1
while i < len(lines) and lines[i].strip().startswith('ptrvalue'):
    i += 1
assert i - lines.index('gBattleScriptsForMoveEffects::') - 1 == n0, 'gBattleScriptsForMoveEffects has %d rows' % n0
lines[i:i] = ['@ %s' % BEGIN] + ['\tptrvalue BattleScript_EffectHit                    /* %s: the grid plays it */' % e for e in NEW_EFFECTS] + ['@ %s' % END]
wr('data/battle_scripts_1.s', '\n'.join(lines))

# ---- include/constants/moves.h ----
s = strip(rd('include/constants/moves.h'))
count = max(int(x) for x in re.findall(r'#define MOVE_\w+ (\d+)', s) if int(x) < 0xFFFF) + 1   # Emerald's 355
s = re.sub(r'#define MOVES_COUNT \d+', '#define MOVES_COUNT %d' % count, s)
block = ['// %s: Gen 4 moves, in PokeAPI order (Platinum numbers)' % BEGIN]
for i, m in enumerate(new):
    m['num'] = count + i
    block.append('#define MOVE_%s %d' % (m['name'], m['num']))
block.append('// %s' % END)
s = s.replace('#define MOVES_COUNT %d' % count, '\n'.join(block) + '\n\n#define MOVES_COUNT %d' % (count + len(new)))
wr('include/constants/moves.h', s)
assert count + len(new) <= 0x1FF, 'LEVEL_UP_MOVE packs move ids in 9 bits'

# ---- src/data/battle_moves.h ----
s = strip(rd('src/data/battle_moves.h'))
k = s.rstrip().rfind('};')
ent = ['    // %s: Platinum\'s numbers (PokeAPI moves.csv + move_changelog.csv)' % BEGIN]
for m in new:
    ent += ['    [MOVE_%s] =' % m['name'], '    {',
            '        .effect = %s,' % m['effect'], '        .power = %d,' % m['power'], '        .type = TYPE_%s,' % m['type'],
            '        .accuracy = %d,' % m['acc'], '        .pp = %d,' % m['pp'], '        .secondaryEffectChance = %d,' % m['chance'],
            '        .target = %s,' % m['target'], '        .priority = %d,' % m['prio'],
            '        .flags = %s,' % (' | '.join(m['flags']) or '0'), '    },']
ent.append('    // %s' % END)
s = s[:k].rstrip() + '\n' + '\n'.join(ent) + '\n' + s[k:]
wr('src/data/battle_moves.h', s)

# ---- names and descriptions ----
def gname(m):
    n = m['name'].replace('_', ' ')
    return {'X SCISSOR': 'X-SCISSOR', 'WAKE UP SLAP': 'WAKE-UP SLAP'}.get(n, n)
s = strip(rd('src/data/text/move_names.h'))
k = s.rstrip().rfind('};')
ent = ['    // %s' % BEGIN] + ['    [MOVE_%s] = _("%s"),' % (m['name'], gname(m)) for m in new] + ['    // %s' % END]
for m in new:
    assert len(gname(m)) <= 12, gname(m)
s = s[:k].rstrip() + '\n' + '\n'.join(ent) + '\n' + s[k:]
wr('src/data/text/move_names.h', s)

def cname(m): return 's' + ''.join(w.capitalize() for w in m['name'].split('_')) + 'Description'
s = strip(rd('src/data/text/move_descriptions.h'))
k = s.find('// MOVE_NONE is ignored in this table')
strs = ['// %s' % BEGIN]
for m in new:
    a, b = MOVES[m['name']][1].split('\n')
    strs += ['static const u8 %s[] = _(' % cname(m), '    "%s\\n"' % a.replace('"', '\\"'), '    "%s");' % b.replace('"', '\\"'), '']
strs.append('// %s' % END)
s = s[:k] + '\n'.join(strs) + '\n\n' + s[k:]
k = s.rstrip().rfind('};')
ent = ['    // %s' % BEGIN] + ['    [MOVE_%s - 1] = %s,' % (m['name'], cname(m)) for m in new] + ['    // %s' % END]
s = s[:k].rstrip() + '\n' + '\n'.join(ent) + '\n' + s[k:]
wr('src/data/text/move_descriptions.h', s)

# ---- data/battle_anim_scripts.s ----
# (the markers ride on the first and last rows: tools/gen_move_sounds.py reads the table up to its first non-row line)
s = strip(rd('data/battle_anim_scripts.s'))
m0 = re.search(r'\n\tptrvalue Move_COUNT\b', s)
rows = ['\tptrvalue Move_%s @ %s' % (MOVES[m['name']][0], m['name']) for m in new]
rows[0] += ' -- %s: borrowed Emerald animations (tools/new_moves_curated.py)' % BEGIN
rows[-1] += ' -- %s' % END
s = s[:m0.start()] + '\n' + '\n'.join(rows) + s[m0.start():]
wr('data/battle_anim_scripts.s', s)

# ---- the split (M3b) ----
num = {n: int(i) for n, i in re.findall(r'#define MOVE_(\w+) (\d+)', rd('include/constants/moves.h'))}
split = {}
for n, i in num.items():
    if n in ('NONE', 'COUNT', 'UNAVAILABLE') or i >= count + len(new):
        continue
    r = mv[str(i)] if i < count else byname[n]
    split[n] = {'2': 'SPLIT_PHYSICAL', '3': 'SPLIT_SPECIAL'}.get(r['damage_class_id'], 'SPLIT_STATUS')
c = ['// GENERATED by tools/gen_new_moves.py from PokeAPI moves.csv (damage_class_id) - do not edit.',
     '// POC-31 (M3b): the Gen 4 split. Every move is physical, special or status by itself, no longer by its type.',
     '#include "global.h"', '#include "constants/moves.h"', '#include "pkbn/move_split.h"', '',
     'const u8 gPkbnMoveSplit[MOVES_COUNT] =', '{']
c += ['    [MOVE_%s] = %s,' % (n, sp) for n, sp in sorted(split.items(), key=lambda x: num[x[0]])]
c += ['};', '']
wr('src/pkbn/move_split.c', '\n'.join(c))
wr('include/pkbn/move_split.h', '''// GENERATED by tools/gen_new_moves.py - do not edit.
#ifndef GUARD_PKBN_MOVE_SPLIT_H
#define GUARD_PKBN_MOVE_SPLIT_H
#include "constants/moves.h"
#include "constants/pokemon.h"
#define SPLIT_STATUS   0
#define SPLIT_PHYSICAL 1
#define SPLIT_SPECIAL  2
extern const u8 gPkbnMoveSplit[MOVES_COUNT];
// POC-31 (M3b): is this hit physical? The move's own category; for a move with none (MOVE_NONE, a status move used
// as a Program Advance's last chip) Gen 3's rule by type.
#define PKBN_IS_PHYSICAL(move, type) (((move) != 0 && (move) < MOVES_COUNT && gPkbnMoveSplit[(move)] != SPLIT_STATUS) \\
                                      ? gPkbnMoveSplit[(move)] == SPLIT_PHYSICAL : (type) < TYPE_MYSTERY)
#endif // GUARD_PKBN_MOVE_SPLIT_H
''')

changed = [n for n in split if n in num and num[n] < count and
           (split[n] == 'SPLIT_PHYSICAL') != (types[mv[str(num[n])]['type_id']] in
                                               ('NORMAL', 'FIGHTING', 'FLYING', 'POISON', 'GROUND', 'ROCK', 'BUG', 'GHOST', 'STEEL'))
           and split[n] != 'SPLIT_STATUS']
print('new moves: %d (MOVE_%s %d .. MOVE_%s %d), MOVES_COUNT %d' % (len(new), new[0]['name'], new[0]['num'], new[-1]['name'],
                                                                    new[-1]['num'], count + len(new)))
print('Gen 3 moves whose category changes with the split: %d' % len(changed))
import json
json.dump({m['name']: {k: v for k, v in m.items() if k != 'flags'} | {'flags': m['flags']} for m in new},
          open(path('build/pkbn_new_moves.json'), 'w'), indent=1)
