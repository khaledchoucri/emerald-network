#!/usr/bin/env python3
"""Chip memory (MB) and copy caps for every Gen 3 move -- docs/design/08-folder-memory.md.

Reads the moves from the port's own data (src/data/battle_moves.h). Rules (all TUNE):
  damaging move: MB = round(K * power * hits) + adjustments
  power <= 1 (fixed damage, OHKO, variable): MB from PP, like status moves
  status move:   MB = round(200 / PP)   (POC-10: 300/PP left weather moves (PP 5) at 1 copy)
Copy cap = BN6's rule by MB (bn6f asm/asm36.s:10634): <=19 -> 5, 20-29 -> 4, 30-39 -> 3, 40-49 -> 2, >=50 -> 1.
"""
import re, sys, collections

K = 0.3
HITS = {'EFFECT_MULTI_HIT': 3, 'EFFECT_DOUBLE_HIT': 2, 'EFFECT_DOUBLE_POISON_HIT': 2, 'EFFECT_TRIPLE_KICK': 6,
        'EFFECT_BEAT_UP': 3}
ADJ = {'EFFECT_RECHARGE': -5, 'EFFECT_HIGH_CRITICAL': +5, 'EFFECT_QUICK_ATTACK': +8, 'EFFECT_RAZOR_WIND': -3,
       'EFFECT_SOLAR_BEAM': -5, 'EFFECT_SKY_ATTACK': -5, 'EFFECT_SKULL_BASH': -5, 'EFFECT_SEMI_INVULNERABLE': -3,
       'EFFECT_EXPLOSION': -10, 'EFFECT_RECOIL': -3, 'EFFECT_DOUBLE_EDGE': -3, 'EFFECT_FUTURE_SIGHT': -5}
MEGA = {'EFFECT_EXPLOSION', 'EFFECT_RECHARGE', 'EFFECT_OHKO'}

def load(path):
    src = open(path).read()
    moves = {}
    for m in re.finditer(r'\[MOVE_(\w+)\]\s*=\s*\{(.*?)\n    \}', src, re.S):
        name, body = m.group(1), m.group(2)
        g = lambda k: re.search(r'\.%s = ([^,]+),' % k, body).group(1).strip()
        if name == 'NONE':
            continue
        moves[name] = dict(effect=g('effect'), power=int(g('power')), pp=int(g('pp')), prio=int(g('priority')))
    return moves

def mb(mv):
    if mv['power'] <= 1:
        return max(1, round(200 / mv['pp'])) if mv['pp'] else 99
    v = K * mv['power'] * HITS.get(mv['effect'], 1) + ADJ.get(mv['effect'], 0)
    if mv['prio'] > 0 and mv['effect'] != 'EFFECT_QUICK_ATTACK':
        v += 8
    return max(1, round(v))

def cap(m):
    return 5 if m <= 19 else 4 if m <= 29 else 3 if m <= 39 else 2 if m <= 49 else 1

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'src/data/battle_moves.h'
    moves = load(path)
    hist = collections.Counter(cap(mb(v)) for v in moves.values())
    print('%d moves; copy caps: %s' % (len(moves), ', '.join('%d copies: %d' % (c, hist[c]) for c in (5, 4, 3, 2, 1))))
    for n in ('POUND', 'EMBER', 'QUICK_ATTACK', 'WATER_GUN', 'BITE', 'THUNDERBOLT', 'FLAMETHROWER', 'SURF', 'EARTHQUAKE',
              'FIRE_BLAST', 'HYDRO_PUMP', 'DOUBLE_EDGE', 'HYPER_BEAM', 'SELF_DESTRUCT', 'EXPLOSION', 'FURY_SWIPES',
              'DOUBLE_KICK', 'SEISMIC_TOSS', 'SWORDS_DANCE', 'GROWL', 'TOXIC', 'SPORE', 'RECOVER', 'PSYCHO_BOOST',
              'DOOM_DESIRE', 'SHEER_COLD'):
        if n in moves:
            v = moves[n]
            print('  %-14s power %3d pp %2d  MB %2d  cap %d' % (n, v['power'], v['pp'], mb(v), cap(mb(v))))
