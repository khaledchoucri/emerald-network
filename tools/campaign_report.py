#!/usr/bin/env python3
"""Summary of campaign runs (scripts/campaign.sh): per run, battles, losses and where, the lead's level at each Gym
Leader, chip vs buster damage, chips used, dead hands, counter hits, phase strikes, tags, Program Advances, packs,
places, the share of * chips in the folder. Run from the host build folder:

    python3 tools/campaign_report.py OUT [run ...]       (OUT as given to campaign.sh; writes OUT/summary.json)
"""
import json, re, sys, os, glob, collections

OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/pkbn-campaign'
SPECIES = {}
for m in re.finditer(r'#define SPECIES_(\w+)\s+(\d+)', open('include/constants/species.h').read()):
    SPECIES.setdefault(int(m.group(2)), m.group(1))
TRAINERS = {int(m.group(2)): m.group(1) for m in re.finditer(r'#define TRAINER_(\w+)\s+(\d+)', open('include/constants/opponents.h').read())}

RE_CAMP = re.compile(r'\[pkbn-camp\] battle (\d+) seg="([^"]*)" (\w+) (-?\d+) outcome=(\d+) frames=(\d+) money=(\d+) buster=(\d+)/(\d+) party=(\S*)')
RE_HIT = re.compile(r"\[pkbn f\d+\] (.+?)'s (\w+) \(move (\d+)\) hit (.+?): (\d+) dmg")
RE_USES = re.compile(r'\[pkbn f\d+\] (\S.*?) uses (.+?) \((\w+)\)')
RE_NAVI = re.compile(r'\[pkbn f\d+\] navicust (\S+):')
RE_START = re.compile(r'\[pkbn\] (trainer|wild) battle: species (\d+) Lv (\d+)')
RE_CHIP = re.compile(r'chip\s+\d+: (.+?)\s{2,}(\S)\s+MB')

def party(s):
    out = []
    for p in s.split(','):
        if not p: continue
        sp, lv, hp = p.split(':')
        out.append((int(sp), int(lv), hp))
    return out

def analyze(run):
    d = os.path.join(OUT, run)
    lines = open(os.path.join(d, 'log.txt'), errors='replace').read().splitlines()
    players = set()
    battles, cur = [], None
    def new():
        return dict(chipDmg=0, chipHits=0, foeDmg=0, uses=collections.Counter(), kinds=collections.Counter(), dead=0,
                    counters=0, synchro=0, phase=0, tags=0, pas=0, place=set(), rocksHit=0, snared=0, tide=0,
                    redraw=0, pack=0, start=None, folder=None, folderStar=0, folderChips=[], switches=0)
    cur = new()
    end = None
    marks = []
    # player names: the species in the party lines of the campaign log (all of them seen so far and the next one)
    chunks, buf = [], []
    for ln in lines:
        buf.append(ln)
        if RE_CAMP.search(ln):
            chunks.append(buf); buf = []
    chunks.append(buf)
    seq = []
    for ch in chunks:
        names = set()
        for ln in ch:
            m = RE_CAMP.search(ln)
            if m:
                names = {SPECIES.get(sp, '?').replace('_', ' ') for sp, lv, hp in party(m.group(10))}
        seq.append(names)
    lines2 = []
    for i, ch in enumerate(chunks):
        lines2.append(('__names__', seq[i] | (seq[i - 1] if i else set())))
        lines2.extend(ch)
    for ln in lines2:
        if isinstance(ln, tuple):
            players = ln[1]
            continue
        if ln.startswith('[pkbn-camp] ==='):
            marks.append(ln)
        m = RE_START.search(ln)
        if m:
            cur['start'] = (m.group(1), int(m.group(2)), int(m.group(3)))
        if 'folder:' in ln and 'chips (max' in ln:
            cur['folder'] = int(re.search(r'folder: (\d+) chips', ln).group(1))
            cur['folderChips'] = []
        m = RE_CHIP.search(ln)
        if m and cur['folder'] is not None:
            cur['folderChips'].append((m.group(1).strip(), m.group(2)))
        m = RE_HIT.search(ln)
        if m:
            a, kind, mv, t, dmg = m.group(1), m.group(2), int(m.group(3)), m.group(4), int(m.group(5))
            if a in players and t not in players:
                cur['chipDmg'] += dmg; cur['chipHits'] += 1
            elif t in players and a not in players:
                cur['foeDmg'] += dmg
        m = RE_USES.search(ln)
        if m and m.group(1) in players:
            cur['uses'][m.group(2)] += 1
            cur['kinds'][m.group(3)] += 1
        if "can't use: back under the pile" in ln: cur['dead'] += 1
        if 'counter hit on' in ln and not any(p in ln.split('counter hit on ')[1] for p in players): cur['counters'] += 1
        if 'FULL SYNCHRO' in ln: cur['synchro'] += 1
        if 'phase strike:' in ln: cur['phase'] += 1
        if '] TAG: ' in ln: cur['tags'] += 1
        if 'Program Advance formed' in ln: cur['pas'] += 1
        if '] place: ' in ln: cur['place'] |= set(ln.split('] place: ')[1].split())
        if 'tide: the back columns' in ln: cur['tide'] += 1
        if 'rock lands' in ln and 'a hit' in ln: cur['rocksHit'] += 1
        if 'is snared' in ln: cur['snared'] += 1
        if 'redraw:' in ln: cur['redraw'] += 1
        if 'wild pack:' in ln: cur['pack'] = int(re.search(r'wild pack: (\d+)', ln).group(1))
        if 'switched in' in ln: cur['switches'] += 1
        m = RE_CAMP.search(ln)
        if m:
            b = cur
            b.update(n=int(m.group(1)), seg=m.group(2), kind=m.group(3), id=int(m.group(4)), outcome=int(m.group(5)),
                     frames=int(m.group(6)), money=int(m.group(7)), busterHits=int(m.group(8)), busterDmg=int(m.group(9)),
                     party=party(m.group(10)))
            b['place'] = sorted(b['place'])
            battles.append(b)
            cur = new()
        if '[pkbn-camp] END' in ln:
            end = ln
    pl = [json.loads(l) for l in open(os.path.join(d, 'playlog.jsonl'))] if os.path.exists(os.path.join(d, 'playlog.jsonl')) else []
    return dict(run=run, battles=battles, end=end, marks=marks, playlog=pl, players=sorted(players))

