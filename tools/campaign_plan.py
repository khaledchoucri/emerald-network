#!/usr/bin/env python3
"""Campaign plan for src/pkbn/campaign.c (scripts/campaign.sh): the story's battles in Emerald's order, up to the
third badge. Trainers and where they stand come from the game's own map data (data/maps/*/map.json and scripts.inc),
trainer and map numbers from include/constants/opponents.h and map_groups.h.

    python3 tools/campaign_plan.py <host tree> TREECKO|TORCHIC|MUDKIP [wild multiplier] > plan.txt

Left out on purpose: swimmers (no Surf yet), Cycling Road triathletes (no bike yet), Route 103's east side, Mike in
Rusturf Tunnel (he's behind the rocks). "wild n" lines are a guess at a player who walks the grass: 1.0 = about 40
wild battles to Mauville, 0.4 = about 16."""
import json, re, sys
ROOT = sys.argv[1]           # host tree
STARTER = sys.argv[2]        # TREECKO / TORCHIC / MUDKIP
WILD = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0

opp = {m.group(1): int(m.group(2)) for m in re.finditer(r'#define (TRAINER_\w+)\s+(\d+)', open(f'{ROOT}/include/constants/opponents.h').read())}
mg = {}
for m in re.finditer(r'(MAP_\w+)\s*=\s*\((\d+) \| \((\d+) << 8\)\)', open(f'{ROOT}/include/constants/map_groups.h').read()):
    mg[m.group(1)] = (int(m.group(3)), int(m.group(2)))

def mapdata(name):
    return json.load(open(f'{ROOT}/data/maps/{name}/map.json'))

def script_trainer(name, label):
    """The trainer a trainer object's script fights (its first trainerbattle line)."""
    s = open(f'{ROOT}/data/maps/{name}/scripts.inc').read()
    i = s.find(label + '::')
    if i < 0:
        return None
    m = re.search(r'trainerbattle\w* (TRAINER_\w+)', s[i:i + 600])
    return m.group(1) if m else None

def adjacent(o):
    mt = o['movement_type']
    x, y = o['x'], o['y']
    if 'FACE_LEFT' in mt or mt.endswith('_LEFT'): return x - 1, y
    if 'FACE_RIGHT' in mt or mt.endswith('_RIGHT'): return x + 1, y
    if 'FACE_UP' in mt: return x, y - 1
    return x, y + 1

out = []
def mark(t): out.append(f'mark {t}')
def go(name, xy=None):
    d = mapdata(name)
    g, n = mg[d['id']]
    if xy is None:
        w = d['warp_events'][0] if d['warp_events'] else None
        xy = (w['x'], w['y']) if w else (10, 10)
    out.append(f'map {g} {n} {xy[0]} {xy[1]}   # {name}')
def wild(k):
    k = max(0, round(k * WILD))
    if k: out.append(f'wild {k}')
def trainers(name, keep=lambda o: True, order=lambda o: -o['y'], skip=()):
    d = mapdata(name)
    objs = [o for o in d['object_events'] if o.get('trainer_type', 'TRAINER_TYPE_NONE') != 'TRAINER_TYPE_NONE']
    seen = set()
    for o in sorted(objs, key=order):
        if 'SWIMMER' in o['graphics_id'] or not keep(o):
            continue
        t = script_trainer(name, o['script'])
        if t is None or t in seen or t in skip:
            continue
        seen.add(t)
        x, y = adjacent(o)
        out.append(f'trainer {opp[t]} {x} {y}   # {t}')
def trainer(t, comment=''):
    out.append(f'trainer {opp[t]}   # {t} {comment}')
def leader(name, t, key):
    d = mapdata(name)
    o = [o for o in d['object_events'] if o['script'].endswith('_' + t.split('_')[1].capitalize())][0]
    x, y = adjacent(o)
    out.append(f'leader {opp[t]} {x} {y} {key}   # {t}')

S = STARTER
mark('Route 101: Birch\'s rescue'); go('Route101', (10, 10)); out.append('scripted 286 2   # Poochyena Lv2 (Route101 scripts)'); wild(2)
mark('Route 103: rival'); go('Route103', (10, 10)); wild(2); trainer(f'TRAINER_MAY_ROUTE_103_{S}', 'rival')
mark('Oldale: Pokédex, Poké Balls'); out.append('heal'); out.append('buy 4 5')
mark('Route 102'); go('Route102', (20, 10)); wild(4); trainers('Route102')
mark('Petalburg'); out.append('heal')
mark('Route 104 south'); go('Route104', (12, 55)); wild(3); trainers('Route104', keep=lambda o: o['y'] >= 40)
mark('Petalburg Woods'); go('PetalburgWoods', (10, 30)); wild(4); trainers('PetalburgWoods'); trainer('TRAINER_GRUNT_PETALBURG_WOODS', 'Aqua')
mark('Route 104 north'); go('Route104', (20, 20)); wild(2); trainers('Route104', keep=lambda o: o['y'] < 40)
mark('Rustboro'); out.append('heal'); out.append('buy 4 5')
mark('Rustboro Gym'); go('RustboroCity_Gym'); trainers('RustboroCity_Gym', keep=lambda o: 'Roxanne' not in o['script']); leader('RustboroCity_Gym', 'TRAINER_ROXANNE_1', 'stone')
out.append('heal')
mark('Route 116'); go('Route116', (20, 10)); wild(4); trainers('Route116', order=lambda o: o['x'])
mark('Rusturf Tunnel'); go('RusturfTunnel'); wild(2); trainer('TRAINER_GRUNT_RUSTURF_TUNNEL', 'Aqua')
mark('Rustboro: rival'); go('RustboroCity', (20, 30)); out.append('heal'); trainer(f'TRAINER_MAY_RUSTBORO_{S}', 'rival')
mark('Route 106 (Dewford beach)'); go('Route106', (50, 15)); trainers('Route106')
mark('Granite Cave'); go('GraniteCave_1F'); wild(3); go('GraniteCave_B1F'); wild(2)
mark('Dewford'); out.append('heal'); out.append('buy 4 5')
mark('Dewford Gym'); go('DewfordTown_Gym'); trainers('DewfordTown_Gym', keep=lambda o: 'Brawly' not in o['script']); leader('DewfordTown_Gym', 'TRAINER_BRAWLY_1', 'knuckle')
out.append('heal')
mark('Route 109 (Slateport beach)'); go('Route109', (20, 20)); trainers('Route109', keep=lambda o: o['elevation'] != 1)
mark('Slateport: Oceanic Museum'); out.append('heal'); out.append('buy 4 5'); go('SlateportCity_OceanicMuseum_2F'); trainer('TRAINER_GRUNT_MUSEUM_1', 'Aqua'); trainer('TRAINER_GRUNT_MUSEUM_2', 'Aqua')
out.append('heal')
mark('Route 110'); go('Route110', (20, 70)); wild(5); trainers('Route110', keep=lambda o: o['elevation'] != 4); trainer(f'TRAINER_MAY_ROUTE_110_{S}', 'rival')
mark('Mauville: Wally'); out.append('heal'); out.append('buy 4 5'); go('MauvilleCity', (8, 8)); trainer('TRAINER_WALLY_MAUVILLE')
mark('Mauville Gym'); go('MauvilleCity_Gym'); trainers('MauvilleCity_Gym', keep=lambda o: 'Wattson' not in o['script']); leader('MauvilleCity_Gym', 'TRAINER_WATTSON_1', 'dynamo')
out.append('end')
print('\n'.join(out))
