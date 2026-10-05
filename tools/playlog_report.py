#!/usr/bin/env python3
"""Summarise pkbn_playlog.jsonl (written next to the save by every battle, POC-11) for balance tuning.
usage: python3 tools/playlog_report.py [path/to/pkbn_playlog.jsonl]"""
import json, sys, collections
path = sys.argv[1] if len(sys.argv) > 1 else 'pkbn_playlog.jsonl'
rows = [json.loads(l) for l in open(path) if l.strip()]
if not rows:
    sys.exit('no battles logged yet')
won = [r for r in rows if r['outcome'] == 1]
caught = [r for r in rows if r['outcome'] == 7]
hours = max(1, rows[-1]['time'] - rows[0]['time']) / 3600
print('%d battles (%d won, %d caught, %d other) over %.1f h of play' % (len(rows), len(won), len(caught),
      len(rows) - len(won) - len(caught), hours))
for clock in ('turns', 'seconds'):
    c = collections.Counter(r['busting'][clock] for r in won)
    print('Busting Level (%s clock): ' % clock + '  '.join('%s:%d' % ('S' if k == 11 else k, c[k]) for k in sorted(c)))
if won:
    for part in ('time', 'hits', 'steps', 'chain', 'counters', 'nofaint'):
        v = [r['busting'][part] for r in won]
        print('  %-8s avg %+.2f' % (part, sum(v) / len(v)))
    t = sorted(r['turns'] for r in won)
    print('turns per won battle: median %d, 90th pct %d' % (t[len(t) // 2], t[int(len(t) * 0.9)]))
chips = sum(1 for r in rows if r['reward'].startswith('GOT A CHIP') or 'CHIPS' in r['reward'])
print('chip rewards: %d (%.1f per hour, %.0f%% of battles)' % (chips, chips / hours, 100 * chips / len(rows)))
used = [len(r['chips']) for r in won]
if used:
    print('chips used per won battle: avg %.1f; folder ran out in %d battles' % (sum(used) / len(used),
          sum(1 for r in won if r['folderLeft'] == 0 and r['folder'] >= 15)))
print('pack now %d chips, candy %d, money %d' % (rows[-1]['pack'], rows[-1]['candy'], rows[-1]['money']))
