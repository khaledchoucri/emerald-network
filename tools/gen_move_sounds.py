#!/usr/bin/env python3
"""POC-15: each move's sound effects, as Emerald's battle animation plays them.

Reads the game's own animation scripts (data/battle_anim_scripts.s, gBattleAnims_Moves) and walks each move's script
in order, adding up its `delay`s, to get WHEN each sound starts and with which panning:
  playsewithpan / playse / waitplaysewithpan / loopsewithpan / panse*, createsoundtask SoundTask_LoopSEAdjustPanning and
  SoundTask_FireBlast (battle_anim_sound_tasks.c), createvisualtask SoundTask_PlaySE1/2WithPanning, and the cry tasks
  (SoundTask_PlayDoubleCry, SoundTask_PlayCryHighPitch, SoundTask_PlayCryWithEcho: the user's cry).
`call` is followed, `goto` too, branches take their first label. `waitforvisualfinish` / `waitsound` have no fixed
length in the scripts (they wait for sprites); we count WAIT frames for them (TUNE).

Usage: python3 tools/gen_move_sounds.py <pokeemerald dir>   -> writes src/pkbn/move_sounds.c
Also writes Emerald's status and general animations' sounds (gPkbnStatusSounds, gPkbnGeneralSounds; POC-15e).
"""
import re, sys, os
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
WAIT = 8          # frames for waitforvisualfinish / waitsound (TUNE)
MAX_EVENTS = 14
MAX_T = 240

src = open(os.path.join(ROOT, 'data/battle_anim_scripts.s')).read().split('\n')
labels = {}
cur = None
for i, l in enumerate(src):
    m = re.match(r'^([A-Za-z_0-9]+)::?\s*$', l)
    if m:
        cur = m.group(1)
        labels[cur] = i + 1
def table(name):
    out, i = [], labels[name]
    while i < len(src):
        m = re.match(r'\s*ptrvalue\s+(\w+)', src[i])
        if not m:
            break
        out.append(m.group(1))
        i += 1
    return out

# the move -> script table, in move order
order = table('gBattleAnims_Moves')

def args(l, cmd):
    return [a.strip() for a in l.strip()[len(cmd):].split(',')]

def walk(label, t, ev, depth=0):
    """returns (t at end, ended?)"""
    if depth > 8 or label not in labels:
        return t, True
    i = labels[label]
    while i < len(src) and t <= MAX_T:
        l = src[i].split('@')[0].strip()
        i += 1
        if not l or l.startswith('.'):
            continue
        if re.match(r'^[A-Za-z_0-9]+::?$', l):
            continue          # falls through into the next label
        w = l.split()[0]
        if w == 'end':
            return t, True
        if w == 'return':
            return t, False
        if w == 'delay':
            t += int(args(l, 'delay')[0], 0); continue
        if w in ('waitforvisualfinish', 'waitsound'):
            t += WAIT; continue
        if w == 'call':
            t, ended = walk(args(l, 'call')[0], t, ev, depth + 1)
            if ended:
                return t, True
            continue
        if w == 'goto':
            return walk(args(l, 'goto')[0], t, ev, depth + 1)
        if w == 'choosetwoturnanim':
            return walk(args(l, 'choosetwoturnanim')[0], t, ev, depth + 1)
        if w == 'playsewithpan':
            a = args(l, 'playsewithpan'); ev.append((t, a[0], a[1])); continue
        if w == 'playse':
            ev.append((t, args(l, 'playse')[0], '0')); continue
        if w == 'waitplaysewithpan':
            a = args(l, 'waitplaysewithpan'); ev.append((t + int(a[2], 0), a[0], a[1])); continue
        if w == 'loopsewithpan':
            a = args(l, 'loopsewithpan')
            for k in range(int(a[3], 0)):
                ev.append((t + k * int(a[2], 0), a[0], a[1]))
            continue
        if w in ('panse', 'panse_adjustnone', 'panse_adjustall'):
            a = args(l, w); ev.append((t, a[0], a[1])); continue
        if w == 'createsoundtask':
            a = args(l, 'createsoundtask')
            if a[0] == 'SoundTask_LoopSEAdjustPanning':
                # args: se, startPan, targetPan, panIncrement, count, panDelay, interval (plays every interval+1)
                for k in range(int(a[5], 0)):
                    ev.append((t + k * (int(a[7], 0) + 1), a[1], a[2]))
            elif a[0] == 'SoundTask_FireBlast':
                for k in range(0, 111, 11):
                    ev.append((t + 1 + k, a[1], 'SOUND_PAN_ATTACKER'))
                ev.append((t + 117, a[2], 'SOUND_PAN_TARGET')); ev.append((t + 123, a[2], 'SOUND_PAN_TARGET'))
            continue
        if w == 'createvisualtask':
            a = args(l, 'createvisualtask')
            if a[0] in ('SoundTask_PlaySE1WithPanning', 'SoundTask_PlaySE2WithPanning'):
                ev.append((t, a[2], a[3]))
            elif a[0] in ('SoundTask_PlayDoubleCry', 'SoundTask_PlayCryHighPitch', 'SoundTask_PlayCryWithEcho'):
                ev.append((t, 'CRY', '0'))
            continue
        # jumps that depend on the battle: not taken (the script's normal path)
    return t, True

