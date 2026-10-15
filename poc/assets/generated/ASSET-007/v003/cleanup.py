#!/usr/bin/env python3
"""Native normalization of generated HUD parts; Pillow and NumPy required."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
GREYS=['#202020','#585858','#909090','#c8c8c8','#ffffff']
BLUE=['#000000','#0b0a14','#667b99','#9db0ca','#536787','#0d2347']
def rgba(c):return tuple(bytes.fromhex(c[1:]))+(255,)
def boxmask(w,h,x,y,notch):
    m=np.zeros((h,w),bool);m[y:h-y,x:w-x]=True
    for yy in [y,h-y-notch]:
        for xx in [x,w-x-notch]:m[yy:yy+notch,xx:xx+notch]=False
    return m
def frame(size,border,notch=1,palette=BLUE,fill=None):
    w,h=size;bx,by=border;idx=np.zeros((h,w),np.uint8)
    idx[boxmask(w,h,0,0,1)]=1
    idx[boxmask(w,h,1,1,0)]=2
    yy,xx=np.indices((h,w));idx[(idx==2)&((yy==1)|(xx==1))]=3
    idx[(idx==2)&((yy>=h-by)|(xx>=w-bx))]=4
    if bx>=3 and by>=3:
        idx[boxmask(w,h,bx-1,by-1,notch+1 if notch else 0)]=1
    elif by>=3:
        idx[by-1,bx:w-bx]=1;idx[h-by,bx:w-bx]=1
    idx[boxmask(w,h,bx,by,notch)]=5
    arr=np.zeros((h,w,4),np.uint8)
    for i,c in enumerate(palette):arr[idx==i]=rgba(c) if i else (0,0,0,0)
    if fill:arr[idx==5]=rgba(fill)
    return Image.fromarray(arr),idx
def strip(size,rows):
    arr=np.zeros((size[1],size[0],4),np.uint8)
    for y,c in enumerate(rows):arr[y]=rgba(c)
    return Image.fromarray(arr)
def pack(ims):
    out=Image.new('RGBA',(sum(i.width for i in ims)+8*(len(ims)-1),max(i.height for i in ims)))
    x=0
    for im in ims:out.paste(im,(x,0));x+=im.width+8
    return out
def preview(n,im):
    im.save(P/(n+'.png'))
    im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(P/(n+'_review_4x.png'))
    im.resize((max(1,im.width//2),max(1,im.height//2)),Image.Resampling.NEAREST).save(P/(n+'_review_half.png'))
def stretch(im,width,cap):
    w,h=im.size;o=Image.new('RGBA',(width,h))
    o.paste(im.crop((0,0,cap,h)),(0,0));o.paste(im.crop((w-cap,0,w,h)),(width-cap,0))
    o.paste(im.crop((cap,0,w-cap,h)).resize((width-2*cap,h),Image.Resampling.NEAREST),(cap,0))
    return o
tag,_=frame((40,18),(3,3),1,['#000000','#202020','#909090','#ffffff','#585858','#202020'])
trough,_=frame((88,8),(2,2),0)
hpfill=strip((84,4),['#c8c8c8','#ffffff','#909090','#585858'])
gauge,gidx=frame((224,16),(2,4),0)
gfill=strip((220,8),['#585858','#c8c8c8','#ffffff','#c8c8c8','#909090','#909090','#585858','#202020'])
line,_=frame((160,22),(3,3),1,fill='#14315b')
parts={'h2_tag':tag,'h3_trough':trough,'h3_fill':hpfill,'h4_frame':gauge,'h4_fill':gfill,'h5_line':line}
overlays=[]
# Clockwise light segment spans one quarter of the frame's perimeter each phase.
perimeter=[(x,1) for x in range(1,223)]+[(222,y) for y in range(2,15)]+[(x,14) for x in range(221,0,-1)]+[(1,y) for y in range(13,1,-1)]
for phase in range(4):
    a=np.zeros((16,224,4),np.uint8)
    for j in range(len(perimeter)//4):
        x,y=perimeter[(phase*(len(perimeter)//4)+j)%len(perimeter)]
        a[y,x]=rgba('#edf2fa')
    ov=Image.fromarray(a);overlays.append(ov);parts[f'h4_full_{phase+1}']=ov
for n,im in parts.items():preview(n,im)
preview('h4_full',pack(overlays))
composites=[]
for ov in overlays:
    c=gauge.copy();c.alpha_composite(ov);composites.append(c)
preview('h4_full_composited',pack(composites))
composites[0].resize((896,64),Image.Resampling.NEAREST).save(P/'h4_full_playback.gif',save_all=True,append_images=[i.resize((896,64),Image.Resampling.NEAREST) for i in composites[1:]],duration=67,loop=0,disposal=2)
stretch_checks={}
for n,im,cap,widths in [('h2_tag',tag,6,[20,100]),('h3_trough',trough,6,[40,200]),('h5_line',line,8,[40,300])]:
    previews=[]
    a=np.asarray(im)
    assert np.all(a[:,cap:im.width-cap]==a[:,im.width//2:im.width//2+1])
    for width in widths:
        s=stretch(im,width,cap);b=np.asarray(s)
        assert np.array_equal(a[:,:cap],b[:,:cap]) and np.array_equal(a[:,-cap:],b[:,-cap:])
        previews.append(s)
    preview(n+'_stretch',pack(previews))
    stretch_checks[n]={'horizontal_caps_px':cap,'widths':widths,'caps_identical':True,'middle_edges_and_fill_uniform':True}
contact=Image.new('RGBA',(224,18+8+8+8+16+8+22))
for im,y in [(tag,0),(trough,26),(gauge,42),(line,66)]:contact.paste(im,(0,y))
preview('hud_parts',contact)
validation={}
for n,im in parts.items():
    a=np.asarray(im);colors=set(map(tuple,a[a[:,:,3]==255,:3]));assert len(colors)<=16
    assert set(np.unique(a[:,:,3])).issubset({0,255})
    if n in ['h2_tag','h3_fill','h4_fill']:assert colors.issubset({tuple(bytes.fromhex(c[1:])) for c in GREYS})
    validation[n]={'size':list(im.size),'opaque_colors':len(colors),'alpha_values':np.unique(a[:,:,3]).tolist()}
    if n.startswith('h4_full_'):assert not np.any(a[2:14,2:222,3])
assert np.unique(np.asarray(line)[3:19,8:152],axis=0).shape[0]==1
for f in P.glob('*.png'):
    with Image.open(f) as im:im.load()
a=np.asarray(Image.open(P/'h4_full.png'))
for i in range(3):assert not np.any(a[:,i*232+224:i*232+232,3])
validation.update({'stretch_checks':stretch_checks,'text_clearance':{'h2_px':12,'h5_px':16,'actual_game_font_tested':False},'h3_slice_adaptation':'6px horizontal cap, full8px height split4+4; literal6x6 top/bottom corners overlap and are unsupported','h5_frame_adaptation':'1outer+1litframe+1inner, not H1 1+3+1, to leave16px text room','h4_frame_fill_alignment':{'frame':[224,16],'fill':[220,8],'fill_offset':[2,4]},'h4_overlay':{'frames':4,'gap':8,'sheet':[920,16],'timing_game_frames':[4,4,4,4],'loop':True,'center_fully_transparent':True,'standalone_gif_preview_ms':67,'in_game_playback_tested':False},'raw_source':{'sha256':hashlib.sha256((P/'raw/hud_parts_generated.png').read_bytes()).hexdigest(),'size':list(Image.open(P/'raw/hud_parts_generated.png').size),'not_native_multiple':True},'in_game_tested':False})
(P/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
(P/'processing.json').write_text(json.dumps({'source':'raw/hud_parts_generated.png','operations':['interpret generated frame family as indexed stepped masks','normalize dimensions and strokes for text-safe thin parts','remove soft background/fill variation by explicit native reconstruction','quantize to explicit palettes','construct uniform horizontal stretch edges','construct four clockwise hard rim-light phases','pack8px gaps;nearest4x/half previews'],'gray_palette':GREYS,'blue_palette':BLUE,'h5_fill':'#14315b','dependencies':['Pillow','NumPy'],'script':'cleanup.py'},indent=2)+'\n')
print('HUD H2-H5 generated and assertions passed.')