def summary(r):
    B = r['battles']
    tot = lambda k: sum(b[k] for b in B)
    chipD, busD = tot('chipDmg'), tot('busterDmg')
    leaders = [(TRAINERS.get(b['id'], b['id']), b['outcome'], b['party'][0][1] if b['party'] else 0, b['frames']) for b in B if b['kind'] == 'leader']
    rivals = [(TRAINERS.get(b['id']), b['outcome'], b['party'][0][1]) for b in B if b['kind'] == 'trainer' and ('MAY_' in TRAINERS.get(b['id'], '') or 'WALLY' in TRAINERS.get(b['id'], ''))]
    losses = [(b['seg'], b['kind'], TRAINERS.get(b['id'], b['id'])) for b in B if b['outcome'] in (2, 3)]
    star = [sum(1 for c in b['folderChips'] if c[1] == '*') / max(1, len(b['folderChips'])) for b in B if b['folderChips']]
    usesTotal = collections.Counter()
    for b in B: usesTotal.update(b['uses'])
    frames = tot('frames')
    last = B[-1]['party'] if B else []
    return dict(
        run=r['run'], battles=len(B), wins=sum(b['outcome'] in (1, 7) for b in B), losses=len(losses), lossList=losses,
        end=r['end'], hours=round(frames / 60 / 3600, 2), leaders=leaders, rivals=rivals,
        chipShare=round(chipD / max(1, chipD + busD), 3), chipDmg=chipD, busterDmg=busD, busterHits=tot('busterHits'),
        chipsUsed=sum(usesTotal.values()), chipsPerBattle=round(sum(usesTotal.values()) / max(1, len(B)), 2),
        topChips=usesTotal.most_common(8), deadHands=tot('dead'), counters=tot('counters'), synchro=tot('synchro'),
        phase=tot('phase'), tags=tot('tags'), pas=tot('pas'), redraws=tot('redraw'), switches=tot('switches'),
        packs=sum(1 for b in B if b['pack'] > 1), wild=sum(1 for b in B if b['kind'] in ('wild', 'grind', 'scripted')),
        tide=tot('tide'), rocksHit=tot('rocksHit'), snared=tot('snared'),
        places=collections.Counter(p for b in B for p in b['place']),
        starShareFirst=round(star[0], 2) if star else None, starShareLast=round(star[-1], 2) if star else None,
        folderLast=B[-1]['folder'] if B else None,
        party=[(SPECIES.get(sp, sp), lv) for sp, lv, hp in last],
        foeDmgPerBattle=round(tot('foeDmg') / max(1, len(B)), 1),
        secPerBattle=round(frames / 60 / max(1, len(B)), 1),
    )

if __name__ == '__main__':
    runs = sys.argv[2:] or sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(OUT, '*', 'log.txt')))
    out = []
    for run in runs:
        try:
            r = analyze(run)
        except FileNotFoundError:
            continue
        s = summary(r)
        out.append(s)
        
    json.dump(out, open(os.path.join(OUT, 'summary.json'), 'w'), indent=1, default=list)
    for s in out:
        print(f"{s['run']:20} b={s['battles']:3} W={s['wins']:3} L={s['losses']} h={s['hours']} chip%={s['chipShare']} chips/b={s['chipsPerBattle']} dead={s['deadHands']} ctr={s['counters']} ph={s['phase']} tag={s['tags']} pa={s['pas']} packs={s['packs']}/{s['wild']} star={s['starShareFirst']}->{s['starShareLast']}")
        print('   leaders', s['leaders'], ' party', s['party'])
