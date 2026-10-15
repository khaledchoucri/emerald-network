#!/usr/bin/env python3
"""Campaign plan for src/pkbn/campaign.c (scripts/campaign.sh): the story's battles in Emerald's order, up to the
eighth badge (or fewer). Trainers and where they stand come from the game's own map data (data/maps/*/map.json and
scripts.inc), trainer and map numbers from include/constants/opponents.h and map_groups.h.

    python3 tools/campaign_plan.py <host tree> TREECKO|TORCHIC|MUDKIP [wild multiplier] [last badge, 1-8] > plan.txt

The order is Emerald's story: Rustboro, Dewford, Mauville; Mt. Chimney and Lavaridge; Petalburg; Route 119 and Fortree;
Lilycove, Mt. Pyre, the Magma and Aqua Hideouts; Mossdeep and the Space Center; Seafloor Cavern; Sootopolis.

Left out on purpose:
  - before Surf (Norman): swimmers; before the bike: Cycling Road triathletes; Route 103's east side;
  - trainers behind something the player gets later (Rusturf's Mike), rematches;
  - the Space Center's multi battle beside Steven (it needs a partner), Wally at Victory Road (after the 8th badge).
"wild n" lines are a guess at a player who walks the grass: 1.0 = about 40 wild battles to Mauville."""
import json, re, sys
ROOT = sys.argv[1]           # host tree
STARTER = sys.argv[2]        # TREECKO / TORCHIC / MUDKIP
WILD = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
LAST = int(sys.argv[4]) if len(sys.argv) > 4 else 8

opp = {m.group(1): int(m.group(2)) for m in re.finditer(r'#define (TRAINER_\w+)\s+(\d+)', open(f'{ROOT}/include/constants/opponents.h').read())}
mg = {}
for m in re.finditer(r'(MAP_\w+)\s*=\s*\((\d+) \| \((\d+) << 8\)\)', open(f'{ROOT}/include/constants/map_groups.h').read()):
    mg[m.group(1)] = (int(m.group(3)), int(m.group(2)))

def mapdata(name):
    return json.load(open(f'{ROOT}/data/maps/{name}/map.json'))

RE_TB = re.compile(r'trainerbattle\w*\s+(?:TRAINER_BATTLE_\w+,\s*)?(TRAINER_\w+)')
def script_trainer(name, label):
    """The trainer a trainer object's script fights (its first trainerbattle line)."""
    s = open(f'{ROOT}/data/maps/{name}/scripts.inc').read()
    i = s.find(label + '::')
    if i < 0:
        return None
    m = RE_TB.search(s[i:i + 700])
    return m.group(1) if m else None

def adjacent(o):
    mt = o['movement_type']
    x, y = o['x'], o['y']
    if 'FACE_LEFT' in mt or mt.endswith('_LEFT'): return x - 1, y
    if 'FACE_RIGHT' in mt or mt.endswith('_RIGHT'): return x + 1, y
    if 'FACE_UP' in mt: return x, y - 1
    return x, y + 1

out = []
done = set()
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
def heal(): out.append('heal')
def buy(item, n): out.append(f'buy {item} {n}')
def trainers(name, keep=lambda o: True, order=lambda o: -o['y'], swim=False):
    d = mapdata(name)
    objs = [o for o in d['object_events'] if o.get('trainer_type', 'TRAINER_TYPE_NONE') != 'TRAINER_TYPE_NONE']
    for o in sorted(objs, key=order):
        if not swim and 'SWIMM' in o['graphics_id']:
            continue
        if not keep(o):
            continue
        t = script_trainer(name, o['script'])
        if t is None or t in done or t not in opp:
            continue
        done.add(t)
        x, y = adjacent(o)
        out.append(f'trainer {opp[t]} {x} {y}   # {t}')
def trainer(t, comment=''):
    if t in done: return
    done.add(t)
    out.append(f'trainer {opp[t]}   # {t} {comment}')
def leader(name, t, key, xy=None):
    if xy is None:
        d = mapdata(name)
        o = [o for o in d['object_events'] if script_trainer(name, o['script']) == t][0]
        xy = adjacent(o)
    done.add(t)
    out.append(f'leader {opp[t]} {xy[0]} {xy[1]} {key}   # {t}')
def notleader(o): return not any(k in o['script'] for k in ('Roxanne', 'Brawly', 'Wattson', 'Flannery', 'Norman', 'Winona', 'TateAndLiza', 'Juan'))

S = STARTER
POKE, GREAT, ULTRA = 4, 3, 2

