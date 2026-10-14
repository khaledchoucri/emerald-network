#!/usr/bin/env python3
"""Authorized geometry normalization of generated H1; run from any cwd."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent
W,H,C=96,34,8
def mask(inset,notch):
    m=np.zeros((H,W),dtype=bool)
    m[inset:H-inset,inset:W-inset]=True
    for y in (inset,H-inset-notch):
        for x in (inset,W-inset-notch):
            m[y:y+notch,x:x+notch]=False
    return m

# Preserve generated shape's stepped inset construction; normalize its variable
# stroke widths and soft fill into exact 1+3+1 native-pixel material bands.
outer=mask(0,1); rim=mask(1,0); inner=mask(4,3); face=mask(5,2)
idx=np.zeros((H,W),dtype=np.uint8)
idx[outer]=1; idx[rim]=2
yy,xx=np.indices((H,W))
idx[rim & ((yy==1)|(xx==1))]=3
idx[rim & ((yy>=H-4)|(xx>=W-4))]=4
idx[inner]=1; idx[face]=5
palettes={
 'player':['#000000','#0b0a14','#667b99','#9db0ca','#536787','#0d2347'],
 'foe':['#000000','#0b0a14','#b85778','#ec9bb7','#76304d','#2c1222'],
 'synchro1':['#000000','#0b0a14','#bd923d','#f8d87d','#795418','#302213'],
 'synchro2':['#000000','#0b0a14','#dcae4b','#fff0a5','#946b25','#302213'],
}
def render(pal):
    a=np.zeros((H,W,4),dtype=np.uint8)
    p=np.array([tuple(bytes.fromhex(c[1:])) for c in pal],dtype=np.uint8)
    a[:,:,:3]=p[idx]; a[:,:,3]=np.where(idx!=0,255,0)
    return Image.fromarray(a)
def pack(images,gap=8):
    w=sum(i.width for i in images)+gap*(len(images)-1);h=max(i.height for i in images)
    out=Image.new('RGBA',(w,h))
    x=0
    for im in images:out.paste(im,(x,0));x+=im.width+gap
    return out
def stretch(im,size):
    w,h=im.size;nw,nh=size;out=Image.new('RGBA',size)
    for sx,sy,dx,dy in [(0,0,0,0),(w-C,0,nw-C,0),(0,h-C,0,nh-C),(w-C,h-C,nw-C,nh-C)]:
        out.paste(im.crop((sx,sy,sx+C,sy+C)),(dx,dy))
    for box,sz,pos in [((C,0,w-C,C),(nw-2*C,C),(C,0)),((C,h-C,w-C,h),(nw-2*C,C),(C,nh-C)),((0,C,C,h-C),(C,nh-2*C),(0,C)),((w-C,C,w,h-C),(C,nh-2*C),(nw-C,C)),((C,C,w-C,h-C),(nw-2*C,nh-2*C),(C,C))]:
        out.paste(im.crop(box).resize(sz,Image.Resampling.NEAREST),pos)
    return out
def preview(name,im):
    im.save(ROOT/(name+'.png'))
    im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(ROOT/(name+'_review_4x.png'))
    im.resize((max(1,im.width//2),max(1,im.height//2)),Image.Resampling.NEAREST).save(ROOT/(name+'_review_half.png'))
ims={n:render(p) for n,p in palettes.items()}
checks={}
for n,im in ims.items():
    im.save(ROOT/(n+'.png'));a=np.asarray(im)
    edges={
      'top':bool(np.all(a[:C,C:W-C]==a[:C,W//2:W//2+1])),
      'bottom':bool(np.all(a[H-C:,C:W-C]==a[H-C:,W//2:W//2+1])),
      'left':bool(np.all(a[C:H-C,:C]==a[H//2:H//2+1,:C])),
      'right':bool(np.all(a[C:H-C,W-C:]==a[H//2:H//2+1,W-C:])),
      'center':bool(np.all(a[C:H-C,C:W-C]==a[H//2,W//2]))}
    assert all(edges.values())
    assert set(np.unique(a[:,:,3]))=={0,255}
    assert len(set(map(tuple,a[a[:,:,3]==255,:3])))<=16
    checks[n]={'size':list(im.size),'opaque_colors':len(set(map(tuple,a[a[:,:,3]==255,:3]))),'alpha_values':[0,255],'uniform_nineslice':edges}
preview('h1_colorways',pack(list(ims.values())))
preview('synchro',pack([ims['synchro1'],ims['synchro2']]))
stretch_images=[];stretchchecks={}
for name,size in [('player',(44,24)),('player',(200,34)),('foe',(60,34))]:
    im=stretch(ims[name],size);stretch_images.append(im)
    arr=np.asarray(im);base=np.asarray(ims[name])
    corners=[np.array_equal(arr[:C,:C],base[:C,:C]),np.array_equal(arr[:C,-C:],base[:C,-C:]),np.array_equal(arr[-C:,:C],base[-C:,:C]),np.array_equal(arr[-C:,-C:],base[-C:,-C:])]
    assert all(corners);stretchchecks[f'{name}_{size[0]}x{size[1]}']={'corners_identical':corners}
preview('h1_stretch_preview',pack(stretch_images))
for x in range(8,88):
    assert list(idx[:6,x])==[1,3,2,2,1,5]
assert np.array_equal(np.asarray(ims['synchro1'])[face],np.asarray(ims['synchro2'])[face])
checks['geometry']={'same_index_base_all_colorways':True,'middle_top_stroke_indexes':[1,3,2,2,1,5],'stroke_widths_outer_frame_inner':[1,3,1],'corner_slice':8,'stepped_corner_max_extent':7,'flat_player_fill':'#0d2347','synchro_fill_unchanged':True,'sheets_gap':8,'synchro_holds_game_frames':[8,8],'playback_tested':False}
checks['stretch']=stretchchecks
checks['source']={'size':list(Image.open(ROOT/'raw/h1_generated.png').size),'sha256':hashlib.sha256((ROOT/'raw/h1_generated.png').read_bytes()).hexdigest(),'geometry_normalized':True,'raw_native_proportions':False}
checks['font_tested']=False;checks['in_game_tested']=False
(ROOT/'validation.json').write_text(json.dumps(checks,indent=2)+'\n')
(ROOT/'processing.json').write_text(json.dumps({'script':'cleanup.py','dependencies':['Pillow','NumPy'],'source':'raw/h1_generated.png','operations':['generated shape interpreted as indexed stepped-corner template','normalize widths to 1px outer+3px frame+1px inner','flatten player fill to #0d2347','recolour shared indexes','uniform 9slice edges','8px sheet gaps','nearest4x and half previews'],'palettes':palettes},indent=2)+'\n')
print(json.dumps(checks['geometry']))
