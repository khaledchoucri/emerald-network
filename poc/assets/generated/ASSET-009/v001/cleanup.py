from pathlib import Path
from PIL import Image
import numpy as np
import json, hashlib
D=Path(__file__).resolve().parent
H=D.parents[1]/'ASSET-007/v002/player.png'
h=Image.open(H).convert('RGBA')
a=np.array(h)
# Reflow the already-normalized sibling HUD geometry; preserve its 8x8 corner slices.
c=Image.new('RGBA',(264,352))
for sx,sy,sw,sh,dx,dy,dw,dh in [(0,0,8,8,0,0,8,8),(88,0,8,8,256,0,8,8),(0,26,8,8,0,344,8,8),(88,26,8,8,256,344,8,8),(8,0,80,8,8,0,248,8),(8,26,80,8,8,344,248,8),(0,8,8,18,0,8,8,336),(88,8,8,18,256,8,8,336),(8,8,80,18,8,8,248,336)]:
 c.paste(h.crop((sx,sy,sx+sw,sy+sh)).resize((dw,dh),Image.Resampling.NEAREST),(dx,dy))
a=np.array(c)
fill=(a[:,:,:3]==(13,35,71)).all(axis=2)
a[fill,:3]=(7,24,51)
# Quiet plain text bands: no raised boxes, labels, or ornament.
for y0,y1 in [(5,26),(325,347)]:
 region=fill[y0:y1]; a[y0:y1,:,:3][region]=(11,37,80)
# Bright inner right rim, still bounded by the dark outer outline.
a[8:344,262,:3]=(157,176,202)
a[:,:,3]=255
c=Image.fromarray(a,'RGBA'); c.save(D/'window_body.png')
# Four-pixel bezel keeps the contract's ENTIRE 244x112 window transparent.
b=np.zeros((120,252,4),dtype=np.uint8)
outline=(11,10,20,255); light=(157,176,202,255); base=(102,123,153,255); shade=(83,103,135,255)
for j in range(4):
 color=outline if j in (0,3) else base
 b[j:120-j,j:252-j]=color
 if j in (1,2):
  b[j,j:252-j]=light; b[j:120-j,j]=light
  b[119-j,j:252-j]=shade; b[j:120-j,251-j]=shade
b[4:116,4:248]=0
# Square outer corner notches: internal transparent window remains a true rectangle.
for x,y in [(0,0),(250,0),(0,118),(250,118)]:
 b[y:y+2,x:x+2]=0
for x,y in [(2,0),(248,0),(0,2),(250,2),(2,119),(248,119),(0,116),(251,116)]:
 b[y:y+1,x:x+2]=outline
bezel=Image.fromarray(b,'RGBA'); bezel.save(D/'art_frame.png')
preview=c.copy(); preview.alpha_composite(bezel,(6,26)); preview.save(D/'custom_sample.png')
for name in ['window_body','art_frame','custom_sample']:
 im=Image.open(D/(name+'.png')); im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(D/(name+'_review_4x.png')); im.resize((im.width//2,im.height//2),Image.Resampling.NEAREST).save(D/(name+'_half.png'))
colors=set(); records={}
for name,size in [('window_body',(264,352)),('art_frame',(252,120))]:
 im=Image.open(D/(name+'.png')); ar=np.array(im); al=set(np.unique(ar[:,:,3]).tolist()); cs=set(map(tuple,ar[ar[:,:,3]>0,:3])); colors |=cs
 assert im.size==size and al<= {0,255}
 records[name]={'dimensions':list(im.size),'alpha_values':sorted(al),'opaque_colors':len(cs),'sha256':hashlib.sha256((D/(name+'.png')).read_bytes()).hexdigest()}
assert np.all(np.array(c)[:,:,3]==255)
assert np.all(b[4:116,4:248,3]==0)
assert len(colors)<=16
records.update({'combined_opaque_colors':len(colors),'art_window':[4,4,244,112],'composite_placement':[6,26],'in_game_checked':False,'held_parts':['C3','C4','C5','C6','C7']})
(D/'validation.json').write_text(json.dumps(records,indent=2)+'\n')
(D/'processing.json').write_text(json.dumps({'raw':'raw/custom_generated.png','raw_dimensions':list(Image.open(D/'raw/custom_generated.png').size),'frame_geometry_reference':str(H.relative_to(D.parents[4])),'normalization':'HUD 8px corner/edge reflow, exact flat fills and title/footer bands; C2 reduced to 4px bezel and exact rectangular alpha aperture','palette':['#%02x%02x%02x'%co for co in sorted(colors)],'raw_pixel_grid_exact':False,'delivery_scale':1,'preview_scales':[4,0.5]},indent=2)+'\n')
print(json.dumps(records))
