#!/usr/bin/env python3
"""POC-31: writes the reviewed learnsets into the port (Khaled's picks L1a L2c L3a L4a L5a M2a; reviewed line by line on
the Learnset Review page and approved as a whole).

    python3 tools/gen_learnsets.py <host tree> [data/learnset_ladders.json]

data/learnset_ladders.json is tools/learnset_ladders.py's output as reviewed: for every member of the 112 Hoenn lines,
its Emerald learnset ("before") and the new one ("after"). This replaces each member's array in
src/data/pokemon/level_up_learnsets.h with "after", after checking the array still holds "before" (it refuses to write
over a learnset that changed since the review).
Order inside a level: Emerald's own entries keep Emerald's order and the new ones follow them, because a Pokemon given
its level-up moves (wild and trainer Pokemon) keeps the last four it learned.
One fix on top of the review: a ladder step removes the move's earlier entry, and in 32 learnsets that left the
Pokemon with no damaging move until the ladder's Lv 10 step (Wingull's Water Gun, Ralts' Confusion, Pikachu's
ThunderShock ...). Those earlier entries stay (KEEP_EARLY), so the first damaging move comes when it did in Emerald.
Also raises MAX_LEVEL_UP_MOVES (include/constants/pokemon.h) when a learnset outgrows it.
"""
import json, os, re, sys
ROOT = sys.argv[1]
DATA = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'learnset_ladders.json')
P = os.path.join(ROOT, 'src/data/pokemon/level_up_learnsets.h')
s = open(P).read()
ptr = dict(re.findall(r'\[SPECIES_(\w+)\] = s(\w+)LevelUpLearnset', open(os.path.join(ROOT, 'src/data/pokemon/level_up_learnset_pointers.h')).read()))
d = json.load(open(DATA))
power = {}
for mm in re.finditer(r'\[MOVE_(\w+)\] =\s*\{(.*?)\n    \}', open(os.path.join(ROOT, 'src/data/battle_moves.h')).read(), re.S):
    pw = re.search(r'\.power = (\d+)', mm.group(2))
    power[mm.group(1)] = int(pw.group(1)) if pw else 0
def first_hit(ls):
    return min([lv for lv, mv in ls if power.get(mv, 0) > 0] or [999])
kept = []
longest, done = 0, 0
for line in d['lines']:
    for m in line['members']:
        arr = ptr[m['species']]
        rx = re.compile(r'(static const u16 s%sLevelUpLearnset\[\] = \{)(.*?)(\};)' % arr, re.S)
        g = rx.search(s)
        cur = [(int(a), b) for a, b in re.findall(r'LEVEL_UP_MOVE\(\s*(\d+), MOVE_(\w+)\)', g.group(2))]
        after = [tuple(x) for x in m['after']]
        before = [tuple(x) for x in m['before']]
        while first_hit(after) > first_hit(before):   # KEEP_EARLY (see above)
            e = min((x for x in before if power.get(x[1], 0) > 0 and x not in after), key=lambda x: x[0])
            after.append(e); kept.append('%s %s Lv %d' % (m['species'], e[1], e[0]))
        if sorted(cur) == sorted(after):
            continue                                   # already written
        if sorted(cur) != sorted(tuple(x) for x in m['before']):
            raise SystemExit('%s: the learnset changed since the review' % m['species'])
        # Emerald's entries in Emerald's order (a moved one keeps its place among its new level's), new ones after
        pos = {}
        for i, (lv, mv) in enumerate(cur):
            pos.setdefault(mv, i)
        left = list(after)
        def key(e):
            lv, mv = e
            return (lv, 0, pos[mv]) if mv in pos else (lv, 1, mv)
        left.sort(key=key)
        body = '\n' + ''.join('    LEVEL_UP_MOVE(%2d, MOVE_%s),\n' % e for e in left) + '    LEVEL_UP_END\n'
        s = s[:g.start(2)] + body + s[g.end(2):]
        longest = max(longest, len(left)); done += 1
open(P, 'w').write(s)
H = os.path.join(ROOT, 'include/constants/pokemon.h')
h = open(H).read()
mx = int(re.search(r'#define MAX_LEVEL_UP_MOVES\s+(\d+)', h).group(1))
need = max(len(m['after']) + 1 for line in d['lines'] for m in line['members'])
if need > mx:
    h = re.sub(r'#define MAX_LEVEL_UP_MOVES\s+\d+', '#define MAX_LEVEL_UP_MOVES       %d // pkbn POC-31: the new learnsets (was 20)' % need, h)
    open(H, 'w').write(h)
print('kept early entries (%d): %s' % (len(kept), ', '.join(kept)))
print('learnsets written: %d; longest %d; MAX_LEVEL_UP_MOVES %d' % (done, need, max(mx, need)))
