# POC-22: which damaging moves the Pokemon met before the second Gym learn by level 19, by type, with their codes.
# usage: python3 research/poc22/early.py <host tree>
from movedata import *
MV=moves(); LS=learnsets(); EV=evolutions()
EARLY=['MAP_ROUTE101','MAP_ROUTE102','MAP_ROUTE103','MAP_ROUTE104','MAP_PETALBURG_WOODS','MAP_ROUTE116','MAP_RUSTURF_TUNNEL','MAP_GRANITE_CAVE_1F','MAP_ROUTE106','MAP_GRANITE_CAVE_B1F','MAP_GRANITE_CAVE_B2F']
W=wild(EARLY)
for st in ('TREECKO','TORCHIC','MUDKIP'): W[st]=5
CAP=19
def line(sp):
    out=[sp]
    for kind,lv,to in EV.get(sp,[]):
        if kind=='LEVEL' and int(lv)<=CAP: out+=line(to)
        elif kind in('LEVEL_SILCOON','LEVEL_CASCOON') and int(lv)<=CAP: out+=line(to)
    return out
avail={}
for sp in W:
    for s2 in set(line(sp)):
        for lv,m in LS.get(s2,[]):
            if lv<=CAP: avail.setdefault(m,set()).add(sp)
bytype={}
for m,sps in avail.items():
    d=MV[m]
    if d['power']>0: bytype.setdefault(d['type'],[]).append((d['power'],m,lanes(m)[0],sorted(sps)[:4]))
print('wild early:',sorted(W))
for t,l in sorted(bytype.items()):
    print(t); 
    for x in sorted(l): print('   ',x)