# ---- Badge 1: Rustboro ----
mark("Route 101: Birch's rescue"); go('Route101', (10, 10)); out.append('scripted 286 2   # Poochyena Lv2 (Route101 scripts)'); wild(2)
mark('Route 103: rival'); go('Route103', (10, 10)); wild(2); trainer(f'TRAINER_MAY_ROUTE_103_{S}', 'rival')
mark('Oldale: Pokédex, Poké Balls'); heal(); buy(POKE, 5)
mark('Route 102'); go('Route102', (20, 10)); wild(4); trainers('Route102')
mark('Petalburg'); heal()
mark('Route 104 south'); go('Route104', (12, 55)); wild(3); trainers('Route104', keep=lambda o: o['y'] >= 40)
mark('Petalburg Woods'); go('PetalburgWoods', (10, 30)); wild(4); trainers('PetalburgWoods'); trainer('TRAINER_GRUNT_PETALBURG_WOODS', 'Aqua')
mark('Route 104 north'); go('Route104', (20, 20)); wild(2); trainers('Route104', keep=lambda o: o['y'] < 40)
mark('Rustboro'); heal(); buy(POKE, 5)
mark('Rustboro Gym'); go('RustboroCity_Gym'); trainers('RustboroCity_Gym', keep=notleader); leader('RustboroCity_Gym', 'TRAINER_ROXANNE_1', 'stone')
heal()
if LAST >= 2:
    mark('Route 116'); go('Route116', (20, 10)); wild(4); trainers('Route116', order=lambda o: o['x'])
    mark('Rusturf Tunnel'); go('RusturfTunnel'); wild(2); trainer('TRAINER_GRUNT_RUSTURF_TUNNEL', 'Aqua')
    mark('Rustboro: rival'); go('RustboroCity', (20, 30)); heal(); trainer(f'TRAINER_MAY_RUSTBORO_{S}', 'rival')
    mark('Route 106 (Dewford beach)'); go('Route106', (50, 15)); trainers('Route106')
    mark('Granite Cave'); go('GraniteCave_1F'); wild(3); go('GraniteCave_B1F'); wild(2)
    mark('Dewford'); heal(); buy(POKE, 5)
    mark('Dewford Gym'); go('DewfordTown_Gym'); trainers('DewfordTown_Gym', keep=notleader); leader('DewfordTown_Gym', 'TRAINER_BRAWLY_1', 'knuckle')
    heal()
if LAST >= 3:
    mark('Route 109 (Slateport beach)'); go('Route109', (20, 20)); trainers('Route109')
    mark('Slateport: Oceanic Museum'); heal(); buy(POKE, 5); go('SlateportCity_OceanicMuseum_2F'); trainer('TRAINER_GRUNT_MUSEUM_1', 'Aqua'); trainer('TRAINER_GRUNT_MUSEUM_2', 'Aqua')
    heal()
    mark('Route 110'); go('Route110', (20, 70)); wild(5); trainers('Route110', keep=lambda o: o['elevation'] != 4); trainer(f'TRAINER_MAY_ROUTE_110_{S}', 'rival')
    mark('Mauville: Wally'); heal(); buy(POKE, 5); go('MauvilleCity', (8, 8)); trainer('TRAINER_WALLY_MAUVILLE')
    mark('Mauville Gym'); go('MauvilleCity_Gym'); trainers('MauvilleCity_Gym', keep=notleader); leader('MauvilleCity_Gym', 'TRAINER_WATTSON_1', 'dynamo')
    heal()
if LAST >= 4:
    mark('Route 117'); go('Route117', (20, 8)); wild(3); trainers('Route117', order=lambda o: o['x'])
    mark('Route 111 south'); go('Route111', (20, 95)); wild(2); trainers('Route111', keep=lambda o: o['y'] >= 90)
    mark('Route 112'); go('Route112', (20, 30)); wild(3); trainers('Route112')
    mark('Fiery Path'); go('FieryPath'); wild(2)
    mark('Route 113'); go('Route113', (20, 8)); wild(3); trainers('Route113', order=lambda o: o['x'])
    mark('Fallarbor'); heal(); buy(GREAT, 5)
    mark('Route 114'); go('Route114', (20, 10)); wild(3); trainers('Route114')
    mark('Meteor Falls'); go('MeteorFalls_1F_1R'); wild(2)
    mark('Mt. Chimney'); go('MtChimney'); trainers('MtChimney', keep=lambda o: 'MAGMA' not in o['graphics_id'])
    trainer('TRAINER_GRUNT_MT_CHIMNEY_1', 'Magma'); trainer('TRAINER_GRUNT_MT_CHIMNEY_2', 'Magma'); trainer('TRAINER_TABITHA_MT_CHIMNEY', 'Magma admin'); trainer('TRAINER_MAXIE_MT_CHIMNEY', 'Magma leader')
    heal()
    mark('Jagged Pass'); go('JaggedPass'); wild(2); trainers('JaggedPass')
    mark('Lavaridge'); heal(); buy(GREAT, 5)
    mark('Lavaridge Gym'); go('LavaridgeTown_Gym_1F'); trainers('LavaridgeTown_Gym_1F', keep=notleader); go('LavaridgeTown_Gym_B1F'); trainers('LavaridgeTown_Gym_B1F')
    go('LavaridgeTown_Gym_1F'); leader('LavaridgeTown_Gym_1F', 'TRAINER_FLANNERY_1', 'heat')
    heal()
