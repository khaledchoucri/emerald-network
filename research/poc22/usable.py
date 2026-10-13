# POC-22b: who can use all three chips of a recipe (gPkbnCanLearn), and recipe search by species and type.
# usage: python3 research/poc22/usable.py <host tree>   (prints every Program Advance and the species that can do it)
import re,sys,os,itertools
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
H=(sys.argv[1] if len(sys.argv) > 1 else '.').rstrip('/') + '/'
from lanes_curated import MOVES as L, PROGRAM_ADVANCES as OLD
src=open(H+'src/pkbn/chip_data.c').read()
ids=dict((k,int(v)) for k,v in re.findall(r'#define MOVE_(\w+) (\d+)',open(H+'include/constants/moves.h').read()))
bm=open(H+'src/data/battle_moves.h').read()
MV={}
for m in re.finditer(r'\[MOVE_(\w+)\]\s*=\s*\{(.*?)\n    \}',bm,re.S):
    p=re.search(r'\.power = (\d+)',m.group(2)); t=re.search(r'\.type = TYPE_(\w+)',m.group(2))
    MV[m.group(1)]=(int(p.group(1)) if p else 0, t.group(1) if t else '?')
can={sp:[int(x) for x in b.split(',')] for sp,b in re.findall(r'\[SPECIES_(\w+)\] = \{([\d, ]+)\}',src)}
def cl(sp,m): i=ids[m]; return (can[sp][i//8]>>(i%8))&1
def lanes(m): return {t[0]:t[1:] for t in L.get(m,'').split() if t!='*'}
used=set(m for _,r,_ in OLD for m in r)
def search(sps, ptype, lane=None, maxshow=12):
    moves=[m for m in L if m in ids and all(cl(sp,m) for sp in sps)]
    out=[]
    for a,b,c in itertools.permutations(moves,3):
        if MV[c][1]!=ptype or MV[c][0]<=1: continue
        la,lb,lc=lanes(a),lanes(b),lanes(c)
        common=set(la)&set(lb)&set(lc)
        if lane: common&={lane}
        if not common: continue
        if not (MV[c][0]>=MV[a][0] and MV[c][0]>=MV[b][0]): continue
        # roles: a setup or status, c payoff in that lane
        for x in common:
            if lc[x]=='p' and la[x] in ('s','x') and MV[a][0]<=MV[b][0]:
                out.append((MV[c][0], x, a,b,c))
    out=sorted(set(out),reverse=True)
    return out[:maxshow]
if __name__=='__main__':
    for name, rec, _ in OLD:
        users=[sp for sp in can if all(cl(sp,m) for m in rec)]
        print(f"{name:16} {len(users):3} {', '.join(users[:8])}")