moves = []
COUNT = int(re.search(r'#define MOVES_COUNT (\d+)', open(os.path.join(ROOT, 'include/constants/moves.h')).read()).group(1))
for l in open(os.path.join(ROOT, 'include/constants/moves.h')):
    m = re.match(r'#define (MOVE_\w+)\s+(\d+)', l)
    if m and m.group(1) not in ('MOVE_NONE', 'MOVE_UNAVAILABLE', 'MOVES_COUNT') and int(m.group(2)) < min(len(order), COUNT):
        moves.append((int(m.group(2)), m.group(1)))

out = ['// GENERATED by tools/gen_move_sounds.py from data/battle_anim_scripts.s (gBattleAnims_Moves). POC-15.',
       '// Each move\'s sound effects as Emerald\'s battle animation plays them: frame after the move starts, sound, pan.',
       '#include "global.h"', '#include "constants/songs.h"', '#include "constants/battle_anim.h"', '#include "constants/moves.h"',
       '#include "pkbn/move_sounds.h"', '', 'const struct PkbnMoveSound gPkbnMoveSounds[MOVES_COUNT][PKBN_MOVE_SOUNDS] =', '{']
count = 0
for num, name in moves:
    ev = []
    walk(order[num], 0, ev)
    ev = sorted([e for e in ev if e[0] <= MAX_T], key=lambda e: e[0])[:MAX_EVENTS]
    if not ev:
        continue
    count += 1
    items = ', '.join('{ %d, %s, %s }' % (t, 'PKBN_SOUND_CRY' if se == 'CRY' else se, pan) for t, se, pan in ev)
    out.append('    [%s] = { %s },' % (name, items))
out.append('};')

# the status-condition and general animations (B_ANIM_STATUS_*, B_ANIM_*): poison ticks, stat changes, weather...
def extra(tname, cname, count):
    rows = []
    for idx, lab in enumerate(table(tname)[:count]):
        ev = []
        walk(lab, 0, ev)
        ev = sorted([e for e in ev if e[0] <= MAX_T], key=lambda e: e[0])[:MAX_EVENTS]
        items = ', '.join('{ %d, %s, %s }' % (t, 'PKBN_SOUND_CRY' if se == 'CRY' else se, pan) for t, se, pan in ev)
        rows.append('    /* %2d %-26s */ { %s },' % (idx, lab, items or '{ 0 }'))
    return ['', 'const struct PkbnMoveSound %s[%d][PKBN_MOVE_SOUNDS] =' % (cname, count), '{'] + rows + ['};']
out += extra('gBattleAnims_StatusConditions', 'gPkbnStatusSounds', 9)
out += extra('gBattleAnims_General', 'gPkbnGeneralSounds', 23)
open(os.path.join(ROOT, 'src/pkbn/move_sounds.c'), 'w').write('\n'.join(out) + '\n')
print('moves with sounds:', count, 'of', len(moves))
