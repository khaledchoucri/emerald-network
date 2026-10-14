#!/usr/bin/env python3
"""Reproduce ASSET-008 v002 native source delivery; run from repository root."""
import sys,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path('poc/assets/generated/_tools').resolve()))
from prepare_samples import source_cell,fit,fixed_palette,pack,report_image,uniform_nineslice,nineslice_checks,GREYS
OUT=Path(__file__).parent
cfg=json.loads((OUT/'processing.json').read_text()); log=[];results=[]
palette=cfg['neutral_palette']
def save(name,frames,size,gray=False):
 im=pack(frames);p=OUT/(name+'.png');im.save(p)
 results.append(report_image(p,(size[0]*len(frames)+8*(len(frames)-1),size[1]),max_colors=5 if gray else 16,palette=GREYS if gray else palette,cells=(size[0],len(frames))))
 im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(OUT/(name+'_review_4x.png'))
 im.resize((max(1,im.width//2),max(1,im.height//2)),Image.Resampling.NEAREST).save(OUT/(name+'_review_half.png'))
 return im
for job in cfg['jobs']:
 imgs=[source_cell({'input':str(OUT/'raw'/job['raw']), 'crop':c,'trim_alpha':True}, {'minimum_component_pixels':job.get('minimum_component_pixels',32)},log) for c in job['crops']]
 size=tuple(job['size']);frames=[]
 common=min((size[0]-4)/max(x.width for x in imgs),(size[1]-4)/max(x.height for x in imgs))
 for n,im in enumerate(imgs):
  if job.get('common_scale',False):
   new=(max(1,round(im.width*common)),max(1,round(im.height*common))); im=im.resize(new,Image.Resampling.NEAREST);frame=Image.new('RGBA',size);frame.paste(im,((size[0]-new[0]-1 if job['name']=='trail' else (size[0]-new[0])//2),(size[1]-new[1])//2))
  else:frame=fit(im,size,log,margin=2)
  frame,_=fixed_palette(frame,GREYS if job.get('gray') else palette)
  if job['name']=='emblem' and n>=3:
   # Flatten/reserve the engine-rendered symbol square, as on v001 card.
   d=ImageDraw.Draw(frame)
   d.rectangle((25,25,102,102),fill='#161b2d')
   d.rectangle((31,31,96,96),outline='#69758c',width=1)
   d.line((31,31,96,31),fill='#b2bed2',width=1)
   d.line((31,31,31,96),fill='#b2bed2',width=1)
  if job['name']=='shine':
   # Common source streak, native height32, move its centre into each quarter.
   tmp=fit(im,(24,32),log,margin=0);tmp,_=fixed_palette(tmp,palette)
   frame=Image.new('RGBA',(240,36));frame.paste(tmp,(18+n*60,2))
  if job['name']=='banner':frame=uniform_nineslice(frame,10)
  frames.append(frame)
 if job['name']=='turning':
  front=Image.open(OUT.parent/'v001/card_front.png').convert('RGBA');back=Image.open(OUT.parent/'v001/card_back.png').convert('RGBA')
  # Optional review note: inset 1px outline without modifying approved v001.
  ImageDraw.Draw(front).rectangle((52,68,67,83),outline='#69758c',width=1)
  frames=[front,*frames,back];save('card_flip',frames,(72,88));front.save(OUT/'card_front.png')
 else:save(job['name'],frames,size,job.get('gray',False))
 if job['name']=='emblem':frames[-1].save(OUT/'emblem_static.png')
 if job['name']=='banner':log.append({'nineslice10':nineslice_checks(frames[0],10)})
 # Simple diagnostic playback. GIF changes transparency encoding; PNG sheets authoritative.
 if len(frames)>1 and job['name']!='type_symbols':
  preview=[]
  for f in frames:
   bg=Image.new('RGBA',f.size,'#071833');bg.alpha_composite(f);preview.append(bg.convert('RGB').resize((f.width*4,f.height*4),Image.Resampling.NEAREST))
  preview[0].save(OUT/(job['name']+'_playback.gif'),save_all=True,append_images=preview[1:],duration=job.get('duration_ms',34),loop=0)
validation={'results':results,'all_passed':all(r['passed'] for r in results),'operations':log,'runtime_validated':False}
arr=np.asarray(Image.open(OUT/'type_symbols.png'))
hashes=[hashlib.sha256(arr[:,n*40:n*40+32].tobytes()).hexdigest() for n in range(17)]
validation['symbol_checks']={'count':17,'all_nonempty':all(bool(arr[:,n*40:n*40+32,3].any()) for n in range(17)),'distinct_pixel_masks':len(set(hashes))==17,'type_order':cfg['type_order']}
(OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
assert validation['all_passed'],validation
print('Validated',len(results),'sheets')