if LAST >= 5:
    mark('Route 111 desert'); go('Route111', (20, 60)); wild(3); trainers('Route111')
    mark('Petalburg Gym'); heal(); go('PetalburgCity_Gym', (4, 100)); trainers('PetalburgCity_Gym', keep=notleader); leader('PetalburgCity_Gym', 'TRAINER_NORMAN_1', 'balance', (4, 3))
    heal()
if LAST >= 6:
    mark('Route 118'); go('Route118', (20, 10)); wild(3); trainers('Route118', swim=True)
    mark('Route 119'); go('Route119', (20, 100)); wild(4); trainers('Route119', swim=True); trainer(f'TRAINER_MAY_ROUTE_119_{S}', 'rival')
    mark('Weather Institute'); go('Route119_WeatherInstitute_1F'); trainer('TRAINER_GRUNT_WEATHER_INST_1', 'Aqua'); trainer('TRAINER_GRUNT_WEATHER_INST_4', 'Aqua')
    go('Route119_WeatherInstitute_2F'); trainer('TRAINER_GRUNT_WEATHER_INST_2', 'Aqua'); trainer('TRAINER_GRUNT_WEATHER_INST_3', 'Aqua'); trainer('TRAINER_GRUNT_WEATHER_INST_5', 'Aqua'); trainer('TRAINER_SHELLY_WEATHER_INSTITUTE', 'Aqua admin')
    mark('Fortree'); heal(); buy(GREAT, 5)
    mark('Route 120'); go('Route120', (20, 10)); wild(3); trainers('Route120', swim=True)
    mark('Fortree Gym'); heal(); go('FortreeCity_Gym'); trainers('FortreeCity_Gym', keep=notleader); leader('FortreeCity_Gym', 'TRAINER_WINONA_1', 'feather')
    heal()
if LAST >= 7:
    mark('Route 121'); go('Route121', (20, 8)); wild(3); trainers('Route121', swim=True)
    mark('Lilycove: rival'); go('LilycoveCity', (30, 20)); heal(); buy(GREAT, 5); trainer(f'TRAINER_MAY_LILYCOVE_{S}', 'rival')
    mark('Mt. Pyre'); go('MtPyre_1F'); wild(2)
    for f in ('2F', '3F', '4F', '5F', '6F'):
        go(f'MtPyre_{f}'); trainers(f'MtPyre_{f}')
    go('MtPyre_Exterior'); wild(2); go('MtPyre_Summit')
    for k in (1, 2, 3, 4): trainer(f'TRAINER_GRUNT_MT_PYRE_{k}', 'Aqua')
    heal()
    mark('Magma Hideout'); go('MagmaHideout_1F'); wild(2)
    for t in ('1', '2', '3', '4', '5', '14', '11', '12', '13'): trainer(f'TRAINER_GRUNT_MAGMA_HIDEOUT_{t}', 'Magma')
    trainer('TRAINER_TABITHA_MAGMA_HIDEOUT', 'Magma admin'); trainer('TRAINER_MAXIE_MAGMA_HIDEOUT', 'Magma leader')
    heal()
    mark('Aqua Hideout'); go('AquaHideout_B1F'); wild(2)
    for t in (2, 3, 5, 7, 4, 6, 8): trainer(f'TRAINER_GRUNT_AQUA_HIDEOUT_{t}', 'Aqua')
    trainer('TRAINER_MATT', 'Aqua admin')
    heal()
    mark('Route 124'); go('Route124', (20, 10)); trainers('Route124', swim=True)
    mark('Mossdeep'); heal(); buy(ULTRA, 5)
    mark('Mossdeep Gym'); go('MossdeepCity_Gym'); trainers('MossdeepCity_Gym', keep=notleader); leader('MossdeepCity_Gym', 'TRAINER_TATE_AND_LIZA_1', 'mind', (23, 8))
    heal()
if LAST >= 8:
    mark('Space Center'); go('MossdeepCity_SpaceCenter_1F')
    for t in range(1, 8): trainer(f'TRAINER_GRUNT_SPACE_CENTER_{t}', 'Magma')
    heal()
    mark('Route 125-128'); go('Route125', (20, 10)); trainers('Route125', swim=True); go('Route127', (20, 10)); trainers('Route127', swim=True)
    go('Route128', (20, 10)); trainers('Route128', swim=True)
    mark('Seafloor Cavern'); go('SeafloorCavern_Room1'); wild(2)
    for t in (1, 2, 3, 4, 5): trainer(f'TRAINER_GRUNT_SEAFLOOR_CAVERN_{t}', 'Aqua')
    trainer('TRAINER_SHELLY_SEAFLOOR_CAVERN', 'Aqua admin'); trainer('TRAINER_ARCHIE', 'Aqua leader')
    heal()
    mark('Route 126'); go('Route126', (20, 10)); trainers('Route126', swim=True)
    mark('Sootopolis Gym'); heal(); buy(ULTRA, 5); go('SootopolisCity_Gym_B1F'); trainers('SootopolisCity_Gym_B1F')
    go('SootopolisCity_Gym_1F'); leader('SootopolisCity_Gym_1F', 'TRAINER_JUAN_1', 'rain')
    heal()
out.append('end')
print('\n'.join(out))
