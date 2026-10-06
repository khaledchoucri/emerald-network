#!/usr/bin/env python3
# POC-16e: moves for the type ladders and Omega legendaries (src/pkbn/challenge_table.inc): each species' strongest
# level-up moves up to its level - STAB first, different types, then its latest status move - from the game's own data.
# Usage: python3 tools/pick_challenge_moves.py SPECIES:LEVEL ...
import re,sys
import os
root=os.environ.get('PKBN_ROOT', '.')
learn=open(root+'/src/data/pokemon/level_up_learnsets.h').read()
moves=open(root+'/src/data/battle_moves.h').read()
species_info=open(root+'/src/data/pokemon/species_info.h').read()
ptrs=open(root+'/src/data/pokemon/level_up_learnset_pointers.h').read()
def moveinfo(m):
    i=moves.index('[%s]'%m); blk=moves[i:moves.index('},',i)]
    p=int(re.search(r'\.power = (\d+)',blk).group(1)); t=re.search(r'\.type = (TYPE_\w+)',blk).group(1)
    e=re.search(r'\.effect = (\w+)',blk).group(1); return p,t,e
def types(sp):
    i=species_info.index('[SPECIES_%s]'%sp); blk=species_info[i:i+3000]
    m=re.search(r'\.types = \{\s*(TYPE_\w+),\s*(TYPE_\w+)',blk); return m.group(1),m.group(2)
def learnset(sp):
    lab=re.search(r'\[SPECIES_%s\] = (s\w+LevelUpLearnset)'%sp,ptrs).group(1)
    i=learn.index(lab+'[]'); blk=learn[i:learn.index('LEVEL_UP_END',i)]
    return [(int(l),m) for l,m in re.findall(r'LEVEL_UP_MOVE\(\s*(\d+),\s*(MOVE_\w+)\)',blk)]
BAD={'EFFECT_EXPLOSION','EFFECT_OHKO','EFFECT_RECHARGE','EFFECT_FALSE_SWIPE','EFFECT_DREAM_EATER','EFFECT_FOCUS_PUNCH'}
def pick(sp,lv):
    t=types(sp); ls=[m for l,m in learnset(sp) if l<=lv]
    seen=[];[seen.append(m) for m in ls if m not in seen]
    dmg=[];st=[]
    for m in seen:
        p,ty,e=moveinfo(m)
        if p>1 and e not in BAD: dmg.append((p*(1.5 if ty in t else 1),ty,m))
        elif p==0: st.append(m)
    dmg.sort(reverse=True); out=[];used=set()
    for sc,ty,m in dmg:
        if ty in used and len(out)<2: continue
        out.append(m); used.add(ty)
        if len(out)==3: break
    for sc,ty,m in dmg:
        if len(out)>=3: break
        if m not in out: out.append(m)
    if st: out.append(st[-1])
    for sc,ty,m in dmg:
        if len(out)>=4: break
        if m not in out: out.append(m)
    return out[:4]
for a in sys.argv[1:]:
    sp,lv=a.split(':'); print(sp,lv,pick(sp,int(lv)))
