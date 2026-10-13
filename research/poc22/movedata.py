# Parse Emerald data from the host tree (/home/claude/pc) for PA design: moves, learnsets, evolutions, wild tables, lanes.
import re, json, sys
H=sys.argv[1] if len(sys.argv) > 1 else '.'
H=H.rstrip('/') + '/'
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', 'tools'))
from lanes_curated import MOVES as LANEMOVES
def moves():
    s=open(H+'src/data/battle_moves.h').read()
    out={}
    for m in re.finditer(r'\[MOVE_(\w+)\]\s*=\s*\{(.*?)\n    \}',s,re.S):
        body=m.group(2)
        p=re.search(r'\.power = (\d+)',body); t=re.search(r'\.type = TYPE_(\w+)',body); e=re.search(r'\.effect = (\w+)',body)
        out[m.group(1)]=dict(power=int(p.group(1)) if p else 0,type=t.group(1) if t else '?',effect=e.group(1) if e else '')
    return out
def learnsets():
    s=open(H+'src/data/pokemon/level_up_learnsets.h').read()
    ptr=open(H+'src/data/pokemon/level_up_learnset_pointers.h').read()
    sets={}
    for m in re.finditer(r'static const u16 (s\w+LevelUpLearnset)\[\] = \{(.*?)\};',s,re.S):
        sets[m.group(1)]=[(int(a),b) for a,b in re.findall(r'LEVEL_UP_MOVE\(\s*(\d+), MOVE_(\w+)\)',m.group(2))]
    out={}
    for sp,name in re.findall(r'\[SPECIES_(\w+)\] = (s\w+LevelUpLearnset)',ptr):
        out[sp]=sets.get(name,[])
    return out
def evolutions():
    s=open(H+'src/data/pokemon/evolution.h').read()
    out={}
    for sp,body in re.findall(r'\[SPECIES_(\w+)\]\s*=\s*\{(.*?)\},\n',s):
        out[sp]=re.findall(r'\{EVO_(\w+), (\w+), SPECIES_(\w+)\}',body)
    return out
def wild(maps):
    d=json.load(open(H+'src/data/wild_encounters.json'))
    out={}
    for e in d['wild_encounter_groups'][0]['encounters']:
        if e['map'] in maps:
            for k in ('land_mons','water_mons','rock_smash_mons','fishing_mons'):
                if k in e:
                    for mm in e[k]['mons']:
                        sp=mm['species'].replace('SPECIES_',''); out.setdefault(sp,0); out[sp]=max(out[sp],mm['max_level'])
    return out
def lanes(move):
    t=LANEMOVES.get(move,'')
    return [tok[0] for tok in t.split() if tok!='*'], ('*' in t.split())
